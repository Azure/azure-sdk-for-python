# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Let the Rust binding obtain tokens from an async Python credential.

The credential's async methods need an event loop, which schedules their work.
This bridge starts its own loop on a background thread when the first token is
requested, rather than using the customer app's loop.

_start_token_request returns a Future, an object that receives the result
later. The binding waits for it asynchronously and can request cancellation
when the operation times out. Direct Python callers can instead use get_token,
which blocks their calling thread until a result or error is available.

Each acquire call needs one matching release. Calls for the same credential
object share a bridge, though they need not share a Rust driver. The last
release requests cancellation and thread shutdown, not immediate termination.
The close timeout limits how long the caller waits for the thread; credential
code that ignores cancellation may keep running.

The customer app must close its own credential. This bridge does not make it
safe to share a credential's loop-specific resources across event loops or
guarantee that its token methods are called one at a time.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import logging
import math
import os
import threading
import time
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)


class AsyncCredentialBridgeReentrantError(RuntimeError):
    """Raised when ``get_token`` is called from the bridge's own background thread.

    That call would block the only thread able to finish its token request.
    Raise a specific RuntimeError instead of waiting forever.
    """

#: Environment setting for how many seconds close waits for the thread to stop.
#: Default 5 seconds. It limits the wait, not how long background cleanup can take.
JOIN_TIMEOUT_ENV_VAR = "COSMOS_ASYNC_CREDENTIAL_CLOSE_TIMEOUT"
_DEFAULT_JOIN_TIMEOUT_SECONDS = 5.0

# Store one shared bridge per credential object. The lock protects its use count,
# which counts acquire calls, not Python references or Rust drivers.
_REGISTRY: Dict[int, "AsyncTokenCredentialBridge"] = {}
_REGISTRY_LOCK = threading.Lock()


def _join_timeout_from_env() -> float:
    """Read the close-timeout override (in seconds) from the environment, or use 5s.

    Invalid or unrepresentable values are logged and use the default.
    """
    raw = os.environ.get(JOIN_TIMEOUT_ENV_VAR)
    if raw:
        try:
            value = float(raw)
            if math.isfinite(value) and 0 <= value <= threading.TIMEOUT_MAX:
                return value
        except ValueError:
            pass
        _LOGGER.debug("Ignoring invalid %s=%r; using default", JOIN_TIMEOUT_ENV_VAR, raw)
    return _DEFAULT_JOIN_TIMEOUT_SECONDS


def _validate_timeout(value: Optional[float], name: str) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite, nonnegative timeout")
    if not 0 <= value <= threading.TIMEOUT_MAX or not math.isfinite(value):
        raise ValueError(f"{name} must be finite and between 0 and threading.TIMEOUT_MAX")
    return float(value)


def _is_coroutine_method(obj: Any, name: str) -> bool:
    """Check whether the named token method is async and can be awaited.

    Follow __wrapped__ links to find methods hidden by decorators. A wrapper
    without those links may prevent detection.
    """
    method = getattr(obj, name, None)
    if method is None:
        return False
    if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
        return True
    unwrapped = inspect.unwrap(method) if callable(method) else method
    return asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped)


class AsyncTokenCredentialBridge:
    """Run async token requests on one background event loop.

    Prefer an async get_token method; otherwise use async get_token_info.
    Forward arguments and return the token object unchanged, without checking
    its fields. The first token request starts the thread.

    token_timeout limits both the synchronous wait and the scheduled async
    request. Rust calls wait asynchronously and can also cancel that wait using
    their operation deadline. Cancellation still depends on the credential
    responding to the request to stop.

    Use acquire to share one bridge per credential. Direct construction creates
    an unshared bridge whose first close requests shutdown.
    """

    @classmethod
    def acquire(
        cls,
        async_credential: Any,
        token_timeout: Optional[float] = None,
        join_timeout: Optional[float] = None,
    ) -> "AsyncTokenCredentialBridge":
        """Return the shared bridge for ``async_credential``, creating it if needed.

        Match the credential object itself, not whether two credentials contain
        equal values. Each call adds one use that needs a matching release.
        The bridge keeps the credential alive but does not close it.

        All callers sharing the bridge must request the same timeouts.
        Conflicting values raise before adding a use. A credential cannot get
        a replacement bridge while its previous thread is still shutting down.
        """
        key = id(async_credential)
        token_timeout = _validate_timeout(token_timeout, "token_timeout")
        join_timeout = _validate_timeout(
            _join_timeout_from_env() if join_timeout is None else join_timeout, "join_timeout"
        )
        with _REGISTRY_LOCK:
            bridge = _REGISTRY.get(key)
            # Check the object too, rather than relying only on its numeric id.
            if bridge is None or bridge._credential is not async_credential:
                bridge = cls(async_credential, token_timeout=token_timeout, join_timeout=join_timeout)
                bridge._registry_key = key
                _REGISTRY[key] = bridge
            else:
                if bridge._closed:
                    raise RuntimeError("Async-credential bridge is still shutting down")
                if token_timeout != bridge._token_timeout or join_timeout != bridge._join_timeout:
                    raise ValueError("Clients sharing an async credential must use the same bridge timeouts")
            bridge._refcount += 1
            return bridge

    def __init__(
        self,
        async_credential: Any,
        token_timeout: Optional[float] = None,
        join_timeout: Optional[float] = None,
    ) -> None:
        """Store the credential and settings; the background thread is not started yet.

        Use acquire when clients should share a bridge. Direct construction,
        used in tests, creates one that shuts down on its first close.
        """
        self._credential = async_credential
        self._token_timeout = _validate_timeout(token_timeout, "token_timeout")
        self._join_timeout = _validate_timeout(
            _join_timeout_from_env() if join_timeout is None else join_timeout, "join_timeout"
        )
        # If neither method is detected as async, try get_token. An invalid
        # method then fails when the token is requested rather than here.
        if _is_coroutine_method(async_credential, "get_token"):
            self._token_method_name = "get_token"
        elif _is_coroutine_method(async_credential, "get_token_info"):
            self._token_method_name = "get_token_info"
        else:
            self._token_method_name = "get_token"
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._closed = False
        self._pending: "set[concurrent.futures.Future]" = set()
        # _REGISTRY_LOCK protects the credential id and number of acquired uses.
        # A directly constructed bridge has no entry in the shared dictionary.
        self._registry_key: Optional[int] = None
        self._refcount = 0

    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Run and close the background event loop."""
        # Stopping the loop begins cleanup; it does not force token code to stop
        # or close the customer's credential.
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            try:
                AsyncTokenCredentialBridge._drain_loop(loop)
            finally:
                asyncio.set_event_loop(None)
                loop.close()
                with self._lock:
                    self._loop = None
                with _REGISTRY_LOCK:
                    if self._refcount == 0 and _REGISTRY.get(self._registry_key) is self:
                        del _REGISTRY[self._registry_key]

    @staticmethod
    def _drain_loop(loop: asyncio.AbstractEventLoop) -> None:
        """Cancel pending token calls and close async generators."""
        # Tasks must respond to cancellation. These waits have no timeout,
        # even after the caller stops waiting for the thread to finish.
        # Closing async generators does not close the customer's credential.
        try:
            pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        except RuntimeError:
            pending = []
        for task in pending:
            task.cancel()
        try:
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Async-credential bridge loop drain hit an error", exc_info=True)

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Return the background event loop, starting its thread when needed."""
        with self._lock:
            if self._closed:
                raise RuntimeError("AsyncTokenCredentialBridge is closed")
            if self._loop is None:
                new_loop = asyncio.new_event_loop()
                thread = threading.Thread(
                    target=self._run_loop,
                    args=(new_loop,),
                    name="cosmos-async-credential",
                    daemon=True,
                )
                thread.start()
                self._loop = new_loop
                self._thread = thread
            return self._loop

    def _start_token_request(self, *scopes: Any, **kwargs: Any) -> concurrent.futures.Future:
        """Schedule a token request and return a Future the binding can cancel."""
        loop = self._ensure_loop()

        async def invoke() -> Any:
            return await getattr(self._credential, self._token_method_name)(*scopes, **kwargs)

        async def fetch() -> Any:
            if self._token_timeout is None:
                return await invoke()
            return await asyncio.wait_for(invoke(), self._token_timeout)

        with self._lock:
            if self._closed:
                raise RuntimeError("AsyncTokenCredentialBridge is closed")
            coroutine = fetch()
            try:
                future = asyncio.run_coroutine_threadsafe(coroutine, loop)
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
        """Synchronously return the access token for ``scopes``.

        Return the credential's result unchanged. Check for timeout or bridge
        closure between short waits. This method uses token_timeout, not an SDK
        operation deadline, and does not limit time spent creating the async call.
        """
        deadline = None if self._token_timeout is None else time.monotonic() + self._token_timeout
        self._ensure_loop()
        if threading.current_thread() is self._thread:
            # Waiting here would block the only thread that can finish the request.
            raise AsyncCredentialBridgeReentrantError(
                "AsyncTokenCredentialBridge.get_token must not be called from the "
                "bridge's own background thread (the one running its event loop)."
            )
        future = self._start_token_request(*scopes, **kwargs)
        try:
            return self._wait_for_token(future, deadline)
        except concurrent.futures.CancelledError as exc:
            # Closing the bridge or cancelling the credential call can cause this.
            raise RuntimeError(
                "Async credential token acquisition was cancelled or the "
                "Cosmos async-credential bridge was closed."
            ) from exc
        except concurrent.futures.TimeoutError:
            # Stop waiting and request cancellation of any unfinished token call.
            future.cancel()
            raise
        finally:
            with self._lock:
                self._pending.discard(future)

    # Recheck closure between short waits instead of waiting indefinitely
    # for the background thread to finish cancelling its work.
    _WAIT_SLICE_SECONDS = 0.2

    def _wait_for_token(
        self, future: "concurrent.futures.Future", deadline: Optional[float]
    ) -> Any:
        """Wait for the background thread to produce the token, then return it.

        Check closure and the overall token timeout between waits.
        """
        while True:
            if self._closed:
                future.cancel()
                raise concurrent.futures.CancelledError()
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
                # No result yet; recheck closure and the overall deadline.
                continue

    def _close_cosmos_async_bridge(self) -> None:
        """Release one acquired use; the last release requests thread shutdown.

        Call once per acquire, not once per Python reference to this object.
        Releasing twice could remove another client's use. Backends clear their
        own reference before calling this method again.

        The last release cancels pending results and waits up to _join_timeout
        for the thread. If it keeps running, log that fact and prevent a
        replacement loop until it stops. The customer's credential stays open.
        Some cleanup errors can propagate; backend cleanup logs them through
        close_credential_bridge_quietly.
        """
        # Only the last user requests shutdown. Release the shared dictionary
        # lock before waiting for the loop, which also needs that lock to exit.
        if self._registry_key is not None:
            with _REGISTRY_LOCK:
                if self._refcount == 0:
                    return
                self._refcount -= 1
                if self._refcount > 0:
                    return
                with self._lock:
                    self._closed = True
        else:
            with self._lock:
                if self._closed:
                    return
                self._closed = True
        with self._lock:
            loop = self._loop
            thread = self._thread
            pending = list(self._pending)
        if loop is None:
            with _REGISTRY_LOCK:
                if _REGISTRY.get(self._registry_key) is self:
                    del _REGISTRY[self._registry_key]
            return
        try:
            loop.call_soon_threadsafe(loop.stop)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to stop async-credential bridge loop", exc_info=True)
        # Unblock callers waiting for results even if the background thread is
        # slow to stop. _run_loop also requests cancellation of its remaining tasks.
        for future in pending:
            future.cancel()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=self._join_timeout)
            if thread.is_alive():
                _LOGGER.warning(
                    "Async-credential bridge thread did not stop within the close timeout; "
                    "credential cancellation is still pending."
                )
