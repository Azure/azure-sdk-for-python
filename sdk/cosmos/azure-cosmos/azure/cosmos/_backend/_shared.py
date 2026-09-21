# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Share driver setup, page checks, and cleanup between both Rust backends.

The binding is the compiled extension that Python uses to call Rust. It creates
drivers and shares the runtime, the Rust resources used to run their work.
Proxy and connection timeout settings apply to that shared runtime.

Constructing a backend checks settings against an existing runtime without
creating one or reserving settings. The first operation acquires a driver.
The binding checks again then, because another client may have initialized
the runtime in the meantime.
"""
from __future__ import annotations

import logging
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Tuple, Type, Union

from azure.core.exceptions import ServiceResponseError

from ._binding_conversions import acquire_driver_handle_args
from .contracts import PreparedClientConfig, PreparedQuery
from .errors import PagePreflightError, UnsupportedQueryError
from .operations import get_page_binding_method
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
    It is packaged in .libs beside the Rust extension. Set the directory before
    driver creation so the customer need not configure the packaged copy.

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
    that check, driver errors could bypass conversion to the SDK exceptions
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

    The backends convert that error into azure-core's ``ServiceResponseError``.
    This means the wrapper received no HTTP response, not that the request was
    never sent or that the service backend performed no work.
    """
    return _binding_error_type(rust_module, "_DriverTransportError")


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding class raised when the driver cannot finish a query.

    The Rust backends translate it to ``UnsupportedQueryError``.
    It is an execution failure, not permission to retry through Python.
    """
    return _binding_error_type(rust_module, "_UnsupportedQueryFeatureError")


@contextmanager
def page_dispatch_errors(
    deadline: Optional[float],
    unsupported_query_error: _BindingErrorMatcher,
    transport_error: _BindingErrorMatcher,
) -> Iterator[None]:
    """Convert page-fetch errors to SDK errors without catching cancellation."""
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
    prepared: PreparedQuery,
    binding: Optional[Any],
    get_dispatch: Callable[[Optional[str]], Optional[Any]],
    backend_name: str,
    suffix: str = "",
) -> None:
    """Check for the required page-fetch function without creating a driver."""
    if binding is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages: the compiled azure.cosmos._rust "
            "module is not present in this environment. Build it with "
            "`maturin develop` from the repo root."
        )
    uses_cursor = prepared.cursor is not None
    method = get_page_binding_method(prepared.op, uses_cursor=uses_cursor)
    dispatch = get_dispatch(method)
    if uses_cursor and method is not None and dispatch is None:
        raise RuntimeError(
            f"The compiled azure.cosmos._rust extension does not export {method}{suffix}; "
            "rebuild it from the current source."
        )
    if dispatch is None:
        raise PagePreflightError(
            f"{backend_name}.execute_pages does not yet support op={prepared.op!r}."
        )


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Release this client's use of an async-credential bridge.

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
    """Clean up an unused backend's resources on a separate thread when possible.

    Pass only the credential and driver handle to that thread, not the backend
    object being deleted. If a thread cannot start, clean up on the calling thread.
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


class RustBindingShared:
    """Store client settings and provide cleanup used by both Rust backends.

    Each backend calls _init_shared during construction. The sync and async
    classes separately decide how to wait for driver creation and operations.
    """

    def _init_shared(
        self,
        endpoint: str,
        master_key: Optional[str],
        client_config: Optional[PreparedClientConfig],
        token_credential: Optional[Any],
    ) -> None:
        """Store client state and check initialized runtime settings.

        This check does not create the shared Rust runtime or reserve its
        settings. Driver creation checks again in case another client got there
        first.
        """
        self._endpoint = endpoint
        self._master_key = master_key
        # Async credentials arrive wrapped in a bridge that runs their token
        # requests on its own thread. Master-key clients have no token credential.
        self._token_credential = token_credential
        # Pass these settings, such as preferred regions, when acquiring a driver.
        self._client_config = client_config
        # The binding returns a string identifying this client's driver on first
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
            # Construction failed; the factory will release the credential bridge.
            self._token_credential = None
            raise

    def abort_construction(self) -> None:
        """Mark a failed client construction closed and release its credential bridge."""
        with self._driver_handle_lock:
            self._closing = True
        self._close_token_credential_bridge()

    def _initialize_driver(self, binding: Any) -> str:
        """Acquire a driver; the caller handles close racing with this call."""
        configure_packaged_query_plan_interop(binding)
        return binding.acquire_driver_handle(*self._acquire_driver_handle_args())

    def _acquire_driver_handle_args(self) -> tuple[Any, ...]:
        """Build the same driver-creation arguments for sync and async clients."""
        return acquire_driver_handle_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """Release this client's bridge once, leaving the customer's credential open."""
        close_credential_bridge_quietly(self._take_token_credential_for_close())

    def _take_token_credential_for_close(self) -> Optional[Any]:
        with self._driver_handle_lock:
            credential = self._token_credential
            self._token_credential = None
            return credential
