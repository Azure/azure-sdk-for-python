# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``EventStream`` Protocol-level conformance tests.

Asserts contract that applies to ALL bundled impls — Protocol
shape, state-model rules, atomic emit+close, subscribe-not-a-
coroutine,  exception hierarchy.

See ``streaming.md`` §13 rules 1-21 + spec.md  through.
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import AsyncIterator
from typing import Optional, get_type_hints

import pytest

# Internal imports — concrete classes live in _concrete per SC-006b
from azure.ai.agentserver.core.streaming import (
    EventStream,
    EventStreamClosedError,
    EventStreamNotFoundError,
    streams,
)
from azure.ai.agentserver.core.streaming._concrete import (
    BroadcastEventStream,
    FileBackedReplayEventStream,
    ReplayEventStream,
)


pytestmark = pytest.mark.asyncio(loop_scope="function")


# ----------------------------------------------------------------
# Protocol shape (/ streaming.md §4.3 + rule 16)
# ----------------------------------------------------------------


class TestProtocolShape:
    def test_has_exactly_four_data_flow_methods(self) -> None:
        """— Protocol has exactly emit/close/subscribe/last_cursor.
        No `delete` method (registry-owned destruction)."""
        # Protocol attributes accessible via __annotations__ or members
        members = {name for name in dir(EventStream) if not name.startswith("_")}
        assert "emit" in members
        assert "close" in members
        assert "subscribe" in members
        assert "last_cursor" in members
        # Most importantly: no destructive method on the Protocol
        assert "delete" not in members, (
            "Protocol MUST NOT have delete() — destruction is registry-owned " "/ streaming.md §4.3"
        )
        assert "release" not in members, "Protocol MUST NOT have release() — destruction is registry-owned"

    def test_subscribe_is_not_a_coroutine(self) -> None:
        """Rule 16 — `subscribe()` returns AsyncIterator directly,
        not a coroutine. Callable without await."""
        # Check the protocol declares subscribe as a regular def
        # (returning AsyncIterator), not async def
        subscribe = EventStream.subscribe
        assert not inspect.iscoroutinefunction(subscribe), "subscribe MUST NOT be `async def` per rule 16 / "
        # Check on a concrete impl too
        s = BroadcastEventStream()
        it = s.subscribe()
        assert not asyncio.iscoroutine(it), (
            "subscribe() return value must NOT be a coroutine — " "must be an AsyncIterator directly per rule 16"
        )
        assert hasattr(it, "__aiter__"), "return must implement async iteration"

    @pytest.mark.parametrize(
        "factory",
        [
            lambda: BroadcastEventStream(),
            lambda: ReplayEventStream(),
            lambda: ReplayEventStream(cursor_fn=lambda e: e["n"]),
        ],
        ids=["broadcast", "replay-no-cursor", "replay-with-cursor"],
    )
    def test_concrete_classes_satisfy_protocol(self, factory) -> None:
        """All three bundled concrete classes satisfy the runtime-checkable
        Protocol."""
        instance = factory()
        # runtime_checkable Protocol — isinstance works
        assert isinstance(instance, EventStream)


# ----------------------------------------------------------------
# State model (rules 1-9)
# ----------------------------------------------------------------


class TestStateModel:
    async def test_emit_on_closed_raises_closed_error(self) -> None:
        """Rule 4: emit on CLOSED → EventStreamClosedError (NOT bare RuntimeError)."""
        s = BroadcastEventStream()
        await s.close()
        with pytest.raises(EventStreamClosedError):
            await s.emit({"x": 1})

    async def test_emit_on_gone_raises_gone_error(self) -> None:
        """Rule 5: emit on GONE → EventStreamNotFoundError."""
        s = BroadcastEventStream()
        await s._on_delete()  # registry would normally call this
        with pytest.raises(EventStreamNotFoundError):
            await s.emit({"x": 1})

    async def test_subscribe_on_gone_raises_gone_error_at_call_site(self) -> None:
        """Rule 6: subscribe on GONE raises GoneError synchronously at the
        subscribe() call site, NOT inside the iterator."""
        s = BroadcastEventStream()
        await s._on_delete()
        with pytest.raises(EventStreamNotFoundError):
            # Must raise synchronously — before iterator returned
            s.subscribe()

    async def test_last_cursor_on_gone_raises_gone_error(self) -> None:
        """Rule 7: last_cursor on GONE → EventStreamNotFoundError."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        await s._on_delete()
        with pytest.raises(EventStreamNotFoundError):
            await s.last_cursor()

    async def test_close_is_idempotent(self) -> None:
        """Rule 9: close() on CLOSED or GONE → no-op (never raises)."""
        s = BroadcastEventStream()
        await s.close()
        # CLOSED → close again → no-op
        await s.close()
        await s._on_delete()
        # GONE → close → no-op
        await s.close()


# ----------------------------------------------------------------
# Atomic emit+close (rule 14 /)
# ----------------------------------------------------------------


class TestAtomicEmitClose:
    async def test_subscriber_attached_before_emit_sees_both(self) -> None:
        """Rule 14 — subscriber attached before emit(close=True) sees BOTH
        the payload AND end-of-stream."""
        s = BroadcastEventStream()
        results = []

        async def consume():
            async for ev in s.subscribe():
                results.append(ev)

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)  # ensure subscriber attached
        await s.emit({"final": True}, close=True)
        await task
        assert results == [{"final": True}], (
            "subscriber attached before emit(close=True) MUST see the payload " "+ then terminate (rule 14)"
        )

    async def test_subscriber_attached_after_emit_sees_neither(self) -> None:
        """Subscriber attached AFTER emit(close=True) on BroadcastEventStream
        sees neither (no buffer)."""
        s = BroadcastEventStream()
        await s.emit({"final": True}, close=True)
        # Now subscribe — should get nothing
        results = []
        async for ev in s.subscribe():
            results.append(ev)
        assert results == [], "subscriber attached after emit(close=True) on Broadcast MUST see " "nothing"


# ----------------------------------------------------------------
# Exception hierarchy + subscriber cleanup
# ----------------------------------------------------------------


class TestExceptionHierarchyAndCleanup:
    async def test_subscriber_cleanup_within_one_event_loop_tick(self) -> None:
        """Rule 15 — disconnected subscriber is removed from impl's
        internal subscriber list within one event-loop tick."""
        s = BroadcastEventStream()

        async def attach_then_break():
            async for ev in s.subscribe():
                break  # disconnect after first iteration

        # Attach + emit + let subscriber break
        task = asyncio.create_task(attach_then_break())
        await asyncio.sleep(0.01)  # attach
        # Before emit: there should be 1 subscriber registered
        await s.emit({"first": True})
        await task  # subscriber broke out
        await asyncio.sleep(0)  # one event-loop tick
        # The subscriber should have been removed
        # We assert by checking the internal subscriber list (test-only
        # white-box assertion)
        assert len(s._subscriber_queues) == 0, (
            "Disconnected subscriber MUST be removed within one event-loop " "tick per rule 15"
        )


# ----------------------------------------------------------------
# cursor_fn semantics (rules 17-19 / *)
# ----------------------------------------------------------------


class TestCursorFnSemantics:
    async def test_after_silently_ignored_without_cursor_fn_on_replay(
        self,
    ) -> None:
        """Rule 17 — impl without cursor_fn silently ignores non-None
        `after` (no TypeError)."""
        s = ReplayEventStream()  # NO cursor_fn
        # Should NOT raise
        it = s.subscribe(after=42)
        assert hasattr(it, "__aiter__"), "iterator should be returned, not raised"

    async def test_after_silently_ignored_on_broadcast_always(self) -> None:
        """BroadcastEventStream NEVER honours `after` /."""
        s = BroadcastEventStream()
        it = s.subscribe(after=99)
        assert hasattr(it, "__aiter__")

    async def test_after_past_latest_on_active_replay_waits_for_next(
        self,
    ) -> None:
        """Rule 19 (a) — after N past latest buffered on ACTIVE stream:
        subscriber waits for the next live event satisfying cursor_fn > N."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})  # buffered cursor: 1

        results = []

        async def consume():
            async for ev in s.subscribe(after=100):  # past latest
                results.append(ev)

        task = asyncio.create_task(consume())
        await asyncio.sleep(0.01)
        await s.emit({"n": 101})  # > 100
        await s.emit({"n": 200}, close=True)
        await task
        assert results == [{"n": 101}, {"n": 200}], (
            f"after=100 past latest (buffered=1) MUST wait for live events > 100; " f"got {results}"
        )

    async def test_after_past_latest_on_closed_replay_returns_empty(self) -> None:
        """Rule 19 (b) — after N past latest on CLOSED stream → immediately-
        exhausted iterator."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"])
        await s.emit({"n": 1})
        await s.close()

        results = []
        async for ev in s.subscribe(after=100):
            results.append(ev)
        assert results == [], "after=100 past latest on CLOSED MUST return empty iterator"


# ----------------------------------------------------------------
# Concurrent task safety
# ----------------------------------------------------------------


class TestConcurrentSafety:
    async def test_concurrent_emit_subscribe_on_replay(self) -> None:
        """— N concurrent tasks interleaving emit/subscribe/close
        against the same instance must not race or lose events."""
        s = ReplayEventStream(cursor_fn=lambda e: e["n"], ttl_seconds=10)

        # Spawn 5 subscribers + 1 producer concurrently
        all_results = []

        async def subscriber(idx: int):
            seen = []
            async for ev in s.subscribe():
                seen.append(ev["n"])
            all_results.append((idx, seen))

        async def producer():
            for n in range(20):
                await s.emit({"n": n})
                await asyncio.sleep(0)  # yield
            await s.close()

        subs = [asyncio.create_task(subscriber(i)) for i in range(5)]
        await asyncio.sleep(0.01)  # let them attach
        await producer()
        await asyncio.gather(*subs)

        # All 5 subscribers should have seen the same set of events
        for idx, seen in all_results:
            # Order preserved, all values present
            assert seen == list(range(20)), f"subscriber {idx} saw {seen}; expected 0..19 in order"
