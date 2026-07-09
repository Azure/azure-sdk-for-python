# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the transport-layer SSE keep-alive wrapper ``with_keep_alive``."""

from __future__ import annotations

import asyncio
import contextvars
from typing import AsyncIterator, List

import pytest

from azure.ai.agentserver.responses.streaming._sse import encode_keep_alive_comment, with_keep_alive

_KA = encode_keep_alive_comment()


async def _collect(agen: AsyncIterator[str]) -> List[str]:
    return [item async for item in agen]


async def test_passthrough_when_interval_disabled() -> None:
    """None / 0 interval => pure passthrough, no heartbeats, order preserved."""

    async def source() -> AsyncIterator[str]:
        yield "a"
        yield "b"

    assert await _collect(with_keep_alive(source(), None)) == ["a", "b"]
    assert await _collect(with_keep_alive(source(), 0)) == ["a", "b"]


async def test_emits_heartbeat_on_idle_gap() -> None:
    """A keep-alive frame is emitted when the source is idle longer than the interval."""

    async def source() -> AsyncIterator[str]:
        yield "a"
        await asyncio.sleep(0.25)  # idle gap >> interval
        yield "b"

    out = await _collect(with_keep_alive(source(), 0.05))
    assert _KA in out
    # Real items are preserved in order; heartbeats only appear between them.
    assert [item for item in out if item != _KA] == ["a", "b"]
    assert out.index("a") < out.index("b")


async def test_does_not_drop_or_reorder_items() -> None:
    """Items arriving across multiple idle gaps are never dropped or reordered."""

    async def source() -> AsyncIterator[str]:
        for i in range(5):
            await asyncio.sleep(0.03)
            yield f"item-{i}"

    out = await _collect(with_keep_alive(source(), 0.01))
    assert [item for item in out if item != _KA] == [f"item-{i}" for i in range(5)]


async def test_preserves_contextvars_across_yields() -> None:
    """The source is advanced by a single task, so a ContextVar it sets once persists
    across all its yields. (Regression guard: a new-task-per-anext design loses it after
    the first item and corrupts request context + SSE sequence numbers.)"""

    cvar: contextvars.ContextVar[str] = contextvars.ContextVar("cvar", default="UNSET")
    seen: List[str] = []

    async def source() -> AsyncIterator[str]:
        cvar.set("SET")
        seen.append(cvar.get())
        yield "a"
        seen.append(cvar.get())
        yield "b"
        seen.append(cvar.get())

    out = await _collect(with_keep_alive(source(), 5))  # fast drain, no heartbeats
    assert out == ["a", "b"]
    assert seen == ["SET", "SET", "SET"]


async def test_closes_source_deterministically_on_early_close() -> None:
    """Closing the wrapper after one item (client disconnect mid-run) runs the source's
    ``finally`` deterministically rather than deferring it to GC."""

    finalized = asyncio.Event()

    async def source() -> AsyncIterator[str]:
        try:
            yield "a"
            await asyncio.Event().wait()  # block forever after the first item
            yield "b"
        finally:
            finalized.set()

    agen = with_keep_alive(source(), 5)
    first = await agen.__anext__()
    assert first == "a"
    await agen.aclose()
    await asyncio.wait_for(finalized.wait(), timeout=1.0)


async def test_emits_heartbeat_while_source_idle_from_start() -> None:
    """A source idle from the very start still gets keep-alive frames — the reconnect /
    replay GET scenario, where the stream subscribes to an in-flight background run that
    has not emitted anything since the cursor."""

    async def idle_source() -> AsyncIterator[str]:
        await asyncio.Event().wait()  # never yields a real item
        yield "never"  # pragma: no cover

    agen = with_keep_alive(idle_source(), 0.05)
    first = await asyncio.wait_for(agen.__anext__(), timeout=1.0)
    assert first == _KA
    await agen.aclose()


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
