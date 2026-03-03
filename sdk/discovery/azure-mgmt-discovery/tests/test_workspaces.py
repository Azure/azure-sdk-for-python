# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Workspaces operations."""
import uuid
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


# Resource group and workspace that exist in the test environment
WORKSPACE_RESOURCE_GROUP = "olawal"
WORKSPACE_NAME = "wrksptest44"


class TestWorkspaces(DiscoveryMgmtTestCase):
    """Tests for Workspaces operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_workspaces_by_subscription(self):
        """Test listing workspaces in the subscription."""
        workspaces = list(self.client.workspaces.list_by_subscription())
        assert isinstance(workspaces, list)
        assert len(workspaces) >= 1

    @recorded_by_proxy
    def test_list_workspaces_by_resource_group(self):
        """Test listing workspaces in a resource group."""
        workspaces = list(self.client.workspaces.list_by_resource_group(self.resource_group))
        assert isinstance(workspaces, list)
        assert len(workspaces) >= 1

    @recorded_by_proxy
    def test_get_workspace(self):
        """Test getting a specific workspace by name."""
        workspace = self.client.workspaces.get(self.resource_group, WORKSPACE_NAME)
        assert workspace is not None
        # Don't assert on name since it may be sanitized in playback
        assert hasattr(workspace, "name")
        assert hasattr(workspace, "location")
    @recorded_by_proxy
    def test_create_workspace(self):
        """Test creating a workspace."""
        unique_name = f"test-wrksp-{uuid.uuid4().hex[:8]}"
        workspace_data = {
            "location": "uksouth",
            "properties": {
                "supercomputerIds": [
                    "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.Discovery/supercomputers/test-sc-2bbb25b8"
                ],
                "workspaceIdentity": {
                    "id": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourcegroups/olawal/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myidentity"
                },
                "agentSubnetId": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/workspace",
                "privateEndpointSubnetId": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/default",
                "workspaceSubnetId": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/default",
                "logAnalyticsClusterId": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.OperationalInsights/clusters/mycluse",
            }
        }
        operation = self.client.workspaces.begin_create_or_update(
            resource_group_name="olawal",
            workspace_name=unique_name,
            resource=workspace_data,
        )
        workspace = operation.result()
        assert workspace is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_update_workspace(self):
        """Test updating a workspace."""
        workspace = self.client.workspaces.get(self.resource_group, WORKSPACE_NAME)
        # Update with new tags
        workspace_data = {
            "location": workspace.location,
            "tags": {"updated": "true"},
        }
        operation = self.client.workspaces.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=WORKSPACE_NAME,
            resource=workspace_data,
        )
        updated_workspace = operation.result()
        assert updated_workspace is not None
    @recorded_by_proxy
    def test_delete_workspace(self):
        """Test deleting a workspace."""
        operation = self.client.workspaces.begin_delete(
            resource_group_name="olawal",
            workspace_name="test-wrksp-6055c323",
        )
        operation.result()
