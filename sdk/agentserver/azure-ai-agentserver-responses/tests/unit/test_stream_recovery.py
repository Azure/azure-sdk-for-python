# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for stream recovery logic (Phase 3).

Tests:
- append_stream_event appends one event
- get_stream_events reads and filters by sequence number
- Consistency check: max file sequence ≥ metadata last_sequence_number → consistent
- Consistency check: file missing or max < stored → inconsistent
- Configurable TTL: events expired after replay_event_ttl_seconds → returns None
- Hydration: persisted events loaded into fresh subject with correct cursors
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses.hosting._durable_orchestrator import _FW_LAST_SEQ


class TestStreamConsistencyCheck:
    """Verify consistency check logic between metadata and persisted events."""

    @pytest.mark.asyncio
    async def test_consistent_when_file_seq_gte_metadata(self) -> None:
        """Stream is consistent when persisted max seq >= metadata last_seq."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_stream_consistency,
        )

        # File has events up to seq 5, metadata says last_seq=5 → consistent
        events = [_make_event(seq=i) for i in range(6)]
        result = await check_stream_consistency(
            events=events,
            last_sequence_number=5,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_consistent_when_file_seq_gt_metadata(self) -> None:
        """Stream is consistent when file has more events than metadata tracks."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_stream_consistency,
        )

        events = [_make_event(seq=i) for i in range(10)]
        result = await check_stream_consistency(
            events=events,
            last_sequence_number=5,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_inconsistent_when_file_seq_lt_metadata(self) -> None:
        """Stream is inconsistent when file max seq < metadata last_seq."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_stream_consistency,
        )

        events = [_make_event(seq=i) for i in range(3)]
        result = await check_stream_consistency(
            events=events,
            last_sequence_number=5,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_inconsistent_when_no_events(self) -> None:
        """Stream is inconsistent when file has no events but metadata says seq > 0."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_stream_consistency,
        )

        result = await check_stream_consistency(
            events=None,
            last_sequence_number=5,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_consistent_when_both_zero(self) -> None:
        """Stream is consistent when both file and metadata are empty/zero."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_stream_consistency,
        )

        result = await check_stream_consistency(
            events=[],
            last_sequence_number=0,
        )
        assert result is True


class TestStreamEventFiltering:
    """Tests for filtering events by starting_after sequence."""

    @pytest.mark.asyncio
    async def test_filter_events_by_starting_after(self) -> None:
        """Only events with seq > starting_after are returned."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            filter_events_by_sequence,
        )

        events = [_make_event(seq=i) for i in range(10)]
        filtered = filter_events_by_sequence(events, starting_after=5)
        assert len(filtered) == 4  # seq 6, 7, 8, 9
        assert all(e.get("sequence_number", 0) > 5 for e in filtered)

    @pytest.mark.asyncio
    async def test_filter_events_starting_after_zero(self) -> None:
        """starting_after=0 returns all events with seq > 0."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            filter_events_by_sequence,
        )

        events = [_make_event(seq=i) for i in range(5)]  # seq 0,1,2,3,4
        filtered = filter_events_by_sequence(events, starting_after=0)
        # seq > 0 → 1,2,3,4
        assert len(filtered) == 4

    @pytest.mark.asyncio
    async def test_filter_events_starting_after_exceeds_max(self) -> None:
        """starting_after >= max seq returns empty list."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            filter_events_by_sequence,
        )

        events = [_make_event(seq=i) for i in range(5)]
        filtered = filter_events_by_sequence(events, starting_after=10)
        assert len(filtered) == 0


class TestTTLExpiry:
    """Tests for TTL-based event expiry."""

    @pytest.mark.asyncio
    async def test_events_within_ttl_returned(self) -> None:
        """Events within TTL window are returned normally."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_ttl_expired,
        )

        # Terminal time is 5 seconds ago, TTL is 600s → not expired
        terminal_time = time.time() - 5
        assert check_ttl_expired(terminal_time, ttl_seconds=600) is False

    @pytest.mark.asyncio
    async def test_events_beyond_ttl_expired(self) -> None:
        """Events beyond TTL window are considered expired."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_ttl_expired,
        )

        # Terminal time is 700 seconds ago, TTL is 600s → expired
        terminal_time = time.time() - 700
        assert check_ttl_expired(terminal_time, ttl_seconds=600) is True

    @pytest.mark.asyncio
    async def test_no_terminal_time_not_expired(self) -> None:
        """If no terminal time set (still in progress), not expired."""
        from azure.ai.agentserver.responses.streaming._recovery import (
            check_ttl_expired,
        )

        assert check_ttl_expired(None, ttl_seconds=600) is False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_event(
    *, seq: int, event_type: str = "response.output_text.delta"
) -> dict[str, Any]:
    """Create a minimal stream event dict with a sequence number."""
    return {
        "type": event_type,
        "sequence_number": seq,
        "data": {"delta": f"chunk-{seq}"},
    }
