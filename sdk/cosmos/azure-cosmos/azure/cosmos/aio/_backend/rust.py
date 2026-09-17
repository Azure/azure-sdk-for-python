# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async backend that sends operations to the rust driver through the compiled binding.

Terms, consistent across the backend layer: the **binding** is the compiled
``azure.cosmos._rust`` extension Python calls into; the **rust driver** is the
driver the binding builds (it owns the connection pool, request signing, and
region routing); the **driver handle** is the string ``acquire_driver_handle`` returns -- a
key made from ``(endpoint, credential, config)`` that names *which* rust driver a
client uses. The compiled ``_rust`` file contains both the binding and the rust
driver code.

This is one of only two modules allowed to import ``azure.cosmos._rust``
(a unit test enforces that). The binding is not present until it
has been built, so the import is guarded; until then, operations raise
``NotImplementedError`` pointing at the build step.
"""
from __future__ import annotations
from ..._backend.request_settings import native_settings_contract_error
from dataclasses import replace

import asyncio
import json
import logging
import threading
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from azure.cosmos._backend.operations import (
    OP_LIST_CONTAINERS,
    OP_LIST_DATABASES,
    OP_READ_ALL_ITEMS,
    OP_QUERY_CHANGE_FEED,
    OP_QUERY_ITEMS,
    OP_TO_BINDING_METHOD,
    get_page_binding_method,
)
from azure.cosmos._backend.errors import BackendProtocolError, PageNotSupportedByBackendError, QueryNotSupportedByBackendError
from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedClientConfig,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from azure.cosmos._backend._binding_conversions import (
    build_backend_response, build_container_metadata, metadata_exception_from_binding,
)
from azure.cosmos._backend._shared import (
    RustBackendShared,
    _binding_error_type,
    close_credential_bridge_quietly,
    configure_packaged_query_plan_interop,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
)
from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from azure.core.exceptions import ServiceResponseError
from ..._operation_deadline import remaining_timeout
from ...exceptions import CosmosClientTimeoutError

from .cosmos_backend import AsyncCosmosBackend

if TYPE_CHECKING:
    from azure.cosmos._rust import ItemFeedCursor

_LOGGER = logging.getLogger(__name__)

# Paged feeds that take no SQL, so their binding request carries an empty body.
# Every other paged op is a query and must supply one.
_PARAMETERLESS_FEED_OPS = frozenset({OP_READ_ALL_ITEMS, OP_LIST_DATABASES, OP_LIST_CONTAINERS})

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
    configure_packaged_query_plan_interop(_rust_module)
except ImportError:
    _LOGGER.debug(
        "_rust module not available; AsyncRustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# The binding's response-less transport error, captured once at load. A driver
# op that fails before any wire response raises this; we re-raise it as
# azure-core's ServiceResponseError (see driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_native_runtime_module = _rust_module
_REQUEST_CONTRACT_ERROR = native_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up the binding's ``<op>_async`` function for an operation. Read live from
# ``_rust_module`` rather than cached at import, so the tests can swap in a fake
# binding; the extra getattr per call is tiny next to the network round trip.
def _get_binding_function(op: str) -> Optional[Any]:
    """Return the binding's ``<op>_async`` function, or ``None`` if the op is
    unsupported or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method + "_async", None)


def _get_page_dispatch(method: Optional[str]) -> Optional[Any]:
    """Look up the selected async page binding without changing execution mode."""
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method + "_async", None)


def build_binding_request_from_page(prepared: PreparedQuery) -> PreparedRequest:
    """Convert a prepared page request to the request shape accepted by Rust."""
    if prepared.op == OP_QUERY_CHANGE_FEED:
        body = json.dumps(prepared.change_feed, separators=(",", ":")).encode("utf-8")
    elif prepared.op in _PARAMETERLESS_FEED_OPS:
        body = b""
    else:
        if prepared.query is None:
            raise ValueError("{} requires PreparedQuery.query.".format(prepared.op))
        payload: dict[str, Any] = {"query": prepared.query}
        if prepared.parameters:
            payload["parameters"] = list(prepared.parameters)
        if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None:
            payload = {"query": payload, **(prepared.query_scope.as_dict() if prepared.query_scope is not None else {})}
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = dict(prepared.headers)
    query_settings = prepared.settings.query
    if prepared.continuation is not None:
        headers.pop("x-ms-continuation", None)
        query_settings = replace(query_settings, continuation=prepared.continuation)
    if prepared.max_item_count is not None:
        headers.pop("x-ms-max-item-count", None)
        query_settings = replace(query_settings, max_item_count=prepared.max_item_count)
    return PreparedRequest(
        op=prepared.op,
        container_link=prepared.container_link,
        body_bytes=body,
        partition_key=prepared.partition_key,
        headers=headers,
        settings=replace(prepared.settings, query=query_settings),
    )


def _close_driver_handle_quietly(driver_handle: str) -> None:
    """Drop one client's reference to the shared rust driver named by ``handle``;
    never raise.

    Calls the binding's ``release_driver_handle(driver_handle)``, which decrements the rust
    driver's reference count and tears the driver down only when the last client
    sharing it closes. Used by close(), finalization, and when a handle was built
    just as the client was closing and now has to be thrown away.
    """
    if _rust_module is None:
        return
    release_driver_handle = getattr(_rust_module, "release_driver_handle", None)
    if release_driver_handle is None:
        return
    try:
        release_driver_handle(driver_handle)
    except Exception:  # pylint: disable=broad-except
        _LOGGER.debug("Failed closing handle %s", driver_handle, exc_info=True)


def _runtime_configuration() -> Optional[tuple[Optional[bool], Optional[float], Optional[float]]]:
    if _native_runtime_module is None:
        return None
    return _native_runtime_module.runtime_configuration()


class AsyncRustBackend(RustBackendShared, AsyncCosmosBackend):
    """Sends async operations from one ``CosmosClient`` to a shared rust driver.

    Terms are the same as the sync backend: the **binding** is the compiled
    ``azure.cosmos._rust`` extension; the **rust driver** is the driver it builds
    (connection pool, request signing, region routing); the **driver handle** is
    the string ``acquire_driver_handle`` returns, a key made from ``(endpoint, credential,
    config)`` naming which rust driver a client uses. The binding keeps one rust
    driver per distinct ``(endpoint, credential, config)`` and reference-counts it,
    so same-settings clients share one rust driver.

    Each operation calls the binding's ``*_item_async`` function, which returns an
    awaitable that finishes on the binding's shared Tokio runtime -- the one
    process-wide thread pool where every rust driver's work runs, not a per-driver
    runtime. Awaiting it uses no Python thread, so the number of operations in
    flight is limited by the service and the driver's connection pool, not by a
    thread count. The only blocking step is building the handle once in
    ``_ensure_driver_handle``, run on a background thread. When the compiled binding is
    missing, every operation raises ``NotImplementedError``.

    Per-client state, guard registration, and teardown live in
    :class:`~azure.cosmos._backend._shared.RustBackendShared`; this class adds the
    cross-event-loop handle-build coalescing and the awaitable dispatch.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
        strict_isolation: bool = False,
    ) -> None:
        """Store client settings and prepare lazy Rust driver initialization."""
        # Backend-specific fields first, so they exist even if the shared init's
        # strict-mode registration raises and the finalizer then runs.
        # _build_lock lets only one build run at a time, so acquire_driver_handle is called once
        # even when two event loops share this client. _driver_handle_lock (set by the shared
        # init) is held only to set or read the handle and the closing flag, never
        # during acquire_driver_handle, so close() never waits for a build to finish.
        self._build_lock = threading.Lock()
        # When many operations start at once on a fresh client they all need the
        # handle. These hold the one running build so they share it instead of each
        # starting their own (see _ensure_driver_handle). Read and set on the event-loop
        # thread only.
        self._init_future: Optional["asyncio.Future[str]"] = None
        self._init_future_loop: Optional[asyncio.AbstractEventLoop] = None
        # Shared per-client state + endpoint registration (may raise in strict mode).
        self._init_shared(
            endpoint, master_key, client_config, token_credential, strict_isolation
        )

    def _build_driver_handle(self) -> str:
        """Create or share the Rust driver handle on a worker thread."""
        # Runs on a background thread; acquire_driver_handle makes a network call that can take
        # seconds. _build_lock makes that call happen once. It is held during the call,
        # but _driver_handle_lock is not, so close() (which only takes _driver_handle_lock) never
        # waits here. If the client closed during the call, the handle just built is
        # closed instead of left open.
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        if self._driver_handle is not None:
            return self._driver_handle
        surplus_driver_handle: Optional[str] = None
        with self._build_lock:
            # Another loop may have built it while we waited for _build_lock.
            if self._driver_handle is not None:
                return self._driver_handle
            if self._closing:
                raise RuntimeError("AsyncRustBackend: the client is closed.")
            new_driver_handle: Optional[str] = self._initialize_driver(_rust_module, _runtime_configuration)
            with self._driver_handle_lock:
                if self._closing:
                    surplus_driver_handle, new_driver_handle = new_driver_handle, None
                else:
                    self._driver_handle = new_driver_handle
        if surplus_driver_handle is not None:
            _close_driver_handle_quietly(surplus_driver_handle)
        if new_driver_handle is None:
            raise RuntimeError(
                "AsyncRustBackend: the client was closed during initialization."
            )
        return new_driver_handle

    def _take_driver_handle_for_close(self) -> Optional[str]:
        """Mark the client closed and remove its current Rust handle."""
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
            return driver_handle

    async def _ensure_driver_handle(self) -> str:
        """Return the Rust handle, sharing one initialization across callers."""
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        # If the handle is already built, return it without locking.
        driver_handle = self._driver_handle
        if driver_handle is not None:
            return driver_handle
        loop = asyncio.get_running_loop()
        # acquire_driver_handle blocks, so build the handle once on a background thread. When
        # many operations start at once on a fresh client they all reach here before
        # the handle exists; share one build so they don't each start their own. The
        # check-and-set has no await in it, so only one future is created -- a new one
        # if a different loop drives this backend, so it is never bound to a loop that
        # is gone.
        init_future = self._init_future
        if init_future is None or self._init_future_loop is not loop:
            init_future = loop.run_in_executor(None, self._build_driver_handle)
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
        """Drop this client's reference to the shared rust driver.

        Call this once every operation on the client has finished. An operation that
        is still running keeps its own handle, so closing while one is in flight makes
        that operation fail with a closed-client error. Releasing this client's
        reference lets the binding tear the rust driver down when the last client
        sharing it closes.
        """
        driver_handle = self._take_driver_handle_for_close()
        credential = self._take_token_credential_for_close()
        self._release_config_once()

        def teardown() -> None:
            close_credential_bridge_quietly(credential)
            if driver_handle is not None:
                _close_driver_handle_quietly(driver_handle)

        # Transfer ownership before awaiting, so cancellation cannot strand it.
        loop = asyncio.get_running_loop()
        await asyncio.shield(loop.run_in_executor(None, teardown))

    def __del__(self) -> None:
        """Release resources if the client was not closed explicitly."""
        # Fallback for a client that was never closed explicitly; prefer calling
        # close() (or `async with`). The teardown calls into the Rust driver
        # (release_driver_handle) and may join the credential-bridge thread, both of which
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
            credential = self._take_token_credential_for_close()
            driver_handle = self._take_driver_handle_for_close()
            if driver_handle is None and credential is None:
                return

            def _blocking_teardown() -> None:
                """Release resources that may briefly block the current thread."""
                close_credential_bridge_quietly(credential)
                if driver_handle is not None:
                    _close_driver_handle_quietly(driver_handle)

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

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Send one prepared single-response operation."""
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Build it with `maturin develop` from "
                "the repo root."
            )

        driver_handle = await self._ensure_driver_handle()
        # Look up the binding's *_item_async function for this op; None if unsupported.
        binding_function = _get_binding_function(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        # Log which backend and op ran, so a migration can confirm from logs that
        # traffic stays on the Rust path. The handle is omitted (it carries a
        # credential fingerprint).
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_METHOD.get(prepared.op),
        )
        # The *_item_async function returns an awaitable that finishes on the binding's
        # shared Tokio runtime (one process-wide thread pool, not a per-driver runtime),
        # so the pending request does not reserve a dedicated Python worker thread.
        # Only the one-time acquire_driver_handle in _ensure_driver_handle runs on a background thread.
        # A response-less driver failure (transport error, client-side validation,
        # pre-HTTP timeout) surfaces as the binding's DriverTransportError;
        # translate it to azure-core's ServiceResponseError so customer handlers
        # and transport-retry policies match the legacy path.
        try:
            result = (
                await binding_function(driver_handle, prepared)
                if deadline is None
                else await binding_function(driver_handle, prepared, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        if result is None:
            raise BackendProtocolError(f"The binding returned no response for {prepared.op!r}")
        return build_backend_response(*result)

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Get routing facts from the driver's cache, fetching on a miss."""
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        dispatch = getattr(_rust_module, "get_container_metadata_async", None)
        if dispatch is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata_async")
        driver_handle = await self._ensure_driver_handle()
        try:
            result = (
                await dispatch(driver_handle, container_link)
                if deadline is None
                else await dispatch(driver_handle, container_link, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        return build_container_metadata(result)

    async def execute_pages(
        self, prepared: PreparedQuery, *, deadline: Optional[float] = None
    ) -> AsyncIterator[QueryPage]:
        """Yield the one page returned by an async ``query_items`` /
        ``read_all_items`` / ``list_databases`` binding call."""
        self.validate_page_request(prepared)
        method = get_page_binding_method(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        dispatch = _get_page_dispatch(method)
        if dispatch is None:
            raise BackendProtocolError("Validated page dispatch is no longer available")
        driver_handle = await self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            method,
        )
        try:
            if prepared.cursor is not None:
                result = await dispatch(
                    driver_handle,
                    binding_request,
                    prepared.cursor,
                    timeout_seconds=remaining_timeout(deadline),
                )
            else:
                result = await dispatch(driver_handle, binding_request)
            response = build_backend_response(*result)
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _UNSUPPORTED_QUERY_ERROR as exc:
            raise QueryNotSupportedByBackendError(str(exc)) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        continuation = (
            response.headers.get("x-ms-continuation") if response.headers else None
        )
        yield QueryPage(
            status_code=response.status_code,
            continuation=continuation,
            sub_status=response.sub_status,
            headers=response.headers,
            body=response.body,
            diagnostics=response.diagnostics,
            has_more=(
                prepared.cursor.has_more
                if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None
                else None
            ),
            continuation_supported=(
                prepared.cursor.continuation_supported
                if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None
                else True
            ),
        )

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Check module/export availability without acquiring a driver."""
        if _rust_module is None:
            raise PageNotSupportedByBackendError(
                "AsyncRustBackend.execute_pages: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        uses_cursor = prepared.cursor is not None
        method = get_page_binding_method(prepared.op, uses_cursor=uses_cursor)
        dispatch = _get_page_dispatch(method)
        if uses_cursor and method is not None and dispatch is None:
            raise RuntimeError(
                f"The compiled azure.cosmos._rust extension does not export {method}_async; "
                "rebuild it from the current source."
            )
        if dispatch is None:
            raise PageNotSupportedByBackendError(
                "AsyncRustBackend.execute_pages does not yet support op={!r}.".format(
                    prepared.op
                )
            )

    def create_item_feed_cursor(self) -> ItemFeedCursor:
        """Create pager-owned state without acquiring a driver."""
        if _rust_module is None:
            raise PageNotSupportedByBackendError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "ItemFeedCursor"):
            raise RuntimeError(
                "The compiled extension lacks ItemFeedCursor; rebuild it from the current source."
            )
        return _rust_module.ItemFeedCursor()
