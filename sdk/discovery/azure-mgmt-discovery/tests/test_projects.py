# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Projects operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group and workspace used by the playback-only write tests.
WORKSPACE_RESOURCE_GROUP = "rgname"
WORKSPACE_NAME = "sanitized-workspace"
PROJECT_NAME = "sanitized-project"

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_WORKSPACE_NAME = os.environ.get("DISCOVERY_WORKSPACE_NAME", "sanitized-workspace")
READ_PROJECT_NAME = os.environ.get("DISCOVERY_PROJECT_NAME", "sanitized-project")


class TestProjects(DiscoveryMgmtTestCase):
    """Tests for Projects operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME

    @recorded_by_proxy
    def test_list_projects_by_workspace(self):
        """Test listing projects in a workspace."""
        projects = list(self.client.projects.list_by_workspace(READ_RESOURCE_GROUP, READ_WORKSPACE_NAME))
        assert isinstance(projects, list)

    @recorded_by_proxy
    def test_get_project(self):
        """Test getting a specific project by name."""
        project = self.client.projects.get(READ_RESOURCE_GROUP, READ_WORKSPACE_NAME, READ_PROJECT_NAME)
        assert project is not None
        assert hasattr(project, "name")
        assert hasattr(project, "location")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_project(self):
        """Test creating a project."""
        unique_name = PROJECT_NAME
        project_data = models.Project(location="uksouth", properties=models.ProjectProperties(storage_container_ids=[f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Discovery/storageContainers/sanitized-storagecontainer"]))  # type: ignore
        operation = self.client.projects.begin_create_or_update(
            resource_group_name=WORKSPACE_RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME,
            project_name=unique_name,
            resource=project_data,
        )
        project = operation.result()
        assert project is not None
