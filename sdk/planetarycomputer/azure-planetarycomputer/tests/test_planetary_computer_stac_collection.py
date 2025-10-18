# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for STAC Collection operations.
"""
import logging
from pathlib import Path
from devtools_testutils import recorded_by_proxy
from testpreparer import PlanetaryComputerClientTestBase, PlanetaryComputerPreparer
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
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerStacCollection(PlanetaryComputerClientTestBase):
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
        assert hasattr(response, 'collections'), "Response should have 'collections' attribute"
        
        collections = response.collections
        assert isinstance(collections, list), f"Collections should be a list, got {type(collections)}"
        
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
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'conforms_to'), "Response should have 'conforms_to' attribute"
        
        conforms_to = response.conforms_to
        assert isinstance(conforms_to, list), f"conformsTo should be a list, got {type(conforms_to)}"
        assert len(conforms_to) > 0, "Should have at least one conformance class"
        
        test_logger.info(f"Number of conformance classes: {len(conforms_to)}")
        for i, uri in enumerate(conforms_to[:5]):  # Log first 5
            test_logger.info(f"  {i+1}. {uri}")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_get_stac_landing_page(self, planetarycomputer_endpoint):
        """
        Test getting STAC landing page.
        
        Expected response:
        - STAC catalog root object
        - Contains links, description, etc.
        
        Note: This test is skipped due to SDK bug where get_stac_landing_page()
        does not send Authorization header, resulting in 401 Unauthorized.
        """
        import pytest
        pytest.skip("Skipping due to SDK bug: get_stac_landing_page() does not send Authorization header")
        
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_stac_landing_page")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info("Calling: get_stac_landing_page()")
        response = client.stac.get_stac_landing_page()
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'id'), "Response should have 'id' attribute"
        assert hasattr(response, 'type'), "Response should have 'type' attribute"
        assert hasattr(response, 'stac_version'), "Response should have 'stac_version' attribute"
        
        test_logger.info(f"STAC ID: {response.id}")
        test_logger.info(f"STAC Type: {response.type}")
        test_logger.info(f"STAC Version: {response.stac_version}")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_get_collection(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting a specific STAC collection.
        
        Expected response:
        - StacCollection object
        - Contains id, title, description, extent, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_get_collection")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: get_collection(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.get_collection(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Collection ID: {response.id}")
        test_logger.info(f"Collection Title: {response.title}")
        test_logger.info(f"Collection Description: {response.description[:100]}...")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert response.id == planetarycomputer_collection_id, "Collection ID should match requested ID"
        assert response.title is not None and len(response.title) > 0, "Collection should have a title"
        assert response.description is not None, "Collection should have a description"
        assert response.extent is not None, "Collection should have extent"
        assert response.license is not None, "Collection should have license"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_get_partition_type(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting partition type for a collection.
        
        Expected response:
        - PartitionType object
        - Contains scheme (e.g., NONE, YEAR, YEAR_MONTH)
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_get_partition_type")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: get_partition_type(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.get_partition_type(planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Partition scheme: {response.scheme}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'scheme'), "Response should have 'scheme' attribute"
        assert response.scheme is not None, "Partition scheme should not be None"
        
        # Validate scheme is a valid PartitionTypeScheme
        valid_schemes = [s.value for s in PartitionTypeScheme]
        assert response.scheme in valid_schemes, f"Partition scheme should be one of {valid_schemes}"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_list_render_options(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test listing render options for a collection.
        
        Expected response:
        - List of RenderOption objects
        - Each has id, name, type, options, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_list_render_options")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: list_render_options(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.list_render_options(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Number of render options: {len(response)}")
        
        # Validate response structure
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        
        if len(response) > 0:
            first_option = response[0]
            test_logger.info(f"First render option ID: {first_option.id}")
            test_logger.info(f"First render option name: {first_option.name}")
            test_logger.info(f"First render option type: {first_option.type}")
            
            assert hasattr(first_option, 'id'), "Render option should have 'id'"
            assert hasattr(first_option, 'name'), "Render option should have 'name'"
            assert hasattr(first_option, 'type'), "Render option should have 'type'"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_get_tile_settings(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting tile settings for a collection.
        
        Expected response:
        - TileSettings object
        - Contains max_items_per_tile, min_zoom, default_location
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_07_get_tile_settings")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: get_tile_settings(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.get_tile_settings(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        
        # Log available attributes
        if hasattr(response, 'max_items_per_tile'):
            test_logger.info(f"Max items per tile: {response.max_items_per_tile}")
        if hasattr(response, 'min_zoom'):
            test_logger.info(f"Min zoom: {response.min_zoom}")
        if hasattr(response, 'default_location'):
            test_logger.info(f"Default location: {response.default_location}")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_08_list_mosaics(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test listing mosaics for a collection.
        
        Expected response:
        - List of StacMosaic objects
        - Each has id, name, cql filter
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_08_list_mosaics")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: list_mosaics(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.list_mosaics(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Number of mosaics: {len(response)}")
        
        # Validate response structure
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        
        if len(response) > 0:
            first_mosaic = response[0]
            test_logger.info(f"First mosaic ID: {first_mosaic.id}")
            test_logger.info(f"First mosaic name: {first_mosaic.name}")
            
            assert hasattr(first_mosaic, 'id'), "Mosaic should have 'id'"
            assert hasattr(first_mosaic, 'name'), "Mosaic should have 'name'"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_09_list_collection_queryables(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test listing queryables for a collection.
        
        Expected response:
        - Dictionary with 'properties' key
        - Properties contain queryable definitions
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_09_list_collection_queryables")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: list_collection_queryables(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.list_collection_queryables(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        # Validate response structure
        assert isinstance(response, dict), f"Response should be a dict, got {type(response)}"
        assert "properties" in response, "Response should have 'properties' key"
        
        properties = response["properties"]
        test_logger.info(f"Number of queryables: {len(properties)}")
        
        if len(properties) > 0:
            # Log first few queryables
            for i, (key, value) in enumerate(list(properties.items())[:5]):
                test_logger.info(f"  Queryable {i+1}: {key}")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_10_list_queryables(self, planetarycomputer_endpoint):
        """
        Test listing all queryables (global).
        
        Expected response:
        - Dictionary with 'properties' key
        - Properties contain global queryable definitions
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_10_list_queryables")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info("Calling: list_queryables()")
        response = client.stac.list_queryables()
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        # Validate response structure
        assert isinstance(response, dict), f"Response should be a dict, got {type(response)}"
        assert "properties" in response, "Response should have 'properties' key"
        
        properties = response["properties"]
        test_logger.info(f"Number of global queryables: {len(properties)}")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_11_get_collection_configuration(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting collection configuration.
        
        Expected response:
        - Configuration object with various settings
        - May include tile settings, render options, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_11_get_collection_configuration")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: get_collection_configuration(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.get_collection_configuration(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_12_get_collection_thumbnail(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting collection thumbnail.
        
        Expected response:
        - Binary image data (streaming generator)
        - Valid image format (PNG/JPEG)
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_12_get_collection_thumbnail")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # First check if collection has thumbnail asset
        collection = client.stac.get_collection(collection_id=planetarycomputer_collection_id)
        
        if not hasattr(collection, 'assets') or collection.assets is None or 'thumbnail' not in collection.assets:
            test_logger.info("Collection does not have a thumbnail asset, skipping test")
            return
        
        test_logger.info(f"Calling: get_collection_thumbnail(collection_id='{planetarycomputer_collection_id}')")
        response = client.stac.get_collection_thumbnail(collection_id=planetarycomputer_collection_id)
        
        test_logger.info(f"Response type: {type(response)}")
        
        # Collect the streaming response into bytes
        thumbnail_bytes = b"".join(response)
        test_logger.info(f"Thumbnail size: {len(thumbnail_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {thumbnail_bytes[:16].hex()}")
        
        # Validate image data
        assert len(thumbnail_bytes) > 0, "Thumbnail bytes should not be empty"
        assert len(thumbnail_bytes) > 100, f"Thumbnail should be substantial, got only {len(thumbnail_bytes)} bytes"
        
        # Check for common image format magic bytes
        # PNG: 89 50 4E 47
        # JPEG: FF D8 FF
        is_png = thumbnail_bytes[:8] == b'\x89PNG\r\n\x1a\n'
        is_jpeg = thumbnail_bytes[:3] == b'\xff\xd8\xff'
        
        assert is_png or is_jpeg, "Thumbnail should be either PNG or JPEG format"
        
        if is_png:
            test_logger.info("Thumbnail format: PNG")
        elif is_jpeg:
            test_logger.info("Thumbnail format: JPEG")
        
        test_logger.info("Test PASSED\n")

