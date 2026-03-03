# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for STAC Collection lifecycle operations (create, update, delete).
Note: These tests are marked with pytest.mark.live_test_only as they modify collections.
"""
import logging
import time
import pytest
from pathlib import Path
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import recorded_by_proxy, is_live
from testpreparer_async import PlanetaryComputerProClientTestBaseAsync
from testpreparer import PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    StacExtensionSpatialExtent,
    StacCollectionTemporalExtent,
    StacExtensionExtent,
)

# Set up test logger
test_logger = logging.getLogger("test_collection_lifecycle")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "collection_lifecycle_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerCollectionLifecycleAsync(
    PlanetaryComputerProClientTestBaseAsync
):
    """Test suite for STAC Collection lifecycle operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_01_begin_create_collection(self, planetarycomputer_endpoint):
        """
        Test creating a new STAC collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_begin_create_collection")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_collection_id = "test-collection-lifecycle"

        # Check if collection exists and delete it first
        try:
            existing_collection = await client.stac.get_collection(
                collection_id=test_collection_id
            )
            if existing_collection:
                test_logger.info(
                    f"Collection '{test_collection_id}' already exists, deleting first..."
                )
                delete_poller = await client.stac.begin_delete_collection(
                    collection_id=test_collection_id, polling=True
                )
                await delete_poller.result()
                test_logger.info(f"Deleted existing collection '{test_collection_id}'")
        except Exception:
            test_logger.info(
                f"Collection '{test_collection_id}' does not exist, proceeding with creation"
            )

        # Define collection extents
        spatial_extent = StacExtensionSpatialExtent(bounding_box=[[-180, -90, 180, 90]])
        temporal_extent = StacCollectionTemporalExtent(
            interval=[["2020-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]]
        )
        extent = StacExtensionExtent(spatial=spatial_extent, temporal=temporal_extent)

        # Create collection payload
        collection_data = {
            "id": test_collection_id,
            "description": "Test collection for lifecycle operations",
            "extent": extent.as_dict(),
            "license": "proprietary",
            "links": [],
            "stac_version": "1.0.0",
            "title": "Test Collection Lifecycle",
            "type": "Collection",
        }

        test_logger.info("Calling: begin_create_collection(body=collection_data)")
        create_poller = await client.stac.begin_create_collection(
            body=collection_data, polling=True
        )
        result = await create_poller.result()

        test_logger.info(f"Collection created: {result}")
        created_collection = await client.stac.get_collection(
            collection_id=test_collection_id
        )
        assert created_collection is not None
        assert created_collection.id == test_collection_id
        assert created_collection.title == "Test Collection Lifecycle"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_02_create_or_replace_collection(self, planetarycomputer_endpoint):
        """
        Test updating a collection using create or replace.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_create_or_replace_collection")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_collection_id = "test-collection-lifecycle"

        # Get existing collection
        collection = await client.stac.get_collection(collection_id=test_collection_id)

        # Update description
        collection.description = "Test collection for lifecycle operations - UPDATED"

        test_logger.info(
            f"Calling: create_or_replace_collection(collection_id='{test_collection_id}', body=collection)"
        )
        updated_collection = await client.stac.create_or_replace_collection(
            collection_id=test_collection_id, body=collection
        )

        test_logger.info(f"Collection updated: {updated_collection}")
        updated_collection = await client.stac.get_collection(
            collection_id=test_collection_id
        )
        assert (
            updated_collection.description
            == "Test collection for lifecycle operations - UPDATED"
        )

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_03_begin_delete_collection(self, planetarycomputer_endpoint):
        """
        Test deleting a STAC collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_begin_delete_collection")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_collection_id = "test-collection-lifecycle"

        test_logger.info(
            f"Calling: begin_delete_collection(collection_id='{test_collection_id}')"
        )
        delete_poller = await client.stac.begin_delete_collection(
            collection_id=test_collection_id, polling=True
        )
        result = await delete_poller.result()

        test_logger.info(f"Delete operation completed: {result}")

        try:
            await client.stac.get_collection(collection_id=test_collection_id)
            assert False, "Collection should have been deleted"
        except Exception as e:
            test_logger.info(f"Collection successfully deleted (404 expected): {e}")
            assert (
                "404" in str(e) or "Not Found" in str(e) or "ResourceNotFound" in str(e)
            )

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_04_create_collection_asset(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating a collection asset.
        Note: This test uses the existing test collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_create_collection_asset")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Create a simple text file asset
        from io import BytesIO

        # Delete the asset if it already exists
        try:
            test_logger.info(
                "Checking if asset 'test-asset' already exists and deleting if found..."
            )
            await client.stac.delete_collection_asset(
                collection_id=planetarycomputer_collection_id, asset_id="test-asset"
            )
            test_logger.info("Deleted existing 'test-asset'")
        except Exception as e:
            if (
                "404" in str(e)
                or "Not Found" in str(e)
                or "not found" in str(e).lower()
            ):
                test_logger.info(
                    "Asset 'test-asset' does not exist, proceeding with creation"
                )
            else:
                test_logger.warning(f"Error checking/deleting asset: {e}")

        asset_data = {
            "key": "test-asset",
            "href": "https://example.com/test-asset.txt",
            "type": "text/plain",
            "roles": ["metadata"],
            "title": "Test Asset",
        }

        file_content = BytesIO(b"Test asset content")
        file_tuple = ("test-asset.txt", file_content)

        test_logger.info(
            f"Calling: create_collection_asset(collection_id='{planetarycomputer_collection_id}', body={{...}})"
        )
        response = await client.stac.create_collection_asset(
            collection_id=planetarycomputer_collection_id,
            body={"data": asset_data, "file": file_tuple},
        )

        test_logger.info(f"Response: {response}")
        assert response is not None

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_05_replace_collection_asset(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating or replacing a collection asset.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_replace_collection_asset")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from io import BytesIO

        asset_data = {
            "key": "test-asset",
            "href": "https://example.com/test-asset-updated.txt",
            "type": "text/plain",
            "roles": ["metadata"],
            "title": "Test Asset - Updated",
        }

        file_content = BytesIO(b"Test asset content - updated")
        file_tuple = ("test-asset.txt", file_content)

        test_logger.info(
            f"Calling: create_or_replace_collection_asset(collection_id='{planetarycomputer_collection_id}', asset_id='test-asset', body={{...}})"
        )
        response = await client.stac.replace_collection_asset(
            collection_id=planetarycomputer_collection_id,
            asset_id="test-asset",
            body={"data": asset_data, "file": file_tuple},
        )

        test_logger.info(f"Response: {response}")
        assert response is not None

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_06_delete_collection_asset(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test deleting a collection asset.
        First creates an asset specifically for deletion.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_delete_collection_asset")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Create an asset to be deleted using create_collection_asset first
        test_logger.info("Creating asset for deletion: test-asset-to-be-deleted")

        # First create the asset
        from io import BytesIO

        file_content = BytesIO(b"Test asset content for deletion")

        # Prepare data and file tuple for multipart form
        data = {
            "key": "test-asset-to-be-deleted",
            "href": "https://example.com/test-asset-to-delete.txt",
            "type": "text/plain",
            "roles": ["metadata"],
            "title": "Test Asset To Be Deleted",
        }
        file_tuple = ("test-asset-to-delete.txt", file_content)

        await client.stac.create_collection_asset(
            collection_id=planetarycomputer_collection_id,
            body={"data": data, "file": file_tuple},
        )
        test_logger.info("Asset created successfully")

        # Now delete it
        test_logger.info(
            f"Calling: delete_collection_asset(collection_id='{planetarycomputer_collection_id}', asset_id='test-asset-to-be-deleted')"
        )
        await client.stac.delete_collection_asset(
            collection_id=planetarycomputer_collection_id,
            asset_id="test-asset-to-be-deleted",
        )

        test_logger.info("Asset deleted successfully")

        # Verify deletion by checking collection assets
        collection = await client.stac.get_collection(
            collection_id=planetarycomputer_collection_id
        )
        if hasattr(collection, "assets") and collection.assets:
            assert (
                "test-asset-to-be-deleted" not in collection.assets
            ), "Asset should have been deleted"

        test_logger.info("Test PASSED\n")

        await self.close_client()
