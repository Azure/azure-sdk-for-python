# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared lifecycle for the sync and async Python Rust backends.

A backend is the Python dispatch object; a driver is the native CosmosDriver
identified by a driver handle; the runtime owns process-wide transport settings.
Native acquisition is lazy and independent of Python client registration.

Construction reserves client identity and provisional process policies with
register_driver_client. Close releases that registration exactly once and stops
an async credential bridge when present. The Python registry predicts isolation
conflicts; its counts do not own native driver handles or their reference counts.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Type, Union

from ._binding_conversions import acquire_driver_handle_args
from .contracts import PreparedClientConfig
from ._driver_registry import (
    make_credential_key,
    register_driver_client,
    release_driver_client,
    freeze_runtime_policy,
)

_LOGGER = logging.getLogger(__name__)

_BindingErrorMatcher = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
_NO_BINDING_ERRORS: Tuple[Type[BaseException], ...] = ()

_QUERY_PLAN_INTEROP_DIRECTORY_ENV = "AZURE_COSMOS_QUERYPLANINTEROP_DIR"


def configure_packaged_query_plan_interop(rust_module: Optional[Any]) -> None:
    """Expose the wheel's QueryPlanInterop directory to the Rust driver.

    QueryPlanInterop is a separate compiled library that lets the Rust driver
    work out a cross-partition query's plan locally instead of asking the
    Cosmos DB gateway for it. Wheels ship it in ``azure/cosmos/.libs``, beside
    the compiled extension.

    The driver discovers the library through
    ``AZURE_COSMOS_QUERYPLANINTEROP_DIR``. It cannot infer the Python package's
    private ``.libs`` directory, so this sets that environment variable before
    any driver client can lazily load the native library.

    Without this call a customer would have to set an environment variable to
    get a feature their wheel already contains -- and would have no way to know
    that was the difference.

    An explicit user setting wins. A source checkout with no ``.libs``
    directory keeps the driver's normal operating-system search and Gateway
    fallback. Queries stay correct either way; only the extra round trip differs.
    """
    if rust_module is None:
        return
    module_file = getattr(rust_module, "__file__", None)
    if not module_file or _QUERY_PLAN_INTEROP_DIRECTORY_ENV in os.environ:
        return

    try:
        package_directory = Path(module_file).resolve().parent / ".libs"
        if package_directory.is_dir():
            os.environ[_QUERY_PLAN_INTEROP_DIRECTORY_ENV] = str(package_directory)
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
    exception class that silently never matches would let a driver failure reach
    the customer as a raw ``RuntimeError``, so their
    ``except (ServiceRequestError, ServiceResponseError)`` handlers -- and the
    SDK's automatic transport retries -- would quietly stop working. Failing at
    lookup time points at the real cause: a stale compiled extension.
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
    """Return the binding's ``DriverTransportError`` class for ``except`` use.

    The backends convert that error into azure-core's ``ServiceResponseError``.
    A transport failure is one with *no* server response -- a client-side
    validation error, or a timeout before any HTTP exchange.
    """
    return _binding_error_type(rust_module, "DriverTransportError")


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> _BindingErrorMatcher:
    """Return the binding class raised when the driver cannot finish a query.

    The paged dispatch path catches it as its fallback signal and replays the
    page on the legacy transport, so an unsupported query feature degrades to a
    slower path instead of surfacing to the customer as an error.
    """
    return _binding_error_type(rust_module, "UnsupportedQueryFeatureError")


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Stop our async-credential bridge on close, and never raise.

    It checks whether the object *has* the private ``_close_cosmos_async_bridge`` method
    (duck typing -- a "does it have this method" check, not an ``isinstance`` type
    check), so it only ever shuts down *our own* bridge -- never the customer's own
    credential, whose lifetime the customer controls (a sync credential simply has no
    such method and is left untouched).

    Why it exists: without it, the bridge's background thread keeps running after close.
    And without the "quietly" part -- it catches and logs any error -- a teardown error
    on this close/finalizer path could hide the actual close.
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


class RustBackendShared:
    """Mixin holding the state and lifecycle common to both Rust backends.

    Each backend calls ``_init_shared`` from its ``__init__`` to store the common fields
    and register with the guard, then adds only its own logic to build and run the
    driver handle (``self._driver_handle``) -- the one thing the sync and async paths do
    differently.

    ``_init_shared`` sets all the shared attributes: ``_endpoint``, ``_master_key``,
    ``_token_credential``, ``_client_config``, ``_strict_isolation``,
    ``_credential_key``, ``_driver_handle``, ``_driver_handle_lock``, ``_closing``, and
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

        It computes ``_credential_key`` once -- an async/sync token credential by object
        identity, or a master key by a hash, never the plaintext secret -- so open
        and close identify this client to the guard the same way. It also enforces the
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
        # The credential's identity for the driver-isolation guard, keyed the same
        # way the binding keys its driver cache (token object identity, or a
        # master-key hash -- never the plaintext secret). Computed once and
        # reused on release so the registry counts stay balanced.
        self._credential_key = make_credential_key(master_key, token_credential)
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
        # a live client already targets the endpoint with a different config or
        # credential. Start _config_released True so a construction that fails here
        # never releases a registration it never made; set it False only once
        # registration succeeds.
        self._config_released = True
        # Proxy allowance and transport timeouts are process-global for the Rust
        # runtime, not per-account like the driver registration below. Enforce them
        # here before recording a registration; the binding repeats the checks as a
        # lazy-initialization fallback.
        try:
            register_driver_client(
                endpoint,
                client_config,
                credential_key=self._credential_key,
                strict=strict_isolation,
            )
        except BaseException:
            # The factory's resolved_credential scope still owns this hold.
            self._token_credential = None
            raise
        self._config_released = False

    def _release_config_once(self) -> None:
        """Release this client's guard registration exactly once.

        Without the once-guarantee, releasing twice would decrement the guard's count
        too far and could drop an driver entry other clients still share. A lock plus
        the ``_config_released`` flag make it exactly-once no matter how close is reached
        -- handle never built, ``close()`` called twice, or ``close()`` racing the
        object's finalizer.
        """
        with self._driver_handle_lock:
            if self._config_released:
                return
            self._config_released = True
        release_driver_client(
            self._endpoint,
            self._client_config,
            credential_key=self._credential_key,
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
        register_driver_client(self._endpoint, self._client_config, self._credential_key)
        try:
            return binding.acquire_driver_handle(*self._acquire_driver_handle_args())
        finally:
            try:
                settings = runtime_configuration()
                if settings is not None:
                    freeze_runtime_policy(settings)
            finally:
                release_driver_client(self._endpoint, self._client_config, self._credential_key)

    def _acquire_driver_handle_args(self) -> tuple[Any, ...]:
        """Return the arguments for the binding's ``acquire_driver_handle``, in one place.

        Because both backends build their driver handle from these exact same arguments,
        this is what guarantees the sync and async paths ask the binding for the same
        driver identity instead of diverging.
        """
        return acquire_driver_handle_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """Stop the bridge's background thread on close (only our bridge; a customer
        credential is left alone).

        A one-line forwarding method (a "thin wrapper" -- a small method that just calls
        another; *not* the Python-layer "python wrapper"). It calls
        ``close_credential_bridge_quietly(self._token_credential)``. Skip it and the
        bridge's background thread -- plus the credential's event loop running on it --
        keeps running after the client is gone.
        """
        close_credential_bridge_quietly(self._take_token_credential_for_close())

    def _take_token_credential_for_close(self) -> Optional[Any]:
        with self._driver_handle_lock:
            credential = self._token_credential
            self._token_credential = None
            return credential
