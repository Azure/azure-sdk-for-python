# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for StorageContainers operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_SUBSCRIPTION_ID

# Resource group used by the playback-only write tests.
STORAGE_CONTAINER_RESOURCE_GROUP = "rgname"

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_STORAGE_CONTAINER_NAME = os.environ.get("DISCOVERY_STORAGE_CONTAINER_NAME", "sanitized-storagecontainer")


class TestStorageContainers(DiscoveryMgmtTestCase):
    """Tests for StorageContainers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = STORAGE_CONTAINER_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_storage_containers_by_resource_group(self):
        """Test listing storage containers in a resource group."""
        containers = list(self.client.storage_containers.list_by_resource_group(READ_RESOURCE_GROUP))
        assert isinstance(containers, list)

    @recorded_by_proxy
    def test_list_storage_containers_by_subscription(self):
        """Test listing storage containers in the subscription."""
        containers = list(self.client.storage_containers.list_by_subscription())
        assert isinstance(containers, list)

    @recorded_by_proxy
    def test_get_storage_container(self):
        """Test getting a specific storage container by name."""
        container = self.client.storage_containers.get(READ_RESOURCE_GROUP, READ_STORAGE_CONTAINER_NAME)
        assert container is not None
        assert hasattr(container, "name")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_storage_container(self):
        """Test creating a storage container."""
        container_data = models.StorageContainer(
            location="uksouth",
            properties=models.StorageContainerProperties(
                storage_store=models.AzureStorageBlobStore(
                    storage_account_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Storage/storageAccounts/sanitizedstorage",
                ),
            ),
        )
        operation = self.client.storage_containers.begin_create_or_update(
            resource_group_name="rgname",
            storage_container_name="sanitized-storagecontainer",
            resource=container_data,
        )
        container = operation.result()
        assert container is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_update_storage_container(self):
        """Test updating a storage container."""
        container_data = models.StorageContainer(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        )
        operation = self.client.storage_containers.begin_update(
            resource_group_name="rgname",
            storage_container_name="sanitized-storagecontainer",
            properties=container_data,
        )
        updated_container = operation.result()
        assert updated_container is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_storage_container(self):
        """Test deleting a storage container."""
        operation = self.client.storage_containers.begin_delete(
            resource_group_name="rgname",
            storage_container_name="sanitized-storagecontainer",
        )
        operation.result()
