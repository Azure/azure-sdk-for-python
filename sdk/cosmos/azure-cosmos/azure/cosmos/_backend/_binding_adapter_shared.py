# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Share setup, binding checks, and cleanup between the two Python wrappers.

BindingAdapter and AsyncBindingAdapter reuse this Python code, but retain separate
per-client fields. The binding creates CosmosDriver objects through one
CosmosDriverRuntime with shared connection settings.

Construction checks any completed CosmosDriverRuntime initialization without
creating that object or reserving its settings. Driver acquisition checks again,
because another client may have initialized CosmosDriverRuntime in the meantime.
"""
from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Tuple, Type, Union

from azure.core.exceptions import ServiceResponseError
from azure.core.utils import CaseInsensitiveDict

from ._binding_conversions import acquire_driver_handle_args
from .contracts import PreparedClientConfig, PreparedPageRequest, PreparedRequest
from .errors import PagePreflightError, UnsupportedQueryError
from .operations import get_page_binding_function_name
from ..exceptions import CosmosClientTimeoutError

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
    """
    return _binding_error_type(rust_module, "_DriverTransportError")


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding class raised when the driver cannot finish a query.

    The Python wrapper translates it to ``UnsupportedQueryError``.
    It is an execution failure, not permission for fallback to the legacy path.
    """
    return _binding_error_type(rust_module, "_UnsupportedQueryFeatureError")


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
    supplied; otherwise let it propagate unchanged. Convert the binding's
    unsupported-query error to UnsupportedQueryError and its transport error
    to ServiceResponseError, preserving the original exception as the cause.

    Cancellation propagates unchanged, rather than becoming a timeout or
    transport error. This does not guarantee that the service backend stopped
    work already received. No converted error permits repeating the operation
    through the legacy path.
    """
    try:
        yield
    except TimeoutError as exc:
        if deadline is None:
            raise
        raise CosmosClientTimeoutError(error=exc) from exc
    except unsupported_query_error as exc:
        raise UnsupportedQueryError(str(exc)) from exc
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
    A known feed-cursor operation whose required function is missing instead
    raises RuntimeError: the binding must be rebuilt, not treated as an
    optional unsupported operation. Any permitted choice of the legacy path
    belongs to the caller's migration policy, not this check.
    """
    if binding is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages: the compiled azure.cosmos._rust "
            "binding is not present in this environment. Build it with "
            "`maturin develop` from the repo root."
        )
    uses_cursor = prepared.cursor is not None
    binding_function_name = get_page_binding_function_name(prepared.op, uses_cursor=uses_cursor)
    binding_function = lookup_binding_function(binding_function_name)
    if uses_cursor and binding_function_name is not None and binding_function is None:
        raise RuntimeError(
            f"The compiled azure.cosmos._rust binding does not export {binding_function_name}{suffix}; "
            "rebuild it from the current source."
        )
    if binding_function is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages does not yet support op={prepared.op!r}."
        )


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Release this client's use of an async credential bridge.

    The bridge runs async token requests for the binding. Its last user requests
    shutdown of the background thread. Log cleanup failures, and never close
    the customer's credential: the customer app owns it.
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


def finalize_backend_resources(credential: Optional[Any], driver_handle: Optional[str], binding: Any) -> None:
    """Attempt last-resort cleanup of an abandoned Python wrapper's resources.

    Explicit close is the normal path. If a wrapper object is discarded with
    resources still attached, its finalizer passes the detached credential
    and driver handle here, without retaining the wrapper object itself.

    A background thread releases this client's async credential bridge and
    then attempts to release its driver handle. The customer's credential is
    not closed. If thread startup raises RuntimeError, attempt the same
    cleanup on the calling thread; finalization is not always nonblocking.
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

    try:
        threading.Thread(target=teardown, name="cosmos-rust-finalizer", daemon=True).start()
    except RuntimeError:
        # Python may refuse new threads during shutdown; still attempt cleanup.
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

    The two classes separately decide how to wait for driver acquisition
    and operations. Acquisition may reuse an existing CosmosDriver object.
    """

    def _init_shared(
        self,
        endpoint: str,
        master_key: Optional[str],
        client_config: Optional[PreparedClientConfig],
        token_credential: Optional[Any],
    ) -> None:
        """Retain this client's inputs and check initialized CosmosDriverRuntime settings.

        The customer app supplies these values once during client construction.
        Later driver acquisition uses the saved values.

        The Python wrapper retains them like this::

            CosmosClient
                -> _adapter: BindingAdapter object
                    -> _endpoint: supplied account address
                    -> _master_key: supplied account key
                    -> _client_config: PreparedClientConfig
                        -> preferred_locations: ("West US",)

        This example uses account-key authentication. The asynchronous
        CosmosClient retains an AsyncBindingAdapter with the same fields.
        Both adapter classes are Python wrapper code, not the Rust driver.

        The Python wrapper knows this client's requested settings; the binding
        knows whether CosmosDriverRuntime has already been initialized and
        which settings were recorded. Ask the binding to check compatibility
        now so a known conflict is reported during client construction.

        For example, requesting a five-second connection timeout fails this
        check if CosmosDriverRuntime already uses two seconds. The check does
        not create CosmosDriverRuntime or reserve settings. Driver acquisition
        checks again because another client may initialize it after this check.
        """
        self._endpoint = endpoint
        self._master_key = master_key
        # Async credentials arrive in an async credential bridge that runs token
        # requests on its own thread. Master-key clients have no token credential.
        self._token_credential = token_credential
        # Pass these settings, such as preferred regions, when acquiring a driver.
        self._client_config = client_config
        # The binding returns a driver handle identifying a CosmosDriver on first
        # use. Reuse it until close; the subclasses coordinate changes with this lock.
        self._driver_handle: Optional[str] = None
        self._driver_handle_lock = threading.Lock()
        # Once close sets this flag, do not acquire another driver for the client.
        self._closing = False
        try:
            from azure.cosmos import _rust

            validate_runtime = getattr(_rust, "_validate_runtime_configuration", None)
            if not callable(validate_runtime):
                raise RuntimeError(
                    "The compiled azure.cosmos._rust extension does not export "
                    "_validate_runtime_configuration; rebuild it from the current source."
                )
            validate_runtime(client_config)
        except BaseException:
            # Construction failed; the factory will release the async credential bridge.
            self._token_credential = None
            raise

    def abort_construction(self) -> None:
        """Mark failed client construction closed and release its async credential bridge."""
        with self._driver_handle_lock:
            self._closing = True
        self._close_token_credential_bridge()

    def _with_client_headers(self, prepared: PreparedRequest) -> PreparedRequest:
        """Keep unrelated client defaults when a call overrides a header."""
        if self._client_config is None or not self._client_config.headers:
            return prepared
        headers = CaseInsensitiveDict(self._client_config.headers)
        headers.update(prepared.headers)
        return replace(prepared, headers=headers)

    def _initialize_driver(self, binding: Any) -> str:
        """Ask the binding to acquire a driver handle using this client's saved inputs.

        Pass the saved account address, credential, and PreparedClientConfig to
        acquire_driver_handle. The binding may create a CosmosDriver or reuse
        one it already retains; this method's name does not imply a new object.

        The returned handle identifies the retained driver. After the caller
        retains it, the references look like this::

            Python wrapper                         Binding
            _driver_handle = "H"                    driver cache
                                                       "H" -> DriverEntry
                                                                  -> CosmosDriver

        "H" is an illustration, not an actual handle. The handle is a lookup
        key, not the DriverEntry or CosmosDriver object itself.

        This method returns the handle without storing it. The caller decides
        whether to retain it and coordinates acquisition with a concurrent close.
        Acquiring the handle does not execute the pending database or item
        operation.
        """
        configure_packaged_query_plan_interop(binding)
        return binding.acquire_driver_handle(*self._acquire_driver_handle_args())

    def _acquire_driver_handle_args(self) -> tuple[Any, ...]:
        """Build the same driver-handle acquisition arguments for both client types."""
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
        """
        with self._driver_handle_lock:
            credential = self._token_credential
            self._token_credential = None
            return credential
