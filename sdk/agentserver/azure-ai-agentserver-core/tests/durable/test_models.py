# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for data models and exceptions."""

import pytest

from azure.ai.agentserver.core.durable._models import (
    TaskCreateRequest,
    TaskInfo,
    TaskPatchRequest,
)
from azure.ai.agentserver.core.durable._exceptions import (
    TaskCancelled,
    TaskFailed,
    TaskNotFound,
    TaskSuspended,
)


class TestTaskStatus:
    """Tests for TaskStatus literal type."""

    def test_valid_status_strings(self) -> None:
        """Valid status values are plain strings."""
        statuses = ["pending", "in_progress", "suspended", "completed"]
        for s in statuses:
            assert isinstance(s, str)


class TestTaskCreateRequest:
    """Tests for TaskCreateRequest."""

    def test_minimal(self) -> None:
        """Minimal request has required fields."""
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="sess",
            status="pending",
            payload={},
        )
        assert req.agent_name == "agent"
        assert req.status == "pending"

    def test_default_status(self) -> None:
        """Default status is 'pending'."""
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="sess",
        )
        assert req.status == "pending"

    def test_optional_fields_default_none(self) -> None:
        """Optional fields default to None."""
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="sess",
        )
        assert req.lease_owner is None
        assert req.lease_instance_id is None
        assert req.lease_duration_seconds is None
        assert req.id is None
        assert req.title is None


class TestTaskPatchRequest:
    """Tests for TaskPatchRequest."""

    def test_empty_patch(self) -> None:
        """An empty patch is valid."""
        patch = TaskPatchRequest()
        assert patch.status is None
        assert patch.payload is None
        assert patch.if_match is None

    def test_status_patch(self) -> None:
        """Patch can set status."""
        patch = TaskPatchRequest(status="in_progress")
        assert patch.status == "in_progress"


class TestExceptions:
    """Tests for custom durable task exceptions."""

    def test_task_failed_message(self) -> None:
        """TaskFailed stores task_id and error."""
        exc = TaskFailed("task-1", error={"message": "boom", "type": "ValueError"})
        assert exc.task_id == "task-1"
        assert "boom" in str(exc)
        assert exc.error["type"] == "ValueError"

    def test_task_suspended_reason(self) -> None:
        """TaskSuspended stores task_id and reason."""
        exc = TaskSuspended("task-2", reason="waiting for approval")
        assert exc.task_id == "task-2"
        assert "waiting for approval" in str(exc)

    def test_task_cancelled(self) -> None:
        """TaskCancelled stores task_id."""
        exc = TaskCancelled("task-3")
        assert exc.task_id == "task-3"
        assert "task-3" in str(exc)

    def test_task_not_found(self) -> None:
        """TaskNotFound stores task_id."""
        exc = TaskNotFound("task-123")
        assert exc.task_id == "task-123"
        assert "task-123" in str(exc)

    def test_exception_hierarchy(self) -> None:
        """All exceptions inherit from Exception."""
        assert issubclass(TaskFailed, Exception)
        assert issubclass(TaskSuspended, Exception)
        assert issubclass(TaskCancelled, Exception)
        assert issubclass(TaskNotFound, Exception)
