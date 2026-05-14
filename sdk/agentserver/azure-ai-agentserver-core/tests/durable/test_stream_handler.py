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


# ---------------------------------------------------------------------------
# stream_handler_factory on decorator (recovery uses factory)
# ---------------------------------------------------------------------------


class TestStreamHandlerFactory:
    """Verify stream_handler_factory on the decorator is used for recovery."""

    @pytest.mark.asyncio
    async def test_factory_used_on_fresh_start(self, tmp_path):
        """When no call-site handler provided, factory creates the handler."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            created_handlers: list[RecordingHandler] = []

            def _factory(task_id: str) -> RecordingHandler:
                h = RecordingHandler()
                created_handlers.append(h)
                return h

            @durable_task(
                name="t_factory_fresh",
                stream_handler_factory=_factory,
            )
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("x")
                return "ok"

            run = await my_task.start(task_id="factory-1", input="hi")
            collected = []
            async for chunk in run:
                collected.append(chunk)
            result = await run.result()

            assert result.output == "ok"
            assert collected == ["x"]
            assert len(created_handlers) == 1
            assert created_handlers[0].items_put == ["x"]
            assert created_handlers[0].close_called is True
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_call_site_handler_overrides_factory(self, tmp_path):
        """Call-site stream_handler takes precedence over factory."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            factory_called = False

            def _factory(task_id: str) -> RecordingHandler:
                nonlocal factory_called
                factory_called = True
                return RecordingHandler()

            @durable_task(
                name="t_factory_override",
                stream_handler_factory=_factory,
            )
            async def my_task(ctx: TaskContext[str]) -> str:
                await ctx.stream("y")
                return "ok"

            call_site_handler = RecordingHandler()
            run = await my_task.start(
                task_id="override-1",
                input="hi",
                stream_handler=call_site_handler,
            )
            collected = []
            async for chunk in run:
                collected.append(chunk)
            await run.result()

            assert collected == ["y"]
            assert call_site_handler.items_put == ["y"]
            assert factory_called is False
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_factory_used_on_recovery(self, tmp_path):
        """On crash recovery, factory creates the handler, not QueueStreamHandler."""
        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            created_handlers: list[RecordingHandler] = []

            def _factory(task_id: str) -> RecordingHandler:
                h = RecordingHandler()
                created_handlers.append(h)
                return h

            @durable_task(
                name="t_factory_recovery",
                stream_handler_factory=_factory,
                ephemeral=False,
            )
            async def my_task(ctx: TaskContext[str]) -> str:
                if ctx.entry_mode == "recovered":
                    await ctx.stream("recovered-chunk")
                    return "recovered"
                await ctx.stream("fresh-chunk")
                return "fresh"

            # First run — fresh
            run1 = await my_task.start(task_id="recovery-1", input="hi")
            collected1 = []
            async for chunk in run1:
                collected1.append(chunk)
            result1 = await run1.result()
            assert result1.output == "fresh"
            assert collected1 == ["fresh-chunk"]
            assert len(created_handlers) == 1

            # Simulate crash: force task back to in_progress + stale
            # Write directly to the local file store to backdate updated_at
            import json

            task_file = (
                Path(str(tmp_path)) / "test-agent" / "test-session" / "recovery-1.json"
            )
            with open(task_file, "r") as f:
                data = json.load(f)
            data["status"] = "in_progress"
            data["updated_at"] = "2000-01-01T00:00:00+00:00"
            with open(task_file, "w") as f:
                json.dump(data, f)

            # Recovery — should use factory, not QueueStreamHandler
            run2 = await my_task.start(
                task_id="recovery-1",
                input="hi",
                stale_timeout=1.0,
            )
            collected2 = []
            async for chunk in run2:
                collected2.append(chunk)
            result2 = await run2.result()

            assert result2.output == "recovered"
            assert collected2 == ["recovered-chunk"]
            # Factory should have been called twice total (fresh + recovery)
            assert len(created_handlers) == 2
            assert created_handlers[1].items_put == ["recovered-chunk"]
        finally:
            await _teardown_manager(manager, mgr_mod)
