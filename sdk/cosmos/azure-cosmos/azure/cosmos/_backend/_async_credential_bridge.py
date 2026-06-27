# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Adapt an async token credential to the synchronous ``get_token`` the Rust
driver calls during request signing.

The Rust driver signs each request by calling ``get_token()`` *synchronously*
from one of its background worker threads -- a thread that has no asyncio event
loop running on it. A synchronous credential just returns the token there and
then. An **async** credential's ``get_token`` instead returns a coroutine, and
that worker thread has no event loop to drive it to completion. That mismatch is
why async credentials were refused at construction.

:class:`AsyncTokenCredentialBridge` removes that limitation on the
binding/Python side, with no Rust-driver change:

* It owns a dedicated asyncio event loop running on its own daemon thread.
* Its ``get_token`` (synchronous) submits the credential's coroutine to that
  loop with :func:`asyncio.run_coroutine_threadsafe` and blocks the calling
  (driver) thread on the resulting ``concurrent.futures.Future`` until the token
  is ready.

The wait in ``get_token`` blocks on a ``concurrent.futures.Future``, which in
turn waits on a threading primitive -- and CPython releases the GIL while a
thread is blocked on one. So the loop thread can acquire the GIL and run the
credential's coroutine even though the driver called in while holding the GIL;
there is no deadlock. The returned object is whatever the credential produced
(an ``AccessToken`` / ``AccessTokenInfo``), which already exposes the ``.token``
and ``.expires_on`` attributes the binding reads -- so the existing synchronous
``get_token`` path in the binding works unchanged.
"""
from __future__ import annotations

import asyncio
import inspect
import logging
import threading
from typing import Any, Optional

_LOGGER = logging.getLogger(__name__)


def _is_coroutine_method(obj: Any, name: str) -> bool:
    """True when ``obj.name`` exists and is a coroutine function.

    Unwraps decorators so a wrapped coroutine method is still recognized, mirroring
    the async detection in :func:`azure.cosmos._backend.factory._is_async_credential`.
    """
    method = getattr(obj, name, None)
    if method is None:
        return False
    if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
        return True
    unwrapped = inspect.unwrap(method) if callable(method) else method
    return asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped)


class AsyncTokenCredentialBridge:
    """Wrap an async credential so the Rust driver's synchronous ``get_token`` works.

    See the module docstring for the why and the threading/GIL reasoning. The
    bridge picks the credential's coroutine token method once -- ``get_token``
    (returns an ``AccessToken``) when it is the coroutine, otherwise
    ``get_token_info`` (azure-core ``SupportsTokenInfo``, returns an
    ``AccessTokenInfo``); both expose ``.token`` / ``.expires_on``, which is all
    the binding reads. The dedicated event loop and its thread are created lazily
    on the first ``get_token`` call, so a bridge that is never used (e.g. a client
    that never issues a request) starts no thread.

    The bridge never closes the wrapped credential: the customer owns that
    credential's lifetime, exactly as the synchronous path leaves a customer's
    credential untouched. :meth:`close` only stops the bridge's own loop thread.
    """

    def __init__(self, async_credential: Any) -> None:
        self._credential = async_credential
        # Choose the coroutine token method up front. Prefer get_token (the
        # classic azure.identity.aio shape); fall back to get_token_info for a
        # SupportsTokenInfo-only async credential. If neither is a coroutine
        # (shouldn't happen -- the factory only wraps detected async credentials)
        # default to get_token so the failure is a clear one at call time.
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

    @staticmethod
    def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
        # Owns the loop for the life of the thread: run until stopped, then close.
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            loop.close()

    def _ensure_loop(self) -> asyncio.AbstractEventLoop:
        # Lazily start the dedicated loop thread the first time a token is needed.
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

        Drives the wrapped credential's coroutine on the bridge's dedicated event
        loop and blocks the calling thread until it completes. The result is the
        credential's own token object (``.token`` / ``.expires_on``), returned
        unchanged. Called by the Rust driver from a worker thread during request
        signing; the blocking wait releases the GIL so the loop thread can run.
        """
        loop = self._ensure_loop()
        coro = getattr(self._credential, self._token_method_name)(*scopes, **kwargs)
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        # No timeout: match the synchronous credential path, where a slow
        # get_token blocks too. The driver's own deadlines govern the operation.
        return future.result()

    def _close_cosmos_async_bridge(self) -> None:
        """Stop the dedicated loop thread. Idempotent and never raises.

        Deliberately given a distinctive, private name so a backend can close
        *this bridge* (via a ``getattr`` duck-type check) without ever calling
        ``close()`` on a customer's own credential -- sync or async -- which the
        bridge does not own.
        """
        with self._lock:
            loop = self._loop
            thread = self._thread
            self._loop = None
            self._thread = None
            self._closed = True
        if loop is None:
            return
        try:
            loop.call_soon_threadsafe(loop.stop)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to stop async-credential bridge loop", exc_info=True)
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=5)

