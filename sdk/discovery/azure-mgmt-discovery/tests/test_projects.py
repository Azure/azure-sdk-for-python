# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Projects operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


# Resource group that has a workspace
WORKSPACE_RESOURCE_GROUP = "newapiversiontest"
WORKSPACE_NAME = "wrksptest44"


class TestProjects(DiscoveryMgmtTestCase):
    """Tests for Projects operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME

    @recorded_by_proxy
    def test_list_projects_by_workspace(self):
        """Test listing projects in a workspace."""
        projects = list(self.client.projects.list_by_workspace(self.resource_group, self.workspace_name))
        assert isinstance(projects, list)

    @pytest.mark.skip(reason="Requires existing project in the workspace")
    @recorded_by_proxy
    def test_get_project(self):
        """Test getting a specific project by name."""
        # TODO: Replace with actual project name from test environment
        project = self.client.projects.get(self.resource_group, self.workspace_name, "test-project")
        assert project is not None
        assert hasattr(project, "name")
        assert hasattr(project, "location")

    @pytest.mark.skip(reason="Requires proper ProjectProperties configuration")
    @recorded_by_proxy
    def test_create_project(self):
        """Test creating a project."""
        project_data = {"location": "centraluseuap"}
        operation = self.client.projects.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            project_name="test-project",
            resource=project_data,
        )
        project = operation.result()
        assert project is not None

    @pytest.mark.skip(reason="Requires existing project with properties that can be updated")
    @recorded_by_proxy
    def test_update_project(self):
        """Test updating a project."""
        project_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.projects.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            project_name="test-project",
            resource=project_data,
        )
        updated_project = operation.result()
        assert updated_project is not None

    @pytest.mark.skip(reason="Requires existing project to delete")
    @recorded_by_proxy
    def test_delete_project(self):
        """Test deleting a project."""
        operation = self.client.projects.begin_delete(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            project_name="project-to-delete",
        )
        operation.result()
