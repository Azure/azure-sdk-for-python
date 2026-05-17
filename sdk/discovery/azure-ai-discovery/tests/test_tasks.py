# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Tasks operations.

Covers all 8 methods on WorkspaceClient.tasks:
  - get, create, update, delete
  - list (Paged)
  - start, add_comment, add_execution_history
"""
import json
from datetime import datetime, timezone

from devtools_testutils import recorded_by_proxy
from azure.core.rest import HttpRequest
from azure.ai.discovery._workspace.azure.ai.discovery.models import (
    Task,
    TaskAssignee,
    TaskComment,
    ExecutionHistoryEntry,
)
from .testcase import DiscoveryWorkspaceTestCase
from .constants import AGENT_NAME, investigation_path


class TestTasks(DiscoveryWorkspaceTestCase):
    """Tests for TasksOperations."""

    # ---- helpers ---------------------------------------------------------

    def _create_task(self, client, *, title="sdk-test-task", description="Test task for Python SDK"):
        """Create a task in the configured investigation and return it.

        Tests use the returned task's server-assigned `name` to address it
        in subsequent calls. This avoids hardcoded task IDs that go stale
        between runs.
        """
        investigation_id = investigation_path(self.project_name, self.investigation_name)
        return client.tasks.create(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            body=Task(
                title=title,
                priority="High",
                description=description,
                assigned_to=TaskAssignee(id=AGENT_NAME, type="Application"),
                investigation_id=investigation_id,
            ),
        )

    def _delete_task_quiet(self, client, task_name):
        """Best-effort cleanup; ignore failures so a single test failure
        doesn't cascade into teardown noise."""
        try:
            client.tasks.delete(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=task_name,
            )
        except Exception:
            pass

    # ---- tests -----------------------------------------------------------

    @recorded_by_proxy
    def test_list(self):
        """Test listing tasks in an investigation."""
        client = self.create_workspace_client()
        # Ensure at least one task exists so the assertion `len(tasks) > 0`
        # is meaningful regardless of investigation history.
        created = self._create_task(client, title="task-for-list-test")
        try:
            tasks = list(
                client.tasks.list(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                )
            )
            assert isinstance(tasks, list)
            assert len(tasks) > 0
            for t in tasks:
                assert t.title is not None
                assert t.status is not None
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_create(self):
        """Test creating a task in an investigation."""
        client = self.create_workspace_client()
        task = self._create_task(client, title="A new sdk task")
        try:
            assert task is not None
            assert task.title == "A new sdk task"
            assert task.description == "Test task for Python SDK"
        finally:
            self._delete_task_quiet(client, task.name)

    @recorded_by_proxy
    def test_get(self):
        """Test getting a specific task."""
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-get-test")
        try:
            task = client.tasks.get(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=created.name,
            )
            assert task is not None
            assert task.title == "task-for-get-test"
            assert task.status is not None
            assert task.created_at is not None
            assert task.assigned_to is not None
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_update(self):
        """Test updating a task (PATCH)."""
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-update-test")
        try:
            updated = client.tasks.update(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=created.name,
                resource=Task(
                    title="Updated sdk task title",
                    description="Updated sdk task description",
                ),
            )
            assert updated is not None
            assert updated.title == "Updated sdk task title"
            assert updated.description == "Updated sdk task description"
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_delete(self):
        """Test deleting a task."""
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-delete-test")
        status = client.tasks.delete(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            task_name=created.name,
        )
        # delete returns no content, so the SDK returns None on success
        assert status is None

    @recorded_by_proxy
    def test_list_with_filter(self):
        """Test listing tasks with a filter."""
        client = self.create_workspace_client()
        # Ensure at least one 'New' task exists so the filter has something
        # to match in deterministic replay.
        created = self._create_task(client, title="task-for-filter-test")
        try:
            tasks = list(
                client.tasks.list(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    filter="status eq 'New'",
                )
            )
            assert isinstance(tasks, list)
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_start(self):
        """Test starting execution of a task."""
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-start-test")
        try:
            task = client.tasks.start(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=created.name,
            )
            assert task is not None
            assert task.status is not None
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_add_comment(self):
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-comment-test")
        try:
            task = client.tasks.add_comment(
                task_name=created.name,
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                body=TaskComment(
                    timestamp=datetime(2026, 4, 8, 21, 0, 0, tzinfo=timezone.utc),
                    created_by="test-user",
                    created_by_type="User",
                    text="Test comment",
                ),
            )
            assert task is not None
            assert task.title is not None
        finally:
            self._delete_task_quiet(client, created.name)

    @recorded_by_proxy
    def test_add_execution_history(self):
        """Test adding an execution history entry to a task."""
        client = self.create_workspace_client()
        created = self._create_task(client, title="task-for-exec-history-test")
        try:
            task = client.tasks.add_execution_history(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=created.name,
                body=ExecutionHistoryEntry(
                    created_at=datetime(2026, 4, 8, 21, 0, 0, tzinfo=timezone.utc),
                    action="completed",
                    created_by=AGENT_NAME,
                    created_by_type="Application",
                    summary="Task execution completed",
                ),
            )
            assert task is not None
            assert task.title is not None
            assert task.status is not None
        finally:
            self._delete_task_quiet(client, created.name)