# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance tests for :class:`ReplayEventStream`.

Asserts  (multi-subscriber, in-memory buffer, optional cursor,
optional TTL) +  (per-event TTL semantics + registry-
delete immediate cutoff) +  (``last_cursor`` rule-25
exemption).

See ``streaming.md`` §5.2 + §13 rules 10-15, 22-25.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from azure.ai.agentserver.core.streaming import (
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.core.streaming._concrete import ReplayEventStream


pytestmark = pytest.mark.asyncio(loop_scope="function")


# ----------------------------------------------------------------
# Multi-subscriber + history+live (rules 10-12 /)
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
        """Rule 12 /  — subscribe(after=N) yields exactly cursor>N,
        no gap, no duplicate, in original order."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        for n in range(10):
            await s.emit({"n": n})
        await s.close()

        results = []
        async for ev in s.subscribe(after=4):
            results.append(ev["n"])
        assert results == [5, 6, 7, 8, 9], f"after=4 must yield cursor>4 only; got {results}"


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
        assert results == [0, 1, 2, 3, 4], "close MUST drain queued items before terminating per rule 13"


# ----------------------------------------------------------------
# Per-event TTL (rules 22-25 /)
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
        assert results == [2, 3], f"event 1 should have expired before subscribe; got {results}"

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
        with pytest.raises(EventStreamNotFoundError):
            s.subscribe()


# ----------------------------------------------------------------
# last_cursor rule-25 exemption (rule 8 +)
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
        assert (
            await s.last_cursor() == 10
        ), "last_cursor MUST survive CLOSED+TTL-eviction per rule 8 + rule 25 exemption"
        # NOW some other op fires GONE transition
        with pytest.raises(EventStreamNotFoundError):
            s.subscribe()
        # NOW last_cursor raises Gone
        with pytest.raises(EventStreamNotFoundError):
            await s.last_cursor()


# ----------------------------------------------------------------
# Registry-delete is immediate cutoff
# ----------------------------------------------------------------


class TestRegistryDeleteImmediateCutoff:
    async def test_registry_delete_immediate_cutoff_terminates_subscribers(
        self,
    ) -> None:
        """— registry-driven destruction is immediate cutoff;
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
        assert len(seen) < 5, f"registry-delete MUST cut off mid-drain; " f"consumer saw all {len(seen)} events"


# ----------------------------------------------------------------
#  — Close-clock TTL tombstone (/ SC-15..17, SC-20)
# ----------------------------------------------------------------


class TestTaskStreamsCloseClockTombstone:
    """/ SC-15..17, SC-20 — TTL-since-close is the deterministic
    tombstone trigger (not buffer-state-driven, not observer-driven).

    Reference: docs/task-and-streaming-spec.md §46, §59 C-STR-TTL-1..4.
    """

    async def test_closed_stream_tombstones_after_ttl_since_close(self) -> None:
        """SC-15 /  — emit + close + advance time past TTL →
        next ``streams.get(id)`` raises ``EventStreamNotFoundError``.
        """
        streams.use_in_memory_replay(ttl_seconds=0.1)
        stream = await streams.get_or_create("t--close-clock")
        await stream.emit({"n": 1})
        await stream.close()
        # Wait past the close-clock deadline.
        await asyncio.sleep(0.2)
        # Trigger any opportunistic tombstone check.
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("t--close-clock")

    async def test_active_stream_with_expired_buffer_stays_active(self) -> None:
        """SC-16 /  — an Active stream whose buffer has been
        fully evicted by per-event TTL MUST remain Active; new emits
        succeed and new subscribers see them.

        Strategy: emit n=1; wait TTL+epsilon so buffer is empty;
        subscribe (late subscriber — no history available); emit
        n=2 with close=True; consumer sees only n=2 — proving the
        stream stayed Active after buffer eviction.
        """
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"], ttl_seconds=0.1)
        stream = await streams.get_or_create("t--active-empty")
        await stream.emit({"n": 1})
        await asyncio.sleep(0.2)  # n=1 per-event TTL elapses
        # Buffer is now empty but stream is still Active (no close).
        # Late subscriber attaches; should see only future events.
        seen: list[int] = []

        async def consume():
            async for ev in stream.subscribe():
                seen.append(ev["n"])

        consumer_task = asyncio.create_task(consume())
        # Give the subscriber a tick to register.
        await asyncio.sleep(0.05)
        # Emit a new event after the subscriber attached, with close
        # so the iterator terminates cleanly.
        await stream.emit({"n": 2}, close=True)
        await asyncio.wait_for(consumer_task, timeout=1.0)
        # The new subscriber should have seen exactly n=2 — proving
        # the stream stayed Active after the per-event TTL eviction
        # of the pre-attach n=1 emit.
        assert seen == [2], (
            f" — Active stream w/ empty buffer should accept " f"new subscribers and deliver future events. seen={seen}"
        )

    async def test_no_ttl_means_no_auto_tombstone(self) -> None:
        """SC-17 /  — replay stream without TTL: emit + close
        → buffer retained indefinitely; stream stays Closed; only
        ``delete(id)`` tombstones.
        """
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"])
        stream = await streams.get_or_create("t--no-ttl")
        await stream.emit({"n": 1})
        await stream.close()
        # Even after sleeping, the registry must not tombstone.
        await asyncio.sleep(0.2)
        # get() still returns the same stream instance.
        same = await streams.get("t--no-ttl")
        assert same is stream, " — no-TTL replay stream MUST NOT auto-tombstone"
        # Late subscriber drains the buffered history.
        history: list[int] = []
        async for ev in stream.subscribe():
            history.append(ev["n"])
        assert history == [1]
        # delete() tombstones immediately.
        await streams.delete("t--no-ttl")
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("t--no-ttl")

    async def test_last_cursor_works_until_tombstone(self) -> None:
        """SC-20 /  — ``last_cursor`` works on:
        - Active stream with empty buffer (TTL-evicted) → highest cursor.
        - Closed-but-pre-tombstone stream → highest cursor.
        - After tombstone → raises ``EventStreamNotFoundError``.
        """
        streams.use_in_memory_replay(cursor_fn=lambda e: e["n"], ttl_seconds=0.1)
        stream = await streams.get_or_create("t--last-cursor")
        await stream.emit({"n": 5})
        await stream.emit({"n": 7})

        # Active state, before TTL evicts: last_cursor = 7.
        c = await stream.last_cursor()
        assert c == 7

        # Wait for per-event TTL to evict the buffer (stream still Active).
        await asyncio.sleep(0.2)
        # Active + empty buffer: last_cursor still returns the watermark.
        c = await stream.last_cursor()
        assert c == 7, f" / SC-20 — Active stream w/ empty buffer must " f"still return the high-water cursor. Got {c}."

        # Close the stream. Pre-tombstone (within close-clock window),
        # last_cursor still works.
        await stream.close()
        c = await stream.last_cursor()
        assert c == 7, (
            f" / SC-20 — Closed-but-pre-tombstone stream must " f"still return the high-water cursor. Got {c}."
        )

        # Wait past close + TTL deadline → tombstone fires.
        await asyncio.sleep(0.2)
        # Touch the registry once so opportunistic tombstone happens.
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("t--last-cursor")
        # And last_cursor on the now-tombstoned instance raises NotFound.
        with pytest.raises(EventStreamNotFoundError):
            await stream.last_cursor()
