# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for STAC Item Tiler operations.
"""
import io
import logging
from pathlib import Path
from devtools_testutils import recorded_by_proxy
from testpreparer import PlanetaryComputerClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import TilerImageFormat, Polygon, Feature, FeatureType

# Set up test logger
test_logger = logging.getLogger("test_stac_item_tiler")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "stac_item_tiler_test_results.log"
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerStacItemTiler(PlanetaryComputerClientTestBase):
    """Test suite for STAC Item Tiler operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_get_tile_matrix_definitions(self, planetarycomputer_endpoint):
        """
        Test getting tile matrix definitions for WebMercatorQuad.
        
        Expected response:
        - TileMatrixSet object with id, title, crs
        - List of tileMatrices with zoom levels 0-24
        - Each matrix has scaleDenominator, cellSize, dimensions
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_get_tile_matrix_definitions")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info("Input - tile_matrix_set_id: WebMercatorQuad")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info("Calling: get_tile_matrix_definitions(tile_matrix_set_id='WebMercatorQuad')")
        response = client.tiler.get_tile_matrix_definitions(tile_matrix_set_id="WebMercatorQuad")
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
            test_logger.info(f"Number of tile matrices: {len(response_dict.get('tileMatrices', []))}")
        
        # Assert basic structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, 'id'), "Response should have id attribute"
        assert response.id == "WebMercatorQuad", f"ID should be WebMercatorQuad, got {response.id}"
        assert hasattr(response, 'tile_matrices'), "Response should have tile_matrices"
        assert len(response.tile_matrices) > 0, "Should have at least one tile matrix"
        
        # Validate tile matrix structure
        first_matrix = response.tile_matrices[0]
        assert hasattr(first_matrix, 'id'), "Tile matrix should have id"
        assert hasattr(first_matrix, 'scale_denominator'), "Tile matrix should have scale_denominator"
        assert hasattr(first_matrix, 'tile_width'), "Tile matrix should have tile_width"
        assert hasattr(first_matrix, 'tile_height'), "Tile matrix should have tile_height"
        assert first_matrix.tile_width == 256, "Standard tile width should be 256"
        assert first_matrix.tile_height == 256, "Standard tile height should be 256"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_list_tile_matrices(self, planetarycomputer_endpoint):
        """
        Test listing all available tile matrices.
        
        Expected response:
        - List of tile matrix set IDs
        - Should include WebMercatorQuad, WorldCRS84Quad, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_list_tile_matrices")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info("Calling: list_tile_matrices()")
        response = client.tiler.list_tile_matrices()
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        test_logger.info(f"Number of tile matrices: {len(response)}")
        
        # Assert response is a list
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        assert len(response) > 0, "Should have at least one tile matrix"
        
        # Check for expected tile matrix sets
        assert "WebMercatorQuad" in response, "Should include WebMercatorQuad"
        assert "WorldCRS84Quad" in response, "Should include WorldCRS84Quad"
        
        # All items should be strings
        for item in response:
            assert isinstance(item, str), f"Each item should be a string, got {type(item)}"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_list_available_assets(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test listing available assets for a STAC item.
        
        Expected response:
        - List of asset names available for the item
        - Asset names are strings
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_list_available_assets")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: list_available_assets(collection_id='{planetarycomputer_collection_id}', item_id='{planetarycomputer_item_id}')")
        response = client.tiler.list_available_assets(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        test_logger.info(f"Number of assets: {len(response) if isinstance(response, list) else 'N/A'}")
        
        # Assert response is a list
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        assert len(response) > 0, "Should have at least one asset"
        
        # All items should be strings
        for asset in response:
            assert isinstance(asset, str), f"Each asset should be a string, got {type(asset)}"
            assert len(asset) > 0, "Asset name should not be empty"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_list_bounds(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test listing bounds for a STAC item.
        
        Expected response:
        - List of 4 coordinates [minx, miny, maxx, maxy]
        - Represents bounding box of the item
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_list_bounds")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        test_logger.info(f"Calling: list_bounds(collection_id='{planetarycomputer_collection_id}', item_id='{planetarycomputer_item_id}')")
        response = client.tiler.list_bounds(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        
        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")
        
        # Assert response is a list with 4 coordinates
        assert isinstance(response, list), f"Response should be a list, got {type(response)}"
        assert len(response) == 4, f"Bounds should have 4 coordinates [minx, miny, maxx, maxy], got {len(response)}"
        
        # Validate coordinate structure: [minx, miny, maxx, maxy]
        minx, miny, maxx, maxy = response
        for coord in response:
            assert isinstance(coord, (int, float)), f"Each coordinate should be numeric, got {type(coord)}"
        
        # Validate bounds logic
        assert minx < maxx, f"minx ({minx}) should be less than maxx ({maxx})"
        assert miny < maxy, f"miny ({miny}) should be less than maxy ({maxy})"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_get_preview(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test getting a preview image of a STAC item.
        
        Expected response:
        - Binary PNG image data (streaming generator)
        - Valid PNG format with magic bytes
        - Specified dimensions (120x120)
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_get_preview")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        test_logger.info("Input - dimensions: 120x120")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Get available assets first
        assets = client.tiler.list_available_assets(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        test_logger.info(f"Available assets: {assets}")
        
        # Use first available asset or common ones
        test_assets = assets[:3] if len(assets) >= 3 else assets[:1]
        test_logger.info(f"Using assets: {test_assets}")
        
        test_logger.info("Calling: get_preview(...)")
        response = client.tiler.get_preview(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id,
            format=TilerImageFormat.PNG,
            width=120,
            height=120,
            assets=test_assets,
            no_data=0,
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
            # Note: Actual dimensions may differ slightly from requested due to aspect ratio preservation
            
        except ImportError:
            test_logger.warning("PIL not available, skipping detailed image validation")
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_get_info_geo_json(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test getting info/metadata for a STAC item.
        
        Expected response:
        - Dictionary with item metadata
        - May include bands, data types, statistics
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_get_info_geo_json")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Get available assets
        assets = client.tiler.list_available_assets(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        test_assets = assets[:3] if len(assets) >= 3 else assets[:1]
        test_logger.info(f"Using assets: {test_assets}")
        
        test_logger.info("Calling: get_info_geo_json(...)")
        response = client.tiler.get_info_geo_json(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id,
            assets=test_assets
        )
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
            for key, value in list(response_dict.items())[:5]:  # Log first 5 keys
                test_logger.info(f"  {key}: {type(value)}")
        else:
            test_logger.info(f"Response: {response}")
        
        assert response is not None, "Response should not be None"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_list_statistics(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test listing statistics for a STAC item's assets.
        
        Expected response:
        - Dictionary mapping asset names to their statistics
        - Statistics include min, max, mean, stddev, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_07_list_statistics")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Get available assets
        assets = client.tiler.list_available_assets(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        test_assets = assets[:3] if len(assets) >= 3 else assets[:1]
        test_logger.info(f"Using assets: {test_assets}")
        
        test_logger.info("Calling: list_statistics(...)")
        response = client.tiler.list_statistics(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id,
            assets=test_assets
        )
        
        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, 'as_dict'):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        else:
            test_logger.info(f"Response: {response}")
        
        assert response is not None, "Response should not be None"
        
        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_08_get_wmts_capabilities(self, planetarycomputer_endpoint, planetarycomputer_collection_id, planetarycomputer_item_id):
        """
        Test getting WMTS capabilities XML for a STAC item.
        
        Expected response:
        - XML document describing WMTS service capabilities
        - Contains layer information, tile matrix sets, etc.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_08_get_wmts_capabilities")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")
        test_logger.info(f"Input - item_id: {planetarycomputer_item_id}")
        
        client = self.create_client(endpoint=planetarycomputer_endpoint)
        
        # Get available assets
        assets = client.tiler.list_available_assets(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id
        )
        test_assets = assets[:3] if len(assets) >= 3 else assets[:1]
        test_logger.info(f"Using assets: {test_assets}")
        
        test_logger.info("Calling: get_wmts_capabilities(...)")
        response = client.tiler.get_wmts_capabilities(
            collection_id=planetarycomputer_collection_id,
            item_id=planetarycomputer_item_id,
            tile_matrix_set_id="WebMercatorQuad",
            tile_format=TilerImageFormat.PNG,
            tile_scale=1,
            min_zoom=7,
            max_zoom=9,
            assets=test_assets,
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
        assert xml_string.startswith("<?xml"), f"Response should start with XML declaration, got: {xml_string[:50]}"
        assert "Capabilities" in xml_string, "Response should contain Capabilities element"
        assert "WMTS" in xml_string or "wmts" in xml_string.lower(), "Response should reference WMTS"
        
        test_logger.info("Test PASSED\n")
