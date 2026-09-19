# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared lifecycle and page-dispatch policy for sync and async Rust backends.

A backend is the Python dispatch object; a driver is the native CosmosDriver
identified by a driver handle; the runtime owns process-wide transport settings.
Native acquisition is lazy and independent of Python client registration.

Construction reserves client identity and provisional process policies with
register_driver_client. Close guards against duplicate registration releases and releases
this client's hold on an async credential bridge when present. The Python registry
predicts isolation conflicts; its counts do not own native driver handles or their
reference counts.
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
from ._driver_registry import (
    make_driver_identity,
    register_driver_client,
    release_driver_client,
    freeze_runtime_policy,
)

_LOGGER = logging.getLogger(__name__)

_BindingErrorMatcher = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
_NO_BINDING_ERRORS: Tuple[Type[BaseException], ...] = ()

_QUERY_PLAN_INTEROP_DIRECTORY_ENV = "AZURE_COSMOS_QUERYPLANINTEROP_DIR"
_QUERY_PLAN_INTEROP_CONFIG_LOCK = threading.Lock()


def configure_packaged_query_plan_interop(rust_module: Optional[Any]) -> None:
    """Expose the wheel's QueryPlanInterop directory to the Rust driver.

    QueryPlanInterop is a separate compiled library that lets the Rust driver
    work out a cross-partition query's plan locally instead of asking the
    Cosmos DB gateway for it. Wheels ship it in ``azure/cosmos/.libs``, beside
    the compiled extension.

    The driver discovers the library through
    ``AZURE_COSMOS_QUERYPLANINTEROP_DIR``. It cannot infer the Python package's
    private ``.libs`` directory. Lazy driver initialization calls this before
    the first operation, not during package import. The pinned driver's loader
    accepts only this process-wide setting or the OS library search path; it
    has no per-client library-path option.

    Without this call a customer would have to set an environment variable to
    get a feature their wheel already contains -- and would have no way to know
    that was the difference.

    An explicit user setting wins. A source checkout with no ``.libs``
    directory leaves native library discovery and any query-plan fallback to
    the driver. This helper checks only the directory, not library loadability,
    supported query shapes, or whether a fallback request will succeed.
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

    Returns an empty tuple when there is no binding at all, which is a valid
    ``except`` target that matches nothing, so a core-python client can share
    this code without a branch.

    A binding that is present but does not export ``name`` is a hard error
    rather than a silent miss: the backends rely on catching these classes to
    convert driver failures into the azure-core exceptions customers handle. An
    missing exception class could bypass the intended Python error translation.
    Failing at lookup time identifies an incompatible extension; translation
    itself does not add a Python transport retry around the native operation.
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
    This classification means no HTTP response was returned to this wrapper,
    not that the request was never sent or that the service performed no work.
    """
    return _binding_error_type(rust_module, "_DriverTransportError")


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding class raised when the driver cannot finish a query.

    The Rust backends translate it to ``UnsupportedQueryError``.
    It is an execution failure, not the static preflight signal that permits
    selected migration paths to use legacy dispatch.
    """
    return _binding_error_type(rust_module, "_UnsupportedQueryFeatureError")


@contextmanager
def page_dispatch_errors(
    deadline: Optional[float],
    unsupported_query_error: _BindingErrorMatcher,
    transport_error: _BindingErrorMatcher,
) -> Iterator[None]:
    """Use identical page error mapping without intercepting async cancellation."""
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
    """Check dispatch availability without acquiring either kind of driver handle."""
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
    """Release an SDK credential-bridge hold, logging cleanup failures.

    Only the bridge exposes this private release method. Do not call the
    customer's credential.close(): the application owns that credential.
    The last bridge holder requests shutdown of its background thread.
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


class RustBindingShared:
    """Mixin holding the state and lifecycle common to both Rust backends.

    Each backend calls ``_init_shared`` from its ``__init__`` to store the common fields
    and register with the guard, then adds only its own logic to build and run the
    driver handle (``self._driver_handle``) -- the one thing the sync and async paths do
    differently.

    ``_init_shared`` sets all the shared attributes: ``_endpoint``, ``_master_key``,
    ``_token_credential``, ``_client_config``, ``_strict_isolation``,
    ``_driver_identity``, ``_driver_handle``, ``_driver_handle_lock``, ``_closing``, and
    ``_config_released``.
    """

    def _init_shared(
        self,
        endpoint: str,
        master_key: Optional[str],
        client_config: Optional[PreparedClientConfig],
        token_credential: Optional[Any],
        strict_isolation: bool = False,
    ) -> None:
        """Do all the open work, and register with the guard last, on purpose.

        It sets ``_config_released = True`` *before* registering and flips it to
        ``False`` only *after* registration succeeds -- so a client whose construction
        fails during registration never later tries to release a registration it never
        made. (It is called from each backend's ``__init__`` after that backend has set
        its own fields, so every attribute the finalizer might touch already exists.)

        It asks the binding for ``_driver_identity`` once, without initializing a
        runtime or driver, so open and close use the same native identity.
        It also enforces the
        process-wide proxy and transport-timeout policies *first*, so a runtime
        conflict fails before any registration exists to undo.
        """
        self._endpoint = endpoint
        self._master_key = master_key
        # A token credential (e.g. from azure-identity), or None for master-key
        # auth; credentials.resolve_credential sets exactly one. The driver calls
        # get_token on it when signing requests. An async credential arrives wrapped
        # as AsyncTokenCredentialBridge, which exposes a sync get_token.
        self._token_credential = token_credential
        # Client settings (e.g. preferred_locations) passed to the first acquire_driver_handle
        # call. None means there are none to pass.
        self._client_config = client_config
        self._strict_isolation = strict_isolation
        # The driver handle acquire_driver_handle returns: a key made from (endpoint,
        # credential, config) that names which rust driver this client uses (the
        # rust driver owns the connection pool, request signing, and region
        # routing). Built on the first operation and reused; None until then. The
        # lock guards reading and setting the handle.
        self._driver_handle: Optional[str] = None
        self._driver_handle_lock = threading.Lock()
        # Set by close() under _driver_handle_lock. Both backends check it before handing
        # out a handle, so a closed client refuses further work instead of quietly
        # building a second driver reference and carrying on as if it were open.
        self._closing = False
        # Register against the endpoint last: in strict isolation mode this raises if
        # a live client already targets the account with a different native identity.
        # Start _config_released True so a construction that fails here
        # never releases a registration it never made; set it False only once
        # registration succeeds.
        self._config_released = True
        # Proxy allowance and transport timeouts are process-global for the Rust
        # runtime, not per-account like the driver registration below. Enforce them
        # here before recording a registration; the binding checks them again later
        # in case the runtime is only started at that point.
        try:
            self._driver_identity = make_driver_identity(
                endpoint, master_key, client_config, token_credential
            )
            register_driver_client(
                endpoint,
                client_config,
                driver_identity=self._driver_identity,
                strict=strict_isolation,
            )
        except BaseException:
            # The factory's resolved_credential scope still owns this hold.
            self._token_credential = None
            raise
        self._config_released = False

    def _release_config_once(self) -> None:
        """Attempt this client's guard-registration release at most once.

        The lock and flag allow at most one call to ``release_driver_client``
        from this backend, including concurrent close/finalizer paths. The flag
        is set before that call, so a failed release is not retried here.
        """
        with self._driver_handle_lock:
            if self._config_released:
                return
            self._config_released = True
        release_driver_client(
            self._endpoint,
            self._client_config,
            driver_identity=self._driver_identity,
        )

    def abort_construction(self) -> None:
        """Synchronously unwind a public constructor before native initialization."""
        with self._driver_handle_lock:
            self._closing = True
        self._release_config_once()
        self._close_token_credential_bridge()

    def _initialize_driver(
        self, binding: Any,
        runtime_configuration: Callable[[], Optional[tuple[Optional[bool], Optional[float], Optional[float]]]],
    ) -> str:
        """Hold a reservation across init/close races and observe the real runtime."""
        register_driver_client(self._endpoint, self._client_config, self._driver_identity)
        try:
            configure_packaged_query_plan_interop(binding)
            return binding.acquire_driver_handle(*self._acquire_driver_handle_args())
        finally:
            try:
                settings = runtime_configuration()
                if settings is not None:
                    freeze_runtime_policy(settings)
            finally:
                release_driver_client(self._endpoint, self._client_config, self._driver_identity)

    def _acquire_driver_handle_args(self) -> tuple[Any, ...]:
        """Return the arguments for the binding's ``acquire_driver_handle``, in one place.

        Both backends use this conversion, so equal stored inputs produce the
        same argument mapping. Driver identity and acquisition remain native concerns.
        """
        return acquire_driver_handle_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """Release this client's bridge hold once, leaving the customer's credential open."""
        close_credential_bridge_quietly(self._take_token_credential_for_close())

    def _take_token_credential_for_close(self) -> Optional[Any]:
        with self._driver_handle_lock:
            credential = self._token_credential
            self._token_credential = None
            return credential
