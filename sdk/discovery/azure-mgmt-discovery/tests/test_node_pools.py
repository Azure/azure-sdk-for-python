# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for NodePools operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group and supercomputer used by the playback-only write tests.
NODE_POOL_RESOURCE_GROUP = "rgname"
NODE_POOL_SUPERCOMPUTER_NAME = "sanitized-supercomputer"
NODE_POOL_NAME = "sanitized-nodepool"

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_SUPERCOMPUTER_NAME = os.environ.get("DISCOVERY_SUPERCOMPUTER_NAME", "sanitized-supercomputer")
READ_NODE_POOL_NAME = os.environ.get("DISCOVERY_NODE_POOL_NAME", "sanitized-nodepool")


class TestNodePools(DiscoveryMgmtTestCase):
    """Tests for NodePools operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = NODE_POOL_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_node_pools_by_supercomputer(self):
        """Test listing node pools in a supercomputer."""
        node_pools = list(self.client.node_pools.list_by_supercomputer(READ_RESOURCE_GROUP, READ_SUPERCOMPUTER_NAME))
        assert isinstance(node_pools, list)

    @recorded_by_proxy
    def test_get_node_pool(self):
        """Test getting a specific node pool by name."""
        node_pool = self.client.node_pools.get(READ_RESOURCE_GROUP, READ_SUPERCOMPUTER_NAME, READ_NODE_POOL_NAME)
        assert node_pool is not None
        assert hasattr(node_pool, "name")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_node_pool(self):
        """Test creating a node pool."""
        node_pool_data = models.NodePool(
            location="uksouth",
            properties=models.NodePoolProperties(
                subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                vm_size="Standard_D4s_v6",
                max_node_count=3,
                min_node_count=1,
                scale_set_priority="Regular",
            ),
        )
        operation = self.client.node_pools.begin_create_or_update(
            resource_group_name=NODE_POOL_RESOURCE_GROUP,
            supercomputer_name=NODE_POOL_SUPERCOMPUTER_NAME,
            node_pool_name=NODE_POOL_NAME,
            resource=node_pool_data,
        )
        node_pool = operation.result()
        assert node_pool is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_node_pool(self):
        """Test deleting a node pool."""
        operation = self.client.node_pools.begin_delete(
            resource_group_name=self.resource_group,
            supercomputer_name=NODE_POOL_SUPERCOMPUTER_NAME,
            node_pool_name=NODE_POOL_NAME,
        )
        operation.result()
