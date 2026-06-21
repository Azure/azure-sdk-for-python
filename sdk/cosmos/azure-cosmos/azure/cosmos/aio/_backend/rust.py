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
import os
import threading
from concurrent.futures import ThreadPoolExecutor
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


# Map each op name to its bound Rust function once, at import, so each call is a
# dict lookup instead of a getattr. Empty when the compiled module is absent.
_OP_DISPATCH = {}
if _rust_module is not None:
    for _op, _method in OP_TO_BINDING_METHOD.items():
        _fn = getattr(_rust_module, _method, None)
        if _fn is not None:
            _OP_DISPATCH[_op] = _fn


_DEFAULT_ASYNC_MAX_THREADS = 256


def _async_executor_max_threads() -> int:
    """Size of the async backend's dedicated thread pool.

    The Rust call holds its worker thread for the whole call, so this is the cap
    on how many operations can run at once; beyond it they wait. Threads are
    created on demand up to the cap, so a high cap is free until used. Override
    with ``COSMOS_RUST_ASYNC_MAX_THREADS``; the default is 256, well above
    typical concurrency. It replaces asyncio's shared default pool, which held
    only ``min(32, cpu + 4)`` threads.
    """
    raw = os.environ.get("COSMOS_RUST_ASYNC_MAX_THREADS")
    if raw:
        try:
            value = int(raw)
        except ValueError:
            _LOGGER.warning(
                "Ignoring invalid COSMOS_RUST_ASYNC_MAX_THREADS=%r; using default %d.",
                raw,
                _DEFAULT_ASYNC_MAX_THREADS,
            )
        else:
            if value > 0:
                return value
            _LOGGER.warning(
                "Ignoring non-positive COSMOS_RUST_ASYNC_MAX_THREADS=%r; using default %d.",
                raw,
                _DEFAULT_ASYNC_MAX_THREADS,
            )
    return _DEFAULT_ASYNC_MAX_THREADS


class AsyncRustBackend(AsyncCosmosBackend):
    """Sends async operations to the Rust driver.

    The Rust call blocks until it finishes, so each operation runs on a worker
    thread to keep the event loop free. Those threads come from this backend's
    own pool, not asyncio's shared default pool: the default pool holds only
    ``min(32, cpu + 4)`` threads and is shared across the process, which would
    cap concurrency well below what callers ask for. The dedicated pool is built
    lazily and sized by ``_async_executor_max_threads`` (override:
    ``COSMOS_RUST_ASYNC_MAX_THREADS``). When the compiled module is missing,
    every operation raises ``NotImplementedError``.
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
        # This backend's own thread pool for the blocking Rust calls, built
        # lazily on first use and sized by _async_executor_max_threads(). An
        # unused client creates no threads.
        self._executor: Optional[ThreadPoolExecutor] = None
        self._executor_max_threads = _async_executor_max_threads()

    def _get_executor(self) -> ThreadPoolExecutor:
        # Built on first use, on the event-loop thread; all callers run there,
        # so the check-then-create needs no lock.
        executor = self._executor
        if executor is None:
            executor = ThreadPoolExecutor(
                max_workers=self._executor_max_threads,
                thread_name_prefix="cosmos-rust-async",
            )
            self._executor = executor
        return executor

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
        # One-time call, so it runs on the default pool; the dedicated pool is
        # for the per-operation calls (see execute).
        return await loop.run_in_executor(None, self._init_handle_with_lock)

    async def close(self) -> None:
        """Release the Rust client handle and shut down the dedicated pool."""
        handle = self._take_handle_for_close()
        executor = self._executor
        self._executor = None
        if handle is not None and _rust_module is not None:
            close_client = getattr(_rust_module, "close_client", None)
            if close_client is not None:
                loop = asyncio.get_running_loop()
                try:
                    await loop.run_in_executor(None, close_client, handle)
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.debug(
                        "AsyncRustBackend.close failed for handle=%s", handle, exc_info=True
                    )
        if executor is not None:
            # Don't block the event loop waiting for running calls to finish.
            executor.shutdown(wait=False)

    def __del__(self) -> None:
        try:
            executor = self._executor
            self._executor = None
            if executor is not None:
                executor.shutdown(wait=False)
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
        # Look the bound function up in the dict built at import (see
        # _OP_DISPATCH) instead of a getattr per call.
        dispatch = _OP_DISPATCH.get(prepared.op)
        if dispatch is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        loop = asyncio.get_running_loop()
        # Run the blocking Rust call on this backend's own pool, not asyncio's
        # shared default pool, so concurrency isn't capped at ``min(32, cpu + 4)``.
        result = await loop.run_in_executor(self._get_executor(), dispatch, handle, prepared)
        return build_backend_response(*result)
