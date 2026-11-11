# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async tests for Tasks operations.

Mirrors test_tasks.py against the async ``WorkspaceClient`` from
``azure.ai.discovery.aio``.
"""

from datetime import datetime, timezone

from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.discovery.models import (
    Task,
    TaskAssignee,
    TaskComment,
    ExecutionHistoryEntry,
)
from .testcase import DiscoveryWorkspaceTestCase
from .constants import AGENT_NAME, investigation_path


class TestTasksAsync(DiscoveryWorkspaceTestCase):
    """Async tests for TasksOperations."""

    # ---- helpers ---------------------------------------------------------

    async def _create_task(self, client, *, title="sdk-test-task", description="Test task for Python SDK (async)"):
        investigation_id = investigation_path(self.project_name, self.investigation_name)
        return await client.tasks.create(
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

    async def _delete_task_quiet(self, client, task_name):
        try:
            await client.tasks.delete(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=task_name,
            )
        except Exception:
            pass

    # ---- tests -----------------------------------------------------------

    @recorded_by_proxy_async
    async def test_list(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-list-test-async")
            try:
                tasks = []
                async for t in client.tasks.list(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                ):
                    tasks.append(t)
                assert len(tasks) > 0
                for t in tasks:
                    assert t.title is not None
                    assert t.status is not None
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_create(self):
        client = self.create_async_workspace_client()
        async with client:
            task = await self._create_task(client, title="A new sdk task (async)")
            try:
                assert task is not None
                assert task.title == "A new sdk task (async)"
                assert task.description == "Test task for Python SDK (async)"
            finally:
                await self._delete_task_quiet(client, task.name)

    @recorded_by_proxy_async
    async def test_get(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-get-test-async")
            try:
                task = await client.tasks.get(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    task_name=created.name,
                )
                assert task is not None
                assert task.title == "task-for-get-test-async"
                assert task.status is not None
                assert task.created_at is not None
                assert task.assigned_to is not None
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_stable_update(self):
        """Was ``tasks.update`` in beta; ``stable_update`` in GA."""
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-update-test-async")
            try:
                updated = await client.tasks.stable_update(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    task_name=created.name,
                    resource=Task(
                        title="Updated sdk task title (async)",
                        description="Updated sdk task description (async)",
                    ),
                )
                assert updated is not None
                assert updated.title == "Updated sdk task title (async)"
                assert updated.description == "Updated sdk task description (async)"
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_delete(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-delete-test-async")
            status = await client.tasks.delete(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=created.name,
            )
            assert status is None

    @recorded_by_proxy_async
    async def test_list_with_filter(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-filter-test-async")
            try:
                tasks = []
                async for t in client.tasks.list(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    filter="status eq 'New'",
                ):
                    tasks.append(t)
                # Filter results may be empty but the iteration must succeed.
                assert isinstance(tasks, list)
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_start(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-start-test-async")
            try:
                task = await client.tasks.start(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    task_name=created.name,
                )
                assert task is not None
                assert task.status is not None
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_add_comment(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-comment-test-async")
            try:
                task = await client.tasks.add_comment(
                    task_name=created.name,
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    body=TaskComment(
                        timestamp=datetime(2026, 4, 8, 21, 0, 0, tzinfo=timezone.utc),
                        created_by="test-user",
                        created_by_type="User",
                        text="Test comment (async)",
                    ),
                )
                assert task is not None
                assert task.title is not None
            finally:
                await self._delete_task_quiet(client, created.name)

    @recorded_by_proxy_async
    async def test_add_execution_history(self):
        client = self.create_async_workspace_client()
        async with client:
            created = await self._create_task(client, title="task-for-exec-history-test-async")
            try:
                task = await client.tasks.add_execution_history(
                    project_name=self.project_name,
                    investigation_name=self.investigation_name,
                    task_name=created.name,
                    body=ExecutionHistoryEntry(
                        created_at=datetime(2026, 4, 8, 21, 0, 0, tzinfo=timezone.utc),
                        action="completed",
                        created_by=AGENT_NAME,
                        created_by_type="Application",
                        summary="Task execution completed (async)",
                    ),
                )
                assert task is not None
                assert task.title is not None
                assert task.status is not None
            finally:
                await self._delete_task_quiet(client, created.name)
