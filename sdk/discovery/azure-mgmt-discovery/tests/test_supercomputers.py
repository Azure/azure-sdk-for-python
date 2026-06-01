# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Supercomputers operations."""
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group that contains supercomputers
SUPERCOMPUTER_RESOURCE_GROUP = "olawal"


class TestSupercomputers(DiscoveryMgmtTestCase):
    """Tests for Supercomputers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
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
        mi_id = f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourcegroups/olawal/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myidentity"
        supercomputer_data = models.Supercomputer(
            location="uksouth",
            properties=models.SupercomputerProperties(
                subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/default",
                identities=models.SupercomputerIdentities(
                    cluster_identity=models.Identity(id=mi_id),
                    kubelet_identity=models.Identity(id=mi_id),
                    workload_identities={mi_id: models.UserAssignedIdentity()},
                ),
            ),
        )
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name="olawal",
            supercomputer_name="test-sc-2bbb25b8",
            resource=supercomputer_data,
        )
        supercomputer = operation.result()
        assert supercomputer is not None

    @pytest.mark.skip(reason="server returns 400 on supercomputer PATCH - service-side bug")
    @recorded_by_proxy
    def test_update_supercomputer(self):
        """Test updating a supercomputer."""
        supercomputer_data = models.Supercomputer(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        ) # type: ignore
        operation = self.client.supercomputers.begin_update(
            resource_group_name="olawal",
            supercomputer_name="test-sc-2bbb25b8",
            properties=supercomputer_data,
        )
        updated_supercomputer = operation.result()
        assert updated_supercomputer is not None

    @recorded_by_proxy
    def test_delete_supercomputer(self):
        """Test deleting a supercomputer."""
        operation = self.client.supercomputers.begin_delete(
            resource_group_name="olawal",
            supercomputer_name="test-sc-2bbb25b8",
        )
        operation.result()
