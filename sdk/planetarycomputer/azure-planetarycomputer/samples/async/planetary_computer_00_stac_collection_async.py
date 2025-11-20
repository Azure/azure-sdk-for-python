# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_stac_collection_configuration.py

DESCRIPTION:
    This sample demonstrates STAC collection operations including:
    - Creating and deleting STAC collections
    - Updating collection metadata
    - Getting and managing collection partition types
    - Creating and managing render options
    - Creating and managing collection mosaics
    - Managing tile settings

USAGE:
    python planetarycomputer_stac_collection_configuration.py

    Set the environment variable PLANETARYCOMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID.
"""

import os
import time
import datetime
from io import BytesIO
from urllib.request import urlopen
import asyncio
from azure.planetarycomputer.aio import PlanetaryComputerProClient
from azure.identity.aio import DefaultAzureCredential
from azure.planetarycomputer.models import (
    StacCollection,
    StacExtensionSpatialExtent,
    StacCollectionTemporalExtent,
    StacExtensionExtent,
    PartitionType,
    PartitionTypeScheme,
    RenderOption,
    RenderOptionType,
    StacMosaic,
    TileSettings,
    StacQueryable,
    StacQueryableDefinitionDataType,
)

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.ERROR
)
logging.basicConfig(level=logging.INFO)


async def create_collection(client: PlanetaryComputerProClient, collection_id):
    """Create a new STAC collection with item assets."""
    # Check if collection already exists
    logging.info(f"Checking if collection '{collection_id}' exists...")
    get_all_collections_response = await client.stac.list_collections()

    if any(c.id == collection_id for c in get_all_collections_response["collections"]):
        logging.info(f"Collection '{collection_id}' already exists, deleting it...")
        collection_delete_operation = await client.stac.begin_delete_collection(
            collection_id, polling=True
        )
        await collection_delete_operation.result()
        logging.info(f"Deleted collection '{collection_id}'")

    # Define collection spatial and temporal extents (Georgia state bounds)
    spatial_extent = StacExtensionSpatialExtent(
        bounding_box=[[-85.605165, 30.357851, -80.839729, 35.000659]]
    )
    temporal_extent = StacCollectionTemporalExtent(
        interval=[
            [
                datetime.datetime.fromisoformat("2020-01-01T00:00:00Z"),
                datetime.datetime.fromisoformat("2099-12-31T23:59:59Z"),
            ]
        ]
    )

    extent = StacExtensionExtent(spatial=spatial_extent, temporal=temporal_extent)

    # Create StacCollection object
    collection_payload = StacCollection(
        id=collection_id,
        description="A Subset of imagery for sample MPC Pro GeoCatalog deployments.",
        extent=extent,
        license="proprietary",
        links=[],
        stac_version="1.0.0",
        title="MPC Pro Sample Datasets",
        type="Collection",
    )

    # Add item_assets and other fields as additional data (not part of the model)
    collection_data = collection_payload.as_dict()
    collection_data["providers"] = [
        {
            "url": "https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/",
            "name": "USDA Farm Service Agency",
            "roles": ["producer", "licensor"],
        },
        {"url": "https://www.esri.com/", "name": "Esri", "roles": ["processor"]},
        {
            "url": "https://planetarycomputer.microsoft.com",
            "name": "Microsoft",
            "roles": ["host", "processor"],
        },
    ]
    collection_data["summaries"] = {
        "gsd": [0.3, 0.6, 1],
        "eo:bands": [
            {"name": "Red", "common_name": "red", "description": "visible red"},
            {"name": "Green", "common_name": "green", "description": "visible green"},
            {"name": "Blue", "common_name": "blue", "description": "visible blue"},
            {"name": "NIR", "common_name": "nir", "description": "near-infrared"},
        ],
    }
    collection_data["item_assets"] = {
        "image": {
            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
            "roles": ["data"],
            "title": "RGBIR COG tile",
            "eo:bands": [
                {"name": "Red", "common_name": "red"},
                {"name": "Green", "common_name": "green"},
                {"name": "Blue", "common_name": "blue"},
                {"name": "NIR", "common_name": "nir", "description": "near-infrared"},
            ],
        },
        "metadata": {
            "type": "text/plain",
            "roles": ["metadata"],
            "title": "FGDC Metdata",
        },
        "thumbnail": {
            "type": "image/jpeg",
            "roles": ["thumbnail"],
            "title": "Thumbnail",
        },
    }
    collection_data["stac_extensions"] = [
        "https://stac-extensions.github.io/item-assets/v1.0.0/schema.json",
        "https://stac-extensions.github.io/table/v1.2.0/schema.json",
    ]

    # Create the collection
    logging.info(f"Creating collection '{collection_id}'...")
    collection_create_operation = await client.stac.begin_create_collection(
        body=collection_data, polling=False
    )
    await collection_create_operation.result()
    logging.info(f"Collection '{collection_id}' created successfully")

    # Get the created collection to verify
    logging.info(f"Retrieving collection '{collection_id}'...")
    collection = await client.stac.get_collection(collection_id=collection_id)
    logging.info(f"Retrieved collection: {collection.title}")
    logging.info(f"Description: {collection.description}")

    return collection


async def update_collection(client: PlanetaryComputerProClient, collection_id):
    """Update an existing collection's metadata."""
    # Get the current collection
    logging.info(f"Getting collection '{collection_id}'...")
    collection = await client.stac.get_collection(collection_id=collection_id)

    # Update description
    original_description = collection.description
    collection.description = collection.description + " - Updated for testing"

    # Update the collection
    logging.info("Updating collection...")
    await client.stac.create_or_replace_collection(
        collection_id=collection_id, body=collection
    )

    # Verify the update
    updated_collection = await client.stac.get_collection(collection_id=collection_id)
    logging.info(f"Original description: {original_description}")
    logging.info(f"Updated description: {updated_collection.description}")


async def manage_partition_type(client: PlanetaryComputerProClient, collection_id):
    """Get and update collection partition type."""
    # Get current partition type
    logging.info(f"Getting partition type for collection '{collection_id}'...")
    partition_type = await client.stac.get_partition_type(collection_id)
    logging.info(f"Current partition scheme: {partition_type.scheme}")

    # Check if collection is empty before updating
    items = await client.stac.get_item_collection(collection_id=collection_id)
    if items.features:
        logging.info("Collection is not empty, skipping partition type update")
    else:
        logging.info("Updating partition type to YEAR scheme...")
        await client.stac.replace_partition_type(
            collection_id, body=PartitionType(scheme=PartitionTypeScheme.YEAR)
        )
        logging.info("Partition type updated successfully")


async def manage_render_options(client: PlanetaryComputerProClient, collection_id):
    """Create and manage render options for a collection."""
    # Define render options
    render_option = RenderOption(
        id="natural-color",
        name="Natural color",
        description="RGB from visual assets",
        type=RenderOptionType.RASTER_TILE,
        options="assets=image&asset_bidx=image|1,2,3",
        min_zoom=6,
    )

    # Check if render option already exists
    stac_collection_mosaics_get_all_response = await client.stac.list_render_options(
        collection_id=collection_id
    )

    if any(
        ro.id == render_option.id for ro in stac_collection_mosaics_get_all_response
    ):
        logging.info("Render option 'natural-color' already exists.")
        await client.stac.delete_render_option(
            collection_id=collection_id, render_option_id=render_option.id
        )
        logging.info(
            "Deleted existing render option 'natural-color'. Proceeding to create a new one."
        )

    # Create render option without description initially
    render_option = RenderOption(
        id="natural-color",
        name="Natural color",
        type=RenderOptionType.RASTER_TILE,
        options="assets=image&asset_bidx=image|1,2,3",
        min_zoom=6,
    )

    logging.info(f"Creating render option '{render_option.id}'...")
    await client.stac.create_render_option(
        collection_id=collection_id, body=render_option
    )

    # List render options
    await client.stac.list_render_options(collection_id=collection_id)

    # Update with description
    render_option.description = "RGB from visual assets"

    await client.stac.replace_render_option(
        collection_id=collection_id,
        render_option_id=render_option.id,
        body=render_option,
    )

    # Get the created render option
    retrieved_option = await client.stac.get_render_option(
        collection_id=collection_id, render_option_id=render_option.id
    )
    logging.info(f"Retrieved: {retrieved_option.name}")


async def manage_mosaics(client: PlanetaryComputerProClient, collection_id):
    """Create and manage collection mosaics."""
    # Define a mosaic
    mosaic = StacMosaic(
        id="mos1",
        name="Most recent available",
        cql=[],
    )

    # Check existing mosaics
    stac_collection_mosaics_get_all_response = await client.stac.list_mosaics(
        collection_id=collection_id
    )

    if any(m.id == mosaic.id for m in stac_collection_mosaics_get_all_response):
        logging.info(
            f"Mosaic {mosaic.id} already exists. Deleting it before creating a new one."
        )
        await client.stac.delete_mosaic(
            collection_id=collection_id, mosaic_id=mosaic.id
        )

    # Create Mosaic
    stac_collection_mosaics_add_response = await client.stac.add_mosaic(
        collection_id=collection_id,
        body=mosaic,
    )
    logging.info(stac_collection_mosaics_add_response)

    # Update with description
    mosaic.description = "Most recent available imagery in this collection"

    stac_collection_mosaics_create_or_replace_response = (
        await client.stac.replace_mosaic(
            collection_id=collection_id,
            mosaic_id=mosaic.id,
            body=mosaic,
        )
    )
    logging.info(stac_collection_mosaics_create_or_replace_response)

    # Get the mosaic
    retrieved_mosaic = await client.stac.get_mosaic(
        collection_id=collection_id, mosaic_id=mosaic.id
    )
    logging.info(retrieved_mosaic)


async def manage_tile_settings(client: PlanetaryComputerProClient, collection_id):
    """Get and update tile settings for a collection."""
    # Get current tile settings
    logging.info(f"Getting tile settings for collection '{collection_id}'...")
    tile_settings = await client.stac.get_tile_settings(collection_id=collection_id)
    logging.info(tile_settings)

    # Update tile settings
    logging.info("Updating tile settings...")
    stac_collection_tile_settings_response = await client.stac.replace_tile_settings(
        collection_id=collection_id,
        body=TileSettings(
            default_location=None,  # null in the config
            max_items_per_tile=35,
            min_zoom=6,
        ),
    )
    logging.info(stac_collection_tile_settings_response)


async def get_conformance_class(client: "PlanetaryComputerProClient"):
    """Get STAC conformance classes."""
    result = await client.stac.get_conformance_class()
    logging.info(result)


async def get_landing_page(client: "PlanetaryComputerProClient"):
    """Get STAC landing page."""
    result = await client.stac.get_landing_page()
    logging.info(result)


async def manage_queryables(client: PlanetaryComputerProClient, collection_id):
    """Create and manage queryables for a collection."""
    stac_queryables_get_all_response = await client.stac.get_collection_queryables(
        collection_id=collection_id
    )

    queryable = StacQueryable(
        name="eo:cloud_cover",
        data_type=StacQueryableDefinitionDataType.NUMBER,
        create_index=False,
        definition={
            "data_type": StacQueryableDefinitionDataType.NUMBER,
        },
    )

    if any(
        q == queryable.name
        for q in stac_queryables_get_all_response["properties"].keys()
    ):
        await client.stac.delete_queryable(
            collection_id=collection_id, queryable_name=queryable.name
        )
        logging.info(f"Deleted existing '{queryable.name}' queryable.")

    stac_queryables_create_response = await client.stac.create_queryables(
        collection_id=collection_id,
        body=[queryable],
    )

    logging.info(stac_queryables_create_response)

    queryable.definition["description"] = "Cloud cover percentage"

    create_or_replace_queryable_response = await client.stac.replace_queryable(
        collection_id=collection_id,
        queryable_name=queryable.name,
        body=queryable,
    )

    logging.info(create_or_replace_queryable_response)

    await client.stac.list_queryables()


async def get_collection_configuration(
    client: PlanetaryComputerProClient, collection_id
):
    """Get collection configuration."""
    result = await client.stac.get_collection_configuration(collection_id=collection_id)
    logging.info(result)


async def manage_collection_assets(client: PlanetaryComputerProClient, collection_id):
    """Create and manage collection assets like thumbnails."""
    thumbnail_url = "https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/naip.png"

    # Define thumbnail asset metadata
    data = {
        "key": "thumbnail",
        "href": thumbnail_url,
        "type": "image/png",
        "roles": ["thumbnail"],
        "title": "Thumbnail",
    }

    # Download thumbnail
    with urlopen(thumbnail_url) as thumbnail_response:
        thumbnail_content = thumbnail_response.read()
    thumbnail_bytes = BytesIO(thumbnail_content)
    thumbnail_tuple = ("thumbnail.png", thumbnail_bytes)

    try:
        await client.stac.delete_collection_asset(
            collection_id=collection_id, asset_id="thumbnail"
        )
        logging.info("Deleted existing thumbnail asset.")
    except Exception:
        logging.info("No existing thumbnail asset to delete.")

    # Create Collection Asset
    await client.stac.create_collection_asset(
        collection_id=collection_id, body={"data": data, "file": thumbnail_tuple}
    )

    # Create or replace Collection Asset
    thumbnail_bytes.seek(0)  # Reset BytesIO position
    await client.stac.replace_collection_asset(
        collection_id=collection_id,
        asset_id="thumbnail",
        body={"data": data, "file": thumbnail_tuple},
    )

    # Create or replace Collection Asset again
    thumbnail_bytes.seek(0)  # Reset BytesIO position
    await client.stac.replace_collection_asset(
        collection_id=collection_id,
        asset_id="thumbnail",
        body={"data": data, "file": thumbnail_tuple},
    )

    # Get the thumbnail as bytes
    thumbnail_response = await client.stac.get_collection_thumbnail(
        collection_id=collection_id
    )

    # Convert the generator to bytes
    # Collect the async iterator into a list
    thumbnail_bytes_result_chunks = []
    async for chunk in thumbnail_response:
        thumbnail_bytes_result_chunks.append(chunk)
    thumbnail_bytes_result = b"".join(thumbnail_bytes_result_chunks)

    assert len(thumbnail_bytes_result) > 0


async def main():
    # Get configuration from environment
    endpoint = os.environ.get("PLANETARYCOMPUTER_ENDPOINT")
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID")

    if not endpoint:
        raise ValueError("PLANETARYCOMPUTER_ENDPOINT environment variable must be set")

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerProClient(
        endpoint=endpoint, credential=credential, logging_enable=True
    )

    logging.info(f"Connected to: {endpoint}")
    logging.info(f"Collection ID: {collection_id}\n")

    # Get credential token
    await credential.get_token("https://geocatalog.spatio.azure.com/.default")

    # List all collections
    await client.stac.list_collections()

    # Create and configure collection
    await create_collection(client, collection_id)
    await update_collection(client, collection_id)
    await manage_partition_type(client, collection_id)
    await manage_render_options(client, collection_id)
    await get_conformance_class(client)
    await get_landing_page(client)
    await manage_queryables(client, collection_id)
    await manage_tile_settings(client, collection_id)
    await manage_mosaics(client, collection_id)
    await get_collection_configuration(client, collection_id)
    await manage_collection_assets(client, collection_id)

    logging.info("\nCollection Configuration Complete")

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
