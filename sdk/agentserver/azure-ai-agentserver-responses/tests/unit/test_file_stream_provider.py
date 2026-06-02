# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for file-based stream provider (Phase 3).

Tests:
- Append multiple events → read back in order
- Filter by starting_after → only later events returned
- Delete → file removed → subsequent reads return None
- TTL enforcement: mark terminal time → after TTL → returns None
- Concurrent appends (asyncio) → no corruption (JSON lines integrity)
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.responses.streaming._file_stream_provider import (
    FileStreamProvider,
)


def _make_event(
    seq: int, event_type: str = "response.output_text.delta"
) -> dict[str, Any]:
    return {
        "type": event_type,
        "sequence_number": seq,
        "item_id": f"item_{seq}",
    }


class TestFileStreamProviderAppendRead:
    """Append and read events."""

    @pytest.mark.asyncio
    async def test_append_single_event(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        event = _make_event(0)
        await provider.append_stream_event("resp_1", event)

        events = await provider.get_stream_events("resp_1")
        assert events is not None
        assert len(events) == 1
        assert events[0]["sequence_number"] == 0

    @pytest.mark.asyncio
    async def test_append_multiple_events_in_order(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        for i in range(5):
            await provider.append_stream_event("resp_2", _make_event(i))

        events = await provider.get_stream_events("resp_2")
        assert events is not None
        assert len(events) == 5
        assert [e["sequence_number"] for e in events] == [0, 1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_read_nonexistent_returns_none(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        events = await provider.get_stream_events("resp_missing")
        assert events is None


class TestFileStreamProviderFiltering:
    """Filter events by starting_after."""

    @pytest.mark.asyncio
    async def test_get_events_with_starting_after(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        for i in range(10):
            await provider.append_stream_event("resp_filter", _make_event(i))

        events = await provider.get_stream_events("resp_filter", starting_after=5)
        assert events is not None
        assert len(events) == 4  # seq 6, 7, 8, 9
        assert all(e["sequence_number"] > 5 for e in events)

    @pytest.mark.asyncio
    async def test_get_events_starting_after_exceeds_max(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        for i in range(5):
            await provider.append_stream_event("resp_exceed", _make_event(i))

        events = await provider.get_stream_events("resp_exceed", starting_after=100)
        assert events is not None
        assert len(events) == 0


class TestFileStreamProviderDelete:
    """Delete removes file."""

    @pytest.mark.asyncio
    async def test_delete_removes_events(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        await provider.append_stream_event("resp_del", _make_event(0))

        # Verify exists
        events = await provider.get_stream_events("resp_del")
        assert events is not None

        # Delete
        await provider.delete_stream_events("resp_del")

        # Verify gone
        events = await provider.get_stream_events("resp_del")
        assert events is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_is_noop(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)
        # Should not raise
        await provider.delete_stream_events("resp_nope")


class TestFileStreamProviderTTL:
    """TTL enforcement after marking terminal."""

    @pytest.mark.asyncio
    async def test_events_available_within_ttl(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(
            storage_dir=tmp_path, replay_event_ttl_seconds=600
        )
        await provider.append_stream_event("resp_ttl", _make_event(0))
        await provider.mark_terminal("resp_ttl")

        # Immediately after terminal — within TTL
        events = await provider.get_stream_events("resp_ttl")
        assert events is not None
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_events_expired_after_ttl(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path, replay_event_ttl_seconds=1)
        await provider.append_stream_event("resp_expired", _make_event(0))
        await provider.mark_terminal("resp_expired")

        # Simulate time passing by backdating the terminal marker
        marker_file = tmp_path / "resp_expired.terminal"
        # Write a timestamp from 2 seconds ago
        marker_file.write_text(str(time.time() - 2))

        events = await provider.get_stream_events("resp_expired")
        assert events is None  # Expired


class TestFileStreamProviderConcurrency:
    """Concurrent appends don't corrupt data."""

    @pytest.mark.asyncio
    async def test_concurrent_appends_no_corruption(self, tmp_path: Path) -> None:
        provider = FileStreamProvider(storage_dir=tmp_path)

        async def append_batch(start: int, count: int) -> None:
            for i in range(start, start + count):
                await provider.append_stream_event("resp_concurrent", _make_event(i))

        # Run 5 concurrent batches of 10 events each
        await asyncio.gather(
            append_batch(0, 10),
            append_batch(10, 10),
            append_batch(20, 10),
            append_batch(30, 10),
            append_batch(40, 10),
        )

        events = await provider.get_stream_events("resp_concurrent")
        assert events is not None
        assert len(events) == 50

        # Verify all events are valid JSON (no corruption)
        seq_numbers = sorted(e["sequence_number"] for e in events)
        assert seq_numbers == list(range(50))


class TestFileStreamProviderBatchCompat:
    """Batch save (existing protocol) compatibility."""

    @pytest.mark.asyncio
    async def test_save_stream_events_batch(self, tmp_path: Path) -> None:
        """save_stream_events (batch) writes all events at once."""
        provider = FileStreamProvider(storage_dir=tmp_path)
        events = [_make_event(i) for i in range(5)]
        await provider.save_stream_events("resp_batch", events)

        read_back = await provider.get_stream_events("resp_batch")
        assert read_back is not None
        assert len(read_back) == 5
