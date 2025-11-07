# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_04_stac_item_tiler_async.py

DESCRIPTION:
    This sample demonstrates STAC item tiling operations from the Azure Planetary Computer Pro SDK.
    Includes asset information retrieval, statistics, tiling, cropping, and preview operations.
    Uses sample datasets and saves tiles locally.

USAGE:
    python planetary_computer_04_stac_item_tiler_async.py

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
"""

import os
import asyncio
from azure.planetarycomputer.aio import PlanetaryComputerProClient
from azure.identity.aio import DefaultAzureCredential
from azure.planetarycomputer.models import (
    TilerImageFormat,
    Polygon,
    Feature,
    FeatureType,
)

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.ERROR
)
logging.basicConfig(level=logging.INFO)


async def display_response(response, filename):
    """Save image response data locally."""
    # Collect the async iterator into a list
    image_bytes_chunks = []
    async for chunk in response:
        image_bytes_chunks.append(chunk)
    image_bytes = b"".join(image_bytes_chunks)
    with open(filename, "wb") as f:
        f.write(image_bytes)
    logging.info(f"Image saved as: {filename} ({len(image_bytes)} bytes)")


async def get_tile_matrix_definitions(client: "PlanetaryComputerProClient"):
    """Get tile matrix definitions for WebMercatorQuad."""
    result = await client.data.get_tile_matrix_definitions(
        tile_matrix_set_id="WebMercatorQuad"
    )
    logging.info(result)


async def list_tile_matrices(client: "PlanetaryComputerProClient"):
    """List all available tile matrices."""
    result = client.data.list_tile_matrices()
    logging.info(result)


async def get_asset_statistics(
    client: PlanetaryComputerProClient, collection_id, item_id
):
    """Get asset statistics for an item."""
    result = await client.data.get_asset_statistics(
        collection_id=collection_id, item_id=item_id, assets=["image"]
    )
    logging.info(result)


async def list_available_assets(
    client: PlanetaryComputerProClient, collection_id, item_id
):
    """List available assets for an item."""
    result = client.data.list_available_assets(
        collection_id=collection_id, item_id=item_id
    )
    logging.info(result)


async def get_item_asset_details(
    client: PlanetaryComputerProClient, collection_id, item_id
):
    """Get basic info for dataset's assets.

    Returns dataset's basic information including data types, bounds, and other metadata
    for the specified assets. If no assets are specified, returns info for all assets.
    """

    # Get info for specific assets
    result_specific = await client.data.get_item_asset_details(
        collection_id=collection_id, item_id=item_id, assets=["image"]
    )
    logging.info("Assets info (image asset only):")
    logging.info(f"  Dataset: {result_specific}")


async def get_bounds(client: PlanetaryComputerProClient, collection_id, item_id):
    """List bounds for an item."""
    result = await client.data.get_bounds(collection_id=collection_id, item_id=item_id)
    logging.info(result)


async def crop_geo_json(
    client: PlanetaryComputerProClient, collection_id, item_id, geojson
):
    """Crop an item using GeoJSON geometry."""
    crop_geo_json_response = await client.data.crop_geo_json(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        assets=["image"],
        asset_band_indices="image|1,2,3",
        body=geojson,
    )
    logging.info("Cropping with GeoJSON completed")
    await display_response(crop_geo_json_response, f"crop_geojson_{item_id}.png")


async def crop_geo_json_with_dimensions(
    client: PlanetaryComputerProClient, collection_id, item_id, geojson
):
    """Crop an item using GeoJSON geometry with specific dimensions."""
    crop_geo_json_with_dimensions_response = (
        await client.data.crop_geo_json_with_dimensions(
            collection_id=collection_id,
            item_id=item_id,
            format=TilerImageFormat.PNG,
            width=512,
            height=512,
            assets=["image"],
            asset_band_indices="image|1,2,3",
            body=geojson,
        )
    )
    await display_response(
        crop_geo_json_with_dimensions_response, f"crop_geojson_dims_{item_id}.png"
    )


async def get_geo_json_statistics(
    client: PlanetaryComputerProClient, collection_id, item_id, geojson
):
    """Get statistics for a GeoJSON area."""
    result = await client.data.get_geo_json_statistics(
        collection_id=collection_id, item_id=item_id, body=geojson, assets=["image"]
    )
    logging.info(result)


async def get_info_geo_json(client: PlanetaryComputerProClient, collection_id, item_id):
    """Get info for GeoJSON."""
    result = await client.data.get_info_geo_json(
        collection_id=collection_id, item_id=item_id, assets=["image"]
    )
    logging.info(result)


async def get_part(client: PlanetaryComputerProClient, collection_id, item_id, bounds):
    """Get a part of an item with specific bounds."""
    get_part_response = await client.data.get_part(
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
        asset_band_indices="image|1,2,3",
    )
    await display_response(get_part_response, f"part_{item_id}.png")


async def get_part_with_dimensions(
    client: PlanetaryComputerProClient, collection_id, item_id, bounds
):
    """Get a part of an item with specific bounds and dimensions."""
    get_part_with_dimensions_response = await client.data.get_part_with_dimensions(
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
        asset_band_indices="image|1,2,3",
    )
    await display_response(
        get_part_with_dimensions_response, f"part_dims_{item_id}.png"
    )


async def get_point(client: PlanetaryComputerProClient, collection_id, item_id, point):
    """Get point value at a specific location."""
    result = await client.data.get_point(
        collection_id=collection_id,
        item_id=item_id,
        assets=["image"],
        longitude=point[0],
        latitude=point[1],
        no_data=0,
    )
    logging.info(f"Point values at ({point[0]}, {point[1]}): {result}")


async def get_preview(client: PlanetaryComputerProClient, collection_id, item_id):
    """Get a preview of an item."""
    get_preview_response = await client.data.get_preview(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices="image|1,2,3",
    )
    await display_response(get_preview_response, f"preview_{item_id}.png")


async def get_preview_with_format(
    client: PlanetaryComputerProClient, collection_id, item_id
):
    """Get a preview of an item with specific format."""
    get_preview_with_format_response = await client.data.get_preview_with_format(
        collection_id=collection_id,
        item_id=item_id,
        format=TilerImageFormat.PNG,
        width=512,
        height=512,
        assets=["image"],
        asset_band_indices="image|1,2,3",
    )
    await display_response(
        get_preview_with_format_response, f"preview_format_{item_id}.png"
    )


async def list_statistics(client: PlanetaryComputerProClient, collection_id, item_id):
    """List statistics for an item."""
    result = client.data.list_statistics(
        collection_id=collection_id, item_id=item_id, assets=["image"]
    )
    logging.info(result)


async def get_tile_json(client: PlanetaryComputerProClient, collection_id, item_id):
    """Get TileJSON for an item."""
    result = await client.data.get_tile_json(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=14,
        assets=["image"],
        asset_band_indices="image|1,2,3",
    )
    logging.info(result)


async def get_tile(client: PlanetaryComputerProClient, collection_id, item_id):
    """Get a specific tile and save it locally."""
    get_tile_with_matrix_set_response = await client.data.get_tile(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        z=14,
        x=4349,
        y=6564,
        scale=1,
        format="png",
        assets=["image"],
        asset_band_indices="image|1,2,3",
    )
    await display_response(
        get_tile_with_matrix_set_response, f"tile_{item_id}_z14_x4349_y6564.png"
    )


async def get_wmts_capabilities(
    client: PlanetaryComputerProClient, collection_id, item_id
):
    """Get WMTS capabilities and save it locally."""
    get_wmts_capabilities_response = await client.data.get_wmts_capabilities(
        collection_id=collection_id,
        item_id=item_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=14,
        assets=["image"],
        asset_band_indices="image|1,2,3",
    )
    # Collect the async iterator into a list
    xml_bytes_chunks = []
    async for chunk in get_wmts_capabilities_response:
        xml_bytes_chunks.append(chunk)
    xml_bytes = b"".join(xml_bytes_chunks)
    xml_string = xml_bytes.decode("utf-8")

    filename = f"wmts_capabilities_{item_id}.xml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_string)
    logging.info(f"WMTS capabilities saved as: {filename}")


async def main():
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("PLANETARYCOMPUTER_ENDPOINT environment variable must be set")

    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")
    item_id = "ga_m_3308421_se_16_060_20211114"

    credential = DefaultAzureCredential()

    client = PlanetaryComputerProClient(endpoint=endpoint, credential=credential)

    # Define geometry for operations
    geometry = Polygon(
        coordinates=[
            [
                [-84.3906, 33.6714],  # bottom-left
                [-84.3814, 33.6714],  # bottom-right
                [-84.3814, 33.6806],  # top-right
                [-84.3906, 33.6806],  # top-left
                [-84.3906, 33.6714],  # close the ring
            ]
        ]
    )
    geojson = Feature(type=FeatureType.FEATURE, geometry=geometry, properties={})

    # Calculate bounds and center point from polygon (within actual dataset bounds)
    bounds = [-84.3930, 33.6798, -84.3670, 33.7058]
    point = [-84.3860, 33.6760]

    # Execute tiler operations
    await get_tile_matrix_definitions(client)
    await list_tile_matrices(client)
    await get_asset_statistics(client, collection_id, item_id)
    await list_available_assets(client, collection_id, item_id)
    await get_item_asset_details(client, collection_id, item_id)
    await get_bounds(client, collection_id, item_id)
    await crop_geo_json(client, collection_id, item_id, geojson)
    await crop_geo_json_with_dimensions(client, collection_id, item_id, geojson)
    await get_geo_json_statistics(client, collection_id, item_id, geojson)
    await get_info_geo_json(client, collection_id, item_id)
    await get_part(client, collection_id, item_id, bounds)
    await get_part_with_dimensions(client, collection_id, item_id, bounds)
    await get_point(client, collection_id, item_id, point)
    await get_preview(client, collection_id, item_id)
    await get_preview_with_format(client, collection_id, item_id)
    await list_statistics(client, collection_id, item_id)
    await get_tile_json(client, collection_id, item_id)
    await get_tile(client, collection_id, item_id)
    await get_wmts_capabilities(client, collection_id, item_id)

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
