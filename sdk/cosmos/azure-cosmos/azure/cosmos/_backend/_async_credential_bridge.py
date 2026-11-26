# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Run async credential calls on the customer event loop.

The asynchronous adapter acquires a bridge on its first use, before native
driver acquisition moves to a worker. The binding schedules token requests
through _start_token_request and waits asynchronously for their results.
The bridge never creates a thread, stops the customer event loop, or closes the
customer's credential.

Clients sharing a credential on the same customer event loop share a bridge. Each acquisition
needs one release. The last release requests cancellation of this bridge's
pending token calls only; cancellation cannot forcibly stop credential code.
The customer app must use the credential on its original customer event loop
and keep that loop running until its async clients and credential have been closed.
"""

from __future__ import annotations

# This bridge schedules credential coroutines; it never implements transport sleeps.
import asyncio  # pylint: disable=do-not-import-asyncio
import concurrent.futures
import inspect
import threading
from typing import Any, Optional

from azure.cosmos._backend.credentials import _is_coroutine_method


_REGISTRY: dict[tuple[int, asyncio.AbstractEventLoop], "AsyncTokenCredentialBridge"] = {}
_REGISTRY_LOCK = threading.Lock()


class AsyncTokenCredentialBridge:
    """Schedule token requests on the customer event loop for the binding."""

    @classmethod
    def acquire(
        cls,
        async_credential: Any,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> "AsyncTokenCredentialBridge":
        """Share one bridge per credential and customer event loop.

        :param async_credential: Customer-owned asynchronous token credential.
        :type async_credential: typing.Any
        :keyword loop: Credential's running event loop, or None to use the current loop.
        :paramtype loop: asyncio.AbstractEventLoop or None
        :return: Shared bridge with one additional acquired use.
        :rtype: ~azure.cosmos._backend._async_credential_bridge.AsyncTokenCredentialBridge
        """
        loop = asyncio.get_running_loop() if loop is None else loop
        cls._require_running_loop(loop)
        key = (id(async_credential), loop)
        with _REGISTRY_LOCK:
            for (credential_id, owner_loop), active in _REGISTRY.items():
                # Registry entries are other instances of this class, not external clients.
                # pylint: disable-next=protected-access
                if credential_id == id(async_credential) and active._credential is async_credential:
                    if owner_loop is not loop:
                        raise RuntimeError("The async credential is already in use on a different application loop")
            bridge = _REGISTRY.get(key)
            if bridge is None:
                bridge = cls(async_credential, loop=loop)
                bridge._registry_key = key
                _REGISTRY[key] = bridge
            bridge._refcount += 1
            return bridge

    def __init__(
        self,
        async_credential: Any,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
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
        """Schedule credential work on its customer event loop and return a cancellable result.

        ``kwargs`` contains token request options forwarded unchanged to the credential.

        :param scopes: Token scopes forwarded unchanged to the credential.
        :type scopes: typing.Any
        :return: Thread-safe future containing the token result or credential failure.
        :rtype: concurrent.futures.Future
        """

        async def invoke() -> tuple[bool, Any]:
            # Carry failures as values so asyncio cannot recreate credential exceptions.
            try:
                result = getattr(self._credential, self._token_method_name)(*scopes, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return True, result
            except BaseException as error:  # pylint: disable=broad-exception-caught
                return False, error

        future: concurrent.futures.Future = concurrent.futures.Future()

        def publish(completed: concurrent.futures.Future) -> None:
            if completed.cancelled():
                future.cancel()
                return
            if not future.set_running_or_notify_cancel():
                return
            try:
                succeeded, value = completed.result()
            except BaseException as error:  # pylint: disable=broad-exception-caught
                future.set_exception(error)
            else:
                if succeeded:
                    future.set_result(value)
                else:
                    future.set_exception(value)

        def cancel_request(completed: concurrent.futures.Future) -> None:
            if completed.cancelled():
                scheduled.cancel()

        with self._lock:
            if self._closed:
                raise RuntimeError("AsyncTokenCredentialBridge is closed")
            self._require_running_loop(self._loop)
            coroutine = invoke()
            try:
                scheduled = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
            except BaseException:
                # Pylint infers the awaited tuple instead of the coroutine object.
                coroutine.close()  # pylint: disable=no-member
                raise
            self._pending.add(future)
        future.add_done_callback(self._discard_pending)
        future.add_done_callback(cancel_request)
        scheduled.add_done_callback(publish)
        return future

    def _discard_pending(self, future: concurrent.futures.Future) -> None:
        with self._lock:
            self._pending.discard(future)

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
            if self._registry_key is not None and _REGISTRY.get(self._registry_key) is self:
                del _REGISTRY[self._registry_key]
        for future in pending:
            future.cancel()
