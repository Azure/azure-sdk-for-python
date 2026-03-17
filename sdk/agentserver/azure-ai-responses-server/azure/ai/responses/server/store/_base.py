"""Persistence abstraction for response execution and replay state."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .._generated import Response
from .._models import ResponseExecution, ResponseStatus, StreamEventRecord


class ResponseStore(Protocol):
    """Protocol implemented by response persistence backends.

    Store implementations must be concurrency-safe for async request handling.
    """

    async def create_execution(self, execution: ResponseExecution, *, ttl_seconds: int | None = None) -> None:
        """Create a new execution entry.

        :raises ValueError: If an entry for ``execution.response_id`` already exists.
        """

    async def get_execution(self, response_id: str) -> ResponseExecution | None:
        """Load execution state by response ID, or ``None`` when not found/expired."""

    async def set_response_snapshot(
        self,
        response_id: str,
        response: Response,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Set latest response snapshot for an existing execution.

        Returns ``True`` when updated and ``False`` when the response ID does not exist.
        """

    async def transition_execution_status(
        self,
        response_id: str,
        next_status: ResponseStatus,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Transition execution lifecycle status for an existing entry.

        Returns ``True`` when updated and ``False`` when the response ID does not exist.
        :raises ValueError: If the transition is invalid.
        """

    async def set_cancel_requested(self, response_id: str, *, ttl_seconds: int | None = None) -> bool:
        """Mark execution cancel intent for an existing entry.

        Returns ``True`` when updated and ``False`` when the response ID does not exist.
        """

    async def append_stream_event(
        self,
        response_id: str,
        event: StreamEventRecord,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Append one stream event to replay history.

        Returns ``True`` when appended and ``False`` when the response ID does not exist.
        :raises ValueError: If replay sequence integrity is violated.
        """

    async def get_stream_events(self, response_id: str) -> list[StreamEventRecord] | None:
        """Get replay events for a response ID, or ``None`` when not found/expired."""

    async def delete(self, response_id: str) -> bool:
        """Delete an execution entry and replay history.

        Returns ``True`` when deleted and ``False`` when not found.
        """

    async def purge_expired(self, *, now: datetime | None = None) -> int:
        """Purge expired entries and return the number of removed records."""
