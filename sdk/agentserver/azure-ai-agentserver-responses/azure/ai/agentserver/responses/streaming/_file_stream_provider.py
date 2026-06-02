# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""File-based stream provider for durable event replay.

Stores SSE events as JSON-lines files on disk. Supports:
- Incremental append (one event at a time during streaming)
- Batch save (existing protocol — writes all events at once)
- Filtering by starting_after sequence number
- Configurable TTL after terminal state (default from options)
- Automatic cleanup after TTL expiry
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any


class FileStreamProvider:
    """File-backed stream event store using JSON lines format.

    Each response gets a file ``{response_id}.jsonl`` containing one JSON object
    per line. A separate ``{response_id}.terminal`` marker records when the
    stream reached terminal state, enabling TTL-based expiry.

    :param storage_dir: Directory to store event files.
    :param replay_event_ttl_seconds: Seconds to retain events after terminal.
        Defaults to 600 (10 minutes). Set to 0 to disable TTL.
    """

    def __init__(
        self,
        storage_dir: Path,
        *,
        replay_event_ttl_seconds: float = 600,
    ) -> None:
        self._storage_dir = storage_dir
        self._ttl = replay_event_ttl_seconds
        self._locks: dict[str, asyncio.Lock] = {}
        storage_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _to_serializable(event: Any) -> dict[str, Any]:
        """Convert event to a JSON-serializable dict."""
        if isinstance(event, dict):
            return event
        # Model objects have as_dict() which recursively converts nested models
        if hasattr(event, "as_dict"):
            return event.as_dict()
        # Fallback for MutableMapping subclasses
        return dict(event)

    def _get_lock(self, response_id: str) -> asyncio.Lock:
        if response_id not in self._locks:
            self._locks[response_id] = asyncio.Lock()
        return self._locks[response_id]

    def _events_path(self, response_id: str) -> Path:
        return self._storage_dir / f"{response_id}.jsonl"

    def _terminal_path(self, response_id: str) -> Path:
        return self._storage_dir / f"{response_id}.terminal"

    async def append_stream_event(
        self,
        response_id: str,
        event: dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Append a single event to the response's event file."""
        lock = self._get_lock(response_id)
        async with lock:
            path = self._events_path(response_id)
            serializable = self._to_serializable(event)
            line = json.dumps(serializable, separators=(",", ":"), default=str) + "\n"
            with open(path, "a", encoding="utf-8") as f:
                f.write(line)

    async def save_stream_events(
        self,
        response_id: str,
        events: list[dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """Batch-write all events (existing protocol compatibility)."""
        lock = self._get_lock(response_id)
        async with lock:
            path = self._events_path(response_id)
            with open(path, "w", encoding="utf-8") as f:
                for event in events:
                    serializable = self._to_serializable(event)
                    f.write(
                        json.dumps(serializable, separators=(",", ":"), default=str)
                        + "\n"
                    )

    async def get_stream_events(
        self,
        response_id: str,
        *,
        starting_after: int | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]] | None:
        """Read events from file, optionally filtering by sequence number.

        Returns None if file doesn't exist or TTL has expired.
        """
        path = self._events_path(response_id)
        if not path.exists():
            return None

        # Check TTL expiry
        terminal_path = self._terminal_path(response_id)
        if terminal_path.exists():
            terminal_time = float(terminal_path.read_text().strip())
            if self._ttl > 0 and (time.time() - terminal_time) > self._ttl:
                # Expired — clean up
                await self.delete_stream_events(response_id)
                return None

        lock = self._get_lock(response_id)
        async with lock:
            if not path.exists():
                return None
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        events: list[dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if line:
                events.append(json.loads(line))

        if starting_after is not None:
            events = [e for e in events if e.get("sequence_number", 0) > starting_after]

        return events

    async def mark_terminal(self, response_id: str, **kwargs: Any) -> None:
        """Record that the stream reached terminal state. Starts TTL countdown."""
        terminal_path = self._terminal_path(response_id)
        terminal_path.write_text(str(time.time()))

    async def delete_stream_events(self, response_id: str, **kwargs: Any) -> None:
        """Remove event file and terminal marker."""
        path = self._events_path(response_id)
        terminal_path = self._terminal_path(response_id)
        if path.exists():
            path.unlink()
        if terminal_path.exists():
            terminal_path.unlink()
        self._locks.pop(response_id, None)
