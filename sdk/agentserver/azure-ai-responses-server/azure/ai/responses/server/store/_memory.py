"""In-memory response store implementation."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

from .._generated import Response
from .._models import ResponseExecution, ResponseStatus, StreamEventRecord, StreamReplayState
from ._base import ResponseStore


@dataclass(slots=True)
class _StoreEntry:
    """Container for one response execution and its replay state."""

    execution: ResponseExecution
    replay: StreamReplayState
    expires_at: datetime | None = None


class InMemoryResponseStore(ResponseStore):
    """In-memory response store with TTL and lifecycle-safe mutation APIs."""

    def __init__(self) -> None:
        """Initialize in-memory state and an async mutation lock."""
        self._entries: Dict[str, _StoreEntry] = {}
        self._lock = asyncio.Lock()

    async def create_execution(self, execution: ResponseExecution, *, ttl_seconds: int | None = None) -> None:
        """Create a new execution and replay container for ``execution.response_id``."""
        async with self._lock:
            self._purge_expired_unlocked()

            if execution.response_id in self._entries:
                raise ValueError(f"response '{execution.response_id}' already exists")

            self._entries[execution.response_id] = _StoreEntry(
                execution=deepcopy(execution),
                replay=StreamReplayState(response_id=execution.response_id),
                expires_at=self._compute_expiry(ttl_seconds),
            )

    async def get_execution(self, response_id: str) -> ResponseExecution | None:
        """Get a defensive copy of execution state for ``response_id`` if present."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return None
            return deepcopy(entry.execution)

    async def set_response_snapshot(
        self,
        response_id: str,
        response: Response,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Set the latest response snapshot for an existing response execution."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.execution.set_response_snapshot(response)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def transition_execution_status(
        self,
        response_id: str,
        next_status: ResponseStatus,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Transition execution state while preserving lifecycle invariants."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.execution.transition_to(next_status)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def set_cancel_requested(self, response_id: str, *, ttl_seconds: int | None = None) -> bool:
        """Mark cancellation requested for an existing execution record."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.execution.cancel_requested = True
            entry.execution.updated_at = datetime.now(timezone.utc)
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def append_stream_event(
        self,
        response_id: str,
        event: StreamEventRecord,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Append one stream event to replay state for an existing execution."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return False

            entry.replay.append(deepcopy(event))
            self._apply_ttl_unlocked(entry, ttl_seconds)
            return True

    async def get_stream_events(self, response_id: str) -> list[StreamEventRecord] | None:
        """Get defensive copies of all replay events for ``response_id``."""
        async with self._lock:
            self._purge_expired_unlocked()
            entry = self._entries.get(response_id)
            if entry is None:
                return None
            return deepcopy(entry.replay.events)

    async def delete(self, response_id: str) -> bool:
        """Delete all state for a response ID if present."""
        async with self._lock:
            self._purge_expired_unlocked()
            return self._entries.pop(response_id, None) is not None

    async def purge_expired(self, *, now: datetime | None = None) -> int:
        """Remove expired entries and return count."""
        async with self._lock:
            return self._purge_expired_unlocked(now=now)

    @staticmethod
    def _compute_expiry(ttl_seconds: int | None) -> datetime | None:
        """Compute an absolute expiration timestamp from a TTL."""
        if ttl_seconds is None:
            return None
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0 when set")
        return datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    def _apply_ttl_unlocked(self, entry: _StoreEntry, ttl_seconds: int | None) -> None:
        """Update entry expiration timestamp when a TTL value is supplied."""
        if ttl_seconds is not None:
            entry.expires_at = self._compute_expiry(ttl_seconds)

    def _purge_expired_unlocked(self, *, now: datetime | None = None) -> int:
        """Remove expired entries without acquiring the lock."""
        current_time = now or datetime.now(timezone.utc)
        expired_ids = [
            response_id
            for response_id, entry in self._entries.items()
            if entry.expires_at is not None and entry.expires_at <= current_time
        ]

        for response_id in expired_ids:
            del self._entries[response_id]

        return len(expired_ids)
