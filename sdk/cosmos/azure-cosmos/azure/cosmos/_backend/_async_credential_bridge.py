# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Let an async token credential work with the rust driver's synchronous ``get_token``.

You build a Cosmos client by handing it a credential -- the object that proves
who you are -- for example::

    credential = DefaultAzureCredential()           # an async credential
    client = CosmosClient(url, credential, _backend="rust")

Terminology used throughout this module:

* **background thread** -- the single thread the bridge starts (named
  ``cosmos-async-credential``, a daemon) to do its async work. It is the bridge's own
  thread, not the program's main thread or a pool thread, and it lives as long as the
  bridge does. Its only job is to run the event loop.
* **event loop** -- the asyncio scheduler that runs *on* the background thread and
  actually runs the credential's coroutine. The thread and the loop are different
  things: the thread is *where* work runs, the loop is *what* runs it. Here one
  background thread hosts exactly one event loop.

The 5,000-foot view -- unlike the engine-isolation guard, this module is not optional;
real features stop working without it. The rust driver's ``get_token`` is synchronous:
a sync credential returns the token directly, but an async credential returns a
coroutine -- a job that still has to be run -- and the driver's worker thread has no
event loop to run it on. So if this module did not exist:

* **Async credentials would simply not work on the rust backend.** Handing a
  ``DefaultAzureCredential`` from ``azure.identity.aio`` to a rust-backed client would
  break at the first item operation: the driver would get back a coroutine instead of a
  token object with ``.token`` / ``.expires_on``, so signing the request fails (and
  Python warns about a coroutine that was never run). Login would fail, and so would
  every request that needs it.
* **The only alternatives would be worse:** use a synchronous credential, or fall back
  to the non-rust backend. Async-identity users -- the common case for the async
  client -- would lose AAD sign-in on the fast path entirely.

In one line: this module makes a feature work, rather than just warning about a
problem -- take it away and the feature is gone, not merely unguarded.

How it bridges the gap. When the client factory (``factory._resolve_credential``) sees
the credential you passed is async, it wraps it in this bridge and hands the bridge to
the driver in the credential's place. The driver calls the bridge's synchronous
``get_token`` from a worker thread; the bridge sends the credential's coroutine to the
background thread, blocks the worker thread until the token comes back, and returns the
credential's own token object unchanged. The two threads don't deadlock because only
one runs Python at a time: while the worker thread sits blocked, it gives up its turn,
so the background thread is free to run the coroutine and produce the token.

What this module owns -- and does not. It owns its background thread and tears it down
cleanly on close: it cancels any in-flight token fetch and shuts the loop's async
generators down first, so the credential's own HTTP session can close instead of being
dropped (which would leak the connection and warn about an unclosed session). It does
**not** own the credential -- that lifetime belongs to the customer, exactly as on the
synchronous path, so the bridge never calls ``close()`` on it.

One bridge per credential. Several clients built from the same async credential share
one bridge -- and so one background thread and one driver -- via ``acquire`` (use it, not the
constructor). ``acquire`` looks the credential up by identity, hands back the same
bridge, and counts live holders; the last holder to close stops the background thread. That
count is this module's own tally of live users -- not Python's object reference
counting, which only frees memory and would never stop the thread.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import logging
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
#: to stop. Default 5s. That background thread is a daemon, so this cap only keeps a slow
#: credential teardown from stalling a client close(); it never blocks process exit.
JOIN_TIMEOUT_ENV_VAR = "COSMOS_ASYNC_CREDENTIAL_CLOSE_TIMEOUT"
_DEFAULT_JOIN_TIMEOUT_SECONDS = 5.0

# When several clients are built from the same async credential, they should share
# one bridge -- and so one background thread and one driver -- instead of each building
# its own. This is where we remember the bridge already made for a given
# credential: we look it up by the credential's identity, hand back the same one,
# and count how many clients are still using it. (That count is our own tally of
# live users, kept so the last client to leave can stop the background thread -- it is
# not Python's object reference counting, which only frees memory and would never
# stop the thread.) _REGISTRY_LOCK keeps two clients built at the same moment from
# each starting a bridge; the last client to close removes the entry.
_REGISTRY: Dict[int, "AsyncTokenCredentialBridge"] = {}
_REGISTRY_LOCK = threading.Lock()


def _join_timeout_from_env() -> float:
    raw = os.environ.get(JOIN_TIMEOUT_ENV_VAR)
    if raw:
        try:
            value = float(raw)
            if value >= 0:
                return value
        except ValueError:
            pass
        _LOGGER.debug("Ignoring invalid %s=%r; using default", JOIN_TIMEOUT_ENV_VAR, raw)
    return _DEFAULT_JOIN_TIMEOUT_SECONDS


def _is_coroutine_method(obj: Any, name: str) -> bool:
    """True when ``obj.name`` exists and is a coroutine function.

    Unwraps decorators first so a decorated coroutine method is still recognized.
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

    The bridge picks the credential's coroutine token method once: ``get_token``
    if that is the coroutine, otherwise ``get_token_info``. Both return a token
    object with ``.token`` and ``.expires_on``, which is all the driver reads. The
    event loop and its thread start on the first ``get_token`` call, so a bridge
    that is never used starts no thread.

    The bridge never closes the wrapped credential -- the customer owns its
    lifetime, just as on the synchronous path. Closing the bridge stops only its
    own background thread, and does it cleanly: it cancels any in-flight token fetch and
    shuts the loop's async generators down first, so the credential's own HTTP
    session can close instead of being dropped (which would leak the connection
    and warn about an unclosed session). A session the credential keeps across
    calls is still only released when the customer closes the credential.

    ``token_timeout`` (optional) caps the wait in ``get_token``. It defaults to
    ``None`` to match the synchronous path, where a slow fetch also blocks and the
    driver's own deadlines apply; set a finite value to guard against a credential
    that never returns. Either way, closing the bridge cancels an in-flight fetch,
    so teardown never leaves a worker thread waiting forever.

    Use ``acquire``, not the constructor, to wrap a credential. ``acquire``
    returns one shared bridge per credential and refcounts it, so the loop is torn
    down only when the last holder closes. The constructor skips the registry (no
    sharing, torn down on the first close) and is kept for tests and callers that
    want an unshared bridge.
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
        across clients maps to one bridge, so the driver (which keys engines by
        the bridge's identity) shares one driver and one background thread. Each call
        adds one to the bridge's refcount; the matching close subtracts one and
        tears the loop down only at zero. The bridge holds a strong reference to
        the credential, so its ``id`` stays valid and unique while it is
        registered.
        """
        key = id(async_credential)
        with _REGISTRY_LOCK:
            bridge = _REGISTRY.get(key)
            # Build a new one if there is no entry, or (a cheap guard) if the id
            # was somehow reused for a different object.
            if bridge is None or bridge._credential is not async_credential:
                bridge = cls(async_credential, token_timeout=token_timeout, join_timeout=join_timeout)
                bridge._registry_key = key
                _REGISTRY[key] = bridge
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
        entry, torn down on its first close) and is kept for tests.
        """
        self._credential = async_credential
        self._token_timeout = token_timeout
        self._join_timeout = _join_timeout_from_env() if join_timeout is None else join_timeout
        # Pick the coroutine token method once. Prefer get_token; fall back to
        # get_token_info for a credential that only offers that one. If neither is
        # a coroutine (the factory only wraps async credentials, so this is not
        # expected) default to get_token so any failure shows up clearly at call
        # time.
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

    @staticmethod
    def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
        # Run the loop until close() stops it, then drain and close it. Draining
        # cancels any task still pending (such as an in-flight token fetch) and
        # shuts down async generators. That both unblocks a get_token waiting on
        # the fetch and lets the credential's connections close cleanly instead of
        # being dropped when the loop closes.
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            try:
                AsyncTokenCredentialBridge._drain_loop(loop)
            finally:
                asyncio.set_event_loop(None)
                loop.close()

    @staticmethod
    def _drain_loop(loop: asyncio.AbstractEventLoop) -> None:
        # Cancel still-pending tasks and run them so the cancellation takes
        # effect, then close async generators. Cancelling an in-flight token task
        # also completes the future a blocked get_token is waiting on, so close()
        # can never leave a driver thread parked forever.
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
        # Start the background thread the first time a token is needed.
        loop = self._loop
        if loop is not None:
            return loop
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

    def get_token(self, *scopes: Any, **kwargs: Any) -> Any:
        """Synchronously return the access token for ``scopes``.

        Runs the credential's coroutine on the bridge's event loop and waits for
        it, then returns the credential's own token object (``.token`` /
        ``.expires_on``) unchanged. The driver calls this from a worker thread
        when it needs a token to attach to a request it is about to send; waiting
        here frees the background thread to run.

        The wait honors ``token_timeout`` when one is set; otherwise it blocks
        like the synchronous path and relies on the driver's deadlines. Either
        way, closing the bridge cancels an in-flight fetch, so teardown never
        leaves this thread parked forever.
        """
        loop = self._ensure_loop()
        if threading.current_thread() is self._thread:
            # A call from the bridge's own background thread would wait on a future only
            # that thread can complete, which would deadlock. Raise instead of
            # hanging.
            raise AsyncCredentialBridgeReentrantError(
                "AsyncTokenCredentialBridge.get_token must not be called from the "
                "bridge's own background thread (the one running its event loop)."
            )
        coro = getattr(self._credential, self._token_method_name)(*scopes, **kwargs)
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        with self._lock:
            self._pending.add(future)
        try:
            return self._wait_for_token(future)
        except concurrent.futures.CancelledError as exc:
            # Closing the bridge cancelled the fetch; return a clear error to the
            # driver instead of a bare CancelledError.
            raise RuntimeError(
                "Async credential token acquisition was cancelled because the "
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

    def _wait_for_token(self, future: "concurrent.futures.Future") -> Any:
        """Wait for the background thread to produce the token, then return it.

        Waits in short slices so it can notice a close between slices and bail out
        promptly, and enforces ``token_timeout`` as an overall deadline.
        """
        deadline = None if self._token_timeout is None else time.monotonic() + self._token_timeout
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
                # This slice elapsed; loop to re-check _closed / overall deadline.
                continue

    def _close_cosmos_async_bridge(self) -> None:
        """Release one hold on the bridge; the last release stops the background thread.

        Idempotent and never raises. The name is deliberately distinctive and
        private so a backend can close this bridge (found with a ``getattr``
        check) without ever calling ``close()`` on the customer's own credential,
        which the bridge does not own.

        For a bridge from ``acquire`` (the normal path) this subtracts one from
        the refcount and stops the loop only once the last holder has released it,
        so one client closing early cannot pull the loop out from under other
        clients still sharing the credential.
        """
        # Only the last holder of a shared (acquired) bridge tears it down; a
        # directly-built bridge (_registry_key is None) always tears down. Held
        # under the registry lock so acquire and close serialize.
        if self._registry_key is not None:
            with _REGISTRY_LOCK:
                if self._refcount > 0:
                    self._refcount -= 1
                if self._refcount > 0:
                    return
                # Last holder: drop the registry entry so a later acquire builds a
                # fresh bridge instead of reusing this closing one.
                if _REGISTRY.get(self._registry_key) is self:
                    del _REGISTRY[self._registry_key]
        with self._lock:
            loop = self._loop
            thread = self._thread
            pending = list(self._pending)
            self._loop = None
            self._thread = None
            self._closed = True
        if loop is None:
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
