# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Abstract async backend type plus re-exports of the data classes.

Same as the sync ``CosmosBackend``, except ``execute`` is a coroutine so the
async container can ``await`` it without bridging threads. ``execute_pages``
and ``execute_batch`` are reserved here too and raise ``NotImplementedError``
until the query and batch operations are added.

``PreparedRequest`` / ``BackendResponse`` and the reserved ``PreparedQuery`` /
``QueryPage`` / ``PreparedBatch`` / ``BatchResponse`` are defined on the sync
side (they carry pure data with no I/O) and re-exported here.
"""
from __future__ import annotations

import abc
from typing import AsyncIterator, Optional

from azure.cosmos._backend.base import (
    BackendReply,
    BackendResponse,
    BatchResponse,
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
    "PreparedBatch",
    "PreparedQuery",
    "PreparedRequest",
    "QueryPage",
]


class AsyncCosmosBackend(abc.ABC):
    """Abstract dispatch target for any Cosmos operation (async).

    The async helper holds one of these by interface and awaits ``execute``
    on it without knowing which concrete backend it has. The operation kind
    is on ``prepared.op``; the backend branches on it.

    The helper already builds the ``PreparedRequest`` before awaiting ``execute``
    and parses the returned ``BackendResponse`` with ``parse_backend_response`` --
    it does this for every operation -- so a backend only has to send the
    request and report the reply. ``execute`` may still return ``None`` as a
    fallback, which tells the helper to run the legacy in-place
    core-python implementation; that path is kept only for testing, not
    production.
    """

    #: Short identifier surfaced in the startup INFO log and the
    #: per-request user-agent suffix. Subclasses set this from
    #: ``BACKEND_NAME_RUST`` etc.
    name: str = "abstract"

    @abc.abstractmethod
    async def execute(self, prepared: Optional[PreparedRequest]) -> Optional[BackendResponse]:
        """Issue a single async Cosmos operation.

        Dispatch on ``prepared.op``. Return ``None`` to let the caller
        run the legacy implementation, or a ``BackendResponse`` to have
        the caller parse the result.
        """
        ...

    # --- Reserved methods for the query and batch operations ---------------
    #
    # Concrete (not abstract) so today's async backends stay valid without
    # implementing them. A backend adds query or batch support by overriding
    # the method; this class does not change.

    def execute_pages(self, prepared: PreparedQuery) -> AsyncIterator[QueryPage]:
        """Return a query (or read-many) result one ``QueryPage`` at a time.

        Reserved: the query operations are not implemented yet, so this raises.
        A backend that supports them overrides it as an async iterator of
        ``QueryPage`` (using ``QUERY_TO_BINDING_METHOD``).
        """
        raise NotImplementedError(
            "execute_pages is reserved for the query and read-many operations "
            "and is not implemented yet."
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

