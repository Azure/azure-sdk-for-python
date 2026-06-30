# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared state and lifecycle for the sync and async Rust backends.

Terminology used throughout this module:

* **python wrapper** -- the plain-Python SDK layer this module lives in. The two Rust
  backends, ``RustBackend`` (sync) and ``AsyncRustBackend`` (async), both mix in the
  ``RustBackendShared`` class defined here.
* **binding** -- the compiled extension ``azure.cosmos._rust`` the wrapper calls into.
* **rust driver** -- the engine (``CosmosDriver``) the binding builds on the first
  operation and identifies by the handle ``init_client`` returns.
* **the guard** -- the ``_driver_registry`` strict-isolation bookkeeping; this module
  is what calls ``register_client_config`` / ``release_client_config`` on it.
* **the bridge** -- ``AsyncTokenCredentialBridge``; when the credential is async this
  module is what stops the bridge's background thread on close.

The 50,000-foot view -- this module is shared plumbing, not a feature. The two Rust
backends do the same bookkeeping for every client (here *client* means a
``CosmosClient`` object the customer creates -- not the customer themselves): store the
endpoint/credential/config, hold the driver handle and its lock, compute the credential
key, register with the engine-isolation guard on open, and undo all of that on close.
The only thing they differ on is *how they build and run the handle* (sync vs async).

So this module puts the identical half in one place -- the mixin class
``RustBackendShared`` plus one helper function. Motivation: if it did not exist, each
backend would carry its own copy of this delicate open/close lifecycle, and the moment
the two copies drift you get real bugs -- one backend forgets to release its guard
registration (leaks the guard's live-client count, so strict mode starts raising
against engines that are already gone), or forgets to stop the bridge's background
thread (it keeps running after close), or computes the credential key differently
(guard keyed inconsistently between the sync and async paths). One copy = those cannot
happen on only one side.


This module imports ``base`` and ``_driver_registry``; neither imports it, so there is
no import cycle.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Optional

from .base import PreparedClientConfig, init_client_args
from ._driver_registry import make_credential_key, register_client_config, release_client_config

_LOGGER = logging.getLogger(__name__)


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Stop our async-credential bridge if ``credential`` is one, and never raise.

    It looks for the private ``_close_cosmos_async_bridge`` method (this is *duck
    typing* -- we check whether the object *has* that method rather than checking its
    type) instead of ``isinstance``, so it only ever closes *our own* wrapper (the
    bridge), never the customer's credential, whose lifetime they own -- a sync
    credential simply has no such method and is left untouched.

    "Quietly" = it swallows and logs any error, because this runs on close/finalizer
    paths where a teardown error must not propagate and mask the close. Shared by both
    backends so the check lives in exactly one place.
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
    and register with the guard, then adds only its own handle-build logic.

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
        """Store all shared fields and register with the guard last.

        Real detail that matters: it sets ``_config_released = True`` *before*
        registering and flips it to ``False`` only *after* registration succeeds -- so a
        construction that fails at registration never tries to release something it
        never registered. (It is called from each backend's ``__init__`` after that
        backend has set its own fields, so every attribute the finalizer might touch
        already exists.) It also computes ``_credential_key`` once -- a token credential
        by object identity, or a master key by fingerprint, never the plaintext secret
        -- so open and close key the guard identically.
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
        # The handle init_client returns, naming the driver-side client (which owns
        # the connection pool, auth, and routing). Built on the first operation and
        # reused; None until then. The lock guards reading and setting the handle.
        self._handle = None
        self._handle_lock = threading.Lock()
        # Register against the endpoint last: in strict isolation mode this raises if
        # a live client already targets the endpoint with a different config or
        # credential. Start _config_released True so a construction that fails here
        # never releases a registration it never made; set it False only once
        # registration succeeds.
        self._config_released = True
        register_client_config(
            endpoint,
            client_config,
            credential_key=self._credential_key,
            strict=strict_isolation,
        )
        self._config_released = False

    def _release_config_once(self) -> None:
        """Drop this client's guard registration exactly once.

        Why once matters: the guard counts live clients (``CosmosClient`` objects) per
        engine, so releasing twice would over-decrement it and could evict an entry
        other clients still share. The ``_handle_lock`` plus the ``_config_released``
        flag guarantee exactly-once no matter how it is reached -- handle never built,
        ``close()`` called twice, or close racing the finalizer.
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
        """Return the positional args for the binding's ``init_client`` call, in one place.

        Because both backends build their handle from these exact args, this is what
        guarantees the sync and async paths ask the binding for the same engine identity
        rather than drifting apart.
        """
        return init_client_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """On close, stop the bridge's background thread (only our bridge; a customer
        credential is left alone).

        Skip it and the background thread -- plus the credential's event loop running on
        it -- keeps running after the client is gone. Thin wrapper over
        ``close_credential_bridge_quietly(self._token_credential)``.
        """
        close_credential_bridge_quietly(self._token_credential)
