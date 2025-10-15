# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetary_computer_05_mosaics_tiler.py

DESCRIPTION:
    This sample demonstrates mosaic tiling operations from the Azure Planetary Computer Pro SDK.

USAGE:
    python planetary_computer_05_mosaics_tiler.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
"""

import os
import io
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import (
    StacSearchParameters,
    FilterLanguage,
    StacSortExtension,
    StacSearchSortingDirection,
    TilerImageFormat,
)
from PIL import Image as PILImage

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def register_mosaics_search(client, collection_id):
    """Register a search for mosaics."""
    register_search_request = StacSearchParameters(
        filter={"args": [{"args": [{"property": "collection"}, collection_id], "op": "="}], "op": "and"},
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


def get_mosaics_tile_json(client, search_hash, collection_id):
    """Get mosaics tile JSON."""
    get_mosaics_tile_json_response = client.tiler.get_mosaics_tile_json(
        search_id=search_hash,
        tile_matrix_set_id="WebMercatorQuad",
        assets=["red_20m", "green_20m", "blue_20m"],
        tile_scale=2,
        color_formula="Gamma RGB 3.2 Saturation 0.8 Sigmoidal RGB 25 0.35",
        no_data=0.0,
        min_zoom=9,
        collection=collection_id,
        tile_format="png",
    )
    logging.info(get_mosaics_tile_json_response.as_dict())


def get_mosaics_tile(client, search_hash, collection_id):
    """Get a mosaic tile."""
    mosaics_tile_matrix_sets_response = client.tiler.get_mosaics_tile(
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
        collection=collection_id,
    )
    mosaics_tile_matrix_sets_bytes = b"".join(mosaics_tile_matrix_sets_response)
    image = PILImage.open(io.BytesIO(mosaics_tile_matrix_sets_bytes))
    logging.info(f"Image loaded: {image.format} {image.size} {image.mode}")


def get_mosaics_wmts_capabilities(client, search_hash):
    """Get WMTS capabilities for mosaics."""
    get_capabilities_xml_response = client.tiler.get_mosaics_wmts_capabilities(
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
    xml_bytes = b"".join(get_capabilities_xml_response)
    xml_string = xml_bytes.decode("utf-8")
    logging.info(xml_string)


def get_mosaics_assets_for_point(client, search_hash):
    """Get mosaic assets for a specific point."""
    get_lon_lat_assets_response = client.tiler.get_mosaics_assets_for_point(
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
    logging.info(get_lon_lat_assets_response[0]["id"])


def get_mosaics_assets_for_tile(client, search_hash, collection_id):
    """Get mosaic assets for a specific tile."""
    result = client.tiler.get_mosaics_assets_for_tile(
        search_id=search_hash,
        tile_matrix_set_id="WebMercatorQuad",
        z=10,
        x=504,
        y=390,
        collection_id=collection_id,
    )
    logging.info(result)


def main():
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    collection_id = os.environ.get("AZURE_COLLECTION_ID", "sentinel-2-l2a")
    client = PlanetaryComputerClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Execute mosaic tiler operations
    register_search_response = register_mosaics_search(client, collection_id)
    search_id = register_search_response["searchid"]

    search = get_mosaics_search_info(client, search_id)

    get_mosaics_tile_json(client, search.hash, collection_id)
    get_mosaics_tile(client, search.hash, collection_id)
    get_mosaics_wmts_capabilities(client, search.hash)
    get_mosaics_assets_for_point(client, search.hash)
    get_mosaics_assets_for_tile(client, search.hash, collection_id)


if __name__ == "__main__":
    main()
