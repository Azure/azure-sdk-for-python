"""Tests for cancellation and timeout features (spec 005).

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

from azure.ai.agentserver.core.durable import (
    TaskContext,
    task,
)

# Spec 016 FR-022 + SC-014 (US6): TaskTerminated is REMOVED — importing
# it from the public package now raises ImportError (verified by
# test_task_terminated_removed_from_durable_package below). The legacy
# import line that used to live here is intentionally absent.
TaskTerminated = None  # type: ignore[assignment]


class _ManagerFixture:
    """Helper to set up a TaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            TaskManager,
        )

        import azure.ai.agentserver.core.durable._manager as mgr_mod

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

            @task(
                name="timeout_coop",
                timeout=timedelta(seconds=0.2),
            )
            async def slow_task(ctx: TaskContext[Any]) -> str:
                # Wait until cooperative cancel fires
                while not ctx.cancel.is_set():
                    await asyncio.sleep(0.01)
                cancel_observed.set()
                return "cooperated"

            run = await slow_task.start(task_id=uuid.uuid4().hex, input=None)
            result = await run.result()

            assert cancel_observed.is_set()
            assert result.output == "cooperated"
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
            assert result.output == "done"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Terminate tests
# ---------------------------------------------------------------------------


class TestTerminate:
    """Spec 016 FR-022 (US6): TaskRun.terminate() and TaskTerminated
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

        Spec 016 FR-022: terminate is removed; cooperative cancel via
        TaskRun.cancel() is the SINGLE 'stop this task' pathway. The
        handler chooses the terminal shape (here, raises
        asyncio.CancelledError which the framework maps to TaskCancelled).
        """
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._exceptions import TaskCancelled

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
        """Spec 016 FR-022 (US6): TaskRun.terminate is gone."""
        from azure.ai.agentserver.core.durable._run import TaskRun

        assert not hasattr(TaskRun, "terminate"), (
            "Spec 016 FR-022: TaskRun.terminate() MUST be removed. "
            "Use TaskRun.cancel() and let the handler choose the "
            "terminal shape via its reaction to ctx.cancel.is_set()."
        )

    def test_task_terminated_removed_from_durable_all(self) -> None:
        """Spec 016 FR-022 + SC-014 (US6): importing TaskTerminated from
        the public durable package raises ImportError (strict removal,
        not just __all__ absence).
        """
        import importlib

        durable_mod = importlib.import_module(
            "azure.ai.agentserver.core.durable"
        )
        assert not hasattr(durable_mod, "TaskTerminated"), (
            "Spec 016 SC-014: TaskTerminated MUST NOT be importable "
            "from azure.ai.agentserver.core.durable."
        )
        with pytest.raises(ImportError):
            # Explicit import binding — must raise ImportError per SC-014.
            from azure.ai.agentserver.core.durable import TaskTerminated  # noqa: F401, PLC0415


class TestExitForRecovery:
    """Spec 016 US8 / FR-027 / FR-028 / SC-015.

    ctx.exit_for_recovery() is the prescribed shutdown shape:
    - Callable only when ctx.shutdown.is_set() (else RuntimeError).
    - Flushes metadata, releases lease, leaves status in_progress.
    - Signals awaiters with TaskCancelled.
    - Preserves queued steering inputs.
    """

    @pytest.mark.asyncio
    async def test_exit_for_recovery_raises_outside_shutdown(self, tmp_path):
        """T094 (c) / FR-027: misuse outside shutdown raises RuntimeError."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._exceptions import TaskFailed

            @task(name="exit_misuse", ephemeral=False)
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
        """T094 (a) / FR-027 / SC-015: handler calls exit_for_recovery
        during shutdown. Stored status MUST remain in_progress; result
        future receives TaskCancelled."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._exceptions import TaskCancelled

            shutdown_triggered = asyncio.Event()

            @task(name="exit_shutdown", ephemeral=False)
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

            with pytest.raises(TaskCancelled):
                await asyncio.wait_for(run.result(), timeout=2.0)

            # Stored status MUST remain in_progress per FR-027(c).
            info = await manager.provider.get(task_id)
            assert info is not None
            assert info.status == "in_progress", (
                f"Spec 016 FR-027(c): status MUST remain in_progress; "
                f"got {info.status!r}"
            )
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    def test_exit_for_recovery_signature(self) -> None:
        """T095 / SC-015 / FR-027: inspect.signature contains only self."""
        import inspect

        sig = inspect.signature(TaskContext.exit_for_recovery)
        params = list(sig.parameters)
        assert params == ["self"], (
            f"Spec 016 FR-027: exit_for_recovery MUST take no parameters "
            f"other than self. Got {params}"
        )
