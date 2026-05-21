# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for lifecycle-aware .run() and .start() on DurableTask."""

import json
from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)
from azure.ai.agentserver.core.durable._exceptions import TaskConflictError


class TestLifecycle:
    """Verify .run()/.start() lifecycle automation."""

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

    def _create_stale_task(self, tmp_path, task_id, status="in_progress"):
        """Write a stale task file directly to simulate a crashed task."""
        from azure.ai.agentserver.core.durable._models import (
            TaskCreateRequest,
        )
        import asyncio

        async def _create(provider):
            await provider.create(
                TaskCreateRequest(
                    id=task_id,
                    agent_name="test-agent",
                    session_id="test-session",
                    status=status,
                    title="stale-test",
                    payload={"input": "old-data"},
                )
            )

        return _create

    def _backdate_task(self, tmp_path, task_id):
        """Set updated_at far in the past."""
        task_file = (
            Path(str(tmp_path)) / "test-agent" / "test-session" / f"{task_id}.json"
        )
        if task_file.exists():
            data = json.loads(task_file.read_text())
            data["updated_at"] = "2020-01-01T00:00:00+00:00"
            task_file.write_text(json.dumps(data))

    @pytest.mark.asyncio
    async def test_run_fresh_no_existing_task(self, tmp_path) -> None:
        """run() on non-existent task → creates and starts, entry_mode='fresh'."""
        observed_mode: list[str] = []

        @durable_task(title="lifecycle-fresh")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "result"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="lc-fresh-1", input="data")
            assert result.output == "result"
            assert observed_mode == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_pending_task(self, tmp_path) -> None:
        """run() on pending task → starts it, entry_mode='fresh'."""
        observed_mode: list[str] = []

        @durable_task(title="lifecycle-pending")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "started"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-pending-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="pending",
                    title="pending-test",
                    payload={"input": "pending-data"},
                )
            )
            result = await my_task.run(task_id="lc-pending-1", input="new-data")
            assert result.output == "started"
            assert observed_mode == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_suspended_task(self, tmp_path) -> None:
        """run() on suspended task → resumes with new input, entry_mode='resumed'."""
        observed: list[tuple[str, str]] = []

        @durable_task(title="lifecycle-resume", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return await ctx.suspend(output="waiting")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result1 = await my_task.run(task_id="lc-resume-1", input="turn-1")
            assert result1.is_suspended
            assert observed[-1] == ("fresh", "turn-1")

            result2 = await my_task.run(task_id="lc-resume-1", input="turn-2")
            assert result2.is_suspended
            assert observed[-1] == ("resumed", "turn-2")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_in_progress_not_stale_raises(self, tmp_path) -> None:
        """run() on in_progress (not stale) task → TaskConflictError."""

        @durable_task(title="lifecycle-conflict")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "never"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-conflict-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="running-test",
                    payload={},
                )
            )
            with pytest.raises(TaskConflictError) as exc_info:
                await my_task.run(task_id="lc-conflict-1", input="data")
            assert exc_info.value.task_id == "lc-conflict-1"
            assert exc_info.value.current_status == "in_progress"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_stale_task_recovers(self, tmp_path) -> None:
        """run() on stale in_progress task → recovers, entry_mode='recovered'."""
        observed_mode: list[str] = []

        @durable_task(title="lifecycle-stale")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "recovered"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-stale-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="stale-test",
                    payload={"input": "old"},
                )
            )
            self._backdate_task(tmp_path, "lc-stale-1")

            result = await my_task.run(
                task_id="lc-stale-1",
                input="new",
                stale_timeout=1.0,
            )
            assert result.output == "recovered"
            assert observed_mode == ["recovered"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_run_completed_task_raises(self, tmp_path) -> None:
        """run() on completed task → TaskConflictError (no restart)."""

        @durable_task(title="lifecycle-completed")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "never"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-completed-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="completed",
                    title="done-test",
                    payload={"output": "final"},
                )
            )
            with pytest.raises(TaskConflictError) as exc_info:
                await my_task.run(task_id="lc-completed-1", input="data")
            assert exc_info.value.current_status == "completed"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_start_follows_lifecycle_rules(self, tmp_path) -> None:
        """start() follows same lifecycle rules as run() — fresh + conflict."""
        observed_mode: list[str] = []

        @durable_task(title="lifecycle-start")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_mode.append(ctx.entry_mode)
            return "started"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Fresh start via .start()
            handle = await my_task.start(task_id="lc-start-1", input="data")
            result = await handle.result()
            assert result.output == "started"
            assert observed_mode == ["fresh"]

            # Conflict: create in_progress task and try .start()
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-start-conflict",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="running",
                    payload={},
                )
            )
            with pytest.raises(TaskConflictError):
                await my_task.start(task_id="lc-start-conflict", input="data")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_stale_timeout_parameter(self, tmp_path) -> None:
        """stale_timeout controls when in_progress is considered stale."""

        @durable_task(title="stale-timeout")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="lc-timeout-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="timeout-test",
                    payload={"input": "old"},
                )
            )
            self._backdate_task(tmp_path, "lc-timeout-1")

            # Very large timeout → not stale → conflict
            with pytest.raises(TaskConflictError):
                await my_task.run(
                    task_id="lc-timeout-1",
                    input="new",
                    stale_timeout=999999999.0,
                )

            # Small timeout → stale → recover
            result = await my_task.run(
                task_id="lc-timeout-1",
                input="new",
                stale_timeout=1.0,
            )
            assert result.output == "ok"
        finally:
            await self._teardown_manager(manager, mgr_mod)
