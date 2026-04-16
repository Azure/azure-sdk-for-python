# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for Collection-scoped Tiler operations.
"""
import logging
from pathlib import Path
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import PlanetaryComputerProClientTestBase, PlanetaryComputerPreparer
from azure.planetarycomputer.models import (
    TilerImageFormat,
    Feature,
    FeatureType,
    Polygon,
)

# Set up test logger
test_logger = logging.getLogger("test_collection_tiler")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "collection_tiler_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerCollectionTiler(PlanetaryComputerProClientTestBase):
    """Test suite for Collection-scoped Tiler operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_01_get_collection_info(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection tiler info."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_get_collection_info")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_info(
            collection_id=planetarycomputer_collection_id,
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE returns 404; managed storage not accessible for data operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_02_get_collection_point(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection point data at a specific location."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_get_collection_point")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Note: assets or expression is required for point queries (returns 400 without one)
        response = client.data.get_collection_point(
            collection_id=planetarycomputer_collection_id,
            longitude=-84.3860,
            latitude=33.6760,
            assets=["image"],
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE returns 404; managed storage not accessible for data operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_03_get_collection_point_assets(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection point assets at a specific location."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_collection_point_assets")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Note: assets or expression is required for point queries (returns 400 without one)
        response = client.data.get_collection_point_assets(
            collection_id=planetarycomputer_collection_id,
            longitude=-84.3860,
            latitude=33.6760,
            assets=["image"],
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE tile rendering returns 404; managed storage not accessible for tile operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_04_get_collection_tile(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting a collection tile."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_get_collection_tile")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_tile_by_scale_and_format(
            collection_id=planetarycomputer_collection_id,
            tile_matrix_set_id="WebMercatorQuad",
            z=14,
            x=4349,
            y=6564,
            scale=1,
            format="png",
            assets=["image"],
            asset_band_indices=["image|1,2,3"],
        )

        image_bytes = b"".join(response)
        test_logger.info(f"Tile size: {len(image_bytes)} bytes")

        assert len(image_bytes) > 0
        assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Should be PNG format"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_05_get_collection_tile_json(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection TileJSON metadata."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_get_collection_tile_json")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_tile_json(
            collection_id=planetarycomputer_collection_id,
            assets=["image"],
            asset_band_indices=["image|1,2,3"],
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"TileJSON keys: {list(response_dict.keys())}")

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE tile rendering returns 404; managed storage not accessible for tile operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_06_get_collection_bbox_crop(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting a bbox crop from a collection."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_06_get_collection_bbox_crop")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_bbox_crop(
            collection_id=planetarycomputer_collection_id,
            minx=-84.3930,
            miny=33.6798,
            maxx=-84.3670,
            maxy=33.7058,
            format="png",
            assets=["image"],
            asset_band_indices=["image|1,2,3"],
        )

        image_bytes = b"".join(response)
        test_logger.info(f"Image size: {len(image_bytes)} bytes")

        assert len(image_bytes) > 0, "Image bytes should not be empty"

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE collection lacks default mosaic metadata with assets for WMTS")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_07_get_collection_wmts_capabilities(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting WMTS capabilities for a collection."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_07_get_collection_wmts_capabilities")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_wmts_capabilities(
            collection_id=planetarycomputer_collection_id,
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        # WMTS returns XML
        if isinstance(response, bytes):
            assert b"WMTSCapabilities" in response or b"xml" in response
            test_logger.info(f"Response size: {len(response)} bytes")
        elif hasattr(response, '__iter__'):
            xml_bytes = b"".join(response)
            test_logger.info(f"Response size: {len(xml_bytes)} bytes")
            assert len(xml_bytes) > 0

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE tile rendering returns 404; managed storage not accessible for tile operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_08_crop_collection_feature_geo_json(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test cropping a collection by GeoJSON feature."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_08_crop_collection_feature_geo_json")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        geojson_feature = Feature(
            type=FeatureType.FEATURE,
            geometry=Polygon(
                coordinates=[
                    [
                        [-84.3930, 33.6798],
                        [-84.3670, 33.6798],
                        [-84.3670, 33.7058],
                        [-84.3930, 33.7058],
                        [-84.3930, 33.6798],
                    ]
                ]
            ),
            properties={},
        )

        response = client.data.crop_collection_feature_geo_json(
            collection_id=planetarycomputer_collection_id,
            body=geojson_feature,
            assets=["image"],
            asset_band_indices=["image|1,2,3"],
        )

        image_bytes = b"".join(response)
        test_logger.info(f"Image size: {len(image_bytes)} bytes")

        assert len(image_bytes) > 0, "Image bytes should not be empty"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_09_list_collection_tilesets(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test listing tilesets for a collection."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_09_list_collection_tilesets")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.list_collection_tilesets(
            collection_id=planetarycomputer_collection_id,
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @pytest.mark.skip(reason="PPE tile rendering returns 404; managed storage not accessible for tile operations")
    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_10_get_collection_assets_for_tile(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection assets for a specific tile."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_10_get_collection_assets_for_tile")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_assets_for_tile(
            collection_id=planetarycomputer_collection_id,
            tile_matrix_set_id="WebMercatorQuad",
            z=13,
            x=2174,
            y=3282,
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

    @PlanetaryComputerPreparer()
    @recorded_by_proxy
    def test_11_get_collection_tileset_metadata(self, planetarycomputer_endpoint, planetarycomputer_collection_id):
        """Test getting collection tileset metadata."""
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_11_get_collection_tileset_metadata")
        test_logger.info("=" * 80)

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        response = client.data.get_collection_tileset_metadata(
            collection_id=planetarycomputer_collection_id,
            tile_matrix_set_id="WebMercatorQuad",
        )

        test_logger.info(f"Response type: {type(response)}")
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")
