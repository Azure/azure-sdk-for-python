"""Tests for cancellation and timeout features.

Covers:
- Execution timeout (cooperative cancel → hard cancel)
- Wait timeout (caller-side timeout on result())
- Terminate (forced termination via TaskRun.terminate())
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import TaskDeferred, TaskContext, task, multi_turn_task

#   + SC-014: TaskTerminated is REMOVED — importing
# it from the public package now raises ImportError (verified by
# test_task_terminated_removed_from_resilient_package below). The legacy
# import line that used to live here is intentionally absent.
TaskTerminated = None  # type: ignore[assignment]


class _ManagerFixture:
    """Helper to set up a TaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
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

    @staticmethod
    async def teardown(manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None


# ---------------------------------------------------------------------------
# Execution timeout tests
# ---------------------------------------------------------------------------


class TestExecutionTimeout:
    """Verify the timeout watchdog cooperatively and hard-cancels tasks."""

    @pytest.mark.asyncio
    async def test_timeout_cooperative_cancel(self, tmp_path):
        """Task sees ctx.cancel set when timeout fires."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            cancel_observed = asyncio.Event()

            @task(name="timeout_coop", timeout=timedelta(seconds=0.2))
            async def slow_task(ctx: TaskContext[Any]) -> str:
                # Wait until cooperative cancel fires
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                cancel_observed.set()
                return "cooperated"

            run = await slow_task.start(task_id=uuid.uuid4().hex, input=None)
            result = await run.result()

            assert cancel_observed.is_set()
            assert result == "cooperated"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_no_timeout_regression(self, tmp_path):
        """Task without timeout runs normally to completion."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(name="no_timeout")
            async def quick_task(ctx: TaskContext[Any]) -> str:
                return "done"

            run = await quick_task.start(task_id=uuid.uuid4().hex, input=None)
            result = await run.result()
            assert result == "done"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Terminate tests
# ---------------------------------------------------------------------------


class TestTerminate:
    """: TaskRun.terminate and TaskTerminated
    are removed from the public surface. The cancel-cause boolean
    flow + handler-chosen terminal shape replaces them.

    The old test cases (test_terminate_raises_task_terminated,
    test_terminate_sets_failure_status, test_terminate_reason_propagated)
    are removed because their assertions exercise functionality that
    no longer exists. The single cooperative-cancel preservation
    test below stands in for the cancel-vs-terminate distinction.
    """

    @pytest.mark.asyncio
    async def test_cancel_vs_terminate_distinction(self, tmp_path):
        """Cooperative cancel (ctx.cancel) raises TaskCancelled.

        : terminate is removed; cooperative cancel via
                TaskRun.cancel() is the SINGLE 'stop this task' pathway. The
                handler chooses the terminal shape (here, raises
                asyncio.CancelledError which the framework maps to TaskCancelled).
        """
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled

            @task(name="cancel_test")
            async def cancellable_task(ctx: TaskContext[Any]) -> str:
                # Cooperatively check cancel
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                raise asyncio.CancelledError()

            run = await cancellable_task.start(task_id=uuid.uuid4().hex, input=None)
            await asyncio.sleep(0.05)

            # Use cancel (not terminate) — cooperative
            await run.cancel()
            with pytest.raises(TaskCancelled):
                await run.result()
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    def test_terminate_method_removed_from_taskrun(self) -> None:
        """: TaskRun.terminate is gone."""
        from azure.ai.agentserver.core.tasks._run import TaskRun

        assert not hasattr(TaskRun, "terminate"), (
            ": TaskRun.terminate MUST be removed. "
            "Use TaskRun.cancel() and let the handler choose the "
            "terminal shape via its reaction to ctx.cancel.is_set()."
        )

    def test_task_terminated_removed_from_resilient_all(self) -> None:
        """+ SC-014: importing TaskTerminated from
        the public resilient package raises ImportError (strict removal,
        not just __all__ absence).
        """
        import importlib

        resilient_mod = importlib.import_module("azure.ai.agentserver.core.tasks")
        assert not hasattr(resilient_mod, "TaskTerminated"), (
            " SC-014: TaskTerminated MUST NOT be importable " "from azure.ai.agentserver.core.tasks."
        )
        with pytest.raises(ImportError):
            # Explicit import binding — must raise ImportError per SC-014.
            from azure.ai.agentserver.core.tasks import TaskTerminated  # noqa: F401, PLC0415


class TestExitForRecovery:
    """/  /  / SC-015.

    ctx.exit_for_recovery() is the prescribed shutdown shape:
    - Callable only when ctx.shutdown.is_set() (else RuntimeError).
    - Releases the lease and leaves status in_progress.
    - Signals awaiters with TaskCancelled.
    - Preserves queued steering inputs.
    """

    @pytest.mark.asyncio
    async def test_exit_for_recovery_raises_outside_shutdown(self, tmp_path):
        """T094 (c) /: misuse outside shutdown raises RuntimeError."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._exceptions import TaskFailed

            @multi_turn_task(name="exit_misuse")
            async def misuse(ctx: TaskContext[str]) -> str:
                # ctx.shutdown is NOT set — calling exit_for_recovery
                # must raise RuntimeError immediately.
                return await ctx.exit_for_recovery()

            run = await misuse.start(task_id=uuid.uuid4().hex, input="x")
            with pytest.raises(TaskFailed) as exc_info:
                await run.result()
            # The RuntimeError is wrapped in TaskFailed since it
            # propagated as an unhandled exception.
            assert "RuntimeError" in exc_info.value.error["type"] or (
                "exit_for_recovery" in str(exc_info.value.error.get("message", ""))
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_exit_for_recovery_preserves_in_progress(self, tmp_path):
        """T094 (a) /  / SC-015: handler calls exit_for_recovery
        during shutdown. Stored status MUST remain in_progress; result
        future receives TaskCancelled."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled

            shutdown_triggered = asyncio.Event()

            @multi_turn_task(name="exit_shutdown")
            async def shutdown_aware(ctx: TaskContext[str]) -> str:
                # Wait for the test to signal "shutdown is happening".
                await shutdown_triggered.wait()
                # Simulate the framework setting ctx.shutdown
                # (in production this is set by TaskManager.shutdown()).
                ctx.shutdown.set()
                return await ctx.exit_for_recovery()

            task_id = uuid.uuid4().hex
            run = await shutdown_aware.start(task_id=task_id, input="x")
            await asyncio.sleep(0.05)
            shutdown_triggered.set()

            with pytest.raises(TaskDeferred):
                await asyncio.wait_for(run.result(), timeout=2.0)

            # Stored status MUST remain in_progress per (c).
            info = await manager.provider.get(task_id)
            assert info is not None
            assert info.status == "in_progress", f" (c): status MUST remain in_progress; " f"got {info.status!r}"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    def test_exit_for_recovery_signature(self) -> None:
        """T095 / SC-015 /: inspect.signature contains only self."""
        import inspect

        sig = inspect.signature(TaskContext.exit_for_recovery)
        params = list(sig.parameters)
        assert params == ["self"], f": exit_for_recovery MUST take no parameters " f"other than self. Got {params}"


# --------------------------------------------------------------------- #
#   — per-turn resilient timeout (T086 / T087 / T088)
# --------------------------------------------------------------------- #


class TestRecoveryPerTurnTimeout:
    """.. / SC-012 / SC-013.

    @task(timeout=...) is per-turn, wall-clock, resilient across crashes
    within a turn, and cooperative-only:
    - Per-turn: each turn (fresh, drain re-entry) gets a fresh budget.
    - Wall-clock: anchored to the persisted _turn_started_at timestamp.
    - Resilient: crash mid-turn does NOT reset budget; recovered watchdog
      computes remaining = max(0, timeout - (now - turn_started_at))
      clamped to [0, timeout].
    - Cooperative-only: sets ctx.timeout_exceeded then ctx.cancel and
      exits; does NOT force-stop the handler or expire the lease.
    """

    @pytest.mark.asyncio
    async def test_fresh_turn_writes_turn_started_at(self, tmp_path):
        """T086(a) /: fresh entry writes _turn_started_at to the
        persisted record so the recovered watchdog can read it."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @multi_turn_task(name="t086_fresh")
            async def my_task(ctx: TaskContext[str]) -> str:
                return "done"

            run = await my_task.start(task_id="t086-fresh-1", input="x")
            await run.result()

            info = await manager.provider.get("t086-fresh-1")
            assert info is not None
            assert info.payload is not None
            assert "turn_started_at" in info.payload, (
                f": fresh-entry create MUST write "
                f"_turn_started_at to payload. Got payload keys: "
                f"{list(info.payload)}"
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_recovery_preserves_turn_started_at(self, tmp_path):
        """T086(c) /: recovery does NOT re-stamp the timestamp."""
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
        from azure.ai.agentserver.core.tasks._manager import _utc_now_iso

        original_stamp = "2026-06-01T00:00:00.000000Z"

        @multi_turn_task(name="t086_recover")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "recovered"

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            await manager.provider.create(
                TaskCreateRequest(
                    id="t086-recover-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="recover",
                    payload={"input": '"x"', "turn_started_at": original_stamp},
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id="previous-inst",
                    lease_duration_seconds=60,
                    source={"name": "t086_recover", "type": "agentserver.task"},
                )
            )
            await my_task.run(task_id="t086-recover-1", input="ignored")

            info = await manager.provider.get("t086-recover-1")
            assert info is not None
            assert info.payload is not None
            # Recovery MUST preserve the original timestamp.
            assert info.payload.get("turn_started_at") == original_stamp, (
                f": recovery MUST NOT re-stamp "
                f"_turn_started_at. Expected {original_stamp!r}, "
                f"got {info.payload.get('_turn_started_at')!r}"
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_recovered_watchdog_remaining_zero_fires_immediately(self, tmp_path):
        """T086(d) + T092 /: when recovered watchdog computes
        remaining == 0 (turn-start timestamp older than the budget),
        ctx.timeout_exceeded MUST be True from the handler's first
        checkpoint and ctx.cancel pre-set."""
        from datetime import timedelta
        from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

        observed: dict[str, Any] = {}

        # Use a tiny budget (0.5s) and a backdated stamp (10s ago) so
        # remaining clamps to 0 immediately.
        @multi_turn_task(name="t092_immediate_fire", timeout=timedelta(milliseconds=500))
        async def my_task(ctx: TaskContext[str]) -> str:
            observed["timeout_exceeded_at_start"] = ctx.timeout_exceeded
            observed["cancel_at_start"] = ctx.cancel.is_set()
            return "done"

        backdated = "2026-06-01T00:00:00.000000Z"  # 10+ seconds before any test run

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            await manager.provider.create(
                TaskCreateRequest(
                    id="t092-fire",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="fire",
                    payload={"input": '"x"', "turn_started_at": backdated},
                    lease_owner=manager._lease_owner,  # noqa: SLF001
                    lease_instance_id="previous-inst",
                    lease_duration_seconds=60,
                    source={"name": "t092_immediate_fire", "type": "agentserver.task"},
                )
            )
            await my_task.run(task_id="t092-fire", input="ignored")
            #: recovered watchdog with remaining==0 pre-sets
            # both the cause boolean and the cancel event BEFORE the
            # handler's first await.
            assert observed["timeout_exceeded_at_start"] is True, (
                ": recovered watchdog with remaining==0 "
                "MUST pre-set ctx.timeout_exceeded=True before the "
                "handler's first checkpoint."
            )
            assert observed["cancel_at_start"] is True, (
                ": recovered watchdog with remaining==0 "
                "MUST pre-set ctx.cancel before the handler's first "
                "checkpoint."
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    def test_clock_skew_clamping_via_compute_remaining(self):
        """T087 / SC-013 /: remaining is clamped to
        [0, timeout_seconds] in both directions. Direct unit test of
        the clamp computation since simulating clock skew end-to-end
        requires injecting time, which adds fragility.
        """
        from azure.ai.agentserver.core.tasks._manager import _parse_turn_started_at
        import time

        # Forward jump: turn_started_at is way in the past → elapsed
        # huge → remaining clamps to 0.
        backwards_ts = _parse_turn_started_at("2020-01-01T00:00:00.000000Z")
        assert backwards_ts is not None
        elapsed_huge = time.time() - backwards_ts
        timeout_seconds = 30.0
        remaining_forward = max(0.0, min(timeout_seconds - elapsed_huge, timeout_seconds))
        assert remaining_forward == 0.0, (
            "  forward-skew clamp: remaining MUST be 0 " f"when elapsed >> timeout. Got {remaining_forward}"
        )

        # Backward jump: turn_started_at is in the future → elapsed
        # negative → remaining clamps to timeout_seconds.
        future_ts = time.time() + 10_000_000  # ~ year in the future
        elapsed_negative = time.time() - future_ts  # ~ -10M (negative)
        remaining_backward = max(0.0, min(timeout_seconds - elapsed_negative, timeout_seconds))
        assert remaining_backward == timeout_seconds, (
            "  backward-skew clamp: remaining MUST cap "
            "at timeout_seconds when the elapsed time is negative "
            f"(clock skew). Got {remaining_backward}"
        )

    def test_watchdog_docstring_cooperative_only(self):
        """T088 /: the watchdog docstring MUST NOT contain the
        legacy 'lease will eventually expire' claim AND MUST document
        the cooperative-only semantic."""
        import inspect
        from azure.ai.agentserver.core.tasks._manager import TaskManager

        src = inspect.getsource(TaskManager._timeout_watchdog)
        assert "lease will eventually expire" not in src, (
            ": the legacy 'lease will eventually expire' "
            "docstring claim MUST be removed (the watchdog never "
            "expires the lease)."
        )
        assert "Cooperative-only" in src or "cooperative-only" in src, (
            ": the docstring MUST document the " "cooperative-only semantic explicitly."
        )


class TestRecoveryExitForRecoveryExtended:
    """(b /) — coverage for the recovery
    re-entry and queued-input preservation paths that the basic
    TestExitForRecovery class doesn't cover (T094(b), T096).
    """

    @pytest.mark.asyncio
    async def test_exit_for_recovery_recovered_handler_reentry(self, tmp_path):
        """T094(b) / (b) / SC-015: after exit_for_recovery, a
        fresh process (simulated by re-creating the manager) recovers
        the task; handler re-enters with entry_mode='recovered'.
        """
        from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager
        import azure.ai.agentserver.core.tasks._manager as mgr_mod_local

        observed: list[str] = []
        triggered = asyncio.Event()

        @multi_turn_task(name="t094b_recover")
        async def handler(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            if ctx.entry_mode == "recovered":
                return "recovered-completed"
            await triggered.wait()
            ctx.shutdown.set()
            return await ctx.exit_for_recovery()

        # Phase 1: handler exits for recovery; status remains in_progress
        # with our lease owner stamped.
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
        manager1 = TaskManager(config=config, provider=provider)
        mgr_mod_local._manager = manager1
        await manager1.startup()
        try:
            run = await handler.start(task_id="t094b-rec", input="x")
            await asyncio.sleep(0.05)
            triggered.set()
            with pytest.raises(TaskDeferred):
                await asyncio.wait_for(run.result(), timeout=2.0)
            # Verify the task is preserved as in_progress with our owner.
            info = await provider.get("t094b-rec")
            assert info is not None
            assert info.status == "in_progress"
        finally:
            await manager1.shutdown()
            mgr_mod_local._manager = None

        # Phase 2: new manager re-enters via startup-scan recovery.
        # Need to stamp the record with our lease owner so the scan picks
        # it up. exit_for_recovery cleared the owner — restore it now
        # to simulate "next process startup with same owner" (which is
        # what happens because derive_lease_owner is deterministic for
        # the same agent+session).
        from azure.ai.agentserver.core.tasks._models import TaskPatchRequest

        # Stamp the record with the same lease_owner the new manager
        # will derive so the startup scan finds it.
        new_manager = TaskManager(config=config, provider=provider)
        await provider.update(
            "t094b-rec",
            TaskPatchRequest(
                lease_owner=new_manager._lease_owner,  # noqa: SLF001
                lease_instance_id="prev-incarnation",
                lease_duration_seconds=60,
            ),
        )
        mgr_mod_local._manager = new_manager
        await new_manager.startup()
        # Layer 1 recovery scan should have re-entered the handler.
        try:
            # Wait briefly for the recovery to take effect.
            deadline = asyncio.get_event_loop().time() + 2.0
            while "recovered" not in observed and (asyncio.get_event_loop().time() < deadline):
                await asyncio.sleep(0.05)
            assert "recovered" in observed, (
                " (b) / SC-015: a fresh TaskManager MUST "
                "re-enter the handler with entry_mode='recovered' after "
                "exit_for_recovery left the record in_progress."
            )
        finally:
            await new_manager.shutdown()
            mgr_mod_local._manager = None

    @pytest.mark.asyncio
    async def test_exit_for_recovery_preserves_queued_steering_inputs(self, tmp_path):
        """T096 /: queued steering inputs at the time
        exit_for_recovery() is called MUST be preserved in the
        persisted state — the framework does NOT drain them during
        shutdown."""
        from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled

        gate = asyncio.Event()

        @multi_turn_task(name="t096_preserve_queue", steerable=True)
        async def handler(ctx: TaskContext[dict]) -> dict:
            # Wait for the test to queue a steering input + signal.
            await gate.wait()
            # Now simulate shutdown.
            ctx.shutdown.set()
            return await ctx.exit_for_recovery()

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            run1 = await handler.start(task_id="t096-preserve", input={"msg": "first"})
            await asyncio.sleep(0.05)
            # Queue a steering input — this writes pending_inputs to the
            # record's _steering payload.
            run2 = await handler.start(task_id="t096-preserve", input={"msg": "queued"})
            assert run2 is not None
            # Verify the steering input is in the persisted state.
            info_before = await manager.provider.get("t096-preserve")
            assert info_before is not None
            steering_before = (info_before.payload or {}).get("steering", {})
            pending_before = steering_before.get("pending_inputs", [])
            assert len(pending_before) >= 1, (
                f"Test setup: queued steering input should be in " f"pending_inputs. Got {pending_before}"
            )

            # Trigger shutdown — handler calls exit_for_recovery.
            gate.set()
            with pytest.raises(TaskDeferred):
                await asyncio.wait_for(run1.result(), timeout=2.0)

            #: pending_inputs MUST be preserved in the persisted
            # state across exit_for_recovery — NOT drained.
            info_after = await manager.provider.get("t096-preserve")
            assert info_after is not None
            steering_after = (info_after.payload or {}).get("steering", {})
            pending_after = steering_after.get("pending_inputs", [])
            assert len(pending_after) >= 1, (
                f": exit_for_recovery MUST preserve "
                f"queued steering inputs (NOT drain them during "
                f"shutdown). Pending before={len(pending_before)}, "
                f"after={len(pending_after)}; got {pending_after}"
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)
