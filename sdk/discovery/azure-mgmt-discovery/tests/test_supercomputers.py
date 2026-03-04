# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Supercomputers operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase

# Resource group that contains supercomputers
SUPERCOMPUTER_RESOURCE_GROUP = "olawal"


class TestSupercomputers(DiscoveryMgmtTestCase):
    """Tests for Supercomputers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = SUPERCOMPUTER_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_supercomputers_by_resource_group(self):
        """Test listing supercomputers in a resource group."""
        supercomputers = list(self.client.supercomputers.list_by_resource_group(self.resource_group))
        assert isinstance(supercomputers, list)

    @recorded_by_proxy
    def test_list_supercomputers_by_subscription(self):
        """Test listing supercomputers in the subscription."""
        supercomputers = list(self.client.supercomputers.list_by_subscription())
        assert isinstance(supercomputers, list)
    @recorded_by_proxy
    def test_get_supercomputer(self):
        """Test getting a specific supercomputer by name."""
        supercomputer = self.client.supercomputers.get(self.resource_group, "test-sc-2bbb25b8")
        assert supercomputer is not None
        assert hasattr(supercomputer, "name")
        assert hasattr(supercomputer, "location")
    @recorded_by_proxy
    def test_create_supercomputer(self):
        """Test creating a supercomputer."""
        mi_id = "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourcegroups/olawal/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myidentity"
        supercomputer_data = {
            "location": "uksouth",
            "properties": {
                "subnetId": "/subscriptions/31b0b6a5-2647-47eb-8a38-7d12047ee8ec/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/default",
                "identities": {
                    "clusterIdentity": {"id": mi_id},
                    "kubeletIdentity": {"id": mi_id},
                    "workloadIdentities": {mi_id: {}}
                }
            }
        }
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name="olawal",
            supercomputer_name="test-sc-2bbb25b8",
            resource=supercomputer_data,
        )
        supercomputer = operation.result()
        assert supercomputer is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_update_supercomputer(self):
        """Test updating a supercomputer."""
        supercomputer_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name="test-supercomputer",
            resource=supercomputer_data,
        )
        updated_supercomputer = operation.result()
        assert updated_supercomputer is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_supercomputer(self):
        """Test deleting a supercomputer."""
        operation = self.client.supercomputers.begin_delete(
            resource_group_name="olawal",
            supercomputer_name="test-sc-497dd382",
        )
        operation.result()
