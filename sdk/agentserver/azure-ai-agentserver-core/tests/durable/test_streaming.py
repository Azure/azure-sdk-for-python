"""Tests for streaming support (ctx.stream + async-for on TaskRun)."""

from __future__ import annotations

import asyncio

import pytest

from azure.ai.agentserver.core.durable._context import TaskContext
from azure.ai.agentserver.core.durable._metadata import TaskMetadata
from azure.ai.agentserver.core.durable._run import TaskRun, _STREAM_SENTINEL


def _make_ctx(stream_queue=None, **overrides):
    defaults = dict(
        task_id="t1",
        title="test",
        session_id="s1",
        agent_name="a1",
        tags={},
        input=None,
        metadata=TaskMetadata(),
        stream_queue=stream_queue,
    )
    defaults.update(overrides)
    return TaskContext(**defaults)


def _make_run(stream_queue=None, result_future=None, **overrides):
    loop = asyncio.get_event_loop()
    if result_future is None:
        result_future = loop.create_future()
    defaults = dict(
        task_id="t1",
        provider=None,
        result_future=result_future,
        metadata=TaskMetadata(),
        cancel_event=asyncio.Event(),
        stream_queue=stream_queue,
    )
    defaults.update(overrides)
    return TaskRun(**defaults)


class TestContextStream:
    """ctx.stream() puts items on the queue."""

    @pytest.mark.asyncio
    async def test_stream_puts_item(self):
        q: asyncio.Queue = asyncio.Queue()
        ctx = _make_ctx(stream_queue=q)
        await ctx.stream("hello")
        assert q.get_nowait() == "hello"

    @pytest.mark.asyncio
    async def test_stream_multiple_items(self):
        q: asyncio.Queue = asyncio.Queue()
        ctx = _make_ctx(stream_queue=q)
        await ctx.stream(1)
        await ctx.stream(2)
        await ctx.stream(3)
        assert q.get_nowait() == 1
        assert q.get_nowait() == 2
        assert q.get_nowait() == 3

    @pytest.mark.asyncio
    async def test_stream_no_queue_noop(self):
        ctx = _make_ctx(stream_queue=None)
        # Should not raise
        await ctx.stream("ignored")

    @pytest.mark.asyncio
    async def test_stream_various_types(self):
        q: asyncio.Queue = asyncio.Queue()
        ctx = _make_ctx(stream_queue=q)
        items = ["text", 42, {"key": "val"}, [1, 2], None, True]
        for item in items:
            await ctx.stream(item)
        collected = [q.get_nowait() for _ in range(len(items))]
        assert collected == items


class TestTaskRunAsyncIter:
    """TaskRun.__aiter__ / __anext__ consume the stream queue."""

    @pytest.mark.asyncio
    async def test_iterate_items(self):
        q: asyncio.Queue = asyncio.Queue()
        run = _make_run(stream_queue=q)
        await q.put("a")
        await q.put("b")
        await q.put(_STREAM_SENTINEL)

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == ["a", "b"]

    @pytest.mark.asyncio
    async def test_empty_stream(self):
        """Sentinel immediately → no items."""
        q: asyncio.Queue = asyncio.Queue()
        run = _make_run(stream_queue=q)
        await q.put(_STREAM_SENTINEL)

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == []

    @pytest.mark.asyncio
    async def test_no_queue_stops_immediately(self):
        run = _make_run(stream_queue=None)
        collected = []
        async for item in run:
            collected.append(item)
        assert collected == []

    @pytest.mark.asyncio
    async def test_stream_and_result(self):
        """Stream items, then also await result()."""
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        run = _make_run(stream_queue=q, result_future=fut)

        await q.put("chunk1")
        await q.put("chunk2")
        await q.put(_STREAM_SENTINEL)
        fut.set_result("final")

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == ["chunk1", "chunk2"]
        result = await run.result()
        assert result == "final"  # Unit test uses raw future, not manager pipeline

    @pytest.mark.asyncio
    async def test_concurrent_producer_consumer(self):
        """Producer streams while consumer iterates."""
        q: asyncio.Queue = asyncio.Queue()
        run = _make_run(stream_queue=q)

        async def produce():
            for i in range(5):
                await q.put(i)
                await asyncio.sleep(0.01)
            await q.put(_STREAM_SENTINEL)

        collected = []

        async def consume():
            async for item in run:
                collected.append(item)

        await asyncio.gather(produce(), consume())
        assert collected == [0, 1, 2, 3, 4]


class TestStreamingErrorCases:
    """Streaming under error/suspend/cancel conditions."""

    @pytest.mark.asyncio
    async def test_sentinel_after_error(self):
        """Even on error, sentinel terminates iteration."""
        q: asyncio.Queue = asyncio.Queue()
        run = _make_run(stream_queue=q)
        await q.put("partial")
        await q.put(_STREAM_SENTINEL)

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == ["partial"]

    @pytest.mark.asyncio
    async def test_aiter_returns_self(self):
        run = _make_run(stream_queue=asyncio.Queue())
        assert run.__aiter__() is run
