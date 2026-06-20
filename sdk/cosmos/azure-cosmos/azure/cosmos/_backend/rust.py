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



class RustBackend(CosmosBackend):
    """Sends operations to the Rust driver.

    Takes the account endpoint and key. The client handle -- the opaque
    token ``init_client`` returns, which references the live client the
    Rust driver builds from that endpoint and key -- is built once, on the
    first operation, and then reused; every operation passes it back to the
    Rust module. Python never inspects the handle, it just hands it back.
    Each operation is routed by its kind; when the compiled module is
    missing, every operation raises ``NotImplementedError``.
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
        # A synchronous token credential (e.g. an azure-identity credential),
        # or ``None`` for master-key auth. Exactly one of ``master_key`` /
        # ``token_credential`` is set by the factory. When present it is handed
        # to init_client, which wraps it so the Rust driver can call its
        # ``get_token`` during request signing.
        self._token_credential = token_credential
        # Client-construction settings (e.g. preferred_locations) carried into
        # the driver on the first init_client call. ``None`` means "nothing to
        # carry" -- init_client then behaves exactly as the two-argument form.
        self._client_config = client_config
        # Opaque token from init_client() that names the live Rust-side client
        # (it owns the connection pool, auth, and routing). Built lazily on the
        # first operation and reused; None means "not built yet". The lock lets
        # only the first concurrent caller build it, so two callers don't each
        # build (and leak) a separate client.
        self._handle: Optional[str] = None
        self._handle_lock = threading.Lock()

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
        """Entry point every point operation (read/create/upsert/replace/delete/patch) goes through to reach the Rust driver."""
        if prepared is None:
            # Nothing to send.
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = self._ensure_handle()
        binding_method = OP_TO_BINDING_METHOD.get(prepared.op)
        if binding_method is None:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        dispatch = getattr(_rust_module, binding_method)
        return build_backend_response(*dispatch(handle, prepared))
