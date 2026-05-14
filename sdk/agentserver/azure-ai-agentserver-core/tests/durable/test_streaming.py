"""Tests for streaming support (ctx.stream + async-for on TaskRun)."""

from __future__ import annotations

import asyncio

import pytest

from azure.ai.agentserver.core.durable._context import TaskContext
from azure.ai.agentserver.core.durable._metadata import TaskMetadata
from azure.ai.agentserver.core.durable._run import TaskRun
from azure.ai.agentserver.core.durable._stream import QueueStreamHandler


def _make_ctx(stream_handler=None, **overrides):
    defaults = dict(
        task_id="t1",
        title="test",
        session_id="s1",
        agent_name="a1",
        tags={},
        input=None,
        metadata=TaskMetadata(),
        stream_handler=stream_handler,
    )
    defaults.update(overrides)
    return TaskContext(**defaults)


def _make_run(stream_handler=None, result_future=None, **overrides):
    loop = asyncio.get_event_loop()
    if result_future is None:
        result_future = loop.create_future()
    defaults = dict(
        task_id="t1",
        provider=None,
        result_future=result_future,
        metadata=TaskMetadata(),
        cancel_event=asyncio.Event(),
        stream_handler=stream_handler,
    )
    defaults.update(overrides)
    return TaskRun(**defaults)


class TestContextStream:
    """ctx.stream() puts items via the handler."""

    @pytest.mark.asyncio
    async def test_stream_puts_item(self):
        handler = QueueStreamHandler()
        ctx = _make_ctx(stream_handler=handler)
        await ctx.stream("hello")
        assert await handler.get() == "hello"

    @pytest.mark.asyncio
    async def test_stream_multiple_items(self):
        handler = QueueStreamHandler()
        ctx = _make_ctx(stream_handler=handler)
        await ctx.stream(1)
        await ctx.stream(2)
        await ctx.stream(3)
        assert await handler.get() == 1
        assert await handler.get() == 2
        assert await handler.get() == 3

    @pytest.mark.asyncio
    async def test_stream_no_handler_noop(self):
        ctx = _make_ctx(stream_handler=None)
        # Should not raise
        await ctx.stream("ignored")

    @pytest.mark.asyncio
    async def test_stream_various_types(self):
        handler = QueueStreamHandler()
        ctx = _make_ctx(stream_handler=handler)
        items = ["text", 42, {"key": "val"}, [1, 2], None, True]
        for item in items:
            await ctx.stream(item)
        collected = [await handler.get() for _ in range(len(items))]
        assert collected == items


class TestTaskRunAsyncIter:
    """TaskRun.__aiter__ / __anext__ consume via the stream handler."""

    @pytest.mark.asyncio
    async def test_iterate_items(self):
        handler = QueueStreamHandler()
        run = _make_run(stream_handler=handler)
        await handler.put("a")
        await handler.put("b")
        await handler.close()

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == ["a", "b"]

    @pytest.mark.asyncio
    async def test_empty_stream(self):
        """close() immediately → no items."""
        handler = QueueStreamHandler()
        run = _make_run(stream_handler=handler)
        await handler.close()

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == []

    @pytest.mark.asyncio
    async def test_no_handler_stops_immediately(self):
        run = _make_run(stream_handler=None)
        collected = []
        async for item in run:
            collected.append(item)
        assert collected == []

    @pytest.mark.asyncio
    async def test_stream_and_result(self):
        """Stream items, then also await result()."""
        handler = QueueStreamHandler()
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        run = _make_run(stream_handler=handler, result_future=fut)

        await handler.put("chunk1")
        await handler.put("chunk2")
        await handler.close()
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
        handler = QueueStreamHandler()
        run = _make_run(stream_handler=handler)

        async def produce():
            for i in range(5):
                await handler.put(i)
                await asyncio.sleep(0.01)
            await handler.close()

        collected = []

        async def consume():
            async for item in run:
                collected.append(item)

        await asyncio.gather(produce(), consume())
        assert collected == [0, 1, 2, 3, 4]


class TestStreamingErrorCases:
    """Streaming under error/suspend/cancel conditions."""

    @pytest.mark.asyncio
    async def test_close_terminates_iteration(self):
        """close() terminates iteration cleanly."""
        handler = QueueStreamHandler()
        run = _make_run(stream_handler=handler)
        await handler.put("partial")
        await handler.close()

        collected = []
        async for item in run:
            collected.append(item)
        assert collected == ["partial"]

    @pytest.mark.asyncio
    async def test_aiter_returns_self(self):
        run = _make_run(stream_handler=QueueStreamHandler())
        assert run.__aiter__() is run
