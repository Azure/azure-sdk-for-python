# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_stac_specification.py

DESCRIPTION:
    This sample demonstrates STAC API conformance, catalog operations, and item management:
    - Checking API conformance
    - Getting the landing page
    - Searching collections
    - Searching and querying items with filters, bounding boxes, temporal ranges
    - Working with queryables
    - Creating, updating, and deleting STAC items
    - Creating or replacing STAC items (idempotent operations)

USAGE:
    python planetarycomputer_stac_specification.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID (default: naip).
"""

import os
import json
import time
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import (
    StacSearchParameters,
    FilterLanguage,
    StacSearchSortingDirection,
    StacSortExtension,
    StacItem,
)
from azure.core.exceptions import HttpResponseError

import logging

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def get_landing_page(client):
    """Get the STAC landing page."""
    landing_page = client.stac.get_stac_landing_page()

    for link in landing_page.links[:5]:  # Show first 5 links
        logging.info(f"  - {link.rel}: {link.href}")


def search_collections(client):
    """Search and list STAC collections."""
    collections = client.stac.list_collections()

    # Show first few collections
    for collection in collections.collections[:3]:
        if collection.description:
            desc = collection.description[:100] + "..." if len(collection.description) > 100 else collection.description
            logging.info(f"  - {collection.id}: {desc}")


def search_items(client, collection_id):
    """Search STAC items with filters and sorting."""
    # Create Search using StacSearchParameters with NAIP-specific query
    # Using date_time with range format instead of CQL2-JSON temporal filter
    search_post_request = StacSearchParameters(
        collections=[collection_id],
        filter_lang=FilterLanguage.CQL2_JSON,
        filter={
            "op": "s_intersects",
            "args": [
                {"property": "geometry"},
                {
                    "type": "Polygon",
                    "coordinates": [[
                        [-84.46416308610219, 33.6033686729869],
                        [-84.38815071170247, 33.6033686729869],
                        [-84.38815071170247, 33.6713179813099],
                        [-84.46416308610219, 33.6713179813099],
                        [-84.46416308610219, 33.6033686729869]
                    ]]
                }
            ]
        },
        date_time="2021-01-01T00:00:00Z/2022-12-31T00:00:00Z",
        sort_by=[StacSortExtension(field="datetime", direction=StacSearchSortingDirection.DESC)],
        limit=50
    )

    # Create Search
    search_post_response = client.stac.search(body=search_post_request)
    logging.info(f"Search returned {len(search_post_response.features)} items")
    logging.info(json.dumps(search_post_response.as_dict()))

def get_sample_stac_item(collection_id: str, item_id: str) -> StacItem:
    """Create a sample STAC item based on NAIP data."""
    return StacItem({
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": item_id,
        "collection": collection_id,
        "bbox": [
            -84.441543,
            33.559319,
            -84.370855,
            33.628174
        ],
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-84.372901, 33.559319],
                    [-84.370855, 33.626731],
                    [-84.439551, 33.628174],
                    [-84.441543, 33.560757],
                    [-84.372901, 33.559319]
                ]
            ]
        },
        "properties": {
            "gsd": 0.6,
            "datetime": "2021-11-14T16:00:00Z",
            "naip:year": "2021",
            "proj:bbox": [737508.0, 3716388.0, 743886.0, 3723870.0],
            "proj:epsg": 26916,
            "providers": [
                {
                    "url": "https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/",
                    "name": "USDA Farm Service Agency",
                    "roles": ["producer", "licensor"]
                }
            ],
            "naip:state": "ga",
            "proj:shape": [12470, 10630],
            "proj:transform": [0.6, 0.0, 737508.0, 0.0, -0.6, 3723870.0, 0.0, 0.0, 1.0]
        },
        "links": [
            {
                "rel": "collection",
                "type": "application/json",
                "href": "https://planetarycomputer.microsoft.com/api/stac/v1/collections/naip"
            },
            {
                "rel": "root",
                "href": "./catalog.json",
                "type": "application/json",
                "title": "NAIP: National Agriculture Imagery Program"
            },
            {
                "rel": "parent",
                "href": "./catalog.json",
                "type": "application/json",
                "title": "NAIP: National Agriculture Imagery Program"
            }
        ],
        "assets": {
            "image": {
                "href": "https://naipeuwest.blob.core.windows.net/naip/v002/ga/2021/ga_060cm_2021/33084/m_3308429_ne_16_060_20211114.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
                "title": "RGBIR COG tile",
                "eo:bands": [
                    {"name": "Red", "common_name": "red"},
                    {"name": "Green", "common_name": "green"},
                    {"name": "Blue", "common_name": "blue"},
                    {"name": "NIR", "common_name": "nir", "description": "near-infrared"}
                ]
            },
            "thumbnail": {
                "href": "https://naipeuwest.blob.core.windows.net/naip/v002/ga/2021/ga_060cm_2021/33084/m_3308429_ne_16_060_20211114.200.jpg",
                "type": "image/jpeg",
                "roles": ["thumbnail"],
                "title": "Thumbnail"
            },
            "tilejson": {
                "title": "TileJSON with default rendering",
                "href": "https://planetarycomputer.microsoft.com/api/data/v1/item/tilejson.json?collection=naip&item=ga_m_3308429_ne_16_060_20211114&assets=image&asset_bidx=image%7C1%2C2%2C3&format=png",
                "type": "application/json",
                "roles": ["tiles"]
            },
            "rendered_preview": {
                "title": "Rendered preview",
                "rel": "preview",
                "href": "https://planetarycomputer.microsoft.com/api/data/v1/item/preview.png?collection=naip&item=ga_m_3308429_ne_16_060_20211114&assets=image&asset_bidx=image%7C1%2C2%2C3&format=png",
                "roles": ["overview"],
                "type": "image/png"
            }
        },
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
        ]
    })
    
def create_stac_item(client, collection_id, item_id):
    """Create a STAC item."""
    stac_item = get_sample_stac_item(collection_id, item_id)
    stac_item_get_items_response = client.stac.list_items(collection_id=collection_id)

    if any(item.id == stac_item.id for item in stac_item_get_items_response.features):
        logging.info(f"Item {stac_item.id} already exists. Deleting it before creating a new one.")
        client.stac.begin_delete_item(collection_id=collection_id, item_id=stac_item.id, polling=True).result()
        logging.info(f"Deleted item {stac_item.id}. Proceeding to create a new one.")
        time.sleep(15)
    else:
        logging.info(f"Item {stac_item.id} does not exist. Proceeding to create it.")

    stac_item.collection = collection_id

    try:
        stac_item_create_response = client.stac.begin_create_item(collection_id=collection_id, body=stac_item, polling=True)
        stac_item_create_response.result()
        print(f"Created item {item_id}")
    except HttpResponseError as e:
        logging.error(f"Failed to create item {stac_item.id}: {e.message}")
        pass


def update_stac_item(client, collection_id, item_id):
    """Update a STAC item."""
    stac_item = get_sample_stac_item(collection_id, item_id)
    stac_item.properties["platform"] = "NAIP Imagery"

    stac_item_create_or_update_response = client.stac.begin_update_item(
        collection_id=collection_id, item_id=stac_item.id, body=stac_item, polling=True
    )

    stac_item_create_or_update_response.result()
    logging.info(f"Updated item {stac_item.id}, platform: {stac_item.properties['platform']}")


def create_or_replace_stac_item(client, collection_id, item_id):
    """Create or replace a STAC item (idempotent operation).
    
    This demonstrates using begin_create_or_replace_item which is idempotent:
    - If the item doesn't exist, it creates it
    - If the item exists, it replaces it completely
    - Multiple calls with the same data produce the same result
    """
    # Create initial item
    stac_item = get_sample_stac_item(collection_id, item_id)
    
    create_poller = client.stac.begin_create_or_replace_item(
        collection_id=collection_id, item_id=item_id, body=stac_item, polling=True
    )
    create_poller.result()
    logging.info(f"Created item {item_id}")
    
    # Verify creation
    created_item = client.stac.get_item(collection_id=collection_id, item_id=item_id)
    logging.info(f"Verified item {created_item.id}")
    
    # Update and replace item (idempotent - same call replaces completely)
    stac_item.properties["platform"] = "NAIP Imagery Updated"
    stac_item.properties["processing_level"] = "L2"
    
    replace_poller = client.stac.begin_create_or_replace_item(
        collection_id=collection_id, item_id=item_id, body=stac_item, polling=True
    )
    replace_poller.result()
    logging.info(f"Replaced item {item_id}")
    
    # Verify replacement
    replaced_item = client.stac.get_item(collection_id=collection_id, item_id=item_id)
    logging.info(f"Verified replaced item, platform: {replaced_item.properties.get('platform', 'N/A')}")


def get_collection(client, collection_id):
    """Get a STAC collection."""
    collection = client.stac.get_collection(collection_id=collection_id)
    logging.info(f"Retrieved collection: {collection.id}")


def query_items(client, collection_id):
    """Query items using CQL2 filters."""
    # Query with filter
    query_options = StacSearchParameters(
        collections=[collection_id],
        filter_lang=FilterLanguage.CQL2_JSON,
        filter={"op": "<", "args": [{"property": "eo:cloud_cover"}, 10]},
        limit=5,
    )

    query_results = client.stac.search(body=query_options)
    if query_results.features:
        for item in query_results.features:
            if item.properties and item.properties.date_time:
                logging.info(f"  - {item.id}: {item.properties.date_time}")

    # Sorted query
    sorted_options = StacSearchParameters(
        collections=[collection_id],
        sort_by=[StacSortExtension(field="eo:cloud_cover", direction=StacSearchSortingDirection.ASC)],
        limit=3,
    )

    sorted_results = client.stac.search(body=sorted_options)

    if sorted_results.features:
        for item in sorted_results.features:
            if item.properties and item.properties.date_time:
                logging.info(f"  - {item.id}: {item.properties.date_time}")


def get_queryables(client, collection_id):
    """Get queryable properties for a collection."""
    queryables = client.stac.list_collection_queryables(collection_id=collection_id)
    properties = queryables.get("properties")

    if properties:
        for prop_name in list(properties.keys())[:10]:  # Show first 10
            logging.info(f"  - {prop_name}: {properties[prop_name].get('description', '')}")


def main():
    # Get configuration from environment
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")
    collection_id = os.environ.get("PLANETARYCOMPUTER_COLLECTION_ID", "naip-sample-datasets")
    item_id = os.environ.get("PLANETARYCOMPUTER_ITEM_ID", "ga_m_3308421_se_16_060_20211114")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerClient(endpoint=endpoint, credential=credential, logging_enable=False)

    # Execute STAC specification operations
    get_landing_page(client)
    search_collections(client)
    search_items(client, collection_id)
    query_items(client, collection_id)
    get_queryables(client, collection_id)

    # Execute STAC item operations
    create_stac_item(client, collection_id, item_id)
    update_stac_item(client, collection_id, item_id)
    create_or_replace_stac_item(client, collection_id, f"{item_id}_replace_demo")
    get_collection(client, collection_id)


if __name__ == "__main__":
    main()
