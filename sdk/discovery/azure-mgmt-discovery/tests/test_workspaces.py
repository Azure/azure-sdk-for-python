# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Workspaces operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Live resources used by read-only (list/get) tests. These exist in the test
# subscription and are only ever read, never mutated.
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_WORKSPACE_NAME = os.environ.get("DISCOVERY_WORKSPACE_NAME", "sanitized-workspace")

# Synthetic resource names used only by the write (create/update/delete) tests.
# Those tests are playback-only (enforced in conftest.py: they are skipped when
# AZURE_TEST_RUN_LIVE is set), so these values only ever appear in recorded
# requests and are never sent to a live endpoint.
WORKSPACE_RESOURCE_GROUP = "rgname"
WORKSPACE_NAME = "sanitized-workspace"


class TestWorkspaces(DiscoveryMgmtTestCase):
    """Tests for Workspaces operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
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
        workspaces = list(self.client.workspaces.list_by_resource_group(READ_RESOURCE_GROUP))
        assert isinstance(workspaces, list)
        assert len(workspaces) >= 1

    @recorded_by_proxy
    def test_get_workspace(self):
        """Test getting a specific workspace by name."""
        workspace = self.client.workspaces.get(READ_RESOURCE_GROUP, READ_WORKSPACE_NAME)
        assert workspace is not None
        # Don't assert on name since it may be sanitized in playback
        assert hasattr(workspace, "name")
        assert hasattr(workspace, "location")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_workspace(self):
        """Test creating a workspace."""
        workspace_name = "sanitized-workspace"
        workspace_data = models.Workspace(
            location="uksouth",
            properties=models.WorkspaceProperties(
                supercomputer_ids=[],
                workspace_identity=models.Identity(
                    id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sanitized-identity"
                ),
                agent_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                private_endpoint_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                workspace_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                customer_managed_keys="Enabled",
                key_vault_properties=models.KeyVaultProperties(
                    key_name="discoverykey",
                    key_vault_uri="https://sanitized.vault.azure.net/",
                    key_version="2c9db3cf55d247b4a1c1831fbbdad906",
                ),
                log_analytics_cluster_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.OperationalInsights/clusters/sanitized-cluster",
                public_network_access="Disabled",
            ),
        )
        operation = self.client.workspaces.begin_create_or_update(
            resource_group_name="rgname",
            workspace_name=workspace_name,
            resource=workspace_data,
        )
        workspace = operation.result()
        assert workspace is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_update_workspace(self):
        """Test updating a workspace by changing the key vault key version."""
        # PATCH the workspace with the new key version
        update_data = models.Workspace(
            properties=models.WorkspaceProperties(
                key_vault_properties=models.KeyVaultProperties(
                    key_name="discoverykey",
                    key_version="956de2fc802f49eba81ddcc348ebc27c",
                ),
            ),
        )
        operation = self.client.workspaces.begin_update(
            resource_group_name=self.resource_group,
            workspace_name=WORKSPACE_NAME,
            properties=update_data,
        )
        updated_workspace = operation.result()
        assert updated_workspace is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_workspace(self):
        """Test deleting a workspace."""
        operation = self.client.workspaces.begin_delete(
            resource_group_name="rgname",
            workspace_name="sanitized-workspace",
        )
        operation.result()
