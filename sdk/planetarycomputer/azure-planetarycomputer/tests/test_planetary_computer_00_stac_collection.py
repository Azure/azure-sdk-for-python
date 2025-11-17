# pylint: disable=line-too-long,useless-suppression,too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for STAC Collection operations.
"""

import logging
import time
import datetime
from pathlib import Path
from devtools_testutils import recorded_by_proxy, is_live
from testpreparer import PlanetaryComputerProClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    PartitionTypeScheme,
)

# Set up test logger
test_logger = logging.getLogger("test_stac_collection")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "stac_collection_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerStacCollection(PlanetaryComputerProClientTestBase):
    """Test suite for STAC Collection operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_list_collections(self, planetarycomputer_endpoint):
        """
        Test listing all STAC collections.

        Expected response:
        - Dictionary with 'collections' key
        - List of collection objects
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_list_collections")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Calling: list_collections()")
        response = client.stac.list_collections()

        test_logger.info(f"Response type: {type(response)}")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(
            response, "collections"
        ), "Response should have 'collections' attribute"

        collections = response.collections
        assert isinstance(
            collections, list
        ), f"Collections should be a list, got {type(collections)}"

        test_logger.info(f"Number of collections: {len(collections)}")

        if len(collections) > 0:
            first_collection = collections[0]
            test_logger.info(f"First collection ID: {first_collection.id}")
            test_logger.info(f"First collection title: {first_collection.title}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_get_conformance_class(self, planetarycomputer_endpoint):
        """
        Test getting STAC conformance classes.

        Expected response:
        - Dictionary with 'conformsTo' key
        - List of conformance URIs
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_get_conformance_class")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Calling: get_conformance_class()")
        response = client.stac.get_conformance_class()

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(
            response, "conforms_to"
        ), "Response should have 'conforms_to' attribute"

        conforms_to = response.conforms_to
        assert isinstance(
            conforms_to, list
        ), f"conformsTo should be a list, got {type(conforms_to)}"
        assert len(conforms_to) > 0, "Should have at least one conformance class"

        test_logger.info(f"Number of conformance classes: {len(conforms_to)}")
        for i, uri in enumerate(conforms_to[:5]):  # Log first 5
            test_logger.info(f"  {i + 1}. {uri}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_get_collection(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting a specific STAC collection.

        Expected response:
        - StacCollection object
        - Contains id, title, description, extent, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_collection")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_collection(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_collection(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Collection ID: {response.id}")
        test_logger.info(f"Collection Title: {response.title}")
        test_logger.info(f"Collection Description: {response.description[:100]}...")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert (
            response.id == planetarycomputer_collection_id
        ), "Collection ID should match requested ID"
        assert (
            response.title is not None and len(response.title) > 0
        ), "Collection should have a title"
        assert response.description is not None, "Collection should have a description"
        assert response.extent is not None, "Collection should have extent"
        assert response.license is not None, "Collection should have license"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_get_partition_type(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting partition type for a collection.

        Expected response:
        - PartitionType object
        - Contains scheme (e.g., NONE, YEAR, YEAR_MONTH)
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_get_partition_type")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_partition_type(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_partition_type(planetarycomputer_collection_id)

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Partition scheme: {response.scheme}")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, "scheme"), "Response should have 'scheme' attribute"
        assert response.scheme is not None, "Partition scheme should not be None"

        # Validate scheme is a valid PartitionTypeScheme
        valid_schemes = [s.value for s in PartitionTypeScheme]
        assert (
            response.scheme in valid_schemes
        ), f"Partition scheme should be one of {valid_schemes}"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_list_render_options(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test listing render options for a collection.

        Expected response:
        - List of RenderOption objects
        - Each has id, name, type, options, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_list_render_options")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: list_render_options(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.list_render_options(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Number of render options: {len(response)}")

        # Validate response structure
        assert isinstance(
            response, list
        ), f"Response should be a list, got {type(response)}"

        if len(response) > 0:
            first_option = response[0]
            test_logger.info(f"First render option ID: {first_option.id}")
            test_logger.info(f"First render option name: {first_option.name}")
            test_logger.info(f"First render option type: {first_option.type}")

            assert hasattr(first_option, "id"), "Render option should have 'id'"
            assert hasattr(first_option, "name"), "Render option should have 'name'"
            assert hasattr(first_option, "type"), "Render option should have 'type'"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_get_tile_settings(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting tile settings for a collection.

        Expected response:
        - TileSettings object
        - Contains max_items_per_tile, min_zoom, default_location
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_get_tile_settings")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_tile_settings(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_tile_settings(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")

        # Validate response structure
        assert response is not None, "Response should not be None"

        # Log available attributes
        if hasattr(response, "max_items_per_tile"):
            test_logger.info(f"Max items per tile: {response.max_items_per_tile}")
        if hasattr(response, "min_zoom"):
            test_logger.info(f"Min zoom: {response.min_zoom}")
        if hasattr(response, "default_location"):
            test_logger.info(f"Default location: {response.default_location}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_list_mosaics(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test listing mosaics for a collection.

        Expected response:
        - List of StacMosaic objects
        - Each has id, name, cql filter
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_07_list_mosaics")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: list_mosaics(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.list_mosaics(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Number of mosaics: {len(response)}")

        # Validate response structure
        assert isinstance(
            response, list
        ), f"Response should be a list, got {type(response)}"

        if len(response) > 0:
            first_mosaic = response[0]
            test_logger.info(f"First mosaic ID: {first_mosaic.id}")
            test_logger.info(f"First mosaic name: {first_mosaic.name}")

            assert hasattr(first_mosaic, "id"), "Mosaic should have 'id'"
            assert hasattr(first_mosaic, "name"), "Mosaic should have 'name'"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_08_get_collection_queryables(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting queryables for a collection.

        Expected response:
        - Dictionary with 'properties' key
        - Properties contain queryable definitions
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_08_get_collection_queryables")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_collection_queryables(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_collection_queryables(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(
            f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}"
        )

        # Validate response structure
        assert isinstance(
            response, dict
        ), f"Response should be a dict, got {type(response)}"
        assert "properties" in response, "Response should have 'properties' key"

        properties = response["properties"]
        test_logger.info(f"Number of queryables: {len(properties)}")

        if len(properties) > 0:
            # Log first few queryables
            for i, (key, value) in enumerate(list(properties.items())[:5]):
                test_logger.info(f"  Queryable {i + 1}: {key}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_09_list_queryables(self, planetarycomputer_endpoint):
        """
        Test listing all queryables (global).

        Expected response:
        - Dictionary with 'properties' key
        - Properties contain global queryable definitions
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_09_list_queryables")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Calling: list_queryables()")
        response = client.stac.list_queryables()

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(
            f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}"
        )

        # Validate response structure
        assert isinstance(
            response, dict
        ), f"Response should be a dict, got {type(response)}"
        assert "properties" in response, "Response should have 'properties' key"

        properties = response["properties"]
        test_logger.info(f"Number of global queryables: {len(properties)}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_10_get_collection_configuration(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting collection configuration.

        Expected response:
        - Configuration object with various settings
        - May include tile settings, render options, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_10_get_collection_configuration")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_collection_configuration(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_collection_configuration(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")

        # Validate response structure
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_11_get_collection_thumbnail(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting collection thumbnail.

        Expected response:
        - Binary image data (streaming generator)
        - Valid image format (PNG/JPEG)
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_11_get_collection_thumbnail")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # First check if collection has thumbnail asset
        collection = client.stac.get_collection(
            collection_id=planetarycomputer_collection_id
        )

        if (
            not hasattr(collection, "assets")
            or collection.assets is None
            or "thumbnail" not in collection.assets
        ):
            assert False, "Collection does not have a thumbnail asset"

        test_logger.info(
            f"Calling: get_collection_thumbnail(collection_id='{planetarycomputer_collection_id}')"
        )
        response = client.stac.get_collection_thumbnail(
            collection_id=planetarycomputer_collection_id
        )

        test_logger.info(f"Response type: {type(response)}")

        # Collect the streaming response into bytes
        thumbnail_bytes = b"".join(response)
        test_logger.info(f"Thumbnail size: {len(thumbnail_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {thumbnail_bytes[:16].hex()}")

        # Validate image data
        assert len(thumbnail_bytes) > 0, "Thumbnail bytes should not be empty"
        assert (
            len(thumbnail_bytes) > 100
        ), f"Thumbnail should be substantial, got only {len(thumbnail_bytes)} bytes"

        # Check for common image format magic bytes
        # PNG: 89 50 4E 47
        # JPEG: FF D8 FF
        is_png = thumbnail_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        is_jpeg = thumbnail_bytes[:3] == b"\xff\xd8\xff"

        assert is_png or is_jpeg, "Thumbnail should be either PNG or JPEG format"

        if is_png:
            test_logger.info("Thumbnail format: PNG")
        elif is_jpeg:
            test_logger.info("Thumbnail format: JPEG")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_12_create_render_option(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating a render option for a collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_12_create_render_option")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import RenderOption, RenderOptionType

        # Check if render option already exists and delete it
        try:
            client.stac.get_render_option(
                collection_id=planetarycomputer_collection_id,
                render_option_id="test-natural-color",
            )
            test_logger.info(
                "Render option 'test-natural-color' already exists, deleting it first"
            )
            client.stac.delete_render_option(
                collection_id=planetarycomputer_collection_id,
                render_option_id="test-natural-color",
            )
            test_logger.info("Existing render option deleted")
        except Exception as e:
            test_logger.info(f"Render option does not exist (expected): {e}")

        render_option = RenderOption(
            id="test-natural-color",
            name="Test Natural color",
            type=RenderOptionType.RASTER_TILE,
            options="assets=image&asset_bidx=image|1,2,3",
            min_zoom=6,
        )

        test_logger.info(
            f"Calling: create_render_option(collection_id='{planetarycomputer_collection_id}', body={render_option})"
        )
        response = client.stac.create_render_option(
            collection_id=planetarycomputer_collection_id, body=render_option
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-natural-color"
        assert response.name == "Test Natural color"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_13_get_render_option(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting a specific render option.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_13_get_render_option")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_render_option(collection_id='{planetarycomputer_collection_id}', render_option_id='test-natural-color')"
        )
        response = client.stac.get_render_option(
            collection_id=planetarycomputer_collection_id,
            render_option_id="test-natural-color",
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-natural-color"
        assert response.name is not None

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_14_replace_render_option(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating or replacing a render option.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_14_replace_render_option")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import RenderOption, RenderOptionType

        render_option = RenderOption(
            id="test-natural-color",
            name="Test Natural color updated",
            description="RGB from visual assets - updated",
            type=RenderOptionType.RASTER_TILE,
            options="assets=image&asset_bidx=image|1,2,3",
            min_zoom=6,
        )

        test_logger.info(
            f"Calling: create_or_replace_render_option(collection_id='{planetarycomputer_collection_id}', render_option_id='test-natural-color', body={render_option})"
        )
        response = client.stac.replace_render_option(
            collection_id=planetarycomputer_collection_id,
            render_option_id="test-natural-color",
            body=render_option,
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-natural-color"
        assert response.description == "RGB from visual assets - updated"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_14a_delete_render_option(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test deleting a render option.
        First creates a render option specifically for deletion.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_14a_delete_render_option")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import RenderOption, RenderOptionType

        # Create a render option to be deleted
        render_option = RenderOption(
            id="test-render-opt-delete",
            name="Test Render Option To Be Deleted",
            type=RenderOptionType.RASTER_TILE,
            options="assets=image&asset_bidx=image|1,2,3",
            min_zoom=6,
        )

        test_logger.info(f"Creating render option for deletion: {render_option.id}")
        client.stac.create_render_option(
            collection_id=planetarycomputer_collection_id, body=render_option
        )

        # Verify it exists
        retrieved = client.stac.get_render_option(
            collection_id=planetarycomputer_collection_id,
            render_option_id="test-render-opt-delete",
        )
        assert retrieved is not None
        test_logger.info("Render option created successfully")

        # Now delete it
        test_logger.info(
            f"Calling: delete_render_option(collection_id='{planetarycomputer_collection_id}', render_option_id='test-render-opt-delete')"
        )
        client.stac.delete_render_option(
            collection_id=planetarycomputer_collection_id,
            render_option_id="test-render-opt-delete",
        )

        test_logger.info("Render option deleted successfully")

        # Verify deletion
        try:
            client.stac.get_render_option(
                collection_id=planetarycomputer_collection_id,
                render_option_id="test-render-opt-delete",
            )
            assert False, "Render option should have been deleted"
        except Exception as e:
            test_logger.info(f"Confirmed deletion (404 expected): {e}")
            assert (
                "404" in str(e)
                or "Not Found" in str(e)
                or "not found" in str(e).lower()
            )

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_15_add_mosaic(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test adding a mosaic to a collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_15_add_mosaic")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import StacMosaic

        # Check if mosaic already exists and delete it
        try:
            client.stac.get_mosaic(
                collection_id=planetarycomputer_collection_id, mosaic_id="test-mosaic-1"
            )
            test_logger.info("Mosaic 'test-mosaic-1' already exists, deleting it first")
            client.stac.delete_mosaic(
                collection_id=planetarycomputer_collection_id, mosaic_id="test-mosaic-1"
            )
            test_logger.info("Existing mosaic deleted")
        except Exception as e:
            test_logger.info(f"Mosaic does not exist (expected): {e}")

        mosaic = StacMosaic(
            id="test-mosaic-1",
            name="Test Most recent available",
            cql=[],
        )

        test_logger.info(
            f"Calling: add_mosaic(collection_id='{planetarycomputer_collection_id}', body={mosaic})"
        )
        response = client.stac.add_mosaic(
            collection_id=planetarycomputer_collection_id, body=mosaic
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-mosaic-1"
        assert response.name == "Test Most recent available"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_16_get_mosaic(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test getting a specific mosaic.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_16_get_mosaic")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_mosaic(collection_id='{planetarycomputer_collection_id}', mosaic_id='test-mosaic-1')"
        )
        response = client.stac.get_mosaic(
            collection_id=planetarycomputer_collection_id, mosaic_id="test-mosaic-1"
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-mosaic-1"
        assert response.name is not None

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_17_replace_mosaic(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating or replacing a mosaic.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_17_replace_mosaic")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import StacMosaic

        mosaic = StacMosaic(
            id="test-mosaic-1",
            name="Test Most recent available",
            description="Most recent available imagery in this collection - updated",
            cql=[],
        )

        test_logger.info(
            f"Calling: create_or_replace_mosaic(collection_id='{planetarycomputer_collection_id}', mosaic_id='test-mosaic-1', body={mosaic})"
        )
        response = client.stac.replace_mosaic(
            collection_id=planetarycomputer_collection_id,
            mosaic_id="test-mosaic-1",
            body=mosaic,
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.id == "test-mosaic-1"
        assert response.description is not None

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_17a_delete_mosaic(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test deleting a mosaic.
        First creates a mosaic specifically for deletion.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_17a_delete_mosaic")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import StacMosaic

        # Create a mosaic to be deleted
        mosaic = StacMosaic(
            id="test-mosaic-to-be-deleted",
            name="Test Mosaic To Be Deleted",
            cql=[],
        )

        test_logger.info(f"Creating mosaic for deletion: {mosaic.id}")
        client.stac.add_mosaic(
            collection_id=planetarycomputer_collection_id, body=mosaic
        )

        # Verify it exists
        retrieved = client.stac.get_mosaic(
            collection_id=planetarycomputer_collection_id,
            mosaic_id="test-mosaic-to-be-deleted",
        )
        assert retrieved is not None
        test_logger.info("Mosaic created successfully")

        # Now delete it
        test_logger.info(
            f"Calling: delete_mosaic(collection_id='{planetarycomputer_collection_id}', mosaic_id='test-mosaic-to-be-deleted')"
        )
        client.stac.delete_mosaic(
            collection_id=planetarycomputer_collection_id,
            mosaic_id="test-mosaic-to-be-deleted",
        )

        test_logger.info("Mosaic deleted successfully")

        # Verify deletion
        try:
            client.stac.get_mosaic(
                collection_id=planetarycomputer_collection_id,
                mosaic_id="test-mosaic-to-be-deleted",
            )
            assert False, "Mosaic should have been deleted"
        except Exception as e:
            test_logger.info(f"Confirmed deletion (404 expected): {e}")
            assert (
                "404" in str(e)
                or "Not Found" in str(e)
                or "not found" in str(e).lower()
            )

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_18_replace_partition_type(self, planetarycomputer_endpoint):
        """
        Test replacing partition type by creating a temporary collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_18_replace_partition_type")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import (
            PartitionType,
            PartitionTypeScheme,
            StacExtensionSpatialExtent,
            StacCollectionTemporalExtent,
            StacExtensionExtent,
        )

        # Create a temporary collection for partition type testing
        test_collection_id = "test-partition-type-collection"
        test_logger.info(f"Creating temporary collection: {test_collection_id}")

        # Check if collection exists and delete it first
        try:
            existing_collection = client.stac.get_collection(
                collection_id=test_collection_id
            )
            if existing_collection:
                test_logger.info(
                    f"Collection '{test_collection_id}' already exists, deleting first..."
                )
                delete_poller = client.stac.begin_delete_collection(
                    collection_id=test_collection_id, polling=True
                )
                delete_poller.result()
                test_logger.info(f"Deleted existing collection '{test_collection_id}'")
        except Exception:
            test_logger.info(
                f"Collection '{test_collection_id}' does not exist, proceeding with creation"
            )

        # Define collection extents
        spatial_extent = StacExtensionSpatialExtent(bounding_box=[[-180, -90, 180, 90]])

        temporal_extent = StacCollectionTemporalExtent(
            interval=[
                [
                    datetime.datetime.fromisoformat("2020-01-01T00:00:00+00:00"),
                    datetime.datetime.fromisoformat("2099-12-31T23:59:59+00:00"),
                ]
            ]
        )

        extent = StacExtensionExtent(spatial=spatial_extent, temporal=temporal_extent)
        # Create collection payload
        collection_data = {
            "id": test_collection_id,
            "description": "Temporary collection for partition type testing",
            "extent": extent.as_dict(),
            "license": "proprietary",
            "links": [],
            "stac_version": "1.0.0",
            "title": "Test Partition Type Collection",
            "type": "Collection",
        }

        # Create the collection using the correct API
        test_logger.info("Creating collection using begin_create_collection")
        create_poller = client.stac.begin_create_collection(
            body=collection_data, polling=True
        )
        create_poller.result()
        test_logger.info("Temporary collection created")

        try:
            # Set partition type
            partition_type = PartitionType(scheme=PartitionTypeScheme.YEAR)

            test_logger.info(
                f"Calling: replace_partition_type(collection_id='{test_collection_id}', body={partition_type})"
            )
            client.stac.replace_partition_type(
                collection_id=test_collection_id, body=partition_type
            )

            # Verify the change
            updated_partition = client.stac.get_partition_type(test_collection_id)
            assert updated_partition.scheme == PartitionTypeScheme.YEAR

            test_logger.info("Partition type set successfully")

        finally:
            # Clean up: delete the temporary collection
            test_logger.info(f"Deleting temporary collection: {test_collection_id}")
            try:
                delete_poller = client.stac.begin_delete_collection(
                    collection_id=test_collection_id, polling=True
                )
                delete_poller.result()
                test_logger.info("Temporary collection deleted")
            except Exception as e:
                test_logger.warning(f"Failed to delete temporary collection: {e}")

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_19_replace_tile_settings(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test replacing tile settings for a collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_19_replace_tile_settings")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import TileSettings

        tile_settings = TileSettings(
            default_location=None,
            max_items_per_tile=35,
            min_zoom=6,
        )

        test_logger.info(
            f"Calling: replace_tile_settings(collection_id='{planetarycomputer_collection_id}', body={tile_settings})"
        )
        response = client.stac.replace_tile_settings(
            collection_id=planetarycomputer_collection_id, body=tile_settings
        )

        test_logger.info(f"Response: {response}")
        assert response is not None
        assert response.max_items_per_tile == 35
        assert response.min_zoom == 6

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_20_create_queryables(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating queryables for a collection.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_20_create_queryables")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import (
            StacQueryable,
            StacQueryableDefinitionDataType,
        )

        # Check if queryable already exists and delete it
        try:
            queryables = client.stac.get_collection_queryables(
                collection_id=planetarycomputer_collection_id
            )
            if "test:property" in queryables.get("properties", {}):
                test_logger.info(
                    "Queryable 'test:property' already exists, deleting it first"
                )
                client.stac.delete_queryable(
                    collection_id=planetarycomputer_collection_id,
                    queryable_name="test:property",
                )
                test_logger.info("Existing queryable deleted")
            else:
                test_logger.info("Queryable does not exist (expected)")
        except Exception as e:
            test_logger.info(f"Error checking queryable existence: {e}")

        queryable = StacQueryable(
            name="test:property",
            data_type=StacQueryableDefinitionDataType.NUMBER,
            create_index=False,
            definition={
                "data_type": StacQueryableDefinitionDataType.NUMBER,
            },
        )

        test_logger.info(
            f"Calling: create_queryables(collection_id='{planetarycomputer_collection_id}', body=[queryable])"
        )
        response = client.stac.create_queryables(
            collection_id=planetarycomputer_collection_id, body=[queryable]
        )

        test_logger.info(f"Response: {response}")
        assert response is not None

        # Response is a list of queryables
        assert isinstance(
            response, list
        ), f"Response should be a list, got {type(response)}"
        assert len(response) > 0, "Response should contain at least one queryable"

        # Verify our queryable was created
        queryable_names = [
            q.get("name") if isinstance(q, dict) else q.name for q in response
        ]
        assert (
            "test:property" in queryable_names
        ), "Created queryable 'test:property' should be in response"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_21_replace_queryable(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating or replacing a queryable.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_21_replace_queryable")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import (
            StacQueryable,
            StacQueryableDefinitionDataType,
        )

        queryable = StacQueryable(
            name="test:property",
            data_type=StacQueryableDefinitionDataType.NUMBER,
            create_index=False,
            definition={
                "description": "Test property - updated",
            },
        )

        test_logger.info(
            f"Calling: create_or_replace_queryable(collection_id='{planetarycomputer_collection_id}', queryable_name='test:property', body=queryable)"
        )
        response = client.stac.replace_queryable(
            collection_id=planetarycomputer_collection_id,
            queryable_name="test:property",
            body=queryable,
        )

        test_logger.info(f"Response: {response}")
        assert response is not None

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_21a_delete_queryable(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test deleting a queryable.
        First creates a queryable specifically for deletion.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_21a_delete_queryable")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        from azure.planetarycomputer.models import (
            StacQueryable,
            StacQueryableDefinitionDataType,
        )

        # Create a queryable to be deleted
        queryable = StacQueryable(
            name="test:property_to_be_deleted",
            data_type=StacQueryableDefinitionDataType.NUMBER,
            create_index=False,
            definition={
                "description": "Test property for deletion",
            },
        )

        test_logger.info(f"Creating queryable for deletion: {queryable.name}")
        client.stac.create_queryables(
            collection_id=planetarycomputer_collection_id, body=[queryable]
        )

        # Verify it exists
        queryables = client.stac.get_collection_queryables(
            collection_id=planetarycomputer_collection_id
        )
        assert "test:property_to_be_deleted" in queryables["properties"]
        test_logger.info("Queryable created successfully")

        # Now delete it
        test_logger.info(
            f"Calling: delete_queryable(collection_id='{planetarycomputer_collection_id}', queryable_name='test:property_to_be_deleted')"
        )
        client.stac.delete_queryable(
            collection_id=planetarycomputer_collection_id,
            queryable_name="test:property_to_be_deleted",
        )

        test_logger.info("Queryable deleted successfully")

        # Verify deletion
        queryables_after = client.stac.get_collection_queryables(
            collection_id=planetarycomputer_collection_id
        )
        assert (
            "test:property_to_be_deleted" not in queryables_after["properties"]
        ), "Queryable should have been deleted"

        test_logger.info("Test PASSED\n")
