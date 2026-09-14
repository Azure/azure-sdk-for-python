# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Supercomputers operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group used by the playback-only write tests.
SUPERCOMPUTER_RESOURCE_GROUP = "rgname"

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_SUPERCOMPUTER_NAME = os.environ.get("DISCOVERY_SUPERCOMPUTER_NAME", "sanitized-supercomputer")


class TestSupercomputers(DiscoveryMgmtTestCase):
    """Tests for Supercomputers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = SUPERCOMPUTER_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_supercomputers_by_resource_group(self):
        """Test listing supercomputers in a resource group."""
        supercomputers = list(self.client.supercomputers.list_by_resource_group(READ_RESOURCE_GROUP))
        assert isinstance(supercomputers, list)

    @recorded_by_proxy
    def test_list_supercomputers_by_subscription(self):
        """Test listing supercomputers in the subscription."""
        supercomputers = list(self.client.supercomputers.list_by_subscription())
        assert isinstance(supercomputers, list)

    @recorded_by_proxy
    def test_get_supercomputer(self):
        """Test getting a specific supercomputer by name."""
        supercomputer = self.client.supercomputers.get(READ_RESOURCE_GROUP, READ_SUPERCOMPUTER_NAME)
        assert supercomputer is not None
        assert hasattr(supercomputer, "name")
        assert hasattr(supercomputer, "location")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_supercomputer(self):
        """Test creating a supercomputer."""
        mi_id = f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sanitized-identity"
        supercomputer_data = models.Supercomputer(
            location="uksouth",
            properties=models.SupercomputerProperties(
                subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                identities=models.SupercomputerIdentities(
                    cluster_identity=models.Identity(id=mi_id),
                    kubelet_identity=models.Identity(id=mi_id),
                    workload_identities={mi_id: models.UserAssignedIdentity()},
                ),
            ),
        )
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name="rgname",
            supercomputer_name="sanitized-supercomputer",
            resource=supercomputer_data,
        )
        supercomputer = operation.result()
        assert supercomputer is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_supercomputer(self):
        """Test deleting a supercomputer."""
        operation = self.client.supercomputers.begin_delete(
            resource_group_name="rgname",
            supercomputer_name="sanitized-supercomputer",
        )
        operation.result()
