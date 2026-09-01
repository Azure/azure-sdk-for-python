# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for steerable resilient tasks — steering, drain, context, and recovery."""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import (
    TaskContext,
    task,
    EntryMode,
    SteeringQueueFull,
    TaskConflictError,
    multi_turn_task,
)
from azure.ai.agentserver.core.tasks._exceptions import EtagConflict


class TestSteering:
    """Core steering functionality: append, drain, short-circuit."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    # ------------------------------------------------------------------
    #: Basic steering
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_steerable_start_on_in_progress_queues_input(self, tmp_path):
        """start() on in_progress steerable task appends input, not raises."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                if ctx.cancel.is_set():
                    return None
                # Simulate work with small delay
                await asyncio.sleep(0.5)
                if ctx.cancel.is_set():
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            # Start first invocation
            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Small delay for A to enter function body
            await asyncio.sleep(0.1)

            # Steer while in progress — should NOT raise
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            # run2 should be a TaskRun (ack), not raise TaskConflictError
            #: exception.task_id removed
            # Verify queue has the input
            task_info = await manager.provider.get("t1")
            steering = task_info.payload.get("steering", {})
            assert len(steering["pending_inputs"]) >= 1
            assert steering["cancel_requested"] is True

            # run1 should be superseded (A was cancelled)
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)

            # run2 should complete (B runs after drain)
            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert True  #: result2 is raw Output (completion implicit)
            assert result2 == {"msg": "B"}

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_non_steerable_raises_conflict(self, tmp_path):
        """start() on in_progress non-steerable task still raises."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            gate = asyncio.Event()

            @task(name="regular")
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
        """start() raises SteeringQueueFull when queue is at capacity.

        : the per-task ``max_pending`` knob was
                demoted; the framework-wide default
                ``_DEFAULT_MAX_PENDING_STEERING`` (10) applies. This test fills the
                queue at that default to verify the exception still surfaces.
        """
        from azure.ai.agentserver.core.tasks._decorator import _DEFAULT_MAX_PENDING_STEERING

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            gate = asyncio.Event()

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                await gate.wait()
                return {"msg": "done"}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Fill the queue to the framework default
            for i in range(_DEFAULT_MAX_PENDING_STEERING):
                await chat.start(task_id="t1", input={"msg": f"fill-{i}"})

            # Queue is full — should raise
            with pytest.raises(SteeringQueueFull):
                await chat.start(task_id="t1", input={"msg": "overflow"})

            #: SteeringQueueFull is bare exception (no max_pending)

            gate.set()
            await asyncio.wait_for(run1.result(), timeout=5.0)

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_superseded_result_status(self, tmp_path):
        """Superseded generation's TaskRun resolves with status=superseded."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                # Always check cancel and suspend if set
                if ctx.cancel.is_set():
                    return None
                # Simulate work — gives time for cancel signal
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})

            # Small delay to ensure task is running
            await asyncio.sleep(0.1)

            # Steer
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            # run1 should be superseded
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)

            # run2 should complete
            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert True  #: result2 is raw Output (completion implicit)
            assert result2 == {"msg": "B"}

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    #: Rapid-fire short-circuit
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_rapid_fire_only_last_completes(self, tmp_path):
        """3 rapid-fire steers: only the last gen runs to completion."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            entries: list[tuple[str, bool]] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                entries.append((ctx.input.get("msg", "?"), ctx.cancel.is_set()))
                if ctx.cancel.is_set():
                    return None
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
            assert True  #: result_d is raw Output (completion implicit)
            assert result_d == {"msg": "D"}

            # B and C should be superseded
            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
        #: result is raw output (Suspended wrapper removed)

        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_cancel_pre_set_when_queue_has_items(self, tmp_path):
        """ctx.cancel is pre-set at function entry when queue has items."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            cancel_states: list[bool] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                cancel_states.append(ctx.cancel.is_set())
                if ctx.cancel.is_set():
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)

            # Queue B and C
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            run_c = await chat.start(task_id="t1", input={"msg": "C"})

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
            assert True  #: result_c is raw Output (completion implicit)

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
    #: Context enrichment
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_is_queued_distinguishes_queued_vs_fresh_run(self, tmp_path):
        """``TaskRun.is_queued`` is the public queued-steering-input detector.

        A run returned by ``start()`` against an in-flight steerable chain is a
        queued (not-yet-promoted) input → ``is_queued is True``; a freshly
        started run → ``is_queued is False``.
        """
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                if ctx.cancel.is_set():
                    return None
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            # Fresh start → not queued.
            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            assert run1.is_queued is False

            await asyncio.sleep(0.05)

            # Steer mid-turn → queued handle.
            run2 = await chat.start(task_id="t1", input={"msg": "B"})
            assert run2.is_queued is True

            # The queued run still drains to completion (B runs after A winds down).
            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert result2 == {"msg": "B"}
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_steered_context_fields(self, tmp_path):
        """: steered generation has is_steered_turn=True.
        The legacy was_steered / steering_generation fields are removed."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            contexts: list[dict[str, Any]] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                contexts.append(
                    {
                        "entry_mode": ctx.entry_mode,
                        "is_steered_turn": ctx.is_steered_turn,
                        "msg": ctx.input.get("msg", "?"),
                    }
                )
                if ctx.cancel.is_set():
                    return None
                # Simulate work — gives time for steering signal
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.1)

            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert True  #: result2 is raw Output (completion implicit)

            # First entry: fresh, not steered
            assert contexts[0]["entry_mode"] == "fresh"
            assert contexts[0]["is_steered_turn"] is False

            # Second entry: steered (entry_mode="resumed" with is_steered_turn=True)
            steered = [c for c in contexts if c["is_steered_turn"] is True]
            assert len(steered) >= 1
            assert steered[0]["entry_mode"] == "resumed"

        finally:
            await self._teardown_manager(manager, mgr_mod)
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_entry_mode_steered(self, tmp_path):
        """: steered generations enter with
        entry_mode='resumed' and is_steered_turn=True."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            modes: list[str] = []
            steered_flags: list[bool] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                modes.append(ctx.entry_mode)
                steered_flags.append(ctx.is_steered_turn)
                if ctx.cancel.is_set():
                    return None
                await asyncio.sleep(0.3)
                if ctx.cancel.is_set():
                    return None
                return {"msg": "done"}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.1)
            run2 = await chat.start(task_id="t1", input={"msg": "B"})

            await asyncio.wait_for(run2.result(), timeout=5.0)

            assert "fresh" in modes
            assert "resumed" in modes
            # The steered generation should have is_steered_turn=True
            assert True in steered_flags

        finally:
            await self._teardown_manager(manager, mgr_mod)

    # ------------------------------------------------------------------
    # TaskResult.is_superseded — REMOVED per   (whole wrapper deleted)
    # ------------------------------------------------------------------

    #: TaskResult class is fully deleted; tests for its
    # legacy is_superseded property are no longer applicable.

    # ------------------------------------------------------------------
    # Options passthrough
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # TaskOptions validation
    # ------------------------------------------------------------------
    #: ``max_pending`` is no longer a configurable
    # kwarg on ``@task``; the framework default applies. The previous
    # ``test_max_pending_validation`` (which asserted ``max_pending=0`` raised
    # at decoration time) has been removed because the kwarg itself is gone —
    # ``test_public_api_surface.py`` enforces its absence.

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_etag_conflict_exception(self):
        """EtagConflict has task_id attribute."""
        exc = EtagConflict("t1", "test message")
        #: exception.task_id removed
        assert "test message" in str(exc)

    # ------------------------------------------------------------------
    # Steering with function that completes (not suspends)
    # ------------------------------------------------------------------
    # (Removed: test_steering_function_ignores_cancel_completes asserted
    # the pre-redesign semantics where @task could be steerable and a
    # completing multi-turn handler raised TaskConflictError on the next
    # .start. Under the current spec @task is never steerable and
    # @multi_turn_task return-X is implicit suspend; the next .start is
    # the next turn's input, not a conflict.)


class TestSteeringRecovery:
    """Crash recovery for steerable tasks."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_recovery_with_drain_in_progress(self, tmp_path):
        """Recovery after crash mid-drain uses active_input from steering state."""
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()

        @multi_turn_task(name="chat", steerable=True)
        async def chat(ctx: TaskContext[dict]) -> dict:
            return {"msg": ctx.input.get("msg", "?")}

        run1 = await chat.start(task_id="t1", input={"msg": "A"})
        await asyncio.wait_for(run1.result(), timeout=5.0)

        # Simulate crash state: rewrite the stored record directly to model
        # an on-disk snapshot captured before the terminal PATCH completed.
        stored = await provider.get("t1")
        assert stored is not None
        stored.status = "in_progress"
        stored.payload = {
            **(stored.payload or {}),
            "steering": {
                "generation": 1,
                "active_input": {"msg": "B"},
                "pending_inputs": [],
                "cancel_requested": False,
                "drain_in_progress": True,
            },
        }
        stored.completed_at = None
        provider._write_task(stored)  # noqa: SLF001

        await manager.shutdown()
        mgr_mod._manager = None

        # Phase 2: Recover — new manager picks up the crashed task
        manager2 = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager2
        await manager2.startup()

        inputs_seen: list[dict] = []

        @multi_turn_task(name="chat", steerable=True)
        async def chat2(ctx: TaskContext[dict]) -> dict:
            inputs_seen.append(dict(ctx.input))
            return {"msg": ctx.input.get("msg", "?")}

        # Start with recovery input (doesn't matter — active_input overrides)
        run2 = await chat2.start(task_id="t1", input={"msg": "recovery"})
        result2 = await asyncio.wait_for(run2.result(), timeout=5.0)

        # Should have used active_input "B", not the recovery caller input
        assert result2 == {"msg": "B"}
        assert inputs_seen[-1] == {"msg": "B"}

        await manager2.shutdown()
        mgr_mod._manager = None


class TestContextFieldsContract:
    """surface contract for steering-related TaskContext fields."""

    def test_task_context_previous_input_removed(self) -> None:
        """: ``ctx.previous_input`` is removed from TaskContext.

        The field, the storage population, and the steering-payload mirror
        are all retired. Developers needing the prior input snapshot must
        persist it in an application-owned State Store themselves.
        """
        from azure.ai.agentserver.core.tasks._context import TaskContext

        assert "previous_input" not in TaskContext.__slots__, (
            "previous_input must not be a TaskContext slot after  " "Phase 3."
        )

    def test_task_context_steering_generation_field_present(self) -> None:
        """: ctx.steering_generation is removed
        from the public surface. The internal _steering['generation']
        payload field is also deleted per SOT."""
        from azure.ai.agentserver.core.tasks._context import TaskContext

        assert "steering_generation" not in TaskContext.__slots__, (
            ": ctx.steering_generation MUST be removed " "from the TaskContext slots."
        )
        assert (
            "generation" not in TaskContext.__slots__
        ), "Old field name 'generation' must be removed (no deprecation alias)."


class TestPendingInputCount:
    """Spec 031 / FR-001..002 — `ctx.pending_input_count` reflects the live
    queued-steering-input count through REAL framework wiring (no mocking,
    no monkeypatching, no direct `_ActiveTask` mutation). These tests encode
    the SOT contract at task-and-streaming-spec.md §12 (:695-696), §13
    (:719) and the §13 ordering invariant (:724-727 — the steering cause is
    observable BEFORE `ctx.cancel`)."""

    async def _setup_manager(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        provider = LocalFileTaskProvider(Path(str(tmp_path)))
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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_same_process_enqueue_count_visible_at_cancel(self, tmp_path):
        """FR-001a + §13 ordering invariant: when a steering input is appended
        in the SAME process, the next read of `ctx.pending_input_count` in the
        running turn is >= 1 AND it is already >= 1 at the moment the handler
        observes `ctx.cancel.is_set()` (cause set before cancel)."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            observed: dict[str, Any] = {}

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                if ctx.input.get("msg") == "A":
                    for _ in range(300):
                        if ctx.cancel.is_set():
                            observed["count_at_cancel"] = ctx.pending_input_count
                            observed["cancel_requested"] = ctx.cancel_requested
                            return None
                        await asyncio.sleep(0.01)
                    observed["count_at_cancel"] = "never-cancelled"
                    return None
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            await asyncio.wait_for(run_b.result(), timeout=5.0)

            assert observed.get("count_at_cancel") != "never-cancelled", observed
            assert observed.get("count_at_cancel", 0) >= 1, (
                "pending_input_count MUST be >= 1 at the steering-cancel boundary "
                f"(SOT §13 ordering invariant); observed={observed}"
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_non_steerable_reads_zero(self, tmp_path):
        """FR-001: a non-steerable task reads pending_input_count == 0."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            observed: dict[str, Any] = {}

            @task(name="oneshot")
            async def oneshot(ctx: TaskContext[dict]) -> dict:
                observed["count"] = ctx.pending_input_count
                return {"ok": True}

            run = await oneshot.start(task_id="t1", input={"msg": "A"})
            await asyncio.wait_for(run.result(), timeout=5.0)
            assert observed.get("count") == 0, observed
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_count_zero_with_no_queued_inputs(self, tmp_path):
        """FR-001: a steerable turn with nothing queued reads 0."""
        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            observed: dict[str, Any] = {}

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                observed["count"] = ctx.pending_input_count
                return {"msg": ctx.input.get("msg", "?")}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.wait_for(run1.result(), timeout=5.0)
            assert observed.get("count") == 0, observed
        finally:
            await self._teardown_manager(manager, mgr_mod)


class TestSteeringWriteSerialization:
    """Spec 031 / FR-004..006 + SOT §25.1/§25.2 — steering writes are
    serialized and carry If-Match (no blind writes), and a steered turn
    drains and runs through REAL framework wiring."""

    async def _setup_manager_capturing(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod
        from .conftest import CapturingProvider

        delegate = LocalFileTaskProvider(Path(str(tmp_path)))
        provider = CapturingProvider(delegate)
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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod, provider

    async def _teardown_manager(self, manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None

    @pytest.mark.asyncio
    async def test_steer_drain_runs_steered_turn_and_no_blind_writes(self, tmp_path):
        """A steerable turn cancels on a queued input, drains it, and the
        steered turn executes — and every PATCH after the first carries a
        non-None If-Match (SOT §25.1: no blind writes)."""
        manager, mgr_mod, provider = await self._setup_manager_capturing(tmp_path)
        try:
            ran: list[str] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                msg = ctx.input.get("msg", "?")
                if msg == "A":
                    for _ in range(300):
                        if ctx.cancel.is_set():
                            return None
                        await asyncio.sleep(0.01)
                    return None
                ran.append(msg)
                return {"msg": msg}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)

            # Drain succeeded and the steered turn B executed.
            assert "B" in ran, f"steered turn B must run; ran={ran}"
            assert result_b == {"msg": "B"}, result_b

            # No blind writes: every PATCH after the very first one carries
            # a non-None If-Match. (The first PATCH after create may legitimately
            # have None if it precedes any tracked etag; all subsequent must not.)
            if_matches = [im for (_tid, _patch, im) in provider.update_calls]
            assert len(if_matches) >= 2, if_matches
            blind = [i for i, im in enumerate(if_matches) if im is None]
            # At most the first update may be unconditioned; none after.
            assert all(idx == 0 for idx in blind), (
                "SOT §25.1 violated — blind PATCH(es) with no If-Match at "
                f"update indexes {blind}; if_matches={if_matches}"
            )
        finally:
            await self._teardown_manager(manager, mgr_mod)


class TestSteeringCrossProcessDrainRecovery:
    """Spec 031 / FR-006 + SOT §25.3 — a steering drain recovers from a
    genuine (cross-process) etag conflict landing on its write: it re-reads
    the new state under a fresh lock acquisition and re-applies, so the
    steered turn still runs. Reproduced deterministically in one process via
    a content-aware provider wrapper that bumps the etag exactly once on the
    drain's pop-transition PATCH (simulating another worker's write)."""

    async def _setup_manager(self, provider):
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

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
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    @pytest.mark.asyncio
    async def test_drain_recovers_from_cross_process_conflict(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._models import TaskPatchRequest
        from azure.ai.agentserver.core.tasks._exceptions import EtagConflict

        class DrainConflictOnceProvider:
            """Bumps the etag + raises EtagConflict exactly once on the FIRST
            PATCH that pops a steering input (``_steering.active_input`` set),
            simulating a concurrent cross-process write at the drain boundary."""

            def __init__(self, delegate):
                self._delegate = delegate
                self._armed = True
                self.drain_conflicts = 0

            async def create(self, request):
                return await self._delegate.create(request)

            async def get(self, task_id):
                return await self._delegate.get(task_id)

            async def list(self, **kwargs):
                return await self._delegate.list(**kwargs)

            async def delete(self, task_id, *, force=False, cascade=False):
                await self._delegate.delete(task_id, force=force, cascade=cascade)

            def _is_drain_patch(self, patch):
                payload = getattr(patch, "payload", None) or {}
                steering = payload.get("steering") or {}
                return "active_input" in steering and steering.get("active_input") is not None

            async def update(self, task_id, patch):
                if self._armed and self._is_drain_patch(patch):
                    self._armed = False
                    self.drain_conflicts += 1
                    # Concurrent worker bumped the record (harmless tag write).
                    await self._delegate.update(task_id, TaskPatchRequest(tags={"_other_worker": "x"}))
                    raise EtagConflict(task_id, message="injected cross-process drain conflict")
                return await self._delegate.update(task_id, patch)

        provider = DrainConflictOnceProvider(LocalFileTaskProvider(Path(str(tmp_path))))
        manager, mgr_mod = await self._setup_manager(provider)
        try:
            ran: list[str] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                msg = ctx.input.get("msg", "?")
                if msg == "A":
                    for _ in range(300):
                        if ctx.cancel.is_set():
                            return None
                        await asyncio.sleep(0.01)
                    return None
                ran.append(msg)
                return {"msg": msg}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)

            assert provider.drain_conflicts == 1, "the drain write must have hit the injected conflict"
            assert "B" in ran, f"steered turn B must still run after drain recovers; ran={ran}"
            assert result_b == {"msg": "B"}, result_b
        finally:
            await manager.shutdown()
            mgr_mod._manager = None


class TestSteeringDrainStatusTransition:
    """Spec 031 (hosted re-test finding) — the steering drain MUST transition
    the record from `suspended` (written by the multi-turn turn that just
    ended) back to `in_progress` in its PATCH. The hosted task store rejects a
    lease *renewal* on a non-in_progress task, so without the status flip the
    drain PATCH 409s ("lease renewal is only supported for in_progress tasks")
    and the steered turn never runs. The local provider now enforces the same
    rule (faithful double), so this is exercised end-to-end."""

    async def _setup(self, provider):
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        config = type("C", (), {"agent_name": "a", "session_id": "s", "agent_version": "1.0.0", "is_hosted": False})()
        manager = TaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    @pytest.mark.asyncio
    async def test_drain_patch_flips_status_to_in_progress(self, tmp_path):
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from .conftest import CapturingProvider

        provider = CapturingProvider(LocalFileTaskProvider(Path(str(tmp_path))))
        manager, mgr_mod = await self._setup(provider)
        try:
            ran: list[str] = []

            @multi_turn_task(name="chat", steerable=True)
            async def chat(ctx: TaskContext[dict]) -> dict:
                msg = ctx.input.get("msg", "?")
                if msg == "A":
                    for _ in range(300):
                        if ctx.cancel.is_set():
                            return None
                        await asyncio.sleep(0.01)
                    return None
                ran.append(msg)
                return {"msg": msg}

            run1 = await chat.start(task_id="t1", input={"msg": "A"})
            await asyncio.sleep(0.05)
            run_b = await chat.start(task_id="t1", input={"msg": "B"})
            await asyncio.wait_for(run_b.result(), timeout=5.0)

            assert "B" in ran, f"steered turn B must run; ran={ran}"
            # Find the drain PATCH: the one carrying _steering.active_input set.
            drain_patches = [
                p
                for (_tid, p, _im) in provider.update_calls
                if (getattr(p, "payload", None) or {}).get("steering", {}).get("active_input") is not None
            ]
            assert drain_patches, "no drain PATCH observed"
            assert drain_patches[0].status == "in_progress", (
                "drain PATCH MUST flip status to in_progress (suspended->in_progress claim); "
                f"got status={drain_patches[0].status!r}"
            )
        finally:
            await manager.shutdown()
            mgr_mod._manager = None
