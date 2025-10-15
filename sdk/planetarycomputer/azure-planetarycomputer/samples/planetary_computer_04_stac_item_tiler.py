# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_04_stac_item_tiler.py

DESCRIPTION:
    This sample demonstrates STAC item tiling operations from the Azure Planetary Computer Pro SDK.

USAGE:
    python planetary_computer_04_stac_item_tiler.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
"""

import os
import io
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import TilerImageFormat, Polygon, Feature, FeatureType
from PIL import Image as PILImage

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def display_response(response):
    """Display image response data."""
    image_bytes = b"".join(response)
    image = PILImage.open(io.BytesIO(image_bytes))
    logging.info(f"Image loaded: {image.format} {image.size} {image.mode}")
    return image


def get_tile_matrix_definitions(client):
    """Get tile matrix definitions for WebMercatorQuad."""
    result = client.tiler.get_tile_matrix_definitions(tile_matrix_set_id="WebMercatorQuad")
    logging.info(result)


def list_tile_matrices(client):
    """List all available tile matrices."""
    result = client.tiler.list_tile_matrices()
    logging.info(result)


def get_asset_statistics(client, collection_id, item_id):
    """Get asset statistics for an item."""
    result = client.tiler.get_asset_statistics(collection_id=collection_id, item_id=item_id)
    logging.info(result)


def list_available_assets(client, collection_id, item_id):
    """List available assets for an item."""
    result = client.tiler.list_available_assets(collection_id=collection_id, item_id=item_id)
    logging.info(result)


def list_bounds(client, collection_id, item_id):
    """List bounds for an item."""
    result = client.tiler.list_bounds(collection_id=collection_id, item_id=item_id)
    logging.info(result)


def crop_geo_json(client, collection_id, item_id, geojson, assets):
    """Crop an item using GeoJSON geometry."""
    crop_geo_json_response = client.tiler.crop_geo_json(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        assets=assets,
        body=geojson,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    logging.info(crop_geo_json_response)
    display_response(crop_geo_json_response)


def crop_geo_json_with_dimensions(client, collection_id, item_id, geojson, assets):
    """Crop an item using GeoJSON geometry with specific dimensions."""
    crop_geo_json_with_dimensions_response = client.tiler.crop_geo_json_with_dimensions(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=assets,
        body=geojson,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    display_response(crop_geo_json_with_dimensions_response)


def get_geo_json_statistics(client, collection_id, item_id, geojson, assets):
    """Get statistics for a GeoJSON area."""
    result = client.tiler.get_geo_json_statistics(
        collection_id=collection_id, item_id=item_id, body=geojson, assets=assets
    )
    logging.info(result)


def get_info_geo_json(client, collection_id, item_id, assets):
    """Get info for GeoJSON."""
    result = client.tiler.get_info_geo_json(collection_id=collection_id, item_id=item_id, assets=assets)
    logging.info(result)


def get_part(client, collection_id, item_id, assets):
    """Get a part of an item with specific bounds."""
    get_part_response = client.tiler.get_part(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        minx=-4.35,
        miny=39.647784,
        maxx=-4.09,
        maxy=40.645928,
        width=120,
        height=120,
        assets=assets,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    display_response(get_part_response)


def get_part_with_dimensions(client, collection_id, item_id, assets):
    """Get a part of an item with specific bounds and dimensions."""
    get_part_with_dimensions_response = client.tiler.get_part_with_dimensions(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        minx=-4.35,
        miny=39.647784,
        maxx=-4.09,
        maxy=40.645928,
        width=120,
        height=120,
        assets=assets,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    display_response(get_part_with_dimensions_response)


def get_point(client, collection_id, item_id, assets):
    """Get point value at a specific location."""
    result = client.tiler.get_point(
        collection_id=collection_id, item_id=item_id, assets=assets, longitude=-4.09, latitude=39.91, no_data=0
    )
    logging.info(result)


def get_preview(client, collection_id, item_id, assets):
    """Get a preview of an item."""
    get_preview_response = client.tiler.get_preview(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=120,
        height=120,
        assets=assets,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    display_response(get_preview_response)


def get_preview_with_format(client, collection_id, item_id, assets):
    """Get a preview of an item with specific format."""
    get_preview_with_format_response = client.tiler.get_preview_with_format(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=120,
        height=120,
        assets=assets,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    display_response(get_preview_with_format_response)


def list_statistics(client, collection_id, item_id, assets):
    """List statistics for an item."""
    result = client.tiler.list_statistics(collection_id=collection_id, item_id=item_id, assets=assets)
    logging.info(result)


def get_tile_json(client, collection_id, item_id):
    """Get TileJSON for an item."""
    result = client.tiler.get_tile_json(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=9,
        assets=["red_20m", "green_20m", "blue_20m"],
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    logging.info(result)


def get_tile(client, collection_id, item_id):
    """Get a specific tile."""
    get_tile_with_matrix_set_response = client.tiler.get_tile(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        z=13,
        x=3998,
        y=3095,
        scale=1,
        format="png",
        assets=["red_20m", "green_20m", "blue_20m"],
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0.0,
    )
    display_response(get_tile_with_matrix_set_response)


def get_wmts_capabilities(client, collection_id, item_id, assets):
    """Get WMTS capabilities."""
    get_wmts_capabilities_response = client.tiler.get_wmts_capabilities(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=9,
        assets=assets,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0,
    )
    xml_bytes = b"".join(get_wmts_capabilities_response)
    xml_string = xml_bytes.decode("utf-8")
    logging.info(xml_string[:81])


def main():
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    collection_id = os.environ.get("AZURE_COLLECTION_ID", "sentinel-2-l2a")
    item_id = os.environ.get("AZURE_ITEM_ID", "S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602")
    assets = ["red", "green", "blue"]

    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Define geometry for operations that need it
    geometry = Polygon(
        coordinates=[
            [
                [-4.266, 40.231356],  # bottom-left
                [-4.174, 40.231356],  # bottom-right
                [-4.174, 40.323356],  # top-right
                [-4.266, 40.323356],  # top-left
                [-4.266, 40.231356],  # close the ring
            ]
        ]
    )
    geojson = Feature(type=FeatureType.FEATURE, geometry=geometry, properties={})

    # Execute tiler operations
    get_tile_matrix_definitions(client)
    list_tile_matrices(client)
    get_asset_statistics(client, collection_id, item_id)
    list_available_assets(client, collection_id, item_id)
    list_bounds(client, collection_id, item_id)
    crop_geo_json(client, collection_id, item_id, geojson, assets)
    crop_geo_json_with_dimensions(client, collection_id, item_id, geojson, assets)
    get_geo_json_statistics(client, collection_id, item_id, geojson, assets)
    get_info_geo_json(client, collection_id, item_id, assets)
    get_part(client, collection_id, item_id, assets)
    get_part_with_dimensions(client, collection_id, item_id, assets)
    get_point(client, collection_id, item_id, assets)
    get_preview(client, collection_id, item_id, assets)
    get_preview_with_format(client, collection_id, item_id, assets)
    list_statistics(client, collection_id, item_id, assets)
    get_tile_json(client, collection_id, item_id)
    get_tile(client, collection_id, item_id)
    get_wmts_capabilities(client, collection_id, item_id, assets)


if __name__ == "__main__":
    main()
