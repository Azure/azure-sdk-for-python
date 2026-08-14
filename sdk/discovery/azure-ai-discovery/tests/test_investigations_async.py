# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async tests for Investigations operations.

Mirrors test_investigations.py against the async ``WorkspaceClient`` from
``azure.ai.discovery.aio``.
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.discovery.models import (
    Investigation,
    DiscoveryEngineUpdate,
    Task,
)
from .testcase import DiscoveryWorkspaceTestCase


class TestInvestigationsAsync(DiscoveryWorkspaceTestCase):
    """Async tests for InvestigationsOperations."""

    @recorded_by_proxy_async
    async def test_create_or_replace_new(self):
        client = self.create_async_workspace_client()
        async with client:
            investigation = await client.investigations.create_or_replace(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                resource=Investigation(description="New investigation", display_name="New Test"),
            )
            assert investigation is not None
            assert investigation.description == "New investigation"
            assert investigation.display_name == "New Test"

    @recorded_by_proxy_async
    async def test_list(self):
        """``investigations.list`` returns ``PagedInvestigation``; iterate ``.value``."""
        client = self.create_async_workspace_client()
        async with client:
            page = await client.investigations.list(project_name=self.project_name)
            assert page.value is not None
            assert len(page.value) > 0
            for inv in page.value:
                assert inv.project_name == self.project_name
                assert inv.status is not None
                assert inv.created_at is not None

    @recorded_by_proxy_async
    async def test_get(self):
        client = self.create_async_workspace_client()
        async with client:
            investigation = await client.investigations.get(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
            )
            assert investigation is not None
            assert investigation.project_name == self.project_name
            assert investigation.status is not None
            assert investigation.created_at is not None
            assert investigation.last_modified_at is not None

    @recorded_by_proxy_async
    async def test_update_discovery_engine(self):
        # See sync test for explanation of why we use ``system_prompt`` and not
        # ``discovery_engine_status`` (the latter is not a field on the Update model).
        client = self.create_async_workspace_client()
        async with client:
            engine = await client.investigations.update_discovery_engine(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                body=DiscoveryEngineUpdate(system_prompt="Updated system prompt for test (async)"),
            )
            assert engine is not None
            assert hasattr(engine, "discovery_engine_status")

    @recorded_by_proxy_async
    async def test_get_discovery_engine(self):
        client = self.create_async_workspace_client()
        async with client:
            engine = await client.investigations.get_discovery_engine(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
            )
            assert engine is not None
            assert hasattr(engine, "discovery_engine_status")

    @recorded_by_proxy_async
    async def test_start_discovery_engine(self):
        client = self.create_async_workspace_client()
        async with client:
            test_task = await client.tasks.create(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                body=Task(title="test-task-async", description="Task for engine start test (async)"),
            )
            engine = await client.investigations.start_discovery_engine(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
            )
            await client.tasks.delete(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                task_name=test_task.name,
            )
            assert engine is not None
            assert hasattr(engine, "discovery_engine_status")

    @recorded_by_proxy_async
    async def test_get_discovery_engine_memory(self):
        client = self.create_async_workspace_client()
        async with client:
            memory = await client.investigations.get_discovery_engine_memory(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
            )
            assert memory is not None

    @recorded_by_proxy_async
    async def test_stop_discovery_engine(self):
        client = self.create_async_workspace_client()
        async with client:
            engine = await client.investigations.stop_discovery_engine(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
            )
            assert engine is not None

    @recorded_by_proxy_async
    async def test_create_or_replace_update(self):
        client = self.create_async_workspace_client()
        async with client:
            investigation = await client.investigations.create_or_replace(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                resource=Investigation(description="Updated via replace", display_name="updated-new-test"),
            )
            assert investigation is not None
            assert investigation.description == "Updated via replace"
            assert investigation.display_name == "updated-new-test"

    @recorded_by_proxy_async
    async def test_update(self):
        client = self.create_async_workspace_client()
        async with client:
            investigation = await client.investigations.update(
                project_name=self.project_name,
                investigation_name=self.investigation_name,
                resource=Investigation(description="Updated description", display_name="updated-test"),
            )
            assert investigation is not None
            assert investigation.description == "Updated description"

    @recorded_by_proxy_async
    async def test_get_operation_status(self):
        """Start a delete LRO without waiting, extract op id, query status."""
        client = self.create_async_workspace_client()
        async with client:
            await client.investigations.create_or_replace(
                project_name=self.project_name,
                investigation_name="test-op-status-async",
                resource=Investigation(
                    description="Sacrificial investigation for getOperationStatus test (async)",
                    display_name="Op Status Test Async",
                ),
            )

            poller = await client.investigations.begin_delete(
                project_name=self.project_name,
                investigation_name="test-op-status-async",
                polling=False,
            )
            initial_response = poller._polling_method._initial_response
            op_location = initial_response.http_response.headers.get("operation-location", "")
            operation_id = op_location.split("/operations/")[-1].split("?")[0]
            assert operation_id, "Could not extract operation_id from operation-location header"

            status = await client.investigations.get_operation_status(
                project_name=self.project_name,
                investigation_name="test-op-status-async",
                operation_id=operation_id,
            )
            assert status is not None
            assert status["status"] is not None

    @recorded_by_proxy_async
    async def test_begin_delete(self):
        client = self.create_async_workspace_client()
        async with client:
            await client.investigations.create_or_replace(
                project_name=self.project_name,
                investigation_name="sdk-test-delete-async",
                resource=Investigation(
                    description="Sacrificial investigation for delete test (async)",
                    display_name="Delete Status Test Async",
                ),
            )

            poller = await client.investigations.begin_delete(
                project_name=self.project_name,
                investigation_name="sdk-test-delete-async",
            )
            await poller.wait()
            assert poller.done()
            assert poller.status() == "Succeeded"
