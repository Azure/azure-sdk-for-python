"""Tests for pluggable StreamHandler protocol (spec 009).

Covers:
- T010: Custom handler receives items via put()/get()
- T011: Default behavior unchanged when no handler provided
- T013: Steerable task with custom handler across generations
- T015: close() called on success
- T016: close() called on failure
- T017: close() error logged but doesn't change task outcome
- T018: put() error propagates to ctx.stream()
- T021: Late-join consumer iterates stream via get_active_run()
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.durable import (
    QueueStreamHandler,
    StreamHandler,
    TaskContext,
    durable_task,
)
from azure.ai.agentserver.core.durable._stream import QueueStreamHandler as _QSH


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


async def _setup_manager(tmp_path):
    """Create a DurableTaskManager with local file storage."""
    from azure.ai.agentserver.core.durable._local_provider import (
        LocalFileDurableTaskProvider,
    )
    from azure.ai.agentserver.core.durable._manager import DurableTaskManager

    import azure.ai.agentserver.core.durable._manager as mgr_mod

    provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
    config = type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    manager = DurableTaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, mgr_mod


async def _teardown_manager(manager, mgr_mod):
    await manager.shutdown()
    mgr_mod._manager = None


# ---------------------------------------------------------------------------
# Custom handler for testing
# ---------------------------------------------------------------------------


class RecordingHandler:
    """A StreamHandler that records all put/get/close calls."""

    def __init__(self) -> None:
        self.items_put: list[Any] = []
        self.close_called: bool = False
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._sentinel = object()

    async def put(self, item: Any) -> None:
        self.items_put.append(item)
        await self._queue.put(item)

    async def get(self) -> Any:
        item = await self._queue.get()
        if item is self._sentinel:
            raise StopAsyncIteration
        return item

    async def close(self) -> None:
        self.close_called = True
        await self._queue.put(self._sentinel)


class FailingPutHandler:
    """A StreamHandler whose put() always raises."""

    async def put(self, item: Any) -> None:
        raise RuntimeError("put() failed")

    async def get(self) -> Any:
        raise StopAsyncIteration

    async def close(self) -> None:
        pass


class FailingCloseHandler:
    """A StreamHandler whose close() always raises."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._sentinel = object()

    async def put(self, item: Any) -> None:
        await self._queue.put(item)

    async def get(self) -> Any:
        item = await self._queue.get()
        if item is self._sentinel:
            raise StopAsyncIteration
        return item

    async def close(self) -> None:
        await self._queue.put(self._sentinel)
        raise RuntimeError("close() failed")


# ---------------------------------------------------------------------------
# Phase 3: Custom Handler Dispatch (T010, T011)
# ---------------------------------------------------------------------------


class TestCustomHandlerDispatch:
    """T010/T011: custom handler receives items; default unchanged."""

    @pytest.mark.asyncio
    async def test_custom_handler_receives_items(self, tmp_path):
        """T010: Custom handler receives all items via put(), consumer
        gets them via get()."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = RecordingHandler()

            @durable_task(name="t010_custom_stream")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("chunk-1")
                await ctx.stream("chunk-2")
                await ctx.stream("chunk-3")
                return "done"

            run = await my_task.start(
                task_id="t010-1",
                input="hello",
                stream_handler=handler,
            )

            collected = []
            async for chunk in run:
                collected.append(chunk)

            result = await run.result()
            assert result.output == "done"
            assert collected == ["chunk-1", "chunk-2", "chunk-3"]
            assert handler.items_put == ["chunk-1", "chunk-2", "chunk-3"]
            assert handler.close_called is True
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_default_handler_when_none_provided(self, tmp_path):
        """T011: When no handler provided, default QueueStreamHandler works."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:

            @durable_task(name="t011_default_stream")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("a")
                await ctx.stream("b")
                return "ok"

            run = await my_task.start(
                task_id="t011-1",
                input="test",
            )

            collected = []
            async for chunk in run:
                collected.append(chunk)

            result = await run.result()
            assert result.output == "ok"
            assert collected == ["a", "b"]
        finally:
            await _teardown_manager(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Phase 4: Steering Carry-Over (T013)
# ---------------------------------------------------------------------------


class TestSteeringCarryOver:
    """T013: Handler survives steering re-entries."""

    @pytest.mark.asyncio
    async def test_handler_carries_across_steering(self, tmp_path):
        """T013: Items from both generations flow through same handler."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = RecordingHandler()
            gen1_started = asyncio.Event()

            @durable_task(name="t013_steerable", steerable=True)
            async def steerable_task(ctx: TaskContext[dict]) -> dict:
                gen = ctx.generation
                await ctx.stream({"gen": gen, "event": "start"})

                if gen == 0:
                    gen1_started.set()
                    # Wait for cancel (steering)
                    while not ctx.cancel.is_set():
                        await asyncio.sleep(0.01)
                    await ctx.stream({"gen": gen, "event": "cancelled"})
                    return await ctx.suspend(reason="steered")

                await ctx.stream({"gen": gen, "event": "finish"})
                return {"gen": gen, "status": "completed"}

            # Start gen 0 with custom handler
            run1 = await steerable_task.start(
                task_id="t013-1",
                input={"msg": "first"},
                stream_handler=handler,
            )

            # Wait for gen 0 to start streaming
            await gen1_started.wait()

            # Steer — gen 0 gets cancelled, gen 1 starts
            run2 = await steerable_task.start(
                task_id="t013-1",
                input={"msg": "second"},
            )

            # Consume all items from run1 (which carries the handler)
            collected = []
            async for chunk in run1:
                collected.append(chunk)

            # Handler should have items from both generations
            assert handler.close_called is True
            assert any(item.get("gen") == 0 for item in handler.items_put)
            assert any(item.get("gen") == 1 for item in handler.items_put)
        finally:
            await _teardown_manager(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Phase 5: Stream Closure (T015, T016, T017, T018)
# ---------------------------------------------------------------------------


class TestStreamClosure:
    """T015–T018: close() lifecycle and error propagation."""

    @pytest.mark.asyncio
    async def test_close_called_on_success(self, tmp_path):
        """T015: close() is called when task succeeds."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = RecordingHandler()

            @durable_task(name="t015_success")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("data")
                return "success"

            run = await my_task.start(
                task_id="t015-1",
                input="x",
                stream_handler=handler,
            )
            result = await run.result()
            assert result.output == "success"
            assert handler.close_called is True
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_close_called_on_failure(self, tmp_path):
        """T016: close() is called when task fails."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = RecordingHandler()

            @durable_task(name="t016_failure")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("before-error")
                raise ValueError("boom")

            run = await my_task.start(
                task_id="t016-1",
                input="x",
                stream_handler=handler,
            )

            # Drain stream
            collected = []
            async for chunk in run:
                collected.append(chunk)

            assert handler.close_called is True
            assert collected == ["before-error"]
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_close_error_logged_not_propagated(self, tmp_path, caplog):
        """T017: close() error is logged but doesn't change task outcome."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = FailingCloseHandler()

            @durable_task(name="t017_close_error")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("data")
                return "ok"

            run = await my_task.start(
                task_id="t017-1",
                input="x",
                stream_handler=handler,
            )

            collected = []
            async for chunk in run:
                collected.append(chunk)

            # Task should still succeed despite close() error
            result = await run.result()
            assert result.output == "ok"
            assert collected == ["data"]

            # close() error should be logged
            assert any(
                "close() failed" in record.message
                for record in caplog.records
                if record.levelno >= logging.WARNING
            )
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_put_error_propagates(self, tmp_path):
        """T018: put() error propagates to ctx.stream() call site."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            handler = FailingPutHandler()

            @durable_task(name="t018_put_error")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("this will fail")
                return "should not reach"

            run = await my_task.start(
                task_id="t018-1",
                input="x",
                stream_handler=handler,
            )

            # The task should fail because put() raised
            from azure.ai.agentserver.core.durable import TaskFailed

            with pytest.raises(TaskFailed):
                await run.result()
        finally:
            await _teardown_manager(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Phase 6: Late-Join Consumer (T021)
# ---------------------------------------------------------------------------


class TestLateJoinConsumer:
    """T021: Late-join consumer via get_active_run()."""

    @pytest.mark.asyncio
    async def test_late_join_gets_stream_items(self, tmp_path):
        """T021: Code that didn't call start() gets a TaskRun handle
        and iterates stream items via get_active_run()."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            task_started = asyncio.Event()
            proceed = asyncio.Event()

            @durable_task(name="t021_late_join")
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("chunk-1")
                task_started.set()
                await proceed.wait()
                await ctx.stream("chunk-2")
                return "done"

            # Start the task
            run = await my_task.start(
                task_id="t021-1",
                input="hello",
            )

            # Wait for first chunk to be streamed
            await task_started.wait()

            # Late-join: get a handle without being the original caller
            late_run = my_task.get_active_run("t021-1")
            assert late_run is not None

            # Let the task finish
            proceed.set()

            # Both runs should be able to get the result
            result = await run.result()
            assert result.output == "done"

            late_result = await late_run.result()
            assert late_result.output == "done"
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_get_active_run_returns_none_for_inactive(self, tmp_path):
        """get_active_run returns None for a task not currently active."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:

            @durable_task(name="t021_inactive")
            async def my_task(ctx: TaskContext[str]) -> str:
                return "done"

            result = my_task.get_active_run("nonexistent-task")
            assert result is None
        finally:
            await _teardown_manager(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """Verify QueueStreamHandler and custom handlers satisfy Protocol."""

    def test_queue_handler_is_stream_handler(self):
        handler = QueueStreamHandler()
        assert isinstance(handler, StreamHandler)

    def test_recording_handler_is_stream_handler(self):
        handler = RecordingHandler()
        assert isinstance(handler, StreamHandler)

    def test_failing_put_handler_is_stream_handler(self):
        handler = FailingPutHandler()
        assert isinstance(handler, StreamHandler)
