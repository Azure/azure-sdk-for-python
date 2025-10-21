# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_04_stac_item_tiler.py

DESCRIPTION:
    This sample demonstrates STAC item tiling operations from the Azure Planetary Computer Pro SDK.
    Includes asset information retrieval, statistics, tiling, cropping, and preview operations.
    Uses NAIP sample datasets and saves tiles locally.

USAGE:
    python planetary_computer_04_stac_item_tiler.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
"""

import os
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import TilerImageFormat, Polygon, Feature, FeatureType

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def display_response(response, filename):
    """Save image response data locally."""
    image_bytes = b"".join(response)
    with open(filename, "wb") as f:
        f.write(image_bytes)
    logging.info(f"Image saved as: {filename} ({len(image_bytes)} bytes)")


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
    result = client.tiler.get_asset_statistics(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"]
    )
    logging.info(result)


def list_available_assets(client, collection_id, item_id):
    """List available assets for an item."""
    result = client.tiler.list_available_assets(collection_id=collection_id, item_id=item_id)
    logging.info(result)


def get_assets_info(client, collection_id, item_id):
    """Get basic info for dataset's assets.
    
    Returns dataset's basic information including data types, bounds, and other metadata
    for the specified assets. If no assets are specified, returns info for all assets.
    """
    
    # Get info for specific assets
    result_specific = client.tiler.get_assets_info(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"]
    )
    logging.info("Assets info (image asset only):")
    logging.info(f"  Dataset: {result_specific}")


def list_bounds(client, collection_id, item_id):
    """List bounds for an item."""
    result = client.tiler.list_bounds(collection_id=collection_id, item_id=item_id)
    logging.info(result)


def crop_geo_json(client, collection_id, item_id, geojson):
    """Crop an item using GeoJSON geometry."""
    crop_geo_json_response = client.tiler.crop_geo_json(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
        body=geojson,
    )
    logging.info("Cropping with GeoJSON completed")
    display_response(crop_geo_json_response, f"crop_geojson_{item_id}.png")


def crop_geo_json_with_dimensions(client, collection_id, item_id, geojson):
    """Crop an item using GeoJSON geometry with specific dimensions."""
    crop_geo_json_with_dimensions_response = client.tiler.crop_geo_json_with_dimensions(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
        body=geojson,
    )
    display_response(crop_geo_json_with_dimensions_response, f"crop_geojson_dims_{item_id}.png")


def get_geo_json_statistics(client, collection_id, item_id, geojson):
    """Get statistics for a GeoJSON area."""
    result = client.tiler.get_geo_json_statistics(
        collection_id=collection_id,
        item_id=item_id,
        body=geojson,
        assets=["image"]
    )
    logging.info(result)


def get_info_geo_json(client, collection_id, item_id):
    """Get info for GeoJSON."""
    result = client.tiler.get_info_geo_json(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"]
    )
    logging.info(result)


def get_part(client, collection_id, item_id, bounds):
    """Get a part of an item with specific bounds."""
    get_part_response = client.tiler.get_part(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        minx=bounds[0],
        miny=bounds[1],
        maxx=bounds[2],
        maxy=bounds[3],
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    display_response(get_part_response, f"part_{item_id}.png")


def get_part_with_dimensions(client, collection_id, item_id, bounds):
    """Get a part of an item with specific bounds and dimensions."""
    get_part_with_dimensions_response = client.tiler.get_part_with_dimensions(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        minx=bounds[0],
        miny=bounds[1],
        maxx=bounds[2],
        maxy=bounds[3],
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    display_response(get_part_with_dimensions_response, f"part_dims_{item_id}.png")


def get_point(client, collection_id, item_id, point):
    """Get point value at a specific location."""
    result = client.tiler.get_point(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"],
        longitude=point[0],
        latitude=point[1],
        no_data=0,
    )
    logging.info(f"Point values at ({point[0]}, {point[1]}): {result}")


def get_preview(client, collection_id, item_id):
    """Get a preview of an item."""
    get_preview_response = client.tiler.get_preview(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    display_response(get_preview_response, f"preview_{item_id}.png")


def get_preview_with_format(client, collection_id, item_id):
    """Get a preview of an item with specific format."""
    get_preview_with_format_response = client.tiler.get_preview_with_format(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    display_response(get_preview_with_format_response, f"preview_format_{item_id}.png")


def list_statistics(client, collection_id, item_id):
    """List statistics for an item."""
    result = client.tiler.list_statistics(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"]
    )
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
        max_zoom=14,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    logging.info(result)


def get_tile(client, collection_id, item_id):
    """Get a specific tile and save it locally."""
    get_tile_with_matrix_set_response = client.tiler.get_tile(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        z=14,
        x=4349,
        y=6564,
        scale=1,
        format="png",
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    display_response(get_tile_with_matrix_set_response, f"tile_{item_id}_z14_x4349_y6564.png")


def get_wmts_capabilities(client, collection_id, item_id):
    """Get WMTS capabilities and save it locally."""
    get_wmts_capabilities_response = client.tiler.get_wmts_capabilities(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=14,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    xml_bytes = b"".join(get_wmts_capabilities_response)
    xml_string = xml_bytes.decode("utf-8")

    filename = f"wmts_capabilities_{item_id}.xml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_string)
    logging.info(f"WMTS capabilities saved as: {filename}")


def main():
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")
    item_id = os.environ.get("PLANETARYCOMPUTER_ITEM_ID")

    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Define geometry for operations - Georgia NAIP area
    geometry = Polygon(
        coordinates=[
            [
                [-84.43809697097522, 33.63093193547549],
                [-84.41844018562179, 33.63093193547549],
                [-84.41844018562179, 33.64850313084044],
                [-84.43809697097522, 33.64850313084044],
                [-84.43809697097522, 33.63093193547549],
            ]
        ]
    )
    geojson = Feature(type=FeatureType.FEATURE, geometry=geometry, properties={})

    # Calculate bounds and center point from polygon
    bounds = [-84.43809697097522, 33.63093193547549, -84.41844018562179, 33.64850313084044]
    point = [-84.428268578298505, 33.639717533157965]

    # Execute tiler operations
    get_tile_matrix_definitions(client)
    list_tile_matrices(client)
    get_asset_statistics(client, collection_id, item_id)  # Not supported for NAIP
    list_available_assets(client, collection_id, item_id)
    get_assets_info(client, collection_id, item_id)
    list_bounds(client, collection_id, item_id)
    crop_geo_json(client, collection_id, item_id, geojson)
    crop_geo_json_with_dimensions(client, collection_id, item_id, geojson)
    get_geo_json_statistics(client, collection_id, item_id, geojson)
    get_info_geo_json(client, collection_id, item_id)
    get_part(client, collection_id, item_id, bounds)
    get_part_with_dimensions(client, collection_id, item_id, bounds)
    get_point(client, collection_id, item_id, point)
    get_preview(client, collection_id, item_id)
    get_preview_with_format(client, collection_id, item_id)
    list_statistics(client, collection_id, item_id)
    get_tile_json(client, collection_id, item_id)
    get_tile(client, collection_id, item_id)
    get_wmts_capabilities(client, collection_id, item_id)


if __name__ == "__main__":
    main()
