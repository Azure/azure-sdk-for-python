# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the TaskResult wrapper class."""

import pytest

from azure.ai.agentserver.core.durable import TaskResult


class TestTaskResult:
    """Tests for TaskResult construction and properties."""

    def test_completed_result(self):
        """A completed result has is_completed=True, is_suspended=False."""
        r = TaskResult(task_id="t1", output="hello", status="completed")
        assert r.is_completed
        assert not r.is_suspended
        assert r.output == "hello"
        assert r.task_id == "t1"
        assert r.suspension_reason is None

    def test_suspended_result(self):
        """A suspended result has is_suspended=True, is_completed=False."""
        r = TaskResult(
            task_id="t2",
            output={"turn": 1},
            status="suspended",
            suspension_reason="awaiting_user",
        )
        assert r.is_suspended
        assert not r.is_completed
        assert r.output == {"turn": 1}
        assert r.suspension_reason == "awaiting_user"

    def test_suspended_without_output(self):
        """A suspended result can have no output (output=None)."""
        r = TaskResult(task_id="t3", status="suspended")
        assert r.is_suspended
        assert r.output is None
        assert r.suspension_reason is None

    def test_completed_with_none_output(self):
        """A completed result can return None explicitly."""
        r = TaskResult(task_id="t4", output=None, status="completed")
        assert r.is_completed
        assert r.output is None

    def test_completed_with_complex_output(self):
        """TaskResult works with dict outputs."""
        data = {"items": [1, 2, 3], "total": 3}
        r = TaskResult(task_id="t5", output=data, status="completed")
        assert r.output["items"] == [1, 2, 3]
        assert r.output["total"] == 3

    def test_repr_completed(self):
        """__repr__ shows status and output for completed results."""
        r = TaskResult(task_id="t6", output="done", status="completed")
        s = repr(r)
        assert "t6" in s
        assert "completed" in s
        assert "done" in s
        assert "suspension_reason" not in s

    def test_repr_suspended(self):
        """__repr__ includes suspension_reason when present."""
        r = TaskResult(
            task_id="t7", output=None, status="suspended", suspension_reason="waiting"
        )
        s = repr(r)
        assert "suspended" in s
        assert "waiting" in s

    def test_repr_truncates_long_output(self):
        """__repr__ truncates output longer than 60 chars."""
        long_val = "x" * 100
        r = TaskResult(task_id="t8", output=long_val, status="completed")
        s = repr(r)
        assert "..." in s
        assert len(s) < 200


class TestNestedTaskResultGuard:
    """Test that returning TaskResult from a task function raises TypeError."""

    @pytest.mark.asyncio
    async def test_returning_taskresult_raises_typeerror(self, tmp_path):
        """Task function that returns TaskResult directly gets TypeError."""
        import uuid
        from pathlib import Path
        from azure.ai.agentserver.core.durable import TaskContext, durable_task
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
                "agent_name": "test",
                "session_id": "test",
                "agent_version": "1.0.0",
                "is_hosted": False,
            },
        )()
        manager = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()

        try:
            from typing import Any
            from azure.ai.agentserver.core.durable import TaskContext

            @durable_task(name="bad_return")
            async def bad_task(ctx: TaskContext[Any]) -> Any:
                return TaskResult(
                    task_id=ctx.task_id, output="data", status="completed"
                )

            from azure.ai.agentserver.core.durable._exceptions import TaskFailed

            with pytest.raises(TaskFailed):
                await bad_task.run(task_id=uuid.uuid4().hex, input=None)

        finally:
            await manager.shutdown()
            mgr_mod._manager = None
