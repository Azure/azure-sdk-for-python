# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for StorageContainers operations."""
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group that contains storage containers
STORAGE_CONTAINER_RESOURCE_GROUP = "olawal"


class TestStorageContainers(DiscoveryMgmtTestCase):
    """Tests for StorageContainers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
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

    @recorded_by_proxy
    def test_get_storage_container(self):
        """Test getting a specific storage container by name."""
        container = self.client.storage_containers.get(self.resource_group, "test-sc-8bef0d1a")
        assert container is not None
        assert hasattr(container, "name")

    @recorded_by_proxy
    def test_create_storage_container(self):
        """Test creating a storage container."""
        container_data = models.StorageContainer(
            location="uksouth",
            properties=models.StorageContainerProperties(
                storage_store=models.AzureStorageBlobStore(
                    storage_account_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/olawal/providers/Microsoft.Storage/storageAccounts/mytststr",
                ),
            ),
        )
        operation = self.client.storage_containers.begin_create_or_update(
            resource_group_name="olawal",
            storage_container_name="test-sc-8bef0d1a",
            resource=container_data,
        )
        container = operation.result()
        assert container is not None

    @recorded_by_proxy
    def test_update_storage_container(self):
        """Test updating a storage container."""
        container_data = models.StorageContainer(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        )
        operation = self.client.storage_containers.begin_update(
            resource_group_name="olawal",
            storage_container_name="test-sc-8bef0d1a",
            properties=container_data,
        )
        updated_container = operation.result()
        assert updated_container is not None

    @recorded_by_proxy
    def test_delete_storage_container(self):
        """Test deleting a storage container."""
        operation = self.client.storage_containers.begin_delete(
            resource_group_name="olawal",
            storage_container_name="test-sc-8bef0d1a",
        )
        operation.result()
