# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Shared state and lifecycle for the sync and async Rust backends.

Both ``RustBackend`` and ``AsyncRustBackend`` hold the same per-client state --
endpoint, credential, prepared config, the driver handle and its lock, and the
endpoint registration -- and tear it down the same way. That common half lives
here; each backend keeps only what differs.

This module imports ``base`` and ``_driver_registry``; neither imports it, so
there is no import cycle.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Optional

from .base import PreparedClientConfig, init_client_args
from ._driver_registry import make_credential_key, register_client_config, release_client_config

_LOGGER = logging.getLogger(__name__)


def close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Stop our async-credential bridge if ``credential`` is one; never raise.

    The method-name check means this only closes our own wrapper
    (``AsyncTokenCredentialBridge``), never a customer's credential. Shared by both
    backends so the check lives in one place.
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


class RustBackendShared:
    """Mixin holding the state and lifecycle common to both Rust backends.

    A backend calls ``_init_shared`` from its ``__init__`` to store the common
    fields and register against its endpoint, then adds whatever its own handle
    build needs. The teardown helpers here are used by both backends' close and
    finalizer paths.

    ``_init_shared`` sets all the shared attributes: ``_endpoint``,
    ``_master_key``, ``_token_credential``, ``_client_config``,
    ``_strict_isolation``, ``_handle``, ``_handle_lock``, and ``_config_released``.
    """

    def _init_shared(
        self,
        endpoint: str,
        master_key: Optional[str],
        client_config: Optional[PreparedClientConfig],
        token_credential: Optional[Any],
        strict_isolation: bool = False,
    ) -> None:
        """Store the common per-client state and register against the endpoint.

        Called from each backend's ``__init__`` after it has set its own fields, so
        that if the strict-mode registration raises, every attribute the finalizer
        touches already exists.
        """
        self._endpoint = endpoint
        self._master_key = master_key
        # A token credential (e.g. from azure-identity), or None for master-key
        # auth; the factory sets exactly one. The driver calls get_token on it when
        # signing requests. An async credential arrives wrapped as
        # AsyncTokenCredentialBridge, which exposes a sync get_token.
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
        """Drop this client's endpoint registration exactly once, regardless of
        whether the handle was ever built or ``close()`` is called more than once."""
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
        """The positional args for the Rust ``init_client`` call, in one place."""
        return init_client_args(
            self._endpoint,
            self._master_key,
            self._client_config,
            self._token_credential,
        )

    def _close_token_credential_bridge(self) -> None:
        """If the credential is our async-to-sync bridge, stop its event-loop thread."""
        close_credential_bridge_quietly(self._token_credential)
