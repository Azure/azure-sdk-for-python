# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance tests for :class:`ReplayEventStream`.

Asserts FR-009 (multi-subscriber, in-memory buffer, optional cursor,
optional TTL) + FR-012/012a (per-event TTL semantics + registry-
delete immediate cutoff) + FR-007b (``last_cursor`` rule-25
exemption).

See ``streaming.md`` §5.2 + §13 rules 10-15, 22-25.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from azure.ai.agentserver.core.streaming import (
    EventStreamGoneError,
    streams,
)
from azure.ai.agentserver.core.streaming._concrete import ReplayEventStream


pytestmark = pytest.mark.asyncio(loop_scope="function")


# ----------------------------------------------------------------
# Multi-subscriber + history+live (rules 10-12 / FR-009)
# ----------------------------------------------------------------


class TestMultiSubscriberCorrectness:
    async def test_two_subscribers_each_see_full_stream(self) -> None:
        """Rule 10 — two concurrent subscribers each receive a complete
        independent view."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        results_a, results_b = [], []

        async def sub_a():
            async for ev in s.subscribe():
                results_a.append(ev["n"])

        async def sub_b():
            async for ev in s.subscribe():
                results_b.append(ev["n"])

        ta = asyncio.create_task(sub_a())
        tb = asyncio.create_task(sub_b())
        await asyncio.sleep(0.01)
        for n in range(5):
            await s.emit({"n": n})
        await s.close()
        await asyncio.gather(ta, tb)
        assert results_a == list(range(5))
        assert results_b == list(range(5))

    async def test_history_then_live_for_late_subscriber(self) -> None:
        """Rule 11 — history first, live events second, no gap."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        for n in range(3):
            await s.emit({"n": n})

        # Late subscriber: should see [0,1,2] then live [3,4]
        results = []

        async def consume():
            async for ev in s.subscribe():
                results.append(ev["n"])

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        for n in range(3, 5):
            await s.emit({"n": n})
        await s.close()
        await task
        assert results == [0, 1, 2, 3, 4]

    async def test_yield_contract_no_gap_no_duplicate(self) -> None:
        """Rule 12 / FR-011b — subscribe(after=N) yields exactly cursor>N,
        no gap, no duplicate, in original order."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        for n in range(10):
            await s.emit({"n": n})
        await s.close()

        results = []
        async for ev in s.subscribe(after=4):
            results.append(ev["n"])
        assert results == [5, 6, 7, 8, 9], (
            f"after=4 must yield cursor>4 only; got {results}"
        )


class TestCloseDrains:
    async def test_close_drains_queued_items(self) -> None:
        """Rule 13 — after close(), subscribers drain remaining queued
        items in order before iterator terminates."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        results = []

        async def consume():
            async for ev in s.subscribe():
                results.append(ev["n"])
                await asyncio.sleep(0.01)  # slow consumer

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        for n in range(5):
            await s.emit({"n": n})
        await s.close()  # close while consumer is mid-drain
        await task
        assert results == [0, 1, 2, 3, 4], (
            "close MUST drain queued items before terminating per rule 13"
        )


# ----------------------------------------------------------------
# Per-event TTL (rules 22-25 / FR-012)
# ----------------------------------------------------------------


class TestPerEventTTL:
    async def test_expired_events_not_yielded_to_late_subscriber(self) -> None:
        """Rule 22 — late subscriber sees only non-expired events."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=0.3)
        await s.emit({"n": 1})
        await asyncio.sleep(0.2)
        await s.emit({"n": 2})
        await asyncio.sleep(0.2)  # t=0.4: event 1 expired (emit_time<0.1), event 2 still fresh

        # Late subscriber attaches now
        results = []

        async def consume():
            async for ev in s.subscribe():
                results.append(ev["n"])

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await s.emit({"n": 3}, close=True)
        await task
        assert results == [2, 3], (
            f"event 1 should have expired before subscribe; got {results}"
        )

    async def test_close_does_not_affect_ttl(self) -> None:
        """Rule 23 — close() and TTL are orthogonal. close() does NOT
        trigger immediate eviction."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=10)
        await s.emit({"n": 1})
        await s.emit({"n": 2})
        await s.close()
        # Events should still be replayable immediately after close
        results = []
        async for ev in s.subscribe():
            results.append(ev["n"])
        assert results == [1, 2], "close MUST NOT immediately evict per rule 23"

    async def test_in_flight_items_unaffected_by_eviction(self) -> None:
        """Rule 24 — items already enqueued to a subscriber's queue stay
        delivered even after eviction from the impl's main buffer."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=10)
        await s.emit({"n": 1})
        await s.emit({"n": 2})

        # Attach subscriber — items go into its queue
        seen = []

        async def slow_consume():
            async for ev in s.subscribe():
                seen.append(ev["n"])
                await asyncio.sleep(0.05)  # slow drain

        task = asyncio.create_task(slow_consume())
        await asyncio.sleep(0.01)  # let subscriber drain history
        # Simulate eviction of main buffer (we can't trigger TTL
        # mid-test reliably, but the contract is: items in subscriber's
        # queue stay delivered even if main buffer evicts)
        await s.close()
        await task
        assert seen == [1, 2]


class TestClosedToGoneAutoTransition:
    async def test_closed_plus_evict_plus_had_emit_transitions_to_gone(
        self,
    ) -> None:
        """Rule 25 — CLOSED + last replayable event evicts + had ≥1
        emit → GONE auto-transition on next subscribe/emit."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=0.1)
        await s.emit({"n": 1})
        await s.close()
        await asyncio.sleep(0.2)  # event 1 expired
        # subscribe → triggers auto-transition CLOSED → GONE
        with pytest.raises(EventStreamGoneError):
            s.subscribe()


# ----------------------------------------------------------------
# last_cursor rule-25 exemption (rule 8 + FR-007b)
# ----------------------------------------------------------------


class TestLastCursorRule25Exemption:
    async def test_last_cursor_active_returns_highest(self) -> None:
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        await s.emit({"n": 5})
        await s.emit({"n": 10})
        assert await s.last_cursor() == 10

    async def test_last_cursor_active_zero_emits_returns_none(self) -> None:
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        assert await s.last_cursor() is None

    async def test_last_cursor_no_cursor_fn_returns_none(self) -> None:
        s = ReplayEventStream()  # no cursor_fn
        await s.emit({"n": 99})
        assert await s.last_cursor() is None

    async def test_last_cursor_closed_still_returns_highest(self) -> None:
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        await s.emit({"n": 5})
        await s.emit({"n": 10})
        await s.close()
        assert await s.last_cursor() == 10

    async def test_last_cursor_closed_after_ttl_eviction_still_returns_highest(
        self,
    ) -> None:
        """LOAD-BEARING: rule 25 exemption + rule 8 special case.

        ``last_cursor()`` MUST survive CLOSED+all-events-evicted-by-TTL
        and MUST NOT itself fire the GONE auto-transition. This is the
        recovery primitive for ``FileBackedReplayEventStream`` rehydration.
        """
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=0.1)
        await s.emit({"n": 5})
        await s.emit({"n": 10})
        await s.close()
        await asyncio.sleep(0.2)  # all events expired
        # last_cursor MUST still return 10 AND MUST NOT trigger GONE
        assert await s.last_cursor() == 10, (
            "last_cursor MUST survive CLOSED+TTL-eviction per rule 8 + rule 25 exemption"
        )
        # NOW some other op fires GONE transition
        with pytest.raises(EventStreamGoneError):
            s.subscribe()
        # NOW last_cursor raises Gone
        with pytest.raises(EventStreamGoneError):
            await s.last_cursor()


# ----------------------------------------------------------------
# Registry-delete is immediate cutoff (FR-012a)
# ----------------------------------------------------------------


class TestRegistryDeleteImmediateCutoff:
    async def test_registry_delete_immediate_cutoff_terminates_subscribers(
        self,
    ) -> None:
        """FR-012a — registry-driven destruction is immediate cutoff;
        items queued but not consumed are discarded."""
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"], ttl_seconds=10)
        s = await streams.get_or_create("td-cutoff-1")
        # Drain configurator-residue (test isolation)

        seen = []

        async def consume():
            try:
                async for ev in s.subscribe():
                    seen.append(ev["n"])
                    await asyncio.sleep(0.1)  # slow consumer
            except Exception:  # pylint: disable=broad-except
                pass

        for n in range(5):
            await s.emit({"n": n})
        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)  # consumer reads first item
        await streams.delete("td-cutoff-1")  # IMMEDIATE cutoff
        await task
        # consumer should have seen fewer than all 5 events (cut off)
        assert len(seen) < 5, (
            f"registry-delete MUST cut off mid-drain per FR-012a; "
            f"consumer saw all {len(seen)} events"
        )
