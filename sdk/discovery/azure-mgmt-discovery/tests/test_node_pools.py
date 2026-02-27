# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for NodePools operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


class TestNodePools(DiscoveryMgmtTestCase):
    """Tests for NodePools operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = AZURE_RESOURCE_GROUP

    @pytest.mark.skip(
        reason="supercomputers endpoint doesn't support 2026-02-01-preview API yet - needed for node pools"
    )
    @recorded_by_proxy
    def test_list_node_pools_by_supercomputer(self):
        """Test listing node pools in a supercomputer."""
        # TODO: Replace with actual supercomputer name
        supercomputer_name = "test-supercomputer"
        node_pools = list(self.client.node_pools.list_by_supercomputer(self.resource_group, supercomputer_name))
        assert isinstance(node_pools, list)

    @pytest.mark.skip(reason="Requires existing NodePool in the supercomputer")
    @recorded_by_proxy
    def test_get_node_pool(self):
        """Test getting a specific node pool by name."""
        supercomputer_name = "test-supercomputer"
        node_pool = self.client.node_pools.get(self.resource_group, supercomputer_name, "test-nodepool")
        assert node_pool is not None
        assert hasattr(node_pool, "name")

    @pytest.mark.skip(reason="Requires NodePoolProperties with VM size and network configuration")
    @recorded_by_proxy
    def test_create_node_pool(self):
        """Test creating a node pool."""
        supercomputer_name = "test-supercomputer"
        node_pool_data = {"location": "centraluseuap"}
        operation = self.client.node_pools.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name=supercomputer_name,
            node_pool_name="test-nodepool",
            resource=node_pool_data,
        )
        node_pool = operation.result()
        assert node_pool is not None

    @pytest.mark.skip(reason="Requires existing NodePool to update")
    @recorded_by_proxy
    def test_update_node_pool(self):
        """Test updating a node pool."""
        supercomputer_name = "test-supercomputer"
        node_pool_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.node_pools.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name=supercomputer_name,
            node_pool_name="test-nodepool",
            resource=node_pool_data,
        )
        updated_node_pool = operation.result()
        assert updated_node_pool is not None

    @pytest.mark.skip(reason="Requires existing NodePool to delete")
    @recorded_by_proxy
    def test_delete_node_pool(self):
        """Test deleting a node pool."""
        supercomputer_name = "test-supercomputer"
        operation = self.client.node_pools.begin_delete(
            resource_group_name=self.resource_group,
            supercomputer_name=supercomputer_name,
            node_pool_name="nodepool-to-delete",
        )
        operation.result()
