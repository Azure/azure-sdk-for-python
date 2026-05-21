# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for DurableTask.get() method."""

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)


class TestGet:
    """Verify DurableTask.get() returns TaskInfo or None."""

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
    async def test_get_existing_task(self, tmp_path) -> None:
        """get() returns TaskInfo for an existing task."""

        @durable_task(title="get-test", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            return await ctx.suspend(output="paused")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="get-1", input="data")
            assert result.is_suspended

            info = await my_task.get("get-1")
            assert info is not None
            assert info.id == "get-1"
            assert info.status == "suspended"
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, tmp_path) -> None:
        """get() returns None for a non-existent task."""

        @durable_task(title="get-test")
        async def my_task(ctx: TaskContext[str]) -> str:
            return "ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            info = await my_task.get("does-not-exist")
            assert info is None
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_get_returns_correct_state(self, tmp_path) -> None:
        """get() returns correct info for various task states."""

        @durable_task(title="get-states", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            return await ctx.suspend(output="waiting")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Create tasks in different states via the provider
            from azure.ai.agentserver.core.durable._models import TaskCreateRequest

            await manager.provider.create(
                TaskCreateRequest(
                    id="state-suspended",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="suspended",
                    title="suspended-task",
                    payload={"output": "half-done"},
                )
            )
            await manager.provider.create(
                TaskCreateRequest(
                    id="state-completed",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="completed",
                    title="done-task",
                    payload={"output": "final"},
                )
            )
            await manager.provider.create(
                TaskCreateRequest(
                    id="state-in-progress",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="running-task",
                    payload={},
                )
            )

            suspended = await my_task.get("state-suspended")
            assert suspended is not None
            assert suspended.status == "suspended"

            completed = await my_task.get("state-completed")
            assert completed is not None
            assert completed.status == "completed"

            in_progress = await my_task.get("state-in-progress")
            assert in_progress is not None
            assert in_progress.status == "in_progress"
        finally:
            await self._teardown_manager(manager, mgr_mod)
