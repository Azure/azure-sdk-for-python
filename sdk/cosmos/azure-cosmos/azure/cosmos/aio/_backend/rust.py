# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async backend that sends operations to the compiled Rust module.

This is one of only two modules allowed to import ``azure.cosmos._rust``
(a unit test enforces that). The compiled module is not present until it
has been built, so the import is guarded; until then, operations raise
``NotImplementedError`` pointing at the build step.
"""
from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any, Optional

from azure.cosmos._backend.base import (
    OP_TO_BINDING_METHOD,
    PreparedClientConfig,
    build_backend_response,
    init_client_args,
)
from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from .base import AsyncCosmosBackend, BackendResponse, PreparedRequest

_LOGGER = logging.getLogger(__name__)

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; AsyncRustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )



class AsyncRustBackend(AsyncCosmosBackend):
    """Sends async operations to the Rust driver.

    The Rust call blocks until it finishes, so each operation runs on a
    worker thread to keep the event loop free. Each operation is routed by
    its kind; when the compiled module is missing, every operation raises
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
        # A synchronous token credential (e.g. an azure-identity credential),
        # or ``None`` for master-key auth. Exactly one of ``master_key`` /
        # ``token_credential`` is set by the factory. When present it is handed
        # to init_client, which wraps it so the Rust driver can call its
        # ``get_token`` during request signing. (The factory rejects async
        # credentials, so this is always synchronous.)
        self._token_credential = token_credential
        # Client-construction settings (e.g. preferred_locations) carried into
        # the driver on the first init_client call. ``None`` means "nothing to
        # carry" -- init_client then behaves exactly as the two-argument form.
        self._client_config = client_config
        # Opaque token from init_client() that names the live Rust-side client
        # (it owns the connection pool, auth, and routing). Built lazily on the
        # first operation and reused; None means "not built yet". The lock is a
        # thread lock (not asyncio) because init runs on an executor thread, and
        # it keeps the first concurrent caller the only one that builds.
        self._handle: Optional[str] = None
        self._handle_lock = threading.Lock()

    def _init_handle_with_lock(self) -> str:
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
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

    def _take_handle_for_close(self) -> Optional[str]:
        with self._handle_lock:
            handle = self._handle
            self._handle = None
            return handle

    async def _ensure_handle(self) -> str:
        # If the handle is already built, return it without locking.
        handle = self._handle
        if handle is not None:
            return handle
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._init_handle_with_lock)

    async def close(self) -> None:
        """Release the Rust client handle from the process cache."""
        handle = self._take_handle_for_close()
        if handle is None or _rust_module is None:
            return
        close_client = getattr(_rust_module, "close_client", None)
        if close_client is None:
            return
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, close_client, handle)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("AsyncRustBackend.close failed for handle=%s", handle, exc_info=True)

    def __del__(self) -> None:
        try:
            handle = self._take_handle_for_close()
            if handle is None or _rust_module is None:
                return
            close_client = getattr(_rust_module, "close_client", None)
            if close_client is None:
                return
            close_client(handle)
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Entry point every point operation (read/create/upsert/replace/delete/patch) goes through to reach the Rust driver."""
        if prepared is None:
            return None
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Build it with `maturin develop` from "
                "the repo root."
            )

        handle = await self._ensure_handle()
        loop = asyncio.get_running_loop()
        binding_method = OP_TO_BINDING_METHOD.get(prepared.op)
        if binding_method is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        dispatch = getattr(_rust_module, binding_method)
        result = await loop.run_in_executor(None, dispatch, handle, prepared)
        return build_backend_response(*result)
