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
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import recorded_by_proxy
from testpreparer_async import PlanetaryComputerProClientTestBaseAsync
from testpreparer import PlanetaryComputerPreparer
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
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerMosaicsTilerAsync(PlanetaryComputerProClientTestBaseAsync):
    """Test suite for Mosaics Tiler operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_01_register_mosaics_search(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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

        # Create search parameters - filter to 2021-2022 date range
        register_search_request = StacSearchParameters(
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        test_logger.info(f"Search request: {register_search_request}")

        test_logger.info("Calling: register_mosaics_search(...)")
        response = await client.data.register_mosaics_search(register_search_request)

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(
            response, "search_id"
        ), "Response should have 'search_id' attribute"

        search_id = response.search_id
        assert isinstance(
            search_id, str
        ), f"Search ID should be a string, got {type(search_id)}"
        assert len(search_id) > 0, "Search ID should not be empty"

        test_logger.info(f"Search ID: {search_id}")
        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_02_get_mosaics_search_info(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Registered search ID: {search_id}")

        test_logger.info(f"Calling: get_mosaics_search_info(search_id='{search_id}')")
        response = await client.data.get_mosaics_search_info(search_id=search_id)

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")

        # Validate response structure
        assert response is not None, "Response should not be None"
        assert hasattr(response, "search"), "Response should have 'search' attribute"

        search = response.search
        test_logger.info(f"Search type: {type(search)}")
        assert search is not None, "Search should not be None"
        assert hasattr(search, "hash"), "Search should have 'hash' attribute"

        search_hash = search.hash
        assert isinstance(
            search_hash, str
        ), f"Search hash should be a string, got {type(search_hash)}"
        assert len(search_hash) > 0, "Search hash should not be empty"

        test_logger.info(f"Search hash: {search_hash}")
        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_03_get_mosaics_tile_json(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Using search ID: {search_id}")

        test_logger.info("Calling: get_mosaics_tile_json(...)")
        response = await client.data.get_mosaics_tile_json(
            search_id=search_id,
            tile_matrix_set_id="WebMercatorQuad",
            assets=["image"],
            asset_band_indices="image|1,2,3",
            tile_scale=1,
            min_zoom=9,
            collection=planetarycomputer_collection_id,
            tile_format="png",
        )

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
            test_logger.info(f"TileJSON version: {response_dict.get('tilejson')}")

        # Validate TileJSON structure (note: attributes accessed via as_dict() for serialization)
        assert response is not None, "Response should not be None"
        response_dict = response.as_dict() if hasattr(response, "as_dict") else response

        # Validate key fields exist
        assert "tilejson" in response_dict, "Response should have 'tilejson' key"
        assert "tiles" in response_dict, "Response should have 'tiles' key"

        # Validate tiles array
        tiles = response_dict["tiles"]
        assert isinstance(tiles, list), "Tiles should be a list"
        assert len(tiles) > 0, "Should have at least one tile URL pattern"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_04_get_mosaics_tile(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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
        test_logger.info("Input - tile coordinates: z=13, x=2174, y=3282")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Register search
        register_search_request = StacSearchParameters(
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Using search ID: {search_id}")

        test_logger.info("Calling: get_mosaics_tile(...)")
        response = await client.data.get_mosaics_tile(
            search_id=search_id,
            tile_matrix_set_id="WebMercatorQuad",
            z=13,
            x=2174,
            y=3282,
            scale=1,
            format="png",
            assets=["image"],
            asset_band_indices="image|1,2,3",
            collection=planetarycomputer_collection_id,
        )

        test_logger.info(f"Response type: {type(response)}")

        # Collect the streaming response into bytes
        image_bytes = b"".join([chunk async for chunk in response])
        test_logger.info(f"Image size: {len(image_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {image_bytes[:16].hex()}")

        # Verify PNG magic bytes
        png_magic = b"\x89PNG\r\n\x1a\n"
        assert len(image_bytes) > 0, "Image bytes should not be empty"
        assert (
            len(image_bytes) > 100
        ), f"Image should be substantial, got only {len(image_bytes)} bytes"
        assert (
            image_bytes[:8] == png_magic
        ), "Response should be a valid PNG image (magic bytes mismatch)"

        # Parse and validate the PNG image
        try:
            from PIL import Image as PILImage

            image = PILImage.open(io.BytesIO(image_bytes))
            test_logger.info(f"PIL Image format: {image.format}")
            test_logger.info(f"PIL Image size: {image.size}")
            test_logger.info(f"PIL Image mode: {image.mode}")

            # Validate image properties
            assert (
                image.format == "PNG"
            ), f"Image format should be PNG, got {image.format}"
            width, height = image.size
            assert (
                width > 0 and height > 0
            ), f"Image should have non-zero dimensions, got {width}x{height}"

        except ImportError:
            test_logger.warning("PIL not available, skipping detailed image validation")

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_05_get_mosaics_wmts_capabilities(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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

        # Register search
        register_search_request = StacSearchParameters(
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Using search ID: {search_id}")

        test_logger.info("Calling: get_mosaics_wmts_capabilities(...)")
        response = await client.data.get_mosaics_wmts_capabilities(
            search_id=search_id,
            tile_matrix_set_id="WebMercatorQuad",
            tile_format=TilerImageFormat.PNG,
            tile_scale=1,
            min_zoom=7,
            max_zoom=13,
            assets=["image"],
            asset_band_indices="image|1,2,3",
        )

        test_logger.info(f"Response type: {type(response)}")

        # Collect XML bytes
        xml_bytes = b"".join([chunk async for chunk in response])
        test_logger.info(f"XML size: {len(xml_bytes)} bytes")

        # Decode to string
        xml_string = xml_bytes.decode("utf-8")
        test_logger.info(f"XML first 200 chars: {xml_string[:200]}")

        # Validate XML structure
        assert len(xml_bytes) > 0, "XML bytes should not be empty"
        # Note: WMTS Capabilities XML may not have <?xml declaration
        assert (
            "<Capabilities" in xml_string
        ), "Response should contain Capabilities element"
        assert (
            "WMTS" in xml_string or "wmts" in xml_string.lower()
        ), "Response should reference WMTS"
        assert (
            "TileMatrix" in xml_string
        ), "Response should contain TileMatrix information"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_06_get_mosaics_assets_for_point(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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
        test_logger.info(
            "Input - point: longitude=-84.43202751899601, latitude=33.639647639722273"
        )

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Register search
        register_search_request = StacSearchParameters(
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Using search ID: {search_id}")

        test_logger.info("Calling: get_mosaics_assets_for_point(...)")
        response = await client.data.get_mosaics_assets_for_point(
            search_id=search_id,
            longitude=-84.43202751899601,
            latitude=33.639647639722273,
            coordinate_reference_system="EPSG:4326",
            items_limit=100,
            exit_when_full=True,
            scan_limit=100,
            skip_covered=True,
            time_limit=30,
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(
            f"Number of assets: {len(response) if isinstance(response, list) else 'N/A'}"
        )

        # Validate response structure
        assert isinstance(
            response, list
        ), f"Response should be a list, got {type(response)}"

        # If we have assets, validate structure
        if len(response) > 0:
            first_asset = response[0]
            test_logger.info(f"First asset type: {type(first_asset)}")

            # Asset is a StacAsset object that can be accessed as dict
            assert first_asset is not None, "First asset should not be None"

            # StacAsset behaves like a dict - access via key
            asset_dict = (
                first_asset.as_dict()
                if hasattr(first_asset, "as_dict")
                else first_asset
            )
            assert (
                "id" in asset_dict
            ), f"Asset should have 'id' key, got keys: {list(asset_dict.keys())}"

            asset_id = asset_dict["id"]
            test_logger.info(f"First asset ID: {asset_id}")
            assert isinstance(
                asset_id, str
            ), f"Asset ID should be a string, got {type(asset_id)}"
            assert len(asset_id) > 0, "Asset ID should not be empty"
        else:
            test_logger.info("No assets returned for this point")

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_07_get_mosaics_assets_for_tile(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
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
        test_logger.info("Input - tile coordinates: z=13, x=2174, y=3282")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Register search
        register_search_request = StacSearchParameters(
            filter={
                "op": "and",
                "args": [
                    {
                        "op": "=",
                        "args": [
                            {"property": "collection"},
                            planetarycomputer_collection_id,
                        ],
                    },
                    {
                        "op": ">=",
                        "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"],
                    },
                    {
                        "op": "<=",
                        "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"],
                    },
                ],
            },
            filter_lang=FilterLanguage.CQL2_JSON,
            sort_by=[
                StacSortExtension(
                    direction=StacSearchSortingDirection.DESC, field="datetime"
                )
            ],
        )
        register_response = await client.data.register_mosaics_search(
            register_search_request
        )
        search_id = register_response.search_id
        test_logger.info(f"Using search ID: {search_id}")

        test_logger.info("Calling: get_mosaics_assets_for_tile(...)")
        response = await client.data.get_mosaics_assets_for_tile(
            search_id=search_id,
            tile_matrix_set_id="WebMercatorQuad",
            z=13,
            x=2174,
            y=3282,
            collection_id=planetarycomputer_collection_id,
        )

        test_logger.info(f"Response type: {type(response)}")
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response keys: {list(response_dict.keys())}")
        else:
            test_logger.info(f"Response: {response}")

        # Validate response is not None
        assert response is not None, "Response should not be None"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_08_create_static_image(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test creating a static image from a mosaic search.

        Expected response:
        - Object with image ID that can be used to retrieve the image
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_08_create_static_image")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        from azure.planetarycomputer.models import (
            ImageParameters,
            Polygon,
        )

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # Define geometry for the static image
        geometry = Polygon(
            coordinates=[
                [
                    [-84.45378097481053, 33.6567321707079],
                    [-84.39805886744838, 33.6567321707079],
                    [-84.39805886744838, 33.61945681366625],
                    [-84.45378097481053, 33.61945681366625],
                    [-84.45378097481053, 33.6567321707079],
                ]
            ]
        )

        test_logger.info(f"Geometry: {geometry}")

        # Create CQL2-JSON filter
        cql_filter = {
            "op": "and",
            "args": [
                {
                    "op": "=",
                    "args": [
                        {"property": "collection"},
                        planetarycomputer_collection_id,
                    ],
                },
                {
                    "op": "anyinteracts",
                    "args": [
                        {"property": "datetime"},
                        {"interval": ["2023-01-01T00:00:00Z", "2023-12-31T00:00:00Z"]},
                    ],
                },
            ],
        }

        # Create image request
        image_request = ImageParameters(
            cql=cql_filter,
            zoom=13,
            geometry=geometry,
            render_parameters=f"assets=image&asset_bidx=image|1,2,3&collection={planetarycomputer_collection_id}",
            columns=1080,
            rows=1080,
            image_size="1080x1080",
            show_branding=False,
        )

        test_logger.info(
            f"Image request: columns={image_request.columns}, rows={image_request.rows}, zoom={image_request.zoom}"
        )

        test_logger.info("Calling: create_static_image(...)")
        response = await client.data.create_static_image(
            collection_id=planetarycomputer_collection_id, body=image_request
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")

        # Log response details based on type
        if hasattr(response, "as_dict"):
            response_dict = response.as_dict()
            test_logger.info(f"Response dict keys: {list(response_dict.keys())}")
            test_logger.info(f"Response dict: {response_dict}")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_09_get_static_image(
        self, planetarycomputer_endpoint, planetarycomputer_collection_id
    ):
        """
        Test retrieving a static image by ID.

        Expected response:
        - Binary image data (streaming generator)
        - Valid PNG format with magic bytes
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_09_get_static_image")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - collection_id: {planetarycomputer_collection_id}")

        from azure.planetarycomputer.models import (
            ImageParameters,
            Polygon,
        )

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        # First create a static image to get an ID
        geometry = Polygon(
            coordinates=[
                [
                    [-84.45378097481053, 33.6567321707079],
                    [-84.39805886744838, 33.6567321707079],
                    [-84.39805886744838, 33.61945681366625],
                    [-84.45378097481053, 33.61945681366625],
                    [-84.45378097481053, 33.6567321707079],
                ]
            ]
        )

        cql_filter = {
            "op": "and",
            "args": [
                {
                    "op": "=",
                    "args": [
                        {"property": "collection"},
                        planetarycomputer_collection_id,
                    ],
                },
                {
                    "op": "anyinteracts",
                    "args": [
                        {"property": "datetime"},
                        {"interval": ["2023-01-01T00:00:00Z", "2023-12-31T00:00:00Z"]},
                    ],
                },
            ],
        }

        image_request = ImageParameters(
            cql=cql_filter,
            zoom=13,
            geometry=geometry,
            render_parameters=f"assets=image&asset_bidx=image|1,2,3&collection={planetarycomputer_collection_id}",
            columns=1080,
            rows=1080,
            image_size="1080x1080",
            show_branding=False,
        )

        create_response = await client.data.create_static_image(
            collection_id=planetarycomputer_collection_id, body=image_request
        )

        url = create_response.url

        # Extract image ID from URL - split by '?' to remove query params, then get last path segment
        image_id = url.split("?")[0].split("/")[-1]

        test_logger.info(f"Created image with ID: {image_id}")
        test_logger.info(f"Image URL: {url}")

        # Assert that we got a valid image ID
        assert (
            image_id is not None and len(image_id) > 0
        ), f"Failed to get image ID from create_static_image response: {create_response}"

        test_logger.info(
            f"Calling: get_static_image(collection_id='{planetarycomputer_collection_id}', id='{image_id}')"
        )
        image_data = await client.data.get_static_image(
            collection_id=planetarycomputer_collection_id, id=image_id
        )

        test_logger.info(f"Image data type: {type(image_data)}")

        # Collect the streaming response into bytes
        image_bytes = b"".join([chunk async for chunk in image_data])
        test_logger.info(f"Image size: {len(image_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {image_bytes[:16].hex()}")

        await self.close_client()
