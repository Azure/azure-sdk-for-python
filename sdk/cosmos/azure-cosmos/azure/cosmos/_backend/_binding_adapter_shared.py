# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Code shared by the sync and async adapters, BindingAdapter and AsyncBindingAdapter.

This covers client setup, connecting to the service, converting errors, and
cleanup. Each client keeps its own settings. Creating a client checks its
settings but does not connect to the service.
"""
from __future__ import annotations

import contextvars
import logging
import os
import sys
import threading
import time
from contextlib import contextmanager
from concurrent.futures import Future
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterator, Optional, Tuple, Type, Union

from azure.core.exceptions import ServiceResponseError
from azure.core.utils import CaseInsensitiveDict

from ._binding_conversions import acquire_driver_handle_args, response_exception_from_binding
from .contracts import PreparedClientConfig, PreparedPageRequest, PreparedRequest
from .errors import BindingProtocolError, PagePreflightError, UnsupportedQueryError, UNSUPPORTED_AGGREGATE_QUERY_MESSAGE
from .operations import get_page_binding_function_name
from ..exceptions import CosmosClientTimeoutError, CosmosHttpResponseError
from .._constants import _Constants
from ..runtime import CosmosRuntime

if TYPE_CHECKING:
    from .._rust import _DriverHandle

_LOGGER = logging.getLogger(__name__)

_BindingErrorMatcher = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
_NO_BINDING_ERRORS: Tuple[Type[BaseException], ...] = ()

_QUERY_PLAN_INTEROP_DIRECTORY_ENV = "AZURE_COSMOS_QUERYPLANINTEROP_DIR"
_QUERY_PLAN_INTEROP_CONFIG_LOCK = threading.Lock()


def configure_packaged_query_plan_interop(rust_module: Optional[Any]) -> None:
    """Let the driver find the query-planning library included in the package.

    QueryPlanInterop is a compiled library that helps the driver decide how to
    run a query across partitions without asking the service backend for a plan.
    It is packaged in .libs beside the compiled extension file. Set the directory
    before driver acquisition so the customer app need not configure the copy.

    An existing AZURE_COSMOS_QUERYPLANINTEROP_DIR setting wins. If .libs is
    absent, leave discovery to the driver. Finding the directory does not prove
    the library can load or handle a particular query.

    :param rust_module: Loaded native binding module, or None when unavailable.
    :type rust_module: typing.Any
    """
    if rust_module is None:
        return
    module_file = getattr(rust_module, "__file__", None)
    if not module_file or _QUERY_PLAN_INTEROP_DIRECTORY_ENV in os.environ:
        return

    try:
        package_directory = Path(module_file).resolve().parent / ".libs"
        if package_directory.is_dir():
            with _QUERY_PLAN_INTEROP_CONFIG_LOCK:
                os.environ.setdefault(_QUERY_PLAN_INTEROP_DIRECTORY_ENV, str(package_directory))
    except OSError:
        _LOGGER.warning(
            "Unable to locate packaged QueryPlanInterop; queries will use Gateway fallback "
            "if the native library is not otherwise discoverable.",
            exc_info=True,
        )


def _binding_error_type(rust_module: Optional[Any], name: str) -> _BindingErrorMatcher:
    """Return one binding exception class for use in an ``except`` clause.

    An absent binding returns an empty tuple, which matches no exceptions.
    A present binding missing the required exception class raises here. Without
    that check, Rust driver errors could bypass conversion to the Python exceptions
    the customer app expects.

    :param rust_module: Loaded native binding module, or None.
    :type rust_module: typing.Any
    :param name: Required exception export name.
    :type name: str
    :return: Exception class, or an empty tuple when the binding is absent.
    :rtype: type[BaseException] or tuple[type[BaseException], ...]
    """
    if rust_module is None:
        return _NO_BINDING_ERRORS
    exc = getattr(rust_module, name, None)
    if isinstance(exc, type) and issubclass(exc, BaseException):
        return exc
    raise RuntimeError(
        "The compiled azure.cosmos._rust extension does not export {0}; "
        "rebuild it from the current source.".format(name)
    )


def driver_transport_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding's ``_DriverTransportError`` class for ``except`` use.

    The Python wrapper converts that error to azure-core's ``ServiceResponseError``.
    This means it received no HTTP response, not that the request was
    never sent or that the service backend performed no work.

    :param rust_module: Loaded native binding module, or None.
    :type rust_module: typing.Any
    :return: Transport exception class, or an empty tuple when no binding is loaded.
    :rtype: type[BaseException] or tuple[type[BaseException], ...]
    """
    return _binding_error_type(rust_module, "_DriverTransportError")


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding class raised when the driver cannot finish a query.

    The Python wrapper translates it to ``UnsupportedQueryError``.
    It is an execution failure, not permission for fallback to the legacy path.

    :param rust_module: Loaded native binding module, or None.
    :type rust_module: typing.Any
    :return: Unsupported-query exception class, or an empty tuple without a binding.
    :rtype: type[BaseException] or tuple[type[BaseException], ...]
    """
    return _binding_error_type(rust_module, "_UnsupportedQueryFeatureError")


def is_credential_error(error: BaseException) -> bool:
    """Read binding provenance without invoking credential exception overrides.

    :param error: Exception returned by a binding call.
    :type error: BaseException
    :return: Whether the binding restored this Python credential exception.
    :rtype: bool
    """
    attributes = BaseException.__dict__["__dict__"].__get__(error)
    return attributes.get("_cosmos_credential_error") is True


def operation_timeout_error(error: TimeoutError) -> CosmosClientTimeoutError:
    """Preserve a diagnostic-backed throttle status without inventing response details.

    :param error: Timeout carrying optional binding throttle diagnostics.
    :type error: TimeoutError
    :return: Client timeout whose cause preserves verified throttle status when available.
    :rtype: ~azure.cosmos.exceptions.CosmosClientTimeoutError
    """
    attributes = BaseException.__dict__["__dict__"].__get__(error)
    if "_cosmos_timeout_throttle_status" not in attributes:
        return CosmosClientTimeoutError(error=error)
    status = attributes["_cosmos_timeout_throttle_status"]
    if not isinstance(status, tuple) or len(status) != 2:
        raise BindingProtocolError("The binding returned invalid timeout throttle status")
    # Exact integers exclude bool and subclasses from native diagnostic fields.
    if (
        type(status[0]) is not int  # pylint: disable=unidiomatic-typecheck
        or status[0] != 429
        or type(status[1]) is not int  # pylint: disable=unidiomatic-typecheck
        or not 0 <= status[1] < 2**32
    ):
        raise BindingProtocolError("The binding returned invalid timeout throttle status")
    cause = CosmosHttpResponseError(
        status_code=status[0],
        sub_status=status[1] or None,
        message=(
            "The last completed request before the operation timeout returned HTTP 429; "
            "response details are unavailable."
        ),
    )
    return CosmosClientTimeoutError(error=cause)


@contextmanager
def page_binding_call_errors(
    deadline: Optional[float],
    unsupported_query_error: _BindingErrorMatcher,
    transport_error: _BindingErrorMatcher,
) -> Iterator[None]:
    """Give both Python wrappers the same error conversions for a page fetch.

    When the customer app reads a page of orders, the Python wrapper first
    checks that the required binding function exists. That check is preflight:
    it happens before driver acquisition and outside this helper.

    After acquiring a driver handle and preparing the request, both wrappers
    use this helper around a ``with`` block that:

        builds the binding-call arguments, including the remaining time budget
            -> calls the binding (and awaits its result on the async path)
            -> converts the returned response

    The time budget can expire while building the arguments. Entering this
    block therefore does not prove a request reached the service backend.

    Convert TimeoutError to CosmosClientTimeoutError only when a deadline was
    supplied and the exception is not marked as a credential error; otherwise
    let it propagate unchanged. Convert the binding's
    unsupported-query error to UnsupportedQueryError and its transport error
    to ServiceResponseError, preserving the original exception as the cause.

    Cancellation propagates unchanged, rather than becoming a timeout or
    transport error. This does not guarantee that the service backend stopped
    work already received. No converted error permits repeating the operation
    through the legacy path.

    :param deadline: Absolute monotonic deadline, or None for no timeout conversion.
    :type deadline: float or None
    :param unsupported_query_error: Binding exception class or tuple of classes for unsupported queries.
    :type unsupported_query_error: type[BaseException] or tuple[type[BaseException], ...]
    :param transport_error: Binding exception class or tuple of classes for transport failures.
    :type transport_error: type[BaseException] or tuple[type[BaseException], ...]
    :return: Context manager translating page binding errors.
    :rtype: contextlib.AbstractContextManager[None]
    """
    try:
        yield
    except TimeoutError as exc:
        if deadline is None or is_credential_error(exc):
            raise
        raise operation_timeout_error(exc) from exc
    except unsupported_query_error as exc:
        message = str(exc)
        prefix, marker, feature = message.partition("unsupported query feature: ")
        if marker and (feature == "aggregates" or feature.startswith("aggregates ")):
            message = f"{prefix}{UNSUPPORTED_AGGREGATE_QUERY_MESSAGE}\nDetails: {feature}"
        raise UnsupportedQueryError(message) from exc
    except transport_error as exc:
        raise ServiceResponseError(message=str(exc)) from exc


def validate_page_request(
    prepared: PreparedPageRequest,
    binding: Optional[Any],
    lookup_binding_function: Callable[[Optional[str]], Optional[Any]],
    backend_name: str,
    suffix: str = "",
) -> None:
    """Check binding support before acquiring a driver or fetching a page.

    This check is preflight, not execution. For an orders query:

        no feed cursor -> require the query_items binding function
        feed cursor    -> require the fetch_page_with_cursor binding function

    The asynchronous Python wrapper looks up the corresponding async function.
    This helper neither acquires a driver handle nor fetches results.

    An absent binding or unsupported page operation raises PagePreflightError.
    A known page operation whose required export is missing or not callable
    raises RuntimeError: the binding must be rebuilt, not treated as an
    optional unsupported operation. Any permitted choice of the legacy path
    belongs to the caller's migration policy, not this check.

    :param prepared: Page request whose operation and cursor mode require validation.
    :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
    :param binding: Loaded binding module, or None.
    :type binding: typing.Any
    :param lookup_binding_function: Lookup accepting a binding export name or None.
    :type lookup_binding_function: typing.Callable
    :param backend_name: Adapter name included in error messages.
    :type backend_name: str
    :param suffix: Binding export suffix included in missing-function errors.
    :type suffix: str
    """
    if binding is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages: the compiled azure.cosmos._rust "
            "binding is not present in this environment. Build it with "
            "`maturin develop` from the repo root."
        )
    uses_cursor = prepared.cursor is not None
    binding_function_name = get_page_binding_function_name(prepared.op, uses_cursor=uses_cursor)
    if binding_function_name is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages does not yet support op={prepared.op!r}."
        )
    binding_function = lookup_binding_function(binding_function_name)
    if not callable(binding_function):
        raise RuntimeError(
            f"The compiled azure.cosmos._rust binding does not export {binding_function_name}{suffix} "
            "as a callable; rebuild it from the current source."
        )


def release_driver_handle_quietly(driver_handle: _DriverHandle, binding: Any) -> None:
    """Release one cache acquisition without exposing handles in cleanup errors.

    Other handles and in-flight operations can still retain the same driver.

    :param driver_handle: Owning handle whose cache acquisition should be released.
    :type driver_handle: ~azure.cosmos._rust._DriverHandle
    :param binding: Binding module that exports ``release_driver_handle``, if available.
    :type binding: typing.Any
    """
    release = getattr(binding, "release_driver_handle", None)
    if release is None:
        return
    try:
        release(driver_handle)
    except Exception:  # pylint: disable=broad-except
        # Binding exception text can contain the handle too.
        _LOGGER.debug("Failed releasing the driver handle")


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Release this client's use of an async credential bridge.

    The bridge runs async token requests for the binding. Its last user requests
    cancellation of its pending token calls. Log cleanup failures, and never close
    the customer's credential: the customer app owns it.

    :param credential: Stored credential or bridge whose SDK-owned use should be released.
    :type credential: typing.Any
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


def finalize_adapter_resources(credential: Optional[Any], driver_handle: Optional[_DriverHandle], binding: Any) -> None:
    """Attempt last-resort cleanup of an abandoned Python adapter's resources.

    Explicit close is the normal path. If an adapter is discarded with
    resources still attached, its finalizer passes the detached credential
    and driver handle here, without retaining the adapter itself.

    A background thread releases this client's async credential bridge and
    then attempts to release its driver handle. The customer's credential is
    not closed. During interpreter finalization, run cleanup on the calling
    thread without starting a worker. If worker startup otherwise raises
    RuntimeError, use the same synchronous cleanup and log the failure.
    Finalization is not always nonblocking.

    :param credential: Detached credential or bridge, or None.
    :type credential: typing.Any
    :param driver_handle: Detached owning driver handle, or None.
    :type driver_handle: ~azure.cosmos._rust._DriverHandle or None
    :param binding: Binding module exposing driver release.
    :type binding: typing.Any
    """
    if credential is None and driver_handle is None:
        return
    release = getattr(binding, "release_driver_handle", None)

    def teardown() -> None:
        try:
            close_credential_bridge_quietly(credential)
        finally:
            if driver_handle is not None and callable(release):
                try:
                    release(driver_handle)
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.debug("Failed releasing native resources during finalization")

    if sys.is_finalizing():
        teardown()
        return

    try:
        threading.Thread(target=teardown, name="cosmos-rust-finalizer", daemon=True).start()
    except RuntimeError:
        if not sys.is_finalizing():
            _LOGGER.warning("Could not start finalizer worker; cleaning up on the finalizing thread")
        teardown()


class BindingAdapterShared:
    """Provide common setup and cleanup for BindingAdapter and AsyncBindingAdapter.

    Both classes inherit these methods so a setup or cleanup correction can
    be made in one place. Each constructor calls _init_shared::

        BindingAdapter construction
            -> _init_shared stores fields on that BindingAdapter object

        AsyncBindingAdapter construction
            -> _init_shared stores fields on that AsyncBindingAdapter object

    There is no additional BindingAdapterShared object holding the settings.
    The classes share this implementation, not one set of client fields.

    The sync and async classes each decide how a caller waits for the client
    to connect and for operations to finish.
    """

    # Concrete constructors initialize these fields through _init_shared.
    _endpoint: str
    _master_key: Optional[str]
    _token_credential: Optional[Any]
    _client_config: Optional[PreparedClientConfig]
    _runtime: Optional[CosmosRuntime]
    _init_future: Optional[Future[_DriverHandle]]
    _driver_handle: Optional[_DriverHandle]
    _driver_handle_lock: Any
    _closing: bool

    def _init_shared(
        self,
        endpoint: str,
        master_key: Optional[str],
        client_config: Optional[PreparedClientConfig],
        token_credential: Optional[Any],
        runtime: Optional[CosmosRuntime] = None,
    ) -> None:
        """Save this client's inputs so later operations can use them.

        The customer app supplies these values once, when it creates the client.
        They are kept like this::

            CosmosClient
                -> _adapter: BindingAdapter object
                    -> _endpoint: supplied account address
                    -> _master_key: supplied account key
                    -> _client_config: PreparedClientConfig
                        -> preferred_locations: ("West US",)

        This example uses an account key. The async CosmosClient keeps the same
        fields on an AsyncBindingAdapter.

        If a runtime is passed in, it is kept and used later. If not, the default
        runtime is used when the client first connects to the service.

        Raise ValueError if the settings contain connection timeout, read timeout,
        or proxy settings, which belong to CosmosRuntime. Also raise ValueError for
        fault injection rules unless the SDK was built for testing.

        :param endpoint: Cosmos account endpoint URL.
        :type endpoint: str
        :param master_key: Account key, or None for token authentication.
        :type master_key: str or None
        :param client_config: Prepared client settings, or None for defaults.
        :type client_config: ~azure.cosmos._backend.contracts.PreparedClientConfig or None
        :param token_credential: Borrowed token credential, or None for account-key authentication.
        :type token_credential: typing.Any
        :param runtime: Explicit runtime to retain, or None to select the default at acquisition.
        :type runtime: ~azure.cosmos.runtime.CosmosRuntime or None
        """
        self._endpoint = endpoint
        self._master_key = master_key
        # The async adapter binds async credentials to the application loop on first use.
        # Master-key clients have no token credential.
        self._token_credential = token_credential
        if token_credential is not None:
            override = os.environ.get(_Constants.AAD_SCOPE_OVERRIDE) or None
            if override is not None:
                client_config = replace(
                    client_config or PreparedClientConfig(), aad_scope_override=override
                )
        # Pass these settings, such as preferred regions, when acquiring a driver.
        self._client_config = client_config
        self._runtime = runtime
        # Acquire during async __aenter__() or the first operation needing the driver.
        # Reuse the handle until close; subclasses coordinate changes with this lock.
        self._init_future: Optional[Future[_DriverHandle]] = None
        self._driver_handle: Optional[_DriverHandle] = None
        self._driver_handle_lock = threading.Lock()
        # Once close sets this flag, do not acquire another driver for the client.
        self._closing = False
        try:
            if runtime is not None and not isinstance(runtime, CosmosRuntime):
                raise TypeError("runtime must be CosmosRuntime or None.")
            try:
                from azure.cosmos import _rust
            except ImportError as error:
                raise ImportError(
                    f"The compiled Rust extension azure.cosmos._rust could not be loaded: {error}. "
                    "Install an azure-cosmos wheel built for this operating system, processor, "
                    "and Python version. A source checkout must build the extension first.",
                    name="azure.cosmos._rust",
                ) from error

            if not hasattr(_rust, "_DriverHandle"):
                raise RuntimeError(
                    "The compiled azure.cosmos._rust extension lacks owning driver handles; "
                    "rebuild it from the current source."
                )
            validate_runtime = getattr(_rust, "_validate_runtime_configuration", None)
            if not callable(validate_runtime):
                raise RuntimeError(
                    "The compiled azure.cosmos._rust extension does not export "
                    "_validate_runtime_configuration; rebuild it from the current source."
                )
            validate_runtime(client_config)
        except BaseException:
            # Creating the client failed, so drop the saved credential.
            self._token_credential = None
            raise

    def abort_construction(self) -> None:
        """Mark failed construction closed and clear runtime and credential references."""
        with self._driver_handle_lock:
            self._closing = True
            self._runtime = None
        self._close_token_credential_bridge()

    def _with_client_headers(self, prepared: PreparedRequest) -> PreparedRequest:
        """Keep unrelated client defaults when a call overrides a header.

        :param prepared: Request with per-call header overrides.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
        :return: Request containing merged headers, or the original when no defaults apply.
        :rtype: ~azure.cosmos._backend.contracts.PreparedRequest
        """
        if self._client_config is None or not self._client_config.headers:
            return prepared
        headers = CaseInsensitiveDict(self._client_config.headers)
        headers.update(prepared.headers)
        return replace(prepared, headers=headers)

    def _request_deadline(
        self, deadline: Optional[float], timeout: Optional[float] = None
    ) -> Optional[float]:
        """Preserve an outer budget; otherwise bound this request before driver setup.

        :param deadline: Existing absolute monotonic deadline, or None.
        :type deadline: float or None
        :param timeout: Per-request budget in seconds, or None to use the client default.
        :type timeout: float or None
        :return: Absolute monotonic deadline, or None if no timeout is configured.
        :rtype: float or None
        """
        if deadline is not None:
            return deadline
        if timeout is None and self._client_config is not None:
            timeout = self._client_config.operation_timeout_seconds
        return None if timeout is None else time.monotonic() + timeout

    def _start_driver_acquisition(self, binding: Any, logger: logging.Logger) -> Future[_DriverHandle]:
        """Share one pending attempt; the caller must hold _driver_handle_lock.

        A daemon worker avoids an interpreter-exit join or a shared pool queue.
        Capture inputs and context before close can clear the client's references.

        :param binding: Native module exposing driver acquisition and release.
        :type binding: typing.Any
        :param logger: Logger receiving acquisition failures.
        :type logger: logging.Logger
        :return: Shared future carrying the acquired driver handle or acquisition error.
        :rtype: concurrent.futures.Future[azure.cosmos._rust._DriverHandle]
        """
        future = self._init_future
        if future is None:
            args = self._acquire_driver_handle_args()
            context = contextvars.copy_context()
            future = Future()
            self._init_future = future
            try:
                threading.Thread(
                    target=context.run,
                    args=(self._acquire_driver_handle, future, binding, self._runtime, args, logger),
                    name="cosmos-driver-acquisition",
                    daemon=True,
                ).start()
            except BaseException as error:
                self._init_future = None
                future.set_exception(error)
                raise
        return future

    def _acquire_driver_handle(
        self,
        future: Future[_DriverHandle],
        binding: Any,
        runtime: Optional[CosmosRuntime],
        args: tuple[Any, ...],
        logger: logging.Logger,
    ) -> None:
        """Publish one acquisition, or release a late handle if close won.

        :param future: Shared future on which to publish the acquisition result or error.
        :type future: concurrent.futures.Future[azure.cosmos._rust._DriverHandle]
        :param binding: Native module exposing driver acquisition and release.
        :type binding: typing.Any
        :param runtime: Retained runtime, or None for the default.
        :type runtime: ~azure.cosmos.runtime.CosmosRuntime or None
        :param args: Captured positional driver acquisition arguments.
        :type args: tuple[typing.Any, ...]
        :param logger: Logger receiving acquisition failures.
        :type logger: logging.Logger
        """
        try:
            handle = self._initialize_driver(binding, runtime, acquisition_args=args)
            with self._driver_handle_lock:
                closed = self._closing
                if not closed:
                    self._driver_handle = handle
            if closed:
                release_driver_handle_quietly(handle, binding)
                raise RuntimeError(f"{type(self).__name__}: the client was closed during initialization.")
        # Publish every worker failure, including cancellation, so waiters cannot hang.
        except BaseException as error:  # pylint: disable=broad-exception-caught
            with self._driver_handle_lock:
                self._init_future = None
            future.set_exception(error)
            logger.debug("Rust driver initialization failed")
        else:
            with self._driver_handle_lock:
                self._init_future = None
            future.set_result(handle)

    def _initialize_driver(
        self,
        binding: Any,
        runtime: Optional[CosmosRuntime] = None,
        *,
        acquisition_args: Optional[tuple[Any, ...]] = None,
    ) -> _DriverHandle:
        """Ask the binding to acquire a driver handle using this client's saved inputs.

        The binding may create or reuse a driver; runtime=None selects its default
        runtime. The returned opaque handle retains that driver independently of
        cache eviction.

        This method returns the handle without storing it or executing the pending
        operation. The caller coordinates with close to store or release the handle.
        Account metadata failures use the same error conversion as container metadata.

        :param binding: Native module exposing driver acquisition.
        :type binding: typing.Any
        :param runtime: Explicit runtime, or None for the default.
        :type runtime: ~azure.cosmos.runtime.CosmosRuntime or None
        :keyword acquisition_args: Captured acquisition arguments, or None to build them from stored inputs.
        :paramtype acquisition_args: tuple[typing.Any, ...] or None
        :return: Owning handle retaining the selected driver.
        :rtype: ~azure.cosmos._rust._DriverHandle
        """
        configure_packaged_query_plan_interop(binding)
        # A background acquisition retains its inputs even if close clears the adapter.
        args = self._acquire_driver_handle_args() if acquisition_args is None else acquisition_args
        try:
            if runtime is not None:
                # The adapter is the internal consumer of the runtime's native handle.
                return binding.acquire_driver_handle(*args, runtime=runtime._handle)  # pylint: disable=protected-access
            return binding.acquire_driver_handle(*args)
        except _binding_error_type(binding, "_DriverResponseError") as exc:
            raise response_exception_from_binding(exc) from exc
        except driver_transport_error_type(binding) as exc:
            raise ServiceResponseError(message=str(exc)) from exc

    def _acquire_driver_handle_args(self) -> tuple[Any, ...]:
        """Build the same driver-handle acquisition arguments for both client types.

        :return: Positional binding arguments captured from this client's inputs.
        :rtype: tuple[typing.Any, ...]
        """
        return acquire_driver_handle_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """Release this client's async credential bridge, not the customer's credential."""
        close_credential_bridge_quietly(self._take_token_credential_for_close())

    def _take_token_credential_for_close(self) -> Optional[Any]:
        """Detach this client's stored credential for cleanup outside the lock.

        Read and clear the reference under the same lock so concurrent cleanup
        callers cannot both take it. Return None if no credential is stored,
        including when another caller has already taken it.

        This only transfers the reference. It does not release the async
        credential bridge or close the customer's credential.

        :return: Detached credential or bridge, or None when already removed.
        :rtype: typing.Any
        """
        with self._driver_handle_lock:
            credential = self._token_credential
            self._token_credential = None
            return credential
