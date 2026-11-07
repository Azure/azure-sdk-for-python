# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Dispatch async credential calls to the customer app's running event loop.

The asynchronous adapter acquires a bridge on its first use, before native
driver acquisition moves to a worker. The binding schedules token requests
through _start_token_request and waits asynchronously for their results.
The bridge never creates a thread, stops the application loop, or closes the
customer's credential.

Clients sharing a credential on the same loop share a bridge. Each acquisition
needs one release. The last release requests cancellation of this bridge's
pending token calls only; cancellation cannot forcibly stop credential code.
The customer app must use the credential on its owning loop and keep that loop
running until its async clients and credential have been closed.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import math
import threading
import time
from typing import Any, Optional


class AsyncCredentialBridgeReentrantError(RuntimeError):
    """A synchronous token wait would block the credential's application loop."""


_REGISTRY: dict[tuple[int, asyncio.AbstractEventLoop], "AsyncTokenCredentialBridge"] = {}
_REGISTRY_LOCK = threading.Lock()


def _validate_timeout(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("token_timeout must be a finite, nonnegative timeout")
    if not math.isfinite(value) or not 0 <= value <= threading.TIMEOUT_MAX:
        raise ValueError("token_timeout must be finite and between 0 and threading.TIMEOUT_MAX")
    return float(value)


def _is_coroutine_method(obj: Any, name: str) -> bool:
    method = getattr(obj, name, None)
    if method is None:
        return False
    unwrapped = inspect.unwrap(method) if callable(method) else method
    return inspect.iscoroutinefunction(method) or inspect.iscoroutinefunction(unwrapped)


class AsyncTokenCredentialBridge:
    """Borrow an application loop to obtain tokens without blocking native work."""

    @classmethod
    def acquire(
        cls,
        async_credential: Any,
        token_timeout: Optional[float] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> "AsyncTokenCredentialBridge":
        """Share one bridge per credential and owner loop, with matching timeouts."""
        token_timeout = _validate_timeout(token_timeout)
        loop = asyncio.get_running_loop() if loop is None else loop
        cls._require_running_loop(loop)
        key = (id(async_credential), loop)
        with _REGISTRY_LOCK:
            for (credential_id, owner_loop), active in _REGISTRY.items():
                if credential_id == id(async_credential) and active._credential is async_credential:
                    if owner_loop is not loop:
                        raise RuntimeError("The async credential is already in use on a different application loop")
            bridge = _REGISTRY.get(key)
            if bridge is None:
                bridge = cls(async_credential, token_timeout=token_timeout, loop=loop)
                bridge._registry_key = key
                _REGISTRY[key] = bridge
            elif token_timeout != bridge._token_timeout:
                raise ValueError("Clients sharing an async credential must use the same bridge timeouts")
            bridge._refcount += 1
            return bridge

    def __init__(
        self,
        async_credential: Any,
        token_timeout: Optional[float] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._token_timeout = _validate_timeout(token_timeout)
        self._loop = asyncio.get_running_loop() if loop is None else loop
        self._require_running_loop(self._loop)
        self._credential = async_credential
        self._token_method_name = (
            "get_token_info"
            if not _is_coroutine_method(async_credential, "get_token")
            and _is_coroutine_method(async_credential, "get_token_info")
            else "get_token"
        )
        self._lock = threading.Lock()
        self._closed = False
        self._pending: set[concurrent.futures.Future] = set()
        self._registry_key: Optional[tuple[int, asyncio.AbstractEventLoop]] = None
        self._refcount = 0

    @staticmethod
    def _require_running_loop(loop: asyncio.AbstractEventLoop) -> None:
        if loop.is_closed() or not loop.is_running():
            raise RuntimeError("The async credential's application loop must be running")

    def check_owner_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        if self._closed:
            raise RuntimeError("AsyncTokenCredentialBridge is closed")
        if loop is not self._loop:
            raise RuntimeError("The async credential must be used on its original application loop")
        self._require_running_loop(loop)

    def _start_token_request(self, *scopes: Any, **kwargs: Any) -> concurrent.futures.Future:
        """Return a cancellable result without moving credential work to another loop."""

        async def invoke() -> Any:
            return await getattr(self._credential, self._token_method_name)(*scopes, **kwargs)

        async def fetch() -> Any:
            if self._token_timeout is None:
                return await invoke()
            return await asyncio.wait_for(invoke(), self._token_timeout)

        with self._lock:
            if self._closed:
                raise RuntimeError("AsyncTokenCredentialBridge is closed")
            self._require_running_loop(self._loop)
            coroutine = fetch()
            try:
                future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
            except BaseException:
                coroutine.close()
                raise
            self._pending.add(future)
        future.add_done_callback(self._discard_pending)
        return future

    def _discard_pending(self, future: concurrent.futures.Future) -> None:
        with self._lock:
            self._pending.discard(future)

    def get_token(self, *scopes: Any, **kwargs: Any) -> Any:
        """Support a blocking worker-thread wait, never a wait on the owner loop."""
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None
        if running_loop is self._loop:
            raise AsyncCredentialBridgeReentrantError(
                "AsyncTokenCredentialBridge.get_token must not block its application event loop"
            )
        deadline = None if self._token_timeout is None else time.monotonic() + self._token_timeout
        future = self._start_token_request(*scopes, **kwargs)
        try:
            return self._wait_for_token(future, deadline)
        except concurrent.futures.CancelledError as exc:
            raise RuntimeError(
                "Async credential token acquisition was cancelled or the " "Cosmos async-credential bridge was closed."
            ) from exc
        except BaseException:
            future.cancel()
            raise

    _WAIT_SLICE_SECONDS = 0.2

    def _wait_for_token(self, future: concurrent.futures.Future, deadline: Optional[float]) -> Any:
        while True:
            if self._closed:
                future.cancel()
                raise concurrent.futures.CancelledError()
            self._require_running_loop(self._loop)
            slice_timeout = self._WAIT_SLICE_SECONDS
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise concurrent.futures.TimeoutError()
                slice_timeout = min(slice_timeout, remaining)
            try:
                return future.result(slice_timeout)
            except concurrent.futures.TimeoutError:
                if future.done():
                    raise

    def _close_cosmos_async_bridge(self) -> None:
        """Release one use; cancel only this bridge's work after the last release."""
        with _REGISTRY_LOCK:
            if self._registry_key is not None:
                if self._refcount == 0:
                    return
                self._refcount -= 1
                if self._refcount:
                    return
            with self._lock:
                if self._closed:
                    return
                self._closed = True
                pending = tuple(self._pending)
            if _REGISTRY.get(self._registry_key) is self:
                del _REGISTRY[self._registry_key]
        for future in pending:
            future.cancel()
