# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync backend that sends operations to the compiled Rust module.

This is one of only two modules allowed to import ``azure.cosmos._rust``
(a unit test enforces that). The compiled module is not present until it
has been built, so the import is guarded; until then, operations raise
``NotImplementedError`` pointing at the build step.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Optional


from .base import (
    OP_TO_BINDING_METHOD,
    BackendResponse,
    CosmosBackend,
    PreparedClientConfig,
    PreparedRequest,
    build_backend_response,
    init_client_args,
)
from ._driver_registry import register_client_config, release_client_config
from .constants import BACKEND_NAME_RUST

_LOGGER = logging.getLogger(__name__)

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )


# Look up the binding's function for an operation. Read live from ``_rust_module``
# rather than cached at import, so the tests can swap in a fake binding; the extra
# getattr per call is tiny next to the network round trip.
def _resolve_dispatch(op: str) -> Optional[Any]:
    """Return the binding's ``<op>`` function, or ``None`` if the op is unsupported
    or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


class RustBackend(CosmosBackend):
    """Sends operations to the Rust driver.

    The handle that init_client returns -- an opaque token naming the driver-side
    client built from the endpoint and key -- is built on the first operation and
    reused; every operation passes it back. The handle is not the ``CosmosClient``:
    it is a reference to the driver-side client (which owns the connection pool,
    auth, and routing), several layers below the public object. Operations route by
    kind; when the compiled module is missing, every operation raises
    ``NotImplementedError``.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
    ) -> None:
        self._endpoint = endpoint
        self._master_key = master_key
        # A token credential (e.g. from azure-identity), or ``None`` for master-key
        # auth; the factory sets exactly one. It is passed to init_client so the
        # driver can call get_token when signing requests. An async credential
        # arrives wrapped as AsyncTokenCredentialBridge, which exposes a sync
        # get_token and is closed in _close_token_credential_bridge.
        self._token_credential = token_credential
        # Client settings (e.g. preferred_locations) passed to the first init_client
        # call. ``None`` means there are none to pass.
        self._client_config = client_config
        # The handle init_client returns, naming the driver-side client (which owns
        # the connection pool, auth, and routing). Built on the first operation and
        # reused; ``None`` until then. The lock lets only the first caller build it,
        # so two callers don't each build a separate client.
        self._handle: Optional[str] = None
        self._handle_lock = threading.Lock()
        # Register this client against its endpoint so a second client to the same
        # account with a different config gets a SharedDriverConfigWarning instead of
        # silently inheriting this one's config. Released once on close.
        self._config_released = False
        register_client_config(self._endpoint, self._client_config)

    def _release_config_once(self) -> None:
        # Drop this client's endpoint registration exactly once, regardless of
        # whether the handle was ever built or close() is called more than once.
        with self._handle_lock:
            if self._config_released:
                return
            self._config_released = True
        release_client_config(self._endpoint)

    def _close_token_credential_bridge(self) -> None:
        # If the token credential is our async->sync bridge, stop its dedicated
        # event-loop thread. The named-method duck-type check means we only ever
        # close *our* wrapper, never a customer's own credential (sync or async).
        closer = getattr(self._token_credential, "_close_cosmos_async_bridge", None)
        if callable(closer):
            try:
                closer()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)

    def _ensure_handle(self) -> str:
        # If the handle is already built, return it without locking.
        handle = self._handle
        if handle is not None:
            return handle
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        # Build it once. The lock, with a second check inside, keeps
        # concurrent first callers from each building one.
        with self._handle_lock:
            if self._handle is None:
                self._handle = _rust_module.init_client(
                    *init_client_args(
                        self._endpoint,
                        self._master_key,
                        self._client_config,
                        self._token_credential,
                    )
                )
            return self._handle

    def close(self) -> None:
        """Release the Rust client handle from the process cache."""
        self._release_config_once()
        self._close_token_credential_bridge()
        with self._handle_lock:
            handle = self._handle
            self._handle = None
        if handle is None or _rust_module is None:
            return
        close_client = getattr(_rust_module, "close_client", None)
        if close_client is None:
            return
        try:
            close_client(handle)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("RustBackend.close failed for handle=%s", handle, exc_info=True)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Send one point operation (read/create/upsert/replace/delete/patch) to the Rust driver."""
        if prepared is None:
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = self._ensure_handle()
        # Look up the binding's function for this op; None if unsupported.
        dispatch = _resolve_dispatch(prepared.op)
        if dispatch is None:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        return build_backend_response(*dispatch(handle, prepared))
