# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async backend dispatch. Two wire reply shapes: single responses and pages.

Migrated point and retained-feed helpers execute directly. Remaining migration
coordinators pass an OperationRouting, a lazy builder, a response processor and
an optional legacy callable. Policy is centralized in capabilities.py; request
compatibility remains request-dependent. Explicit legacy selection skips request
building. Only allowed ineligibility/static preflight can route to legacy;
execution, parsing and callback failures never replay.

Prepared records carry wire data, not invocation deadlines. Native item cursors
are created lazily by their owning pagers through the backend factory. Client
registration reservations and native driver references retain separate lifetimes.
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Awaitable, Any, AsyncIterator, Callable, Optional

from azure.cosmos._backend.capabilities import OperationRouting
from azure.cosmos._backend.errors import (
    BackendProtocolError,
    PageNotSupportedByBackendError,
)

from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from azure.cosmos._backend._fallback_metrics import record_rust_compatibility_fallback

__all__ = ["AsyncCosmosBackend"]


if TYPE_CHECKING:
    from azure.cosmos._rust import ItemFeedCursor


class AsyncCosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (async).

    Migrated item helpers call ``execute`` directly, with no legacy port.
    The other dispatch methods remain migration ports for other families.

    A still-migrating async coordinator (``AsyncThroughputHelper``,
    ``AsyncFeedRangeHelper``) holds one of these by interface and drives its
    operations through :meth:`run_operation` or :meth:`run_page_operation`
    without knowing which concrete backend it has. Driver selection and legacy
    fallback happen behind this
    interface: a rust-backed client holds an :class:`AsyncRustBackend` and a
    core-python client holds an
    :class:`~azure.cosmos.aio._backend.legacy.AsyncLegacyBackend`, and every
    coordinator treats both the same -- none of them branch on ``None``, on
    which concrete backend they hold, or on a wire primitive returning
    ``None``. The operation kind is on ``prepared.op``; the backend branches on
    it.

    ``execute`` and ``execute_pages`` are the wire-level primitives used behind
    those two coordinator methods. The core-python
    :class:`~azure.cosmos.aio._backend.legacy.AsyncLegacyBackend` is **not**
    ``PreparedRequest``-driven, so it does not implement ``execute`` and instead
    overrides :meth:`run_operation` and :meth:`run_page_operation` to await the
    legacy operation.

    The legacy implementation and compatibility fallback are temporary parity
    scaffolding; the migration target is complete Rust coverage.
    """

    #: Short identifier surfaced in the startup INFO log and the
    #: per-request user-agent suffix. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Issue a single async Cosmos operation on the wire and return the raw reply.

        Dispatch on ``prepared.op`` and return a ``BackendResponse`` for the
        caller to parse, including for an empty successful body. A missing
        request is invalid; a missing native reply is a protocol error.
        ``deadline`` is the caller's existing absolute monotonic budget,
        converted to remaining time at dispatch.
        This is the rust wire primitive; a backend that does
        not send prepared requests (the core-python legacy backend) does not
        implement it.
        """
        ...

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Get immutable routing facts; unsupported backends must fail explicitly."""
        raise NotImplementedError("This backend does not provide container metadata")

    async def run_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedRequest],
        process_response: Callable[[BackendResponse], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Apply migration policy before dispatch; never replay execution or parsing errors."""
        if routing.uses_legacy():
            if legacy_call is None:
                raise BackendProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return await legacy_call()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BackendProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        response = await self.execute(prepared, deadline=deadline)
        return process_response(response)

    async def run_page_operation(
        self,
        *,
        routing: OperationRouting,
        build_request: Callable[[], PreparedQuery],
        process_response: Callable[[QueryPage], Any],
        legacy_call: Optional[Callable[[], Awaitable[Any]]] = None,
        deadline: Optional[float] = None,
    ) -> Any:
        """Apply migration policy before dispatch; never replay execution or parsing errors."""
        if routing.uses_legacy():
            if legacy_call is None:
                raise BackendProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return await legacy_call()
        prepared = build_request()
        if prepared.op != routing.op:
            raise BackendProtocolError(
                f"Prepared operation {prepared.op!r} does not match {routing.op!r}"
            )
        try:
            self.validate_page_request(prepared)
        except PageNotSupportedByBackendError as error:
            if (
                type(error) is not PageNotSupportedByBackendError
                or not routing.policy.fallback_allowed
                or prepared.continuation is not None
            ):
                raise
            if legacy_call is None:
                raise BackendProtocolError(
                    f"No legacy callable supplied for {routing.op!r}"
                )
            record_rust_compatibility_fallback()
            return await legacy_call()
        pages = self.execute_pages(prepared, deadline=deadline)
        try:
            page = await pages.__anext__()
        except StopAsyncIteration as error:
            raise BackendProtocolError(
                f"{type(self).__name__} returned no page for {routing.op!r}"
            ) from error
        finally:
            close = getattr(pages, "aclose", None)
            if close is not None:
                await close()
        return process_response(page)

    def execute_pages(
        self, prepared: PreparedQuery, *, deadline: Optional[float] = None
    ) -> AsyncIterator[QueryPage]:
        """Return a paged query or read-feed result one ``QueryPage`` at a time.

        The default here raises; ``AsyncRustBackend`` overrides it (using
        ``STATELESS_QUERY_TO_BINDING_METHOD``) as an async iterator of ``QueryPage`` that
        dispatches ``query_items`` / ``read_all_items`` / ``list_databases``. A
        backend that does not implement this -- ``AsyncLegacyBackend`` never
        reaches it, since :meth:`run_page_operation` invokes the legacy call
        directly -- keeps this raising default.

        ``deadline`` supplies the existing monotonic budget to supported native
        cursor execution. Stateless feeds retain their driver request timeouts.
        """
        raise NotImplementedError("execute_pages is not implemented by this backend.")

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Validate static page capability before execution; no I/O or driver acquisition."""

    def create_item_feed_cursor(self) -> ItemFeedCursor:
        """Create local native cursor state, without acquiring a driver."""
        raise NotImplementedError(
            "This backend does not provide native item-feed cursors"
        )
