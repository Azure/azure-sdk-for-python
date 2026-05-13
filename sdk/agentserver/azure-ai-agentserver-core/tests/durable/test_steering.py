# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for steerable durable tasks — steering, drain, context, and recovery."""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    TaskResult,
    durable_task,
    EntryMode,
    EtagConflict,
    SteeringQueueFull,
    TaskConflictError,
)


class TestSteering:
    """Core steering functionality: append, drain, short-circuit."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )
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

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    # ------------------------------------------------------------------
    # US1: Basic steering
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_steerable_start_on_in_progress_queues_input(self, tmp_path):
        """start() on in_progress steerable task appends input, not raises."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                # Simulate work with small delay
                await asyncio.sleep(0.5)
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": ctx.input.get("msg", "?")}

            # Start first invocation
            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Small delay for A to enter function body
            await asyncio.sleep(0.1)

            # Steer while in progress — should NOT raise
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            # run2 should be a TaskRun (ack), not raise TaskConflictError
            assert run2.task_id == "t1"

            # Verify queue has the input
            task_info = await manager.provider.get("t1")
            steering = task_info.payload.get("_steering", {})
            assert len(steering["pending_inputs"]) >= 1
            assert steering["cancel_requested"] is True

            # run1 should be superseded (A was cancelled)
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            assert result1.is_superseded

            # run2 should complete (B runs after drain)
            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert result2.is_completed
            assert result2.output == {"msg": "B"}

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_non_steerable_raises_conflict(self, tmp_path):
        """start() on in_progress non-steerable task still raises."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            gate = asyncio.Event()

            @durable_task(name="regular")
            async def regular(ctx: TaskContext[dict]) -> dict:
                await gate.wait()
                return {"msg": "done"}

            run1 = await regular.start(task_id="t1", input={"msg": "A"})

            with pytest.raises(TaskConflictError):
                await regular.start(task_id="t1", input={"msg": "B"})

            gate.set()
            await asyncio.wait_for(run1.result(), timeout=5.0)

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_steering_queue_full(self, tmp_path):
        """start() raises SteeringQueueFull when queue is at capacity."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            gate = asyncio.Event()

            @durable_task(name="chat", steerable=True, max_pending=2)
            async def chat(ctx: TaskContext[dict]) -> dict:
                await gate.wait()
                return {"msg": "done"}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Fill the queue
            await chat.start(task_id="t1", input={"msg": "B"})
            await chat.start(task_id="t1", input={"msg": "C"})

            # Queue is full — should raise
            with pytest.raises(SteeringQueueFull) as exc_info:
                await chat.start(task_id="t1", input={"msg": "D"})

            assert exc_info.value.max_pending == 2

            gate.set()
            await asyncio.wait_for(run1.result(), timeout=5.0)

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_superseded_result_status(self, tmp_path):
        """Superseded generation's TaskRun resolves with status=superseded."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                # Always check cancel and suspend if set
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                # Simulate work — gives time for cancel signal
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Small delay to ensure task is running
            await asyncio.sleep(0.1)

            # Steer
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            # run1 should be superseded
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            assert result1.is_superseded

            # run2 should complete
            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert result2.is_completed
            assert result2.output == {"msg": "B"}

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    # US2: Rapid-fire short-circuit
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_rapid_fire_only_last_completes(self, tmp_path):
        """3 rapid-fire steers: only the last gen runs to completion."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            entries: list[tuple[str, bool]] = []

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                entries.append((ctx.input.get("msg", "?"), ctx.cancel.is_set()))
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Small delay for A to start
            await asyncio.sleep(0.05)

            # Rapid-fire B, C, D
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            run_c = await chat.start(task_id="t1", input={"msg": "C"})
            run_d = await chat.start(task_id="t1", input={"msg": "D"})

            # D should be the one that completes
            result_d = await asyncio.wait_for(run_d.result(), timeout=5.0)
            assert result_d.is_completed
            assert result_d.output == {"msg": "D"}

            # B and C should be superseded
            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            assert result_b.is_superseded

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
            assert result_c.is_superseded

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_cancel_pre_set_when_queue_has_items(self, tmp_path):
        """ctx.cancel is pre-set at function entry when queue has items."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            cancel_states: list[bool] = []

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                cancel_states.append(ctx.cancel.is_set())
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)

            # Queue B and C
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            run_c = await chat.start(task_id="t1", input={"msg": "C"})

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
            assert result_c.is_completed

            # A: cancel set by steering signal
            # B: cancel pre-set (C still queued)
            # C: cancel NOT set (nothing queued after C)
            # cancel_states should have at least 3 entries
            assert len(cancel_states) >= 3
            # The last one (C) should be False
            assert cancel_states[-1] is False

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    # US3: Context enrichment
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_steered_context_fields(self, tmp_path):
        """Steered generation has was_steered=True, previous_input set."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            contexts: list[dict[str, Any]] = []

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                contexts.append(
                    {
                        "entry_mode": ctx.entry_mode,
                        "was_steered": ctx.was_steered,
                        "previous_input": ctx.previous_input,
                        "generation": ctx.generation,
                        "msg": ctx.input.get("msg", "?"),
                    }
                )
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                # Simulate work — gives time for steering signal
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.1)

            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert result2.is_completed

            # First entry: fresh, not steered
            assert contexts[0]["entry_mode"] == "fresh"
            assert contexts[0]["was_steered"] is False
            assert contexts[0]["generation"] == 0

            # Second entry: steered (entry_mode="resumed" with was_steered=True)
            steered = [c for c in contexts if c["was_steered"] is True]
            assert len(steered) >= 1
            assert steered[0]["entry_mode"] == "resumed"
            assert steered[0]["generation"] > 0

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_steered(self, tmp_path):
        """Steered generations enter with entry_mode='resumed' and was_steered=True."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            modes: list[str] = []
            steered_flags: list[bool] = []

            @durable_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                modes.append(ctx.entry_mode)
                steered_flags.append(ctx.was_steered)
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": "done"}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.1)
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            await asyncio.wait_for(run2.result(), timeout=5.0)

            assert "fresh" in modes
            assert "resumed" in modes
            # The steered generation should have was_steered=True
            assert True in steered_flags

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    # TaskResult.is_superseded
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_task_result_is_superseded(self):
        """TaskResult with status=superseded has is_superseded=True."""
        result = TaskResult(task_id="t1", status="superseded")
        assert result.is_superseded is True
        assert result.is_completed is False
        assert result.is_suspended is False
        assert result.output is None

    @pytest.mark.asyncio
    async def test_task_result_completed_not_superseded(self):
        """TaskResult with status=completed has is_superseded=False."""
        result = TaskResult(task_id="t1", status="completed", output=42)
        assert result.is_superseded is False
        assert result.is_completed is True

    # ------------------------------------------------------------------
    # Options passthrough
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_steerable_via_options(self, tmp_path):
        """steerable can be set via .options()."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            gate = asyncio.Event()

            @durable_task(name="chat")
            async def chat(ctx: TaskContext[dict]) -> dict:
                await gate.wait()
                if ctx.cancel.is_set():
                    return await ctx.suspend(reason="steered")
                return {"msg": "done"}

            steerable_chat = chat.options(steerable=True)

            run1 = await steerable_chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)

            # This should work because steerable=True via options
            run2 = await steerable_chat.start(task_id="t1", input={"msg": "B"})
            assert run2.task_id == "t1"

            gate.set()
            await asyncio.wait_for(run2.result(), timeout=5.0)

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    # DurableTaskOptions validation
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_max_pending_validation(self):
        """max_pending < 1 raises ValueError at decoration time."""
        with pytest.raises(ValueError, match="max_pending"):

            @durable_task(name="bad", max_pending=0)
            async def bad(ctx: TaskContext[dict]) -> dict:
                return {}

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_etag_conflict_exception(self):
        """EtagConflict has task_id attribute."""
        exc = EtagConflict("t1", "test message")
        assert exc.task_id == "t1"
        assert "test message" in str(exc)

    @pytest.mark.asyncio
    async def test_steering_queue_full_exception(self):
        """SteeringQueueFull has task_id and max_pending attributes."""
        exc = SteeringQueueFull("t1", 10)
        assert exc.task_id == "t1"
        assert exc.max_pending == 10
        assert "10" in str(exc)

    # ------------------------------------------------------------------
    # Steering with function that completes (not suspends)
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_steering_function_ignores_cancel_completes(self, tmp_path):
        """If function ignores cancel and returns, steering still works via drain."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            call_count = 0

            @durable_task(name="chat", steerable=True, ephemeral=False)
            async def chat(ctx: TaskContext[dict]) -> dict:
                nonlocal call_count
                call_count += 1
                # Intentionally ignores ctx.cancel
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Wait for A to complete
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            assert result1.is_completed

            # For non-ephemeral completed tasks, steerable or not, raises conflict
            with pytest.raises(TaskConflictError):
                await chat.start(task_id="t1", input={"msg": "B"})

        finally:
            await self._teardown_manager(manager, mgr_mod)


class TestSteeringRecovery:
    """Crash recovery for steerable tasks."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )
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

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_recovery_with_drain_in_progress(self, tmp_path):
        """Recovery after crash mid-drain uses active_input from steering state."""
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )
        from azure.ai.agentserver.core.durable._models import (
            TaskPatchRequest,
        )
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

        # Phase 1: Create a task and simulate crash mid-drain
        manager = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()

        @durable_task(name="chat", steerable=True, ephemeral=False)
        async def chat(ctx: TaskContext[dict]) -> dict:
            return {"msg": ctx.input.get("msg", "?")}

        run1 = await chat.start(task_id="t1", input={"msg": "A"})
        await asyncio.wait_for(run1.result(), timeout=5.0)

        # Simulate crash state: task is in_progress with drain_in_progress
        # Reset status to in_progress and inject steering state
        await provider.update(
            "t1",
            TaskPatchRequest(
                status="in_progress",
                payload={
                    "_steering": {
                        "generation": 1,
                        "active_input": {"msg": "B"},
                        "previous_input": {"msg": "A"},
                        "pending_inputs": [],
                        "cancel_requested": False,
                        "drain_in_progress": True,
                    },
                },
            ),
        )

        await manager.shutdown()
        mgr_mod._manager = None

        # Phase 2: Recover — new manager picks up the crashed task
        manager2 = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager2
        await manager2.startup()

        inputs_seen: list[dict] = []

        @durable_task(name="chat", steerable=True, ephemeral=False)
        async def chat2(ctx: TaskContext[dict]) -> dict:
            inputs_seen.append(dict(ctx.input))
            return {"msg": ctx.input.get("msg", "?")}

        # Start with recovery input (doesn't matter — active_input overrides)
        run2 = await chat2.start(
            task_id="t1", input={"msg": "recovery"}, stale_timeout=0.0
        )
        result2 = await asyncio.wait_for(run2.result(), timeout=5.0)

        # Should have used active_input "B", not the recovery caller input
        assert result2.output == {"msg": "B"}
        assert inputs_seen[-1] == {"msg": "B"}

        await manager2.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_recovery_with_pending_inputs(self, tmp_path):
        """Recovery with pending inputs drains them after function completes."""
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )
        from azure.ai.agentserver.core.durable._models import (
            TaskPatchRequest,
        )
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

        # Phase 1: Create a task normally, then simulate crash with pending
        manager = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()

        @durable_task(name="chat", steerable=True, ephemeral=False)
        async def chat_setup(ctx: TaskContext[dict]) -> dict:
            # Long sleep — we'll kill the manager before it completes
            await asyncio.sleep(10)
            return {"msg": "never"}

        run1 = await chat_setup.start(task_id="t2", input={"msg": "X"})
        await asyncio.sleep(0.1)  # let it start

        # Force shutdown (simulates crash)
        await manager.shutdown()
        mgr_mod._manager = None

        # Patch the task to simulate crash-with-pending state
        await provider.update(
            "t2",
            TaskPatchRequest(
                status="in_progress",
                payload={
                    "input": {"msg": "X"},
                    "_steering": {
                        "generation": 0,
                        "active_input": {"msg": "X"},
                        "pending_inputs": [{"msg": "Y"}, {"msg": "Z"}],
                        "cancel_requested": True,
                        "drain_in_progress": False,
                    },
                },
            ),
        )

        # Phase 2: New manager recovers the task
        manager2 = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager2
        await manager2.startup()

        inputs_seen: list[str] = []

        @durable_task(name="chat", steerable=True, ephemeral=False)
        async def chat(ctx: TaskContext[dict]) -> dict:
            inputs_seen.append(ctx.input.get("msg", "?"))
            if ctx.cancel.is_set():
                return await ctx.suspend(reason="steered")
            return {"msg": ctx.input.get("msg", "?")}

        run2 = await chat.start(
            task_id="t2", input={"msg": "recover"}, stale_timeout=0.0
        )
        result = await asyncio.wait_for(run2.result(), timeout=5.0)

        # Should have drained through X (cancel set) → Y (cancel set) → Z (complete)
        assert result.output == {"msg": "Z"}
        assert "Z" in inputs_seen

        await manager2.shutdown()
        mgr_mod._manager = None
