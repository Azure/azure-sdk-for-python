# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conformance tests for :class:`BroadcastEventStream`.

Asserts  — multicast + no buffer + live-only. No cursor_fn,
no ttl_seconds, no subscribe(after=...), no CLOSED→GONE auto-
transition. See ``streaming.md`` §5.1.
"""

from __future__ import annotations

import asyncio
import inspect

import pytest

from azure.ai.agentserver.core.streaming import EventStreamNotFoundError, streams
from azure.ai.agentserver.core.streaming._concrete import BroadcastEventStream


pytestmark = pytest.mark.asyncio(loop_scope="function")


class TestConstructorShape:
    def test_no_constructor_args(self) -> None:
        """— no cursor_fn, no ttl_seconds, no serializer."""
        sig = inspect.signature(BroadcastEventStream)
        # Only self, no other parameters
        params = list(sig.parameters.values())
        assert all(
            p.name in ("self", "args", "kwargs") for p in params
        ), f"BroadcastEventStream takes NO args; got {params}"

    def test_construct_with_no_args(self) -> None:
        s = BroadcastEventStream()
        # No buffer-related state
        assert not hasattr(s, "_cursor_fn") or s._cursor_fn is None  # type: ignore[attr-defined]
        assert not hasattr(s, "_ttl_seconds") or s._ttl_seconds is None  # type: ignore[attr-defined]


class TestNoBufferLiveOnly:
    async def test_subscriber_attached_after_emit_sees_nothing(self) -> None:
        """— subscribers see ONLY events emitted after they attach.
        No buffer means late attachers miss everything."""
        s = BroadcastEventStream()
        await s.emit({"n": 1})  # before any subscriber
        await s.emit({"n": 2})

        # Late subscriber attaches
        results = []

        async def consume():
            async for ev in s.subscribe():
                results.append(ev["n"])

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await s.emit({"n": 3}, close=True)
        await task
        assert results == [3], f"Broadcast subscriber MUST see only post-attach events; got {results}"

    async def test_multiple_concurrent_subscribers(self) -> None:
        """Multicast — multiple concurrent subscribers each see same
        post-attach stream."""
        s = BroadcastEventStream()
        results_a, results_b, results_c = [], [], []

        async def sub(results):
            async for ev in s.subscribe():
                results.append(ev["n"])

        ta = asyncio.create_task(sub(results_a))
        tb = asyncio.create_task(sub(results_b))
        tc = asyncio.create_task(sub(results_c))
        await asyncio.sleep(0.01)
        for n in range(3):
            await s.emit({"n": n})
        await s.close()
        await asyncio.gather(ta, tb, tc)
        assert results_a == [0, 1, 2]
        assert results_b == [0, 1, 2]
        assert results_c == [0, 1, 2]


class TestNoCursorNoTTL:
    async def test_subscribe_after_silently_ignored(self) -> None:
        """— Broadcast NEVER honours `after`; silently ignored."""
        s = BroadcastEventStream()
        # Must not raise
        it = s.subscribe(after=99)
        assert hasattr(it, "__aiter__")

    async def test_last_cursor_returns_none_on_active(self) -> None:
        """— Broadcast.last_cursor returns None on ACTIVE."""
        s = BroadcastEventStream()
        assert await s.last_cursor() is None
        await s.emit({"x": 1})
        assert await s.last_cursor() is None  # still None — no cursor tracking
        await s.emit({"x": 2})
        assert await s.last_cursor() is None

    async def test_last_cursor_raises_on_gone(self) -> None:
        """— Broadcast.last_cursor on GONE raises."""
        s = BroadcastEventStream()
        await s._on_delete()
        with pytest.raises(EventStreamNotFoundError):
            await s.last_cursor()


class TestNoAutoTransition:
    async def test_closed_broadcast_stays_closed_does_not_become_gone(
        self,
    ) -> None:
        """— Broadcast has NO CLOSED→GONE auto-transition
        (nothing evicts because there's no buffer)."""
        s = BroadcastEventStream()
        await s.emit({"x": 1})
        await s.close()
        # No way for it to spontaneously become GONE
        # Subscribe should give an immediately-empty iterator
        results = []
        async for ev in s.subscribe():
            results.append(ev)
        assert results == []
        # last_cursor should still return None, not raise Gone
        assert await s.last_cursor() is None


class TestAtomicEmitClose:
    async def test_emit_close_true_atomic(self) -> None:
        """Rule 14 — emit(close=True) is observably atomic: attached
        subscriber sees payload AND end-of-stream."""
        s = BroadcastEventStream()
        seen = []

        async def consume():
            async for ev in s.subscribe():
                seen.append(ev)

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await s.emit({"final": True}, close=True)
        await task
        assert seen == [{"final": True}]


class TestSubscriberCleanup:
    async def test_disconnected_subscriber_removed(self) -> None:
        """Rule 15 — disconnected subscriber's queue is removed from
        impl's internal list within one event-loop tick."""
        s = BroadcastEventStream()

        async def attach_then_break():
            async for ev in s.subscribe():
                _ = ev
                break

        task = asyncio.create_task(attach_then_break())
        await asyncio.sleep(0.01)
        await s.emit({"x": 1})
        await task
        await asyncio.sleep(0)
        assert len(s._subscriber_queues) == 0


# ----------------------------------------------------------------
#  — Broadcast NEVER auto-tombstones (/ SC-18)
# ----------------------------------------------------------------


class TestTaskStreamsBroadcastNoAutoTombstone:
    """/ SC-18 — Broadcast streams have no TTL machinery; only
    explicit ``delete(id)`` tombstones. Closed broadcast: ``subscribe()``
    yields an empty iterator that terminates immediately.

    Reference: docs/task-and-streaming-spec.md §43, §44, §59
    C-STR-TTL-3.
    """

    async def test_closed_broadcast_does_not_auto_tombstone(self) -> None:
        """SC-18 — emit + close on a broadcast stream → no auto-tombstone.
        ``subscribe(id)`` returns an empty iterator (no error); only
        explicit ``delete(id)`` tombstones.
        """
        streams.use_in_memory_live()
        stream = await streams.get_or_create("t--broadcast-no-auto")
        await stream.emit({"n": 1})
        await stream.close()
        # Sleep — broadcast must NOT auto-tombstone.
        await asyncio.sleep(0.2)
        # Still resolvable from the registry.
        same = await streams.get("t--broadcast-no-auto")
        assert same is stream

        # subscribe() on closed broadcast yields an empty iterator that
        # terminates immediately.
        items: list = []
        async for ev in stream.subscribe():
            items.append(ev)
        assert items == [], f"closed broadcast subscribe must yield empty iterator; " f"got {items}"

        # Explicit delete tombstones.
        await streams.delete("t--broadcast-no-auto")
        with pytest.raises(EventStreamNotFoundError):
            await streams.get("t--broadcast-no-auto")
