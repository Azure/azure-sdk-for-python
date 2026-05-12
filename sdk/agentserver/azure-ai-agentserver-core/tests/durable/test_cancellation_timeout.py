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
    TaskTerminated,
    durable_task,
)


class _ManagerFixture:
    """Helper to set up a DurableTaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
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

            @durable_task(
                name="timeout_coop",
                timeout=timedelta(seconds=0.2),
                cancel_grace_seconds=5.0,
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
    async def test_timeout_hard_cancel(self, tmp_path):
        """Task that ignores cooperative cancel gets hard-cancelled."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(
                name="timeout_hard",
                timeout=timedelta(seconds=0.1),
                cancel_grace_seconds=0.1,
            )
            async def stubborn_task(ctx: TaskContext[Any]) -> str:
                # Ignore cooperative cancel, just sleep forever
                await asyncio.sleep(100)
                return "never"

            run = await stubborn_task.start(task_id=uuid.uuid4().hex, input=None)
            with pytest.raises(TaskTerminated):
                await run.result()
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_no_timeout_regression(self, tmp_path):
        """Task without timeout runs normally to completion."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="no_timeout")
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
    """Verify TaskRun.terminate() forces failure."""

    @pytest.mark.asyncio
    async def test_terminate_raises_task_terminated(self, tmp_path):
        """terminate() causes result() to raise TaskTerminated."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="terminatable")
            async def long_task(ctx: TaskContext[Any]) -> str:
                await asyncio.sleep(100)
                return "never"

            run = await long_task.start(task_id=uuid.uuid4().hex, input=None)
            await asyncio.sleep(0.05)  # let it start

            await run.terminate()
            with pytest.raises(TaskTerminated):
                await run.result()
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_terminate_sets_failure_status(self, tmp_path):
        """Terminated task is stored as failed (not in_progress)."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="term_status", ephemeral=False)
            async def long_task(ctx: TaskContext[Any]) -> str:
                await asyncio.sleep(100)
                return "never"

            task_id = uuid.uuid4().hex
            run = await long_task.start(task_id=task_id, input=None)
            await asyncio.sleep(0.05)

            await run.terminate()
            with pytest.raises(TaskTerminated):
                await run.result()

            # Give manager time to persist failure
            await asyncio.sleep(0.1)

            info = await manager.provider.get(task_id)
            assert info is not None
            # Failures are stored as "completed" with an error dict
            assert info.status == "completed"
            assert info.error is not None
            assert info.error["type"] == "TaskTerminated"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_cancel_vs_terminate_distinction(self, tmp_path):
        """Cooperative cancel (ctx.cancel) raises TaskCancelled, not TaskTerminated."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._exceptions import TaskCancelled

            @durable_task(name="cancel_test")
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

    @pytest.mark.asyncio
    async def test_terminate_reason_propagated(self, tmp_path):
        """Terminate reason is propagated to TaskTerminated exception."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="term_reason_task")
            async def slow_task(ctx: TaskContext[Any]) -> str:
                await asyncio.sleep(10)
                return "never"

            run = await slow_task.start(task_id=uuid.uuid4().hex, input=None)
            await asyncio.sleep(0.05)

            await run.terminate(reason="user requested stop")
            with pytest.raises(TaskTerminated) as exc_info:
                await run.result()
            assert exc_info.value.reason == "user requested stop"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)
