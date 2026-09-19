# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Adapt an async credential to the Rust binding's synchronous ``get_token``.

``credentials.resolve_credential`` acquires a bridge for an async credential.
On first use the bridge starts a daemon thread running its own asyncio event
loop. The binding awaits ``_start_token_request``'s cancellable result without
blocking a Tokio worker. Its operation deadline cancels that wait and requests
Python cancellation. ``get_token`` remains the synchronous adapter for direct
callers; it returns the token object without inspecting its fields.

The bridge does not schedule token calls on the application's event loop.
This does not make a credential's loop-bound resources safe to use from two
loops, serialize its token calls, or eliminate thread/GIL contention. A direct
call to this synchronous ``get_token`` on an application event-loop thread
would still block that thread.

``acquire`` shares one bridge per credential object and counts acquired holds.
Sharing a bridge does not by itself establish native driver sharing: endpoint
and client configuration also participate in driver identity.

The last matching release cancels tracked futures and requests loop shutdown.
The thread attempts task and async-generator cleanup. A finite join timeout
bounds the caller's join, not completion of cancellation or resource cleanup;
uncooperative credential code can leave the daemon running. The bridge does
not close the customer's credential or guarantee closure of its HTTP session.
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

    That call would wait on a future only that same thread can complete, so it would
    deadlock; the bridge raises this instead of hanging. It subclasses ``RuntimeError``
    so existing callers that catch ``RuntimeError`` keep working, while tests (and
    callers that care) can catch this specific type rather than matching message text.
    """

#: Env var (float seconds) for how long close waits for the bridge's background thread
#: to stop. Default 5s. A finite value bounds the join, not background cleanup.
JOIN_TIMEOUT_ENV_VAR = "COSMOS_ASYNC_CREDENTIAL_CLOSE_TIMEOUT"
_DEFAULT_JOIN_TIMEOUT_SECONDS = 5.0

# Registry holds are separate from Python references and native driver references.
# The lock serializes acquisition and release of a bridge for one credential.
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
    """Return True when ``obj.name`` exists and is an async (coroutine) method.

    The bridge has to pick which of the credential's token methods is the async one --
    ``get_token`` or ``get_token_info`` (see ``__init__``). Picking wrong would run a
    plain value where a coroutine is expected, or the reverse, and break every token
    fetch. A plain ``iscoroutinefunction`` check can miss the truth when the credential
    wraps its token method in a decorator (a common pattern, such as a tracing wrapper),
    which hides the coroutine underneath. ``inspect.unwrap`` follows exposed
    ``__wrapped__`` links; wrappers without those links may remain undetected.
    """
    method = getattr(obj, name, None)
    if method is None:
        return False
    if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
        return True
    unwrapped = inspect.unwrap(method) if callable(method) else method
    return asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped)


class AsyncTokenCredentialBridge:
    """Wrap an async credential so the driver's synchronous ``get_token`` works.

    The bridge selects its token method once, preferring a coroutine
    ``get_token`` over a coroutine ``get_token_info``. These token
    methods normally return ``AccessToken`` and ``AccessTokenInfo``, respectively.
    This adapter returns that object intact and forwards supplied scopes and
    keyword arguments; it does not validate token fields or create request options.
    The event loop and its thread start on the first ``get_token`` call.

    ``token_timeout`` bounds the synchronous result wait and the scheduled
    coroutine; it defaults to ``None``. Native calls await the cancellable
    result instead of this synchronous wait, so their enclosing operation
    deadline can cancel token acquisition. Cancellation is cooperative.

    Use ``acquire``, not the constructor, to wrap a credential. ``acquire``
    returns one shared bridge per credential and refcounts it, so shutdown is
    requested only when the last holder releases it. The constructor skips the
    registry (no sharing, shutdown requested on the first close) and is kept for
    tests and callers that want an unshared bridge.
    """

    @classmethod
    def acquire(
        cls,
        async_credential: Any,
        token_timeout: Optional[float] = None,
        join_timeout: Optional[float] = None,
    ) -> "AsyncTokenCredentialBridge":
        """Return the shared bridge for ``async_credential``, creating it if needed.

        Dedups by ``id(async_credential)``: the same credential object reused
        across clients maps to one bridge, independent of whether their endpoint
        and configuration permit sharing a native driver. Each acquisition
        requires one matching release; zero holders requests loop shutdown.
        The bridge retains the credential while the bridge object is alive,
        including references that outlive its registry entry. The customer
        still owns closing the credential.

        All holders must request the same timeouts. A conflicting acquisition
        raises before adding a hold; it never silently adopts another client's
        policy. A credential whose previous bridge is still shutting down
        cannot acquire a second loop.
        """
        key = id(async_credential)
        token_timeout = _validate_timeout(token_timeout, "token_timeout")
        join_timeout = _validate_timeout(
            _join_timeout_from_env() if join_timeout is None else join_timeout, "join_timeout"
        )
        with _REGISTRY_LOCK:
            bridge = _REGISTRY.get(key)
            # Build a new one if there is no entry, or (a low-cost check) if the id
            # was somehow reused for a different object.
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

        Most callers should use ``acquire``, which shares one bridge per
        credential. Building one directly gives an unshared bridge (no registry
        entry, shutdown requested on its first close) and is kept for tests.
        """
        self._credential = async_credential
        self._token_timeout = _validate_timeout(token_timeout, "token_timeout")
        self._join_timeout = _validate_timeout(
            _join_timeout_from_env() if join_timeout is None else join_timeout, "join_timeout"
        )
        # Pick the coroutine token method once. Prefer get_token (the original
        # TokenCredential, which returns AccessToken); fall back to
        # get_token_info (the newer SupportsTokenInfo, which returns
        # AccessTokenInfo) for a credential that offers only that one.
        # The bridge forwards the returned object without reading its fields.
        #
        # If neither is a coroutine, default to get_token so the failure shows
        # up clearly at call time. The factory only wraps async credentials, so
        # this is not expected.
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
        # Registry bookkeeping (guarded by _REGISTRY_LOCK): _registry_key is the
        # id() acquire() registered this bridge under (None when built directly,
        # which never shares); _refcount is the number of live holders.
        self._registry_key: Optional[int] = None
        self._refcount = 0

    def _run_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Run and close the background event loop."""
        # Run the bridge's own event loop (the one created in _ensure_loop) until
        # final release requests a stop, then attempt to drain and close it.
        # Draining can wait on uncooperative tasks; it does not close the credential.
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
        # Cancellation is cooperative. These awaits have no separate timeout;
        # the caller's join timeout does not bound this background drain.
        # Async-generator cleanup is not a substitute for credential.close().
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
        # Start the background thread the first time a token is needed.
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
        """Return a cancellable result for native async token acquisition."""
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

        Schedule on the bridge's loop and return the credential's result intact.
        The calling thread blocks in a sliced future wait. That wait observes
        ``token_timeout`` and final bridge release; it does not enforce an
        enclosing operation deadline or bound credential coroutine creation.
        """
        deadline = None if self._token_timeout is None else time.monotonic() + self._token_timeout
        self._ensure_loop()
        if threading.current_thread() is self._thread:
            # A call from the bridge's own background thread would wait on a future only
            # that thread can complete, which would deadlock. Raise instead of
            # hanging.
            raise AsyncCredentialBridgeReentrantError(
                "AsyncTokenCredentialBridge.get_token must not be called from the "
                "bridge's own background thread (the one running its event loop)."
            )
        future = self._start_token_request(*scopes, **kwargs)
        try:
            return self._wait_for_token(future, deadline)
        except concurrent.futures.CancelledError as exc:
            # Translate a cancelled result future. Final release is one cause;
            # a credential coroutine can also be cancelled independently.
            raise RuntimeError(
                "Async credential token acquisition was cancelled or the "
                "Cosmos async-credential bridge was closed."
            ) from exc
        except concurrent.futures.TimeoutError:
            # token_timeout elapsed: cancel the leftover fetch and return the
            # timeout to the driver instead of holding the worker thread.
            future.cancel()
            raise
        finally:
            with self._lock:
                self._pending.discard(future)

    # Wait for the fetch in short slices instead of one open-ended
    # future.result(). After each slice the wait re-checks _closed, so a close
    # promptly releases a waiting caller with a CancelledError instead of relying
    # on the cancellation arriving at just the right moment during teardown.
    _WAIT_SLICE_SECONDS = 0.2

    def _wait_for_token(
        self, future: "concurrent.futures.Future", deadline: Optional[float]
    ) -> Any:
        """Wait for the background thread to produce the token, then return it.

        Waits in short slices so it can notice a close between slices and stop waiting
        promptly, and enforces ``token_timeout`` as an overall deadline.
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
                # This slice elapsed; loop to re-check _closed / overall deadline.
                continue

    def _close_cosmos_async_bridge(self) -> None:
        """Release one acquired hold; the last release requests thread shutdown.

        Call once per acquisition, not once per reference to this shared object:
        repeated releases while other holders remain would consume their holds.
        Backends use their own take-once guard. This method does not close the
        customer's credential.

        Final release cancels tracked futures and joins with ``_join_timeout``.
        A still-live thread is retained and reported, and its credential cannot
        acquire a replacement loop until the old loop has closed.
        Cleanup errors outside the guarded loop-stop call can propagate; backend
        cleanup uses ``close_credential_bridge_quietly`` to log ordinary errors.
        """
        # Only the last shared holder requests shutdown. Registry bookkeeping
        # is locked against acquire; loop shutdown occurs outside that lock.
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
        # Also cancel in-flight fetches from this side, so a get_token waiting on
        # one is released even if the background thread is slow to drain. _run_loop also
        # cancels pending tasks as it closes the loop.
        for future in pending:
            future.cancel()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=self._join_timeout)
            if thread.is_alive():
                _LOGGER.warning(
                    "Async-credential bridge thread did not stop within the close timeout; "
                    "credential cancellation is still pending."
                )
