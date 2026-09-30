# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Storage Assets operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase

# Resource group and storage container used by the playback-only write tests.
STORAGE_ASSET_RESOURCE_GROUP = "rgname"
STORAGE_ASSET_CONTAINER_NAME = "sanitized-storagecontainer"

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_STORAGE_CONTAINER_NAME = os.environ.get("DISCOVERY_STORAGE_CONTAINER_NAME", "sanitized-storagecontainer")
READ_STORAGE_ASSET_NAME = os.environ.get("DISCOVERY_STORAGE_ASSET_NAME", "sanitized-storageasset")


class TestStorageAssets(DiscoveryMgmtTestCase):
    """Tests for Storage Assets operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = STORAGE_ASSET_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_storage_assets_by_storage_container(self):
        """Test listing storage assets in a storage container."""
        assets = list(
            self.client.storage_assets.list_by_storage_container(READ_RESOURCE_GROUP, READ_STORAGE_CONTAINER_NAME)
        )
        assert isinstance(assets, list)

    @recorded_by_proxy
    def test_get_storage_asset(self):
        """Test getting a specific storage asset by name."""
        asset = self.client.storage_assets.get(
            READ_RESOURCE_GROUP, READ_STORAGE_CONTAINER_NAME, READ_STORAGE_ASSET_NAME
        )
        assert asset is not None
        assert hasattr(asset, "name")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_storage_asset(self):
        """Test creating a storage asset."""
        storage_container_name = "sanitized-storagecontainer"
        asset_data = models.StorageAsset(
            location="uksouth",
            properties=models.StorageAssetProperties(
                description="Test storage asset for SDK validation",
                path="data/test-assets",
            ),
        )
        operation = self.client.storage_assets.begin_create_or_update(
            resource_group_name="rgname",
            storage_container_name=storage_container_name,
            storage_asset_name="sanitized-storageasset",
            resource=asset_data,
        )
        asset = operation.result()
        assert asset is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_update_storage_asset(self):
        """Test updating a storage asset."""
        asset_data = models.StorageAsset(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        )
        operation = self.client.storage_assets.begin_update(
            resource_group_name="rgname",
            storage_container_name="sanitized-storagecontainer",
            storage_asset_name="sanitized-storageasset",
            properties=asset_data,
        )
        updated_asset = operation.result()
        assert updated_asset is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_storage_asset(self):
        """Test deleting a storage asset."""
        operation = self.client.storage_assets.begin_delete(
            resource_group_name="rgname",
            storage_container_name="sanitized-storagecontainer",
            storage_asset_name="sanitized-storageasset",
        )
        operation.result()
