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
from azure.cosmos._backend._driver_registry import (
    register_client_config,
    release_client_config,
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


# Look up the binding's ``<op>_async`` function for an operation. Read live from
# ``_rust_module`` rather than cached at import, so the tests can swap in a fake
# binding; the extra getattr per call is tiny next to the network round trip.
def _resolve_async_dispatch(op: str) -> Optional[Any]:
    """Return the binding's ``<op>_async`` function, or ``None`` if the op is
    unsupported or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method + "_async", None)


def _close_handle_quietly(handle: str) -> None:
    """Close the driver-side client for ``handle``; never raise.

    Used by close(), finalization, and when a handle was built just as the client
    was closing and now has to be thrown away.
    """
    if _rust_module is None:
        return
    close_client = getattr(_rust_module, "close_client", None)
    if close_client is None:
        return
    try:
        close_client(handle)
    except Exception:  # pylint: disable=broad-except
        _LOGGER.debug("Failed closing handle %s", handle, exc_info=True)


def _close_credential_bridge_quietly(credential: Optional[Any]) -> None:
    """Stop our async-credential bridge if ``credential`` is one; never raise.

    The method-name check means we only ever close our own wrapper
    (``AsyncTokenCredentialBridge``), never a customer's credential. Shared by
    ``close()`` and the finalizer so the duck-typed check lives in one place.
    """
    closer = getattr(credential, "_close_cosmos_async_bridge", None)
    if callable(closer):
        try:
            closer()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed closing async-credential bridge", exc_info=True)


class AsyncRustBackend(AsyncCosmosBackend):
    """Sends async operations to the Rust driver.

    Each operation calls the binding's ``*_item_async`` function, which returns an
    awaitable that finishes on the driver's own runtime. Awaiting it uses no Python
    thread, so the number of operations in flight is limited by the service and the
    driver's connection pool, not by a thread count. The only blocking step is
    building the client once in ``_ensure_handle``, run on a background thread. When
    the compiled module is missing, every operation raises ``NotImplementedError``.
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
        # reused; ``None`` until then.
        self._handle: Optional[str] = None
        # _build_lock lets only one build run at a time, so init_client is called
        # once even when two event loops share this client. _handle_lock is held only
        # to set or read the handle and the closing flag, never during init_client,
        # so close() never waits for a build to finish.
        self._handle_lock = threading.Lock()
        self._build_lock = threading.Lock()
        # Set by close(). A build checks it before storing its handle, so a handle
        # built while the client is closing is closed instead of left open.
        self._closing = False
        # When many operations start at once on a fresh client they all need the
        # handle. These hold the one running build so they share it instead of each
        # starting their own (see _ensure_handle). Read and set on the event-loop
        # thread only.
        self._init_future: Optional["asyncio.Future[str]"] = None
        self._init_future_loop: Optional[asyncio.AbstractEventLoop] = None
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
        # If the credential is our async-to-sync bridge, stop its event-loop thread.
        # The method-name check (in the shared helper) means we only close our own
        # wrapper, never a customer's credential. Stopping an idle loop is near-instant.
        _close_credential_bridge_quietly(self._token_credential)

    def _build_handle(self) -> str:
        # Runs on a background thread; init_client makes a network call that can take
        # seconds. _build_lock makes that call happen once. It is held during the call,
        # but _handle_lock is not, so close() (which only takes _handle_lock) never
        # waits here. If the client closed during the call, the handle just built is
        # closed instead of left open.
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        if self._handle is not None:
            return self._handle
        surplus: Optional[str] = None
        with self._build_lock:
            # Another loop may have built it while we waited for _build_lock.
            if self._handle is not None:
                return self._handle
            if self._closing:
                raise RuntimeError("AsyncRustBackend: the client is closed.")
            new_handle = _rust_module.init_client(
                *init_client_args(
                    self._endpoint,
                    self._master_key,
                    self._client_config,
                    self._token_credential,
                )
            )
            with self._handle_lock:
                if self._closing:
                    surplus, new_handle = new_handle, None
                else:
                    self._handle = new_handle
        if surplus is not None:
            _close_handle_quietly(surplus)
        if new_handle is None:
            raise RuntimeError(
                "AsyncRustBackend: the client was closed during initialization."
            )
        return new_handle

    def _take_handle_for_close(self) -> Optional[str]:
        with self._handle_lock:
            self._closing = True
            handle = self._handle
            self._handle = None
            return handle

    async def _ensure_handle(self) -> str:
        # If the handle is already built, return it without locking.
        handle = self._handle
        if handle is not None:
            return handle
        loop = asyncio.get_running_loop()
        # init_client blocks, so build the handle once on a background thread. When
        # many operations start at once on a fresh client they all reach here before
        # the handle exists; share one build so they don't each start their own. The
        # check-and-set has no await in it, so only one future is created -- a new one
        # if a different loop drives this backend, so it is never bound to a loop that
        # is gone.
        init_future = self._init_future
        if init_future is None or self._init_future_loop is not loop:
            init_future = loop.run_in_executor(None, self._build_handle)
            self._init_future = init_future
            self._init_future_loop = loop
        try:
            return await init_future
        finally:
            # Clear the shared future once it finishes so a failed build is retried
            # next time instead of returning the same error. On success the handle is
            # set, so later calls return it directly and never rebuild.
            if self._init_future is init_future:
                self._init_future = None
                self._init_future_loop = None

    async def close(self) -> None:
        """Release the Rust client handle.

        Call this once every operation on the client has finished. An operation that
        is still running keeps its own handle, so closing while one is in flight makes
        that operation fail with a closed-client error.
        """
        self._release_config_once()
        loop = asyncio.get_running_loop()
        # Stopping the credential bridge can wait a few seconds for its thread (if a
        # token fetch is stuck), so do it on a background thread, not the event loop.
        await loop.run_in_executor(None, self._close_token_credential_bridge)
        handle = self._take_handle_for_close()
        if handle is not None:
            await loop.run_in_executor(None, _close_handle_quietly, handle)

    def __del__(self) -> None:
        # Fallback for a client that was never closed explicitly; prefer calling
        # close() (or `async with`). The teardown calls into the Rust driver
        # (close_client) and may join the credential-bridge thread, both of which
        # can block briefly. A finalizer can run on ANY thread -- including the
        # event-loop thread, when GC collects the client mid-run -- so blocking
        # here would stall that loop. To avoid it: drop the (non-blocking) config
        # registration inline, then run the blocking teardown on a short-lived
        # daemon thread if a loop is running on this thread, or inline otherwise
        # (the usual finalizer case, and interpreter shutdown where a new thread
        # may not start). The closure captures only the handle and credential, not
        # self, so the finalizer does not resurrect the object.
        try:
            self._release_config_once()
            credential = self._token_credential
            handle = self._take_handle_for_close()
            if handle is None and credential is None:
                return

            def _blocking_teardown() -> None:
                _close_credential_bridge_quietly(credential)
                if handle is not None:
                    _close_handle_quietly(handle)

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # No loop on this thread: safe to block here.
                _blocking_teardown()
                return
            try:
                threading.Thread(
                    target=_blocking_teardown,
                    name="cosmos-rust-finalizer",
                    daemon=True,
                ).start()
            except Exception:  # pylint: disable=broad-except
                # Could not start a thread (e.g. during interpreter shutdown);
                # fall back to inline cleanup.
                _blocking_teardown()
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Send one point operation (read/create/upsert/replace/delete/patch) to the Rust driver."""
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
        # Look up the binding's *_item_async function for this op; None if unsupported.
        dispatch = _resolve_async_dispatch(prepared.op)
        if dispatch is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        # The *_item_async function returns an awaitable that finishes on the driver's
        # own runtime, so awaiting it uses no Python thread. Only the one-time
        # init_client in _ensure_handle still runs on a background thread.
        result = await dispatch(handle, prepared)
        return build_backend_response(*result)
