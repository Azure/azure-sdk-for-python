# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_05_mosaics_tiler.py

DESCRIPTION:
    This sample demonstrates mosaic tiling and static image operations from the Azure Planetary Computer Pro SDK.
    Uses sample datasets and saves tiles and images locally.

USAGE:
    python planetary_computer_05_mosaics_tiler.py

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
"""

import os
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import (
    StacSearchParameters,
    FilterLanguage,
    StacSortExtension,
    StacSearchSortingDirection,
    TilerImageFormat,
    ImageRequest,
    Polygon,
)
import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def register_mosaics_search(client, collection_id):
    """Register a search for mosaics filtered to 2021-2022."""
    register_search_request = StacSearchParameters(
        filter={
            "op": "and",
            "args": [
                {"op": "=", "args": [{"property": "collection"}, collection_id]},
                {"op": ">=", "args": [{"property": "datetime"}, "2021-01-01T00:00:00Z"]},
                {"op": "<=", "args": [{"property": "datetime"}, "2022-12-31T23:59:59Z"]}
            ]
        },
        filter_lang=FilterLanguage.CQL2_JSON,
        sort_by=[StacSortExtension(direction=StacSearchSortingDirection.DESC, field="datetime")],
    )
    register_search_response = client.tiler.register_mosaics_search(register_search_request)
    logging.info(register_search_response)
    return register_search_response


def get_mosaics_search_info(client, search_id):
    """Get mosaics search info."""
    mosaics_info_search_response = client.tiler.get_mosaics_search_info(search_id=search_id)
    search = mosaics_info_search_response.search
    return search


def get_mosaics_tile_json(client, search_id, collection_id):
    """Get mosaics tile JSON."""
    get_mosaics_tile_json_response = client.tiler.get_mosaics_tile_json(
        search_id=search_id,
        tile_matrix_set_id="WebMercatorQuad",
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
        tile_scale=1,
        min_zoom=9,
        collection=collection_id,
        tile_format="png",
    )
    logging.info(get_mosaics_tile_json_response.as_dict())


def get_mosaics_tile(client, search_id, collection_id):
    """Get a mosaic tile and save it locally."""
    mosaics_tile_matrix_sets_response = client.tiler.get_mosaics_tile(
        search_id=search_id,
        tile_matrix_set_id="WebMercatorQuad",
        z=13,
        x=2174,
        y=3282,
        scale=1,
        format="png",
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
        collection=collection_id,
    )
    mosaics_tile_matrix_sets_bytes = b"".join(mosaics_tile_matrix_sets_response)
    
    # Save tile locally
    filename = f"mosaic_tile_{search_id}_z13_x2174_y3282.png"
    with open(filename, "wb") as f:
        f.write(mosaics_tile_matrix_sets_bytes)
    logging.info(f"Tile saved as: {filename} ({len(mosaics_tile_matrix_sets_bytes)} bytes)")


def get_mosaics_wmts_capabilities(client, search_id):
    """Get WMTS capabilities for mosaics and save it locally."""
    get_capabilities_xml_response = client.tiler.get_mosaics_wmts_capabilities(
        search_id=search_id,
        tile_matrix_set_id="WebMercatorQuad",
        tile_format=TilerImageFormat.PNG,
        tile_scale=1,
        min_zoom=7,
        max_zoom=13,
        assets=["image"],
        asset_band_indices=["image|1,2,3"],
    )
    xml_bytes = b"".join(get_capabilities_xml_response)
    xml_string = xml_bytes.decode("utf-8")
    
    # Save WMTS capabilities locally
    filename = f"wmts_capabilities_{search_id}.xml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(xml_string)
    logging.info(f"WMTS capabilities saved as: {filename}")


def get_mosaics_assets_for_point(client, search_id):
    """Get mosaic assets for a specific point (center of the bbox)."""
    # Using center point from the coordinate bbox: -84.43202751899601, 33.639647639722273
    get_lon_lat_assets_response = client.tiler.get_mosaics_assets_for_point(
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
    logging.info(f"Assets for point: {get_lon_lat_assets_response[0]['id']}")


def get_mosaics_assets_for_tile(client, search_id, collection_id):
    """Get mosaic assets for a specific tile."""
    result = client.tiler.get_mosaics_assets_for_tile(
        search_id=search_id,
        tile_matrix_set_id="WebMercatorQuad",
        z=13,
        x=2174,
        y=3282,
        collection_id=collection_id,
    )
    logging.info(f"Assets for tile: {result}")


def create_static_image(client, collection_id):
    """Create a static image from a STAC item.
    
    This demonstrates creating a static image tile with specific rendering parameters.
    The image is created asynchronously and can be retrieved using the returned image ID.
    """
    # Define CQL filter with date range
    cql_filter = {
        "op": "and",
        "args": [
            {"op": "=", "args": [{"property": "collection"}, collection_id]},
            {
                "op": "anyinteracts",
                "args": [
                    {"property": "datetime"},
                    {"interval": ["2023-01-01T00:00:00Z", "2023-12-31T00:00:00Z"]}
                ]
            }
        ]
    }
    
    # Define geometry for the image (within dataset bounds)
    geometry = Polygon(coordinates=[[
        [-84.45378097481053, 33.6567321707079],
        [-84.39805886744838, 33.6567321707079],
        [-84.39805886744838, 33.61945681366625],
        [-84.45378097481053, 33.61945681366625],
        [-84.45378097481053, 33.6567321707079]
    ]])
    
    # Create image request with rendering parameters
    image_request = ImageRequest(
        cql=cql_filter,
        zoom=13,
        geometry=geometry,
        render_parameters=f"assets=image&asset_bidx=image|1,2,3&collection={collection_id}",
        columns=1080,
        rows=1080,
        image_size="1080x1080",
        show_branding=False,
    )
    
    # Create static image
    image_response = client.tiler.create_static_image(collection_id=collection_id, body=image_request)
    
    # Extract image ID from the response URL
    image_id = image_response.url.split("?")[0].split("/")[-1]
    logging.info(f"Created static image with ID: {image_id}")
    logging.info(f"Image URL: {image_response.url}")
    
    return image_id


def get_static_image(client, collection_id, image_id):
    """Retrieve a static image by its ID.
    
    This demonstrates fetching the actual image data from a previously created static image.
    The image data is returned as an iterator of bytes.
    """
    # Get static image data
    image_data = client.tiler.get_static_image(collection_id=collection_id, id=image_id)
    
    # Join the generator to get bytes
    image_bytes = b"".join(image_data)
    
    # Save the image locally
    filename = f"static_image_{image_id}"
    with open(filename, "wb") as f:
        f.write(image_bytes)
    
    logging.info(f"Static image saved as: {filename} ({len(image_bytes)} bytes)")


def main():
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")

    assert endpoint is not None
    assert collection_id is not None

    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Execute mosaic tiler operations
    register_search_response = register_mosaics_search(client, collection_id)
    search_id = register_search_response.search_id

    get_mosaics_search_info(client, search_id)
    get_mosaics_tile_json(client, search_id, collection_id)
    get_mosaics_tile(client, search_id, collection_id)
    get_mosaics_wmts_capabilities(client, search_id)
    get_mosaics_assets_for_point(client, search_id)
    get_mosaics_assets_for_tile(client, search_id, collection_id)
    
    # Execute static image operations
    image_id = create_static_image(client, collection_id)
    get_static_image(client, collection_id, image_id)


if __name__ == "__main__":
    main()
