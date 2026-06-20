# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Projects operations."""
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID


# Resource group that has a workspace
WORKSPACE_RESOURCE_GROUP = "aatte"
WORKSPACE_NAME = "itworkaawre"
PROJECT_NAME = "testproject1"


class TestProjects(DiscoveryMgmtTestCase):
    """Tests for Projects operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME

    @recorded_by_proxy
    def test_list_projects_by_workspace(self):
        """Test listing projects in a workspace."""
        projects = list(self.client.projects.list_by_workspace(WORKSPACE_RESOURCE_GROUP, WORKSPACE_NAME))
        assert isinstance(projects, list)

    @recorded_by_proxy
    def test_get_project(self):
        """Test getting a specific project by name."""
        project = self.client.projects.get(self.resource_group, self.workspace_name, PROJECT_NAME)
        assert project is not None
        assert hasattr(project, "name")
        assert hasattr(project, "location")

    @recorded_by_proxy
    def test_create_project(self):
        """Test creating a project."""
        unique_name = PROJECT_NAME
        project_data = models.Project(location="uksouth", properties = models.ProjectProperties(storage_container_ids=[f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/aatte/providers/Microsoft.Discovery/storageContainers/itsconaawre"])) # type: ignore
        operation = self.client.projects.begin_create_or_update(
            resource_group_name=WORKSPACE_RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            project_name=unique_name,
            resource=project_data,
        )
        project = operation.result()
        assert project is not None

    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_update_project(self):
        """Test updating a project."""
        project_data = models.Project(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        ) # type: ignore
        operation = self.client.projects.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            project_name=PROJECT_NAME,
            resource=project_data,
        )
        updated_project = operation.result()
        assert updated_project is not None

    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_project(self):
        """Test deleting a project."""
        operation = self.client.projects.begin_delete(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            project_name=PROJECT_NAME,
        )
        operation.result()
