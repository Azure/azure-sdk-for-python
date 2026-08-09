# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared state and lifecycle for the sync and async Rust backends.

Terms, defined concretely (no abstract words):

* **client** -- one ``CosmosClient`` object the customer creates in their code (not the
  customer themselves).
* **binding** -- the compiled ``azure.cosmos._rust`` extension the Python code calls
  into.
* **rust driver** -- the engine (``CosmosDriver``) the binding builds; it owns the
  network connection pool, the auth (request signing), and region routing. The
  binding keeps **one** rust driver per distinct ``(endpoint, credential, config)``
  and reference-counts it, so several clients with the same settings share a single
  rust driver; the last client to close tears it down.
* **driver handle** -- the value ``init_client`` returns, stored as ``self._handle``.
  It is just a string key made from ``(endpoint, credential, config)`` -- it says
  *which* rust driver the client talks to (it is not the driver object and not the
  ``CosmosClient``). It is ``None`` until the client's first operation, then built
  once (in the ``_handle`` slot created by ``_init_shared``) and reused.
* **the guard** -- the ``_driver_registry`` module: a per-process record that counts
  how many live clients point at each engine for an account. This is a **separate**
  Python-side record from the binding's own driver cache and reference count (above):
  the binding's count does the real driver pooling, while the guard is used only for
  *strict-isolation* enforcement. In strict-isolation mode it raises when a new client
  would force the binding to build a *second* engine for an account that already has
  one.
* **guard registration** -- adding this client to that record, the
  ``register_client_config(...)`` call (count +1). Releasing is
  ``release_client_config(...)`` (count -1).
* **the bridge** -- ``AsyncTokenCredentialBridge``, the wrapper used *only* when the
  customer passes an async credential. It runs a background thread so the (sync) rust
  driver can fetch tokens.

The high-level view -- what this module is. There are two Rust backends,
``RustBackend`` (sync) and ``AsyncRustBackend`` (async). When a customer creates a
client, each backend does the same setup work; on close, the same teardown work. They
differ only in *how they build and run the driver handle* (sync vs async). This file
holds that identical setup/teardown half in one place -- the ``RustBackendShared``
mixin plus two module-level helper functions -- so both backends share it instead of
each keeping its own copy.

The setup ("open") work is: store the endpoint, credential, and config; compute the
credential's identity key; create the empty ``_handle`` slot and its lock; enforce the
process-wide proxy policy; and register this client with the guard.

The teardown ("close") work is: release the guard registration exactly once, and --
only if the credential is an async one -- stop the bridge's background thread. So it is
related to the bridge only on that one close step; for a normal master-key or
sync-token client, the bridge is not involved at all.

If this file did not exist, each backend would keep its own copy of that open/close
code, and the moment the two copies diverge, a bug appears on one side only -- e.g. the
async backend forgets to release its guard registration (the guard's live count leaks,
so strict mode starts wrongly rejecting new clients), or forgets to stop the bridge's
background thread (it keeps running after the client is closed), or computes the
credential key differently (the guard gets keyed inconsistently between the sync and
async paths). One shared copy makes those one-sided bugs impossible.

This module imports ``base`` and ``_driver_registry``; neither imports it, so there is
no import cycle.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Optional, Tuple, Type, Union

from .base import PreparedClientConfig, init_client_args
from ._driver_registry import (
    make_credential_key,
    register_client_config,
    register_proxy_policy,
    register_transport_timeout_policy,
    release_client_config,
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
    driver handle (``self._handle``) -- the one thing the sync and async paths do
    differently.

    ``_init_shared`` sets all the shared attributes: ``_endpoint``, ``_master_key``,
    ``_token_credential``, ``_client_config``, ``_strict_isolation``,
    ``_credential_key``, ``_handle``, ``_handle_lock``, and ``_config_released``.
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
        # auth; factory._resolve_credential sets exactly one. The driver calls
        # get_token on it when signing requests. An async credential arrives wrapped
        # as AsyncTokenCredentialBridge, which exposes a sync get_token.
        self._token_credential = token_credential
        # Client settings (e.g. preferred_locations) passed to the first init_client
        # call. None means there are none to pass.
        self._client_config = client_config
        self._strict_isolation = strict_isolation
        # The credential's identity for the engine-isolation guard, keyed the same
        # way the binding keys its driver cache (token object identity, or a
        # master-key hash -- never the plaintext secret). Computed once and
        # reused on release so the registry counts stay balanced.
        self._credential_key = make_credential_key(master_key, token_credential)
        # The driver handle init_client returns: a key made from (endpoint,
        # credential, config) that names which rust driver this client uses (the
        # rust driver owns the connection pool, request signing, and region
        # routing). Built on the first operation and reused; None until then. The
        # lock guards reading and setting the handle.
        self._handle = None
        self._handle_lock = threading.Lock()
        # Register against the endpoint last: in strict isolation mode this raises if
        # a live client already targets the endpoint with a different config or
        # credential. Start _config_released True so a construction that fails here
        # never releases a registration it never made; set it False only once
        # registration succeeds.
        self._config_released = True
        # Proxy allowance and transport timeouts are process-global for the Rust
        # runtime, not per-account like the engine registration below. Enforce them
        # here before recording a registration; the binding repeats the checks as a
        # lazy-initialization fallback.
        register_proxy_policy(client_config)
        register_transport_timeout_policy(client_config)
        register_client_config(
            endpoint,
            client_config,
            credential_key=self._credential_key,
            strict=strict_isolation,
        )
        self._config_released = False

    def _release_config_once(self) -> None:
        """Release this client's guard registration exactly once.

        Without the once-guarantee, releasing twice would decrement the guard's count
        too far and could drop an engine entry other clients still share. A lock plus
        the ``_config_released`` flag make it exactly-once no matter how close is reached
        -- handle never built, ``close()`` called twice, or ``close()`` racing the
        object's finalizer.
        """
        with self._handle_lock:
            if self._config_released:
                return
            self._config_released = True
        release_client_config(
            self._endpoint,
            self._client_config,
            credential_key=self._credential_key,
        )

    def _init_client_args(self) -> tuple[Any, ...]:
        """Return the arguments for the binding's ``init_client``, in one place.

        Because both backends build their driver handle from these exact same arguments,
        this is what guarantees the sync and async paths ask the binding for the same
        engine identity instead of diverging.
        """
        return init_client_args(
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
        close_credential_bridge_quietly(self._token_credential)
