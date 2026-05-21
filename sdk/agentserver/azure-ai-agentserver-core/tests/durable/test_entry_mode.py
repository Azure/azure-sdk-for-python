# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for TaskContext.entry_mode across all lifecycle paths."""

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    TaskContext,
    durable_task,
)


class TestEntryMode:
    """Verify ctx.entry_mode is set correctly for each lifecycle path."""

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
    async def test_fresh_start_entry_mode(self, tmp_path) -> None:
        """First call to .run() produces entry_mode='fresh'."""
        observed_modes: list[str] = []

        @durable_task(title="test-fresh")
        async def my_task(ctx: TaskContext[str]) -> str:
            observed_modes.append(ctx.entry_mode)
            return "done"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="fresh-1", input="hello")
            assert result.output == "done"
            assert observed_modes == ["fresh"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_developer_resume_entry_mode(self, tmp_path) -> None:
        """Calling .run() on a suspended task produces entry_mode='resumed' with new input."""
        observed: list[tuple[str, str]] = []

        @durable_task(title="test-resume", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append((ctx.entry_mode, ctx.input))
            return await ctx.suspend(output={"partial": True})

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # First call — fresh start, suspends
            result1 = await my_task.run(task_id="resume-1", input="turn-1")
            assert result1.is_suspended
            assert observed == [("fresh", "turn-1")]

            # Second call — should resume with new input
            result2 = await my_task.run(task_id="resume-1", input="turn-2")
            assert result2.is_suspended
            assert observed[-1] == ("resumed", "turn-2")
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_platform_resume_entry_mode(self, tmp_path) -> None:
        """Platform-initiated resume (handle_resume) produces entry_mode='resumed'."""
        observed: list[str] = []

        @durable_task(title="test-platform-resume", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            return await ctx.suspend(output="waiting")

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            # Fresh start — suspends
            result = await my_task.run(task_id="platform-resume-1", input="init")
            assert result.is_suspended
            assert observed == ["fresh"]

            # Platform-initiated resume
            await manager.handle_resume("platform-resume-1")
            # Give the background task time to run
            import asyncio

            await asyncio.sleep(0.2)
            assert "resumed" in observed
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_recovered_entry_mode(self, tmp_path) -> None:
        """Calling .run() on a stale in_progress task produces entry_mode='recovered'."""
        observed: list[str] = []

        @durable_task(title="test-recover", ephemeral=False)
        async def my_task(ctx: TaskContext[str]) -> str:
            observed.append(ctx.entry_mode)
            return "recovered-ok"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            from azure.ai.agentserver.core.durable._models import (
                TaskCreateRequest,
            )

            # Manually create a stale in_progress task
            await manager.provider.create(
                TaskCreateRequest(
                    id="stale-1",
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title="stale-test",
                    payload={"input": "old-data"},
                )
            )

            # Backdate the updated_at to make it stale
            task_file = (
                Path(str(tmp_path)) / "test-agent" / "test-session" / "stale-1.json"
            )
            if task_file.exists():
                import json

                data = json.loads(task_file.read_text())
                data["updated_at"] = "2020-01-01T00:00:00+00:00"
                task_file.write_text(json.dumps(data))

            result = await my_task.run(
                task_id="stale-1",
                input="new-data",
                stale_timeout=1.0,
            )
            assert result.output == "recovered-ok"
            assert observed == ["recovered"]
        finally:
            await self._teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_ignoring_entry_mode_works(self, tmp_path) -> None:
        """A function that never reads entry_mode still works fine."""

        @durable_task(title="test-ignore")
        async def my_task(ctx: TaskContext[str]) -> str:
            # Deliberately NOT reading ctx.entry_mode
            return f"processed: {ctx.input}"

        manager, mgr_mod = await self._setup_manager(tmp_path)
        try:
            result = await my_task.run(task_id="ignore-1", input="data")
            assert result.output == "processed: data"
        finally:
            await self._teardown_manager(manager, mgr_mod)
