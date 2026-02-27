# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Storage Assets operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


class TestStorageAssets(DiscoveryMgmtTestCase):
    """Tests for Storage Assets operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = AZURE_RESOURCE_GROUP

    @pytest.mark.skip(reason="No storage containers exist in test environment")
    @recorded_by_proxy
    def test_list_storage_assets_by_storage_container(self):
        """Test listing storage assets in a storage container."""
        # TODO: Replace with actual storage container name
        storage_container_name = "test-storage-container"
        assets = list(self.client.storage_assets.list_by_storage_container(self.resource_group, storage_container_name))
        assert isinstance(assets, list)

    @pytest.mark.skip(reason="Requires existing StorageContainer and StorageAsset")
    @recorded_by_proxy
    def test_get_storage_asset(self):
        """Test getting a specific storage asset by name."""
        storage_container_name = "test-storage-container"
        asset = self.client.storage_assets.get(self.resource_group, storage_container_name, "test-storage-asset")
        assert asset is not None
        assert hasattr(asset, "name")

    @pytest.mark.skip(reason="Requires StorageAssetProperties with path configuration")
    @recorded_by_proxy
    def test_create_storage_asset(self):
        """Test creating a storage asset."""
        storage_container_name = "test-storage-container"
        asset_data = {"location": "centraluseuap"}
        operation = self.client.storage_assets.begin_create_or_update(
            resource_group_name=self.resource_group,
            storage_container_name=storage_container_name,
            storage_asset_name="test-storage-asset",
            resource=asset_data,
        )
        asset = operation.result()
        assert asset is not None

    @pytest.mark.skip(reason="Requires existing StorageAsset to update")
    @recorded_by_proxy
    def test_update_storage_asset(self):
        """Test updating a storage asset."""
        storage_container_name = "test-storage-container"
        asset_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.storage_assets.begin_create_or_update(
            resource_group_name=self.resource_group,
            storage_container_name=storage_container_name,
            storage_asset_name="test-storage-asset",
            resource=asset_data,
        )
        updated_asset = operation.result()
        assert updated_asset is not None

    @pytest.mark.skip(reason="Requires existing StorageAsset to delete")
    @recorded_by_proxy
    def test_delete_storage_asset(self):
        """Test deleting a storage asset."""
        storage_container_name = "test-storage-container"
        operation = self.client.storage_assets.begin_delete(
            resource_group_name=self.resource_group,
            storage_container_name=storage_container_name,
            storage_asset_name="storage-asset-to-delete",
        )
        operation.result()
