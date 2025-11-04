# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Unit tests for Map Legend operations.
"""
import io
import logging
from pathlib import Path
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import recorded_by_proxy
from testpreparer_async import PlanetaryComputerProClientTestBaseAsync
from testpreparer import PlanetaryComputerPreparer
from azure.planetarycomputer.models import ColorMapNames

# Set up test logger
test_logger = logging.getLogger("test_map_legends")
test_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

# File handler for test logs
log_file = log_dir / "map_legends_test_results.log"
file_handler = logging.FileHandler(log_file, mode="w")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
test_logger.addHandler(file_handler)


class TestPlanetaryComputerMapLegendsAsync(PlanetaryComputerProClientTestBaseAsync):
    """Test suite for Map Legend operations."""

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_01_get_class_map_legend(self, planetarycomputer_endpoint):
        """
        Test getting a class map legend (categorical color map).

        Expected response structure:
        - Dictionary mapping class values (strings) to RGBA color arrays
        - Each color array has 4 integers [R, G, B, A] with values 0-255
        - MTBS Severity classes: 0-6 representing fire severity levels
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_01_get_class_map_legend")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - classmap_name: {ColorMapNames.MTBS_SEVERITY}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_class_map_legend(classmap_name={ColorMapNames.MTBS_SEVERITY})"
        )
        response = await client.data.get_class_map_legend(
            classmap_name=ColorMapNames.MTBS_SEVERITY,
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")

        # Assert response is a dictionary
        assert isinstance(
            response, dict
        ), f"Response should be a dict, got {type(response)}"
        assert len(response) > 0, "Response should not be empty"

        # Assert MTBS Severity classes are present (0-6)
        expected_classes = ["0", "1", "2", "3", "4", "5", "6"]
        for class_value in expected_classes:
            assert (
                class_value in response
            ), f"Class '{class_value}' should be in response"

        # Validate color structure for each class
        for class_value, color in response.items():
            # Each color should be a list/array of 4 RGBA values
            assert isinstance(
                color, (list, tuple)
            ), f"Color for class '{class_value}' should be a list/tuple"
            assert (
                len(color) == 4
            ), f"Color for class '{class_value}' should have 4 RGBA values, got {len(color)}"

            # Each RGBA component should be an integer 0-255
            for i, component in enumerate(color):
                component_name = ["R", "G", "B", "A"][i]
                assert isinstance(
                    component, int
                ), f"{component_name} for class '{class_value}' should be int"
                assert (
                    0 <= component <= 255
                ), f"{component_name} for class '{class_value}' should be 0-255, got {component}"

        # Validate specific colors for known MTBS severity classes
        # Class 0: Transparent (no fire)
        assert response["0"] == [0, 0, 0, 0], "Class 0 should be transparent black"

        # Class 4: Red (high severity)
        assert (
            response["4"][0] == 255
        ), "Class 4 (high severity) should have high red component"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_02_get_interval_legend(self, planetarycomputer_endpoint):
        """
        Test getting an interval legend (continuous color map).

        Expected response structure:
        - List of intervals, each containing [[min, max], [R, G, B, A]]
        - Intervals represent continuous value ranges with color gradients
        - MODIS64_A1: Fire radiative power intervals
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_02_get_interval_legend")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - classmap_name: {ColorMapNames.MODIS64_A1}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_interval_legend(classmap_name={ColorMapNames.MODIS64_A1})"
        )
        response = await client.data.get_interval_legend(
            classmap_name=ColorMapNames.MODIS64_A1
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")

        # Assert response is a list
        assert isinstance(
            response, list
        ), f"Response should be a list, got {type(response)}"
        assert len(response) > 0, "Response should not be empty"

        # Validate each interval structure
        for idx, interval in enumerate(response):
            # Each interval should be a list with 2 elements: [range, color]
            assert isinstance(interval, list), f"Interval {idx} should be a list"
            assert (
                len(interval) == 2
            ), f"Interval {idx} should have 2 elements: [[min, max], [R, G, B, A]]"

            # Validate range component
            value_range = interval[0]
            assert isinstance(
                value_range, list
            ), f"Interval {idx} range should be a list"
            assert len(value_range) == 2, f"Interval {idx} range should have [min, max]"
            min_val, max_val = value_range
            assert isinstance(
                min_val, (int, float)
            ), f"Interval {idx} min should be numeric"
            assert isinstance(
                max_val, (int, float)
            ), f"Interval {idx} max should be numeric"
            assert (
                min_val <= max_val
            ), f"Interval {idx} min ({min_val}) should be <= max ({max_val})"

            # Validate color component
            color = interval[1]
            assert isinstance(color, list), f"Interval {idx} color should be a list"
            assert len(color) == 4, f"Interval {idx} color should have 4 RGBA values"
            for i, component in enumerate(color):
                component_name = ["R", "G", "B", "A"][i]
                assert isinstance(
                    component, int
                ), f"Interval {idx} {component_name} should be int"
                assert (
                    0 <= component <= 255
                ), f"Interval {idx} {component_name} should be 0-255"

        # Validate intervals are sequential (each max should connect to next min)
        for i in range(len(response) - 1):
            current_max = response[i][0][1]
            next_min = response[i + 1][0][0]
            # Allow some tolerance for continuous intervals
            assert (
                abs(current_max - next_min) <= 1
            ), f"Interval {i} max ({current_max}) should connect to interval {i+1} min ({next_min})"

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_03_get_legend_as_png(self, planetarycomputer_endpoint):
        """
        Test getting a legend as a PNG image.

        Expected response:
        - Binary PNG image data (streaming generator)
        - Valid PNG format with magic bytes
        - Typical size: ~500-600 bytes
        - Dimensions: ~387x11 pixels for horizontal color gradient
        - RGBA color mode
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_03_get_legend_as_png")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info("Input - color_map_name: rdylgn")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Calling: get_legend(color_map_name='rdylgn')")
        response = await client.data.get_legend(color_map_name="rdylgn")

        test_logger.info(f"Response type: {type(response)}")

        # Collect the streaming response into bytes
        legend_bytes = b"".join([chunk async for chunk in response])
        test_logger.info(f"Legend size: {len(legend_bytes)} bytes")
        test_logger.info(f"First 16 bytes (hex): {legend_bytes[:16].hex()}")

        # Verify PNG magic bytes (89 50 4E 47 0D 0A 1A 0A)
        png_magic = b"\x89PNG\r\n\x1a\n"
        test_logger.info(f"PNG magic bytes: {png_magic.hex()}")
        test_logger.info(
            f"Response starts with PNG magic: {legend_bytes[:8] == png_magic}"
        )

        # Assert response is valid PNG
        assert len(legend_bytes) > 0, "Legend bytes should not be empty"
        assert (
            len(legend_bytes) > 100
        ), f"Legend should be substantial image, got only {len(legend_bytes)} bytes"
        assert (
            legend_bytes[:8] == png_magic
        ), "Response should be a valid PNG image (magic bytes mismatch)"

        # Parse and validate the PNG image
        try:
            from PIL import Image as PILImage

            legend_image = PILImage.open(io.BytesIO(legend_bytes))
            test_logger.info(f"PIL Image format: {legend_image.format}")
            test_logger.info(f"PIL Image size: {legend_image.size}")
            test_logger.info(f"PIL Image mode: {legend_image.mode}")

            # Assert image properties
            assert legend_image.format == "PNG", "Image format should be PNG"

            # Image dimensions should be non-zero
            width, height = legend_image.size
            assert (
                width > 0 and height > 0
            ), f"Image should have non-zero dimensions, got {width}x{height}"

            # Typical legend is horizontal (width >> height)
            assert (
                width > height
            ), f"Legend should be horizontal (width > height), got {width}x{height}"

            # Color mode should be RGBA (with alpha channel)
            assert (
                legend_image.mode == "RGBA"
            ), f"Image mode should be RGBA, got {legend_image.mode}"

        except ImportError:
            test_logger.warning("PIL not available, skipping image parsing")

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_04_get_legend_with_different_colormap(
        self, planetarycomputer_endpoint
    ):
        """
        Test getting a legend with a different color map (viridis).

        Validates that multiple colormaps work consistently and return valid PNG images.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_04_get_legend_with_different_colormap")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info("Input - color_map_name: viridis")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info("Calling: get_legend(color_map_name='viridis')")
        response = await client.data.get_legend(color_map_name="viridis")

        test_logger.info(f"Response type: {type(response)}")

        # Collect the streaming response into bytes
        legend_bytes = b"".join([chunk async for chunk in response])
        test_logger.info(f"Legend size: {len(legend_bytes)} bytes")

        # Verify PNG magic bytes
        png_magic = b"\x89PNG\r\n\x1a\n"
        assert len(legend_bytes) > 0, "Legend bytes should not be empty"
        assert (
            len(legend_bytes) > 100
        ), f"Legend should be substantial image, got only {len(legend_bytes)} bytes"
        assert legend_bytes[:8] == png_magic, "Response should be a valid PNG image"

        # Parse and validate the PNG image
        try:
            from PIL import Image as PILImage

            legend_image = PILImage.open(io.BytesIO(legend_bytes))
            test_logger.info(f"PIL Image format: {legend_image.format}")
            test_logger.info(f"PIL Image size: {legend_image.size}")
            test_logger.info(f"PIL Image mode: {legend_image.mode}")

            # Validate basic image properties
            assert legend_image.format == "PNG", "Image format should be PNG"
            width, height = legend_image.size
            assert width > 0 and height > 0, "Image should have non-zero dimensions"
            assert width > height, "Legend should be horizontal"

        except ImportError:
            test_logger.warning("PIL not available, skipping image parsing")

        test_logger.info("Test PASSED\n")

        await self.close_client()

    @PlanetaryComputerPreparer()
    @recorded_by_proxy_async
    async def test_05_class_map_legend_structure(self, planetarycomputer_endpoint):
        """
        Test class map legend structure and validate color consistency.

        Validates that class maps return consistent color mappings for categorical data.
        """
        test_logger.info("=" * 80)
        test_logger.info("TEST: test_05_class_map_legend_structure")
        test_logger.info("=" * 80)
        test_logger.info(f"Input - endpoint: {planetarycomputer_endpoint}")
        test_logger.info(f"Input - classmap_name: {ColorMapNames.MTBS_SEVERITY}")

        client = self.create_client(endpoint=planetarycomputer_endpoint)

        test_logger.info(
            f"Calling: get_class_map_legend(classmap_name={ColorMapNames.MTBS_SEVERITY})"
        )
        response = await client.data.get_class_map_legend(
            classmap_name=ColorMapNames.MTBS_SEVERITY,
        )

        test_logger.info(f"Response type: {type(response)}")
        test_logger.info(f"Response: {response}")

        # Assert response is a dictionary
        assert isinstance(response, dict), "Response should be a dict"

        # Validate all keys are string class values
        for key in response.keys():
            assert isinstance(key, str), f"Key '{key}' should be a string"

        # Validate color consistency - all colors should be [R, G, B, A] format
        all_colors = list(response.values())
        for color in all_colors:
            assert len(color) == 4, "All colors should have RGBA format"
            assert all(
                isinstance(c, int) and 0 <= c <= 255 for c in color
            ), "All color components should be integers 0-255"

        # Validate that different classes have different colors (except transparent)
        non_transparent_colors = [
            tuple(c) for c in all_colors if c[3] != 0
        ]  # Exclude transparent
        # Convert to set to check uniqueness
        unique_colors = set(non_transparent_colors)
        assert (
            len(unique_colors) > 1
        ), "Non-transparent classes should have different colors"

        test_logger.info(
            f"Found {len(response)} classes with {len(unique_colors)} unique non-transparent colors"
        )
        test_logger.info("Test PASSED\n")

        await self.close_client()
