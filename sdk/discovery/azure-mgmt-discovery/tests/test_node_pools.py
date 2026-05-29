# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for NodePools operations."""
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group and supercomputer that contain node pools
NODE_POOL_RESOURCE_GROUP = "olawal"
NODE_POOL_SUPERCOMPUTER_NAME = "test-sc-2bbb25b8"
NODE_POOL_NAME = "nodepool1"


class TestNodePools(DiscoveryMgmtTestCase):
    """Tests for NodePools operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = NODE_POOL_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_node_pools_by_supercomputer(self):
        """Test listing node pools in a supercomputer."""
        node_pools = list(self.client.node_pools.list_by_supercomputer(NODE_POOL_RESOURCE_GROUP, NODE_POOL_SUPERCOMPUTER_NAME))
        assert isinstance(node_pools, list)

    @recorded_by_proxy
    def test_get_node_pool(self):
        """Test getting a specific node pool by name."""
        supercomputer_name = NODE_POOL_SUPERCOMPUTER_NAME
        node_pool = self.client.node_pools.get(self.resource_group, supercomputer_name, NODE_POOL_NAME)
        assert node_pool is not None
        assert hasattr(node_pool, "name")

    @recorded_by_proxy
    def test_create_node_pool(self):
        """Test creating a node pool."""
        node_pool_data = models.NodePool(
            location="uksouth",
            properties=models.NodePoolProperties(
                subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/olawal/providers/Microsoft.Network/virtualNetworks/newapiv/subnets/default",
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

    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_update_node_pool(self):
        """Test updating a node pool."""
        node_pool_data = models.NodePool(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        ) # type: ignore
        operation = self.client.node_pools.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name=NODE_POOL_SUPERCOMPUTER_NAME,
            node_pool_name=NODE_POOL_NAME,
            resource=node_pool_data,
        )
        updated_node_pool = operation.result()
        assert updated_node_pool is not None

    @recorded_by_proxy
    def test_delete_node_pool(self):
        """Test deleting a node pool."""
        operation = self.client.node_pools.begin_delete(
            resource_group_name=self.resource_group,
            supercomputer_name=NODE_POOL_SUPERCOMPUTER_NAME,
            node_pool_name=NODE_POOL_NAME,
        )
        operation.result()
