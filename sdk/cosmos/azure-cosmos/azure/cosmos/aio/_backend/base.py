# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract async backend type plus re-exports of the data classes.

Same as the sync ``CosmosBackend``, except ``execute`` is a coroutine so the
async container can ``await`` it without bridging threads. ``execute_pages``
is implemented for ``query_items`` / ``read_all_items`` (see
:class:`~azure.cosmos.aio._backend.rust.AsyncRustBackend`) as an async iterator;
``execute_batch`` is reserved here too and raises ``NotImplementedError`` until
the batch operation is added.

``PreparedRequest`` / ``BackendResponse`` and ``PreparedQuery`` / ``QueryPage`` /
the reserved ``PreparedBatch`` / ``BatchResponse`` and :class:`LegacyOperation`
are defined on the sync side (they carry pure data with no I/O) and re-exported
here.
"""
from __future__ import annotations

import abc
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

from azure.cosmos._backend.base import (
    BackendReply,
    BackendResponse,
    BatchResponse,
    LegacyOperation,
    PreparedBatch,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)

__all__ = [
    "AsyncCosmosBackend",
    "BackendReply",
    "BackendResponse",
    "BatchResponse",
    "LegacyOperation",
    "PreparedBatch",
    "PreparedQuery",
    "PreparedRequest",
    "QueryPage",
]


class AsyncCosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (async).

    A per-family async coordinator (``AsyncItemHelper``, ``AsyncThroughputHelper``,
    ``AsyncFeedRangeHelper``) holds one of these by interface and drives its
    operations through :meth:`run_operation` without knowing which concrete
    backend it has. Engine selection and legacy fallback happen behind this
    interface: a rust-backed client holds an :class:`AsyncRustBackend` and a
    core-python client holds an
    :class:`~azure.cosmos.aio._backend.legacy.AsyncLegacyBackend`, and every
    coordinator treats both the same -- none of them branch on ``None``, on
    which concrete backend they hold, or on ``execute`` returning ``None``. The
    operation kind is on ``prepared.op``; the backend branches on it.

    ``execute`` is the wire-level primitive (send one prepared request, return
    the raw reply) that the rust path uses; the async query/feed-range/offer
    routing helpers await it directly. The core-python
    :class:`~azure.cosmos.aio._backend.legacy.AsyncLegacyBackend` is **not**
    ``PreparedRequest``-driven, so it does not implement ``execute`` and instead
    overrides :meth:`run_operation` to await the legacy operation.
    """

    #: Short identifier surfaced in the startup INFO log and the
    #: per-request user-agent suffix. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single async Cosmos operation on the wire and return the raw reply.

        Dispatch on ``prepared.op`` and return a ``BackendResponse`` for the
        caller to parse. This is the rust wire primitive; a backend that does
        not send prepared requests (the core-python legacy backend) does not
        implement it.
        """
        ...

    async def run_operation(
        self,
        *,
        build_prepared: Callable[[], Awaitable[PreparedRequest]],
        legacy_operation: LegacyOperation,
        parse_response: Callable[[BackendResponse], Any],
        rust_eligible: bool = True,
        fallback_exceptions: tuple[type[BaseException], ...] = (),
    ) -> Any:
        """Run one engine-selected operation end to end and return the final result.

        The async twin of
        :meth:`azure.cosmos._backend.base.CosmosBackend.run_operation`: the
        single entry point every async family coordinator uses so none of them
        ever interpret ``None`` from selection or ``execute`` to decide the
        legacy path.

        The default is the engine (rust) flow: when the request is representable
        by this engine (``rust_eligible``), await ``build_prepared`` to construct
        the ``PreparedRequest`` lazily, await :meth:`execute`, then parse the
        reply (``parse_response`` is synchronous, matching the legacy path);
        otherwise await the supplied legacy operation. ``AsyncLegacyBackend``
        overrides this to always await the legacy operation.

        :keyword build_prepared: Awaitable builder for the rust ``PreparedRequest``
            (invoked only on the rust path).
        :keyword legacy_operation: Typed port to the legacy call; see
            :class:`~azure.cosmos._backend.base.LegacyOperation`. Its ``invoke``
            returns an awaitable of the final result.
        :keyword parse_response: Synchronous parser from ``BackendResponse`` to
            the final result.
        :keyword rust_eligible: ``False`` when this specific request cannot be
            represented on the rust path, which forces the legacy operation even on
            a rust-backed client.
        :keyword fallback_exceptions: Narrow, operation-specific compatibility
            failures that should retry through the supplied legacy operation.
        :returns: The final result the public method returns to the caller.
        :rtype: Any
        """
        if not rust_eligible:
            return await legacy_operation.invoke()
        try:
            prepared = await build_prepared()
            response = await self.execute(prepared)
            assert response is not None  # execute() only returns None for a None prepared request
            return parse_response(response)
        except fallback_exceptions:
            return await legacy_operation.invoke()

    # --- execute_pages is implemented by AsyncRustBackend; execute_batch is
    # reserved for the not-yet-built batch operation ----------------------
    #
    # Concrete (not abstract) so today's async backends stay valid without
    # implementing them. A backend adds query or batch support by overriding
    # the method; this class does not change.

    def execute_pages(self, prepared: PreparedQuery) -> AsyncIterator[QueryPage]:
        """Return a query (or read-many) result one ``QueryPage`` at a time.

        The default here raises; ``AsyncRustBackend`` overrides it (using
        ``QUERY_TO_BINDING_METHOD``) as an async iterator of ``QueryPage`` that
        dispatches ``query_items`` / ``read_all_items``.
        """
        raise NotImplementedError(
            "execute_pages is not implemented by this backend."
        )

    async def execute_batch(self, prepared: PreparedBatch) -> BatchResponse:
        """Run a transactional batch and return one result per operation.

        Reserved: the batch operation is not implemented yet, so this raises.
        A backend that supports it overrides it (using
        ``BATCH_TO_BINDING_METHOD``).
        """
        raise NotImplementedError(
            "execute_batch is reserved for the transactional-batch operation "
            "and is not implemented yet."
        )
