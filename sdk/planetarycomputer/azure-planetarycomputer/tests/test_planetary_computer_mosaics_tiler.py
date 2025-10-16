# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for Mosaics Tiler operations.
"""
import io
import logging
from pathlib import Path
from devtools_testutils import recorded_by_proxy
from testpreparer import PlanetaryComputerClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    StacSearchParameters,
    FilterLanguage,
    StacSortExtension,
    StacSearchSortingDirection,
    TilerImageFormat,
)

# Set up test logger
test_logger = logging.getLogger("test_mosaics_tiler")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "mosaics_tiler_test_results.log"
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerMosaicsTiler(PlanetaryComputerClientTestBase):
    """Test suite for Mosaics Tiler operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_register_mosaics_search(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test registering a mosaics search.
        
        Expected response:
        - Dictionary with 'searchid' key
        - Search ID is a string identifier
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_register_mosaics_search")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Create search parameters
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        test_logger.info(f"Search request: {register_search_request}")
        
        test_logger.info("Calling: register_mosaics_search(...)")
        response = client.tiler.register_mosaics_search(register_search_request)
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'search_id'), "Response should have 'search_id' attribute"
        
        search_id = response.search_id
        assert isinstance(search_id, str), f"Search ID should be a string, got {type(search_id)}"
        assert len(search_id) > 0, "Search ID should not be empty"
        
        test_logger.info(f"Search ID: {search_id}")
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_get_mosaics_search_info(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting mosaics search info.
        
        Expected response:
        - Object with 'search' attribute
        - Search object contains hash and other metadata
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_get_mosaics_search_info")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # First register a search
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        test_logger.info(f"Registered search ID: {search_id}")
        
        test_logger.info(f"Calling: get_mosaics_search_info(search_id='{search_id}')")
        response = client.tiler.get_mosaics_search_info(search_id=search_id)
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        
        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'search'), "Response should have 'search' attribute"
        
        search = response.search
        test_logger.info(f"Search type: {type(search)}")
        assert search is not None, "Search should not be None"
        assert hasattr(search, 'hash'), "Search should have 'hash' attribute"
        
        search_hash = search.hash
        assert isinstance(search_hash, str), f"Search hash should be a string, got {type(search_hash)}"
        assert len(search_hash) > 0, "Search hash should not be empty"
        
        test_logger.info(f"Search hash: {search_hash}")
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_get_mosaics_tile_json(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting mosaics tile JSON.
        
        Expected response:
        - TileJSON object with metadata
        - Contains tilejson version, tiles URL patterns, bounds, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_mosaics_tile_json")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Register search and get hash
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        search_info = client.tiler.get_mosaics_search_info(search_id=search_id)
        search_hash = search_info.search.hash
        test_logger.info(f"Using search hash: {search_hash}")
        
        test_logger.info("Calling: get_mosaics_tile_json(...)")
        response = client.tiler.get_mosaics_tile_json(
            search_id=search_hash,
            tile_matrix_set_id="WebMercatorQuad",
            assets=["red_20m", "green_20m", "blue_20m"],
            tile_scale=2,
            color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
            no_data=0.0,
            min_zoom=9,
            collection=planetarycomputer_collection_id,
            tile_format="png",
        )
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
            test_logger.info(f"TileJSON version: {response_dict.get('tilejson')}")
        
        # Validate TileJSON structure (note: attributes accessed via as_dict() for serialization)
        assert response is not None, "Response should not be None"
        response_dict = response.as_dict() if hasattr(response, 'as_dict') else response
        
        # Validate key fields exist
        assert 'tilejson' in response_dict, "Response should have 'tilejson' key"
        assert 'tiles' in response_dict, "Response should have 'tiles' key"
        
        # Validate tiles array
        tiles = response_dict['tiles']
        assert isinstance(tiles, list), "Tiles should be a list"
        assert len(tiles) > 0, "Should have at least one tile URL pattern"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_get_mosaics_tile(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting a specific mosaic tile.
        
        Expected response:
        - Binary PNG image data (streaming generator)
        - Valid PNG format with magic bytes
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_get_mosaics_tile")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info("Input - tile coordinates: z=10, x=504, y=390")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Register search and get hash
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        search_info = client.tiler.get_mosaics_search_info(search_id=search_id)
        search_hash = search_info.search.hash
        test_logger.info(f"Using search hash: {search_hash}")
        
        test_logger.info("Calling: get_mosaics_tile(...)")
        response = client.tiler.get_mosaics_tile(
            search_id=search_hash,
            tile_matrix_set_id="WebMercatorQuad",
            z=10,
            x=504,
            y=390,
            scale=1,
            format="png",
            assets=["red_20m", "green_20m", "blue_20m"],
            color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
            no_data=0.0,
            collection=planetarycomputer_collection_id,
        )
        
        test_logger.info(f"Response type: {type(response)}")
        
        # Collect the streaming response into bytes
        image_bytes = b"".join(response)
        test_logger.info(f"Image size: {len(image_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {image_bytes[:16].hex()}")
        
        # Verify PNG magic bytes
        png_magic = b'\x89PNG\r\n\x1a\n'
        assert len(image_bytes) > 0, "Image bytes should not be empty"
        assert len(image_bytes) > 100, f"Image should be substantial, got only {len(image_bytes)} bytes"
        assert image_bytes[:8] == png_magic, "Response should be a valid PNG image (magic bytes mismatch)"
        
        # Parse and validate the PNG image
        try:
            from PIL import Image as PILImage
            image = PILImage.open(io.BytesIO(image_bytes))
            test_logger.info(f"PIL Image format: {image.format}")
            test_logger.info(f"PIL Image size: {image.size}")
            test_logger.info(f"PIL Image mode: {image.mode}")
            
            # Validate image properties
            assert image.format == "PNG", f"Image format should be PNG, got {image.format}"
            width, height = image.size
            assert width > 0 and height > 0, f"Image should have non-zero dimensions, got {width}x{height}"
            
        except ImportError:
            test_logger.warning("PIL not available, skipping detailed image validation")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_get_mosaics_wmts_capabilities(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting WMTS capabilities XML for mosaics.
        
        Expected response:
        - XML document describing WMTS service capabilities
        - Contains layer information, tile matrix sets, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_get_mosaics_wmts_capabilities")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Register search and get hash
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        search_info = client.tiler.get_mosaics_search_info(search_id=search_id)
        search_hash = search_info.search.hash
        test_logger.info(f"Using search hash: {search_hash}")
        
        test_logger.info("Calling: get_mosaics_wmts_capabilities(...)")
        response = client.tiler.get_mosaics_wmts_capabilities(
            search_id=search_hash,
            tile_matrix_set_id="WebMercatorQuad",
            tile_format=TilerImageFormat.PNG,
            tile_scale=1,
            min_zoom=7,
            max_zoom=9,
            assets=["red_20m", "green_20m", "blue_20m"],
            color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
            no_data=0,
        )
        
        test_logger.info(f"Response type: {type(response)}")
        
        # Collect XML bytes
        xml_bytes = b"".join(response)
        test_logger.info(f"XML size: {len(xml_bytes)} bytes")
        
        # Decode to string
        xml_string = xml_bytes.decode("utf-8")
        test_logger.info(f"XML first 200 chars: {xml_string[:200]}")
        
        # Validate XML structure
        assert len(xml_bytes) > 0, "XML bytes should not be empty"
        # Note: WMTS Capabilities XML may not have <?xml declaration
        assert "<Capabilities" in xml_string, "Response should contain Capabilities element"
        assert "WMTS" in xml_string or "wmts" in xml_string.lower(), "Response should reference WMTS"
        assert "TileMatrix" in xml_string, "Response should contain TileMatrix information"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_get_mosaics_assets_for_point(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting mosaic assets for a specific point.
        
        Expected response:
        - List of asset dictionaries
        - Each asset has 'id' and other metadata
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_get_mosaics_assets_for_point")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info("Input - point: longitude=-3.0767, latitude=39.1201")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Register search and get hash
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        search_info = client.tiler.get_mosaics_search_info(search_id=search_id)
        search_hash = search_info.search.hash
        test_logger.info(f"Using search hash: {search_hash}")
        
        test_logger.info("Calling: get_mosaics_assets_for_point(...)")
        response = client.tiler.get_mosaics_assets_for_point(
            search_id=search_hash,
            longitude=-3.0767,
            latitude=39.1201,
            coordinate_reference_system="EPSG:4326",
            items_limit=100,
            exit_when_full=True,
            scan_limit=100,
            skip_covered=True,
            time_limit=30,
        )
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Number of assets: {len(response) if isinstance(response, list) else 'N/A'}")
        
        # Validate response structure
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        
        # If we have assets, validate structure
        if len(response) > 0:
            first_asset = response[0]
            test_logger.info(f"First asset type: {type(first_asset)}")
            
            # Asset is a StacAsset object that can be accessed as dict
            assert first_asset is not None, "First asset should not be None"
            
            # StacAsset behaves like a dict - access via key
            asset_dict = first_asset.as_dict() if hasattr(first_asset, 'as_dict') else first_asset
            assert 'id' in asset_dict, f"Asset should have 'id' key, got keys: {list(asset_dict.keys())}"
            
            asset_id = asset_dict['id']
            test_logger.info(f"First asset ID: {asset_id}")
            assert isinstance(asset_id, str), f"Asset ID should be a string, got {type(asset_id)}"
            assert len(asset_id) > 0, "Asset ID should not be empty"
        else:
            test_logger.info("No assets returned for this point")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_get_mosaics_assets_for_tile(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """
        Test getting mosaic assets for a specific tile.
        
        Expected response:
        - List of asset dictionaries
        - Assets that intersect with the specified tile
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_07_get_mosaics_assets_for_tile")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info("Input - tile coordinates: z=10, x=504, y=390")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Register search and get hash
        register_search_request = StacSearchParameters(
            filter={"args": [{"args": [{"property": "collection"}, planetarycomputer_collection_id], "op": "="}], "op": "and"},
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
        )
        register_response = client.tiler.register_mosaics_search(register_search_request)
        search_id = register_response.search_id
        search_info = client.tiler.get_mosaics_search_info(search_id=search_id)
        search_hash = search_info.search.hash
        test_logger.info(f"Using search hash: {search_hash}")
        
        test_logger.info("Calling: get_mosaics_assets_for_tile(...)")
        response = client.tiler.get_mosaics_assets_for_tile(
            search_id=search_hash,
            tile_matrix_set_id="WebMercatorQuad",
            z=10,
            x=504,
            y=390,
            collection_id=planetarycomputer_collection_id,
        )
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        else:
            test_logger.info(f"Response: {response}")
        
        # Validate response is not None
        assert response is not None, "Response should not be None"
        
        test_logger.info("Test PASSED\n")
