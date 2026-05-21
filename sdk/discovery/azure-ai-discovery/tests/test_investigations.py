# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Investigations operations.

Covers all 9 methods on WorkspaceClient.investigations:
  - get
  - create_or_replace, create_or_update
  - begin_delete (LRO)
  - list (Paged)
  - get_discovery_engine, get_discovery_engine_memory, update_discovery_engine
"""
import pytest
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.ai.discovery._workspace.azure.ai.discovery.models import Investigation, DiscoveryEngine, DiscoveryEngineUpdate
from .testcase import DiscoveryWorkspaceTestCase


class TestInvestigations(DiscoveryWorkspaceTestCase):
    """Tests for InvestigationsOperations."""

    @recorded_by_proxy
    def test_create_or_replace_new(self):
        """Test creating a new investigation via create_or_replace (PUT)."""
        client = self.create_workspace_client()
        investigation = client.investigations.create_or_replace(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            resource=Investigation(description="New investigation", display_name="New Test"),
        )
        assert investigation is not None
        assert investigation.description == "New investigation"
        assert investigation.display_name == "New Test"

    @recorded_by_proxy
    def test_list(self):
        client = self.create_workspace_client()
        investigations = list(client.investigations.list(project_name=self.project_name))
        assert isinstance(investigations, list)
        assert len(investigations) > 0
        for inv in investigations:
            assert inv.project_name == self.project_name
            assert inv.status is not None
            assert inv.created_at is not None

    @recorded_by_proxy
    def test_get(self):
        """Test getting a specific investigation."""
        client = self.create_workspace_client()
        investigation = client.investigations.get(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
        )
        assert investigation is not None
        assert investigation.project_name == self.project_name
        assert investigation.status is not None
        assert investigation.created_at is not None
        assert investigation.last_modified_at is not None

    @recorded_by_proxy
    def test_update_discovery_engine(self):
        """Test updating the discovery engine for an investigation."""
        client = self.create_workspace_client()
        engine = client.investigations.update_discovery_engine(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            body=DiscoveryEngineUpdate(discovery_engine_status="Active"),
        )
        assert engine is not None
        assert hasattr(engine, 'discovery_engine_status')

    @recorded_by_proxy
    def test_get_discovery_engine(self):
        """Test getting the discovery engine for an investigation."""
        client = self.create_workspace_client()
        engine = client.investigations.get_discovery_engine(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
        )
        assert engine is not None
        assert hasattr(engine, 'discovery_engine_status')

    @recorded_by_proxy
    def test_start_discovery_engine(self):
        """Test starting the discovery engine for an investigation."""
        client = self.create_workspace_client()
        # Discovery Engine requires at least one task in the investigation before starting
        from azure.ai.discovery._workspace.azure.ai.discovery.models import Task
        test_task = client.tasks.create(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            body=Task(title="test-task", description="Task for engine start test"),
        )
        # assert test_task is not None
        engine = client.investigations.start_discovery_engine(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
        )
        client.tasks.delete(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            task_name=test_task.name
        )
        assert engine is not None
        assert hasattr(engine, 'discovery_engine_status')

    @recorded_by_proxy
    def test_get_discovery_engine_memory(self):
        """Test getting the discovery engine working memory."""
        client = self.create_workspace_client()
        memory = client.investigations.get_discovery_engine_memory(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
        )
        assert memory is not None

    @recorded_by_proxy
    def test_stop_discovery_engine(self):
        """Test stopping the discovery engine for an investigation."""
        client = self.create_workspace_client()
        engine = client.investigations.stop_discovery_engine(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
        )
        assert engine is not None

    @recorded_by_proxy
    def test_create_or_replace_update(self):
        """Test updating an existing investigation via create_or_replace (PUT)."""
        client = self.create_workspace_client()
        investigation = client.investigations.create_or_replace(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            resource=Investigation(description="Updated via replace", display_name="updated-new-test"),
        )
        assert investigation is not None
        assert investigation.description == "Updated via replace"
        assert investigation.display_name == "updated-new-test"

    @recorded_by_proxy
    def test_create_or_update(self):
        """Test creating or updating (PATCH) an investigation."""
        client = self.create_workspace_client()
        investigation = client.investigations.create_or_update(
            project_name=self.project_name,
            investigation_name=self.investigation_name,
            resource=Investigation(description="Updated description", display_name="updated-test"),
        )
        assert investigation is not None
        assert investigation.description == "Updated description"

    @recorded_by_proxy
    def test_get_operation_status(self):
        """Test getting operation status for an investigation LRO.

        Creates a sacrificial investigation, starts its delete LRO without
        waiting, extracts the operation ID from the operation-location header,
        then checks the operation status.
        """
        client = self.create_workspace_client()

        # Create a sacrificial investigation to delete
        client.investigations.create_or_replace(
            project_name=self.project_name,
            investigation_name="test-op-status",
            resource=Investigation(
                description="Sacrificial investigation for getOperationStatus test",
                display_name="Op Status Test",
            ),
        )

        # Start delete LRO without waiting for completion
        poller = client.investigations.begin_delete(
            project_name=self.project_name,
            investigation_name="test-op-status",
            polling=False,
        )

        # Extract operation ID from the operation-location header
        initial_response = poller._polling_method._initial_response
        op_location = initial_response.http_response.headers.get("operation-location", "")
        operation_id = op_location.split("/operations/")[-1].split("?")[0]
        assert operation_id, "Could not extract operation_id from operation-location header"

        # Check the operation status
        status = client.investigations.get_operation_status(
            project_name=self.project_name,
            investigation_name="test-op-status",
            operation_id=operation_id,
        )
        assert status is not None
        assert status["status"] is not None

    @recorded_by_proxy
    def test_begin_delete(self):
        """Test deleting an investigation (LRO) and getting LRO status."""
        client = self.create_workspace_client()

        # Create a sacrificial investigation to delete
        client.investigations.create_or_replace(
            project_name=self.project_name,
            investigation_name="sdk-test-delete",
            resource=Investigation(
                description="Sacrificial investigation for delete test",
                display_name="Delete Status Test",
            ),
        )

        poller = client.investigations.begin_delete(
            project_name=self.project_name,
            investigation_name="sdk-test-delete",
        )
        poller.wait()
        assert poller.done()
        assert poller.status() == "Succeeded"
