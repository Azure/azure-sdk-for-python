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
* **the guard** -- the ``_driver_registry`` module: a per-process ledger that counts
  how many live clients point at each engine for an account. This is a **separate**
  Python-side ledger from the binding's own driver cache and reference count (above):
  the binding's count does the real driver pooling, while the guard is used only for
  *strict-isolation* enforcement. In strict-isolation mode it raises when a new client
  would force the binding to build a *second* engine for an account that already has
  one.
* **guard registration** -- adding this client to that ledger, the
  ``register_client_config(...)`` call (count +1). Releasing is
  ``release_client_config(...)`` (count -1).
* **the bridge** -- ``AsyncTokenCredentialBridge``, the wrapper used *only* when the
  customer passes an async credential. It runs a background thread so the (sync) rust
  driver can fetch tokens.

The 50,000-foot view -- what this module is. There are two Rust backends,
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
code, and the moment the two copies drift you get a bug on one side only -- e.g. the
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
import threading
from typing import Any, Optional

from .base import PreparedClientConfig, init_client_args
from ._driver_registry import (
    make_credential_key,
    register_client_config,
    register_proxy_policy,
    register_transport_timeout_policy,
    release_client_config,
)

_LOGGER = logging.getLogger(__name__)


class _UnmatchableDriverError(BaseException):
    """An exception class that is never raised.

    It exists so that code catching the binding's ``DriverTransportError`` still works
    on an older ``_rust`` build that does not ship that class. Catching this
    never-thrown stand-in is a safe do-nothing.
    """


def driver_transport_error_type(rust_module: Optional[Any]) -> type:
    """Hand back the binding's ``DriverTransportError`` class for ``except`` use.

    Why it exists: the backends convert that error into azure-core's
    ``ServiceResponseError``. Without this, a transport failure (a failure with *no*
    server response -- a client-side validation error or a pre-HTTP timeout) would reach
    the customer as a raw ``RuntimeError``, and their
    ``except (ServiceRequestError, ServiceResponseError)`` handlers and the SDK's
    automatic transport retries would silently stop working on the Rust path.

    On an older binding that does not export the type, it returns the never-raised
    sentinel, so nothing is converted and the original error passes through unchanged.
    """
    exc = getattr(rust_module, "DriverTransportError", None) if rust_module is not None else None
    if isinstance(exc, type) and issubclass(exc, BaseException):
        return exc
    return _UnmatchableDriverError


def driver_unsupported_query_error_type(rust_module: Optional[Any]) -> type:
    """Return the binding error used when the driver rejects a query plan."""
    exc = (
        getattr(rust_module, "UnsupportedQueryFeatureError", None)
        if rust_module is not None
        else None
    )
    if isinstance(exc, type) and issubclass(exc, BaseException):
        return exc
    return _UnmatchableDriverError


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Stop our async-credential bridge on close, and never raise.

    It checks whether the object *has* the private ``_close_cosmos_async_bridge`` method
    (duck typing -- a "does it have this method" check, not an ``isinstance`` type
    check), so it only ever shuts down *our own* bridge -- never the customer's own
    credential, whose lifetime the customer controls (a sync credential simply has no
    such method and is left untouched).

    Why it exists: without it, the bridge's background thread keeps running after close.
    And without the "quietly" part -- it swallows and logs any error -- a teardown error
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
        identity, or a master key by fingerprint, never the plaintext secret -- so open
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
        # master-key fingerprint -- never the plaintext secret). Computed once and
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
        # lazy-initialization backstop.
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

        Without the once-guarantee, releasing twice would over-count-down the guard and
        could drop an engine entry other clients still share. A lock plus the
        ``_config_released`` flag make it exactly-once no matter how close is reached --
        handle never built, ``close()`` called twice, or ``close()`` racing the object's
        finalizer.
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
        engine identity instead of drifting apart.
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
