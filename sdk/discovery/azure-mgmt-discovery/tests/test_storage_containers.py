# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for StorageContainers operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase

# Resource group that contains storage containers
STORAGE_CONTAINER_RESOURCE_GROUP = "deray-private-test"


class TestStorageContainers(DiscoveryMgmtTestCase):
    """Tests for StorageContainers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = STORAGE_CONTAINER_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_storage_containers_by_resource_group(self):
        """Test listing storage containers in a resource group."""
        containers = list(self.client.storage_containers.list_by_resource_group(self.resource_group))
        assert isinstance(containers, list)

    @recorded_by_proxy
    def test_list_storage_containers_by_subscription(self):
        """Test listing storage containers in the subscription."""
        containers = list(self.client.storage_containers.list_by_subscription())
        assert isinstance(containers, list)

    @pytest.mark.skip(reason="Requires existing StorageContainer")
    @recorded_by_proxy
    def test_get_storage_container(self):
        """Test getting a specific storage container by name."""
        container = self.client.storage_containers.get(self.resource_group, "test-storage-container")
        assert container is not None
        assert hasattr(container, "name")

    @pytest.mark.skip(reason="Requires StorageContainerProperties with storage configuration")
    @recorded_by_proxy
    def test_create_storage_container(self):
        """Test creating a storage container."""
        container_data = {"location": "centraluseuap"}
        operation = self.client.storage_containers.begin_create_or_update(
            resource_group_name=self.resource_group,
            storage_container_name="test-storage-container",
            resource=container_data,
        )
        container = operation.result()
        assert container is not None

    @pytest.mark.skip(reason="Requires existing StorageContainer to update")
    @recorded_by_proxy
    def test_update_storage_container(self):
        """Test updating a storage container."""
        container_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.storage_containers.begin_create_or_update(
            resource_group_name=self.resource_group,
            storage_container_name="test-storage-container",
            resource=container_data,
        )
        updated_container = operation.result()
        assert updated_container is not None

    @pytest.mark.skip(reason="Requires existing StorageContainer to delete")
    @recorded_by_proxy
    def test_delete_storage_container(self):
        """Test deleting a storage container."""
        operation = self.client.storage_containers.begin_delete(
            resource_group_name=self.resource_group,
            storage_container_name="storage-container-to-delete",
        )
        operation.result()
