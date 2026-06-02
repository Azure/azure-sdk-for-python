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
# Spec 016 FR-022 (US6): TaskTerminated removed from public __all__.
# Import via the internal _exceptions module for the absence-test below.
try:
    from azure.ai.agentserver.core.durable._exceptions import TaskTerminated  # noqa: F401 — retained for transitional internal-only use
except ImportError:
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
        """Spec 016 FR-022 (US6): TaskTerminated dropped from __all__."""
        from azure.ai.agentserver.core.durable import __all__ as durable_all

        assert "TaskTerminated" not in durable_all, (
            "Spec 016 FR-022: TaskTerminated removed from the public "
            "__all__ as part of the cancel-cause boolean rewrite."
        )
