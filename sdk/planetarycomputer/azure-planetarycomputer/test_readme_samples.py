"""
Validate that all README code samples work against the stable GeoCatalog.

Runs each read-only sample from the README and validates mutating samples
(create/delete) in a safe lifecycle test with cleanup.

Usage:
    python test_readme_samples.py
"""

import asyncio
import os
import traceback

from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

ENDPOINT = "https://stablegeo.eebtfbh5h4bffxbf.uksouth.geocatalog.spatio.azure.com"
COLLECTION_ID = "naip"
ITEM_ID = "ga_m_3308421_se_16_060_20211114"

results = []


def run_sample(name, func):
    """Run a sample and record pass/fail."""
    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"{'='*60}")
    try:
        func()
        print(f"PASS: {name}")
        results.append((name, "PASS", None))
    except Exception as e:
        print(f"FAIL: {name} — {e}")
        traceback.print_exc()
        results.append((name, "FAIL", str(e)))


# ============================================================
# README Sample: List STAC Collections
# ============================================================
def test_list_collections():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    collections_response = client.stac.get_collections()

    for collection in collections_response.collections:
        print(f"Collection: {collection.id}")
        print(f"  Title: {collection.title}")
        print(f"  Description: {collection.description[:100]}...")
        break  # Just verify the first one

    assert len(collections_response.collections) > 0, "No collections returned"


# ============================================================
# README Sample: Search for STAC Items
# ============================================================
def test_search_items():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.planetarycomputer.models import StacSearchParameters, FilterLanguage
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    search_params = StacSearchParameters(
        collections=[COLLECTION_ID],
        filter_lang=FilterLanguage.CQL2_JSON,
        filter={
            "op": "s_intersects",
            "args": [
                {"property": "geometry"},
                {
                    "type": "Polygon",
                    "coordinates": [
                        [[-84.39, 33.76], [-84.37, 33.76], [-84.37, 33.78], [-84.39, 33.78], [-84.39, 33.76]]
                    ],
                },
            ],
        },
        limit=10,
    )

    search_result = client.stac.search(body=search_params)
    print(f"Found {len(search_result.features)} items")
    assert search_result.features is not None, "Search response missing features"


# ============================================================
# README Sample: Get STAC Item Details
# ============================================================
def test_get_item():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    item = client.stac.get_item(
        collection_id=COLLECTION_ID,
        item_id=ITEM_ID,
    )

    print(f"Item ID: {item.id}")
    print(f"Geometry type: {item.geometry.type}")
    print(f"Assets: {list(item.assets.keys())}")

    assert item.id == ITEM_ID


# ============================================================
# README Sample: Create STAC Collection (lifecycle test)
# ============================================================
def test_create_collection_lifecycle():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.planetarycomputer.models import (
        StacCollection,
        StacExtensionSpatialExtent,
        StacCollectionTemporalExtent,
        StacExtensionExtent,
        RenderOption,
        TileSettings,
    )
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    test_collection_id = "readme-validation-test"

    # Cleanup if leftover from previous run
    try:
        client.stac.get_collection(collection_id=test_collection_id)
        print(f"  Cleaning up leftover collection '{test_collection_id}'...")
        client.stac.begin_delete_collection(collection_id=test_collection_id).result()
    except ResourceNotFoundError:
        pass

    # --- Create collection (from README) ---
    collection = StacCollection(
        id=test_collection_id,
        description="A collection of geospatial data",
        license="proprietary",
        extent=StacExtensionExtent(
            spatial=StacExtensionSpatialExtent(bounding_box=[[-180.0, -90.0, 180.0, 90.0]]),
            temporal=StacCollectionTemporalExtent(interval=[[None, None]]),
        ),
        links=[],
        stac_version="1.0.0",
        type="Collection",
    )

    poller = client.stac.begin_create_collection(body=collection)
    poller.result()
    print(f"  Created collection: {test_collection_id}")

    # Verify it exists
    created = client.stac.get_collection(collection_id=test_collection_id)
    assert created.id == test_collection_id

    # --- Configure visualization (from README) ---
    render_option = RenderOption(
        id="true-color",
        name="True Color",
        type="raster-tile",
        options="assets=image&rescale=0,255",
    )
    client.stac.create_render_option(collection_id=test_collection_id, body=render_option)
    print("  Created render option")

    tile_settings = TileSettings(min_zoom=6, max_items_per_tile=10)
    client.stac.replace_tile_settings(collection_id=test_collection_id, body=tile_settings)
    print("  Updated tile settings")

    for option in client.stac.list_render_options(collection_id=test_collection_id):
        print(f"  Render option: {option.id} - {option.name}")

    # --- Cleanup ---
    client.stac.begin_delete_collection(collection_id=test_collection_id).result()
    print(f"  Deleted collection: {test_collection_id}")


# ============================================================
# README Sample: Register and Render Mosaic Tiles
# ============================================================
def test_register_mosaic():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    registration = client.data.register_mosaics_search(
        body={
            "collections": [COLLECTION_ID],
            "filter-lang": "cql2-json",
            "filter": {"op": "=", "args": [{"property": "naip:year"}, "2021"]},
        }
    )
    print(f"Search ID: {registration.search_id}")
    assert registration.search_id is not None

    tile_json = client.data.get_searches_tile_json(
        search_id=registration.search_id,
        tile_matrix_set_id="WebMercatorQuad",
        assets=["image"],
    )
    print(f"Tile URLs: {tile_json.tiles}")
    print(f"Bounds: {tile_json.bounds}")
    assert tile_json.tiles is not None


# ============================================================
# README Sample: Extract Point Values
# ============================================================
def test_extract_point():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    point_data = client.data.get_item_point(
        collection_id=COLLECTION_ID,
        item_id=ITEM_ID,
        longitude=-84.41,
        latitude=33.65,
        assets=["image"],
    )

    print(f"Coordinates: {point_data.coordinates}")
    print(f"Band names: {point_data.band_names}")
    print(f"Values: {point_data.values_property}")
    assert point_data.coordinates is not None


# ============================================================
# README Sample: Generate Map Tiles
# ============================================================
def test_generate_tile():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    tile_response = client.data.get_tile(
        collection_id=COLLECTION_ID,
        item_id=ITEM_ID,
        tile_matrix_set_id="WebMercatorQuad",
        z=14,
        x=4322,
        y=6463,
        assets=["image"],
        format="png",
    )

    tile_bytes = b"".join(tile_response)
    print(f"Tile size: {len(tile_bytes)} bytes")
    assert len(tile_bytes) > 0, "Tile response was empty"


# ============================================================
# README Sample: Generate SAS Token
# ============================================================
def test_sas_token():
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    token_response = client.sas.get_token(
        collection_id=COLLECTION_ID,
        duration_in_minutes=60,
    )

    print(f"SAS Token: {token_response.token[:50]}...")
    print(f"Expiry: {token_response.expires_on}")
    assert token_response.token is not None


# ============================================================
# README Sample: Async Operations
# ============================================================
def test_async_operations():
    from azure.planetarycomputer.aio import PlanetaryComputerProClient as AsyncClient
    from azure.identity.aio import DefaultAzureCredential as AsyncCredential

    async def _run():
        credential = AsyncCredential()
        async with AsyncClient(endpoint=ENDPOINT, credential=credential) as client:
            collections_response = await client.stac.get_collections(headers={"Accept-Encoding": "identity"})
            for collection in collections_response.collections:
                print(f"  Async Collection: {collection.id}")
                break

            item = await client.stac.get_item(
                collection_id=COLLECTION_ID,
                item_id=ITEM_ID,
            )
            print(f"  Async Item: {item.id}")
            assert item.id == ITEM_ID

        await credential.close()

    asyncio.run(_run())


# ============================================================
# README Sample: Error Handling
# ============================================================
def test_error_handling():
    from azure.core.exceptions import HttpResponseError
    from azure.planetarycomputer import PlanetaryComputerProClient
    from azure.identity import DefaultAzureCredential

    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=DefaultAzureCredential())

    try:
        client.stac.get_collection(collection_id="non-existent-collection")
        assert False, "Should have raised HttpResponseError"
    except HttpResponseError as e:
        print(f"Status code: {e.status_code}")
        print(f"Reason: {e.reason}")
        assert e.status_code == 404


# ============================================================
# Run all samples
# ============================================================
def main():
    print(f"Validating README samples against: {ENDPOINT}\n")

    run_sample("List STAC Collections", test_list_collections)
    run_sample("Search for STAC Items", test_search_items)
    run_sample("Get STAC Item Details", test_get_item)
    run_sample("Create Collection Lifecycle", test_create_collection_lifecycle)
    run_sample("Register and Render Mosaic Tiles", test_register_mosaic)
    run_sample("Extract Point Values", test_extract_point)
    run_sample("Generate Map Tiles", test_generate_tile)
    run_sample("Generate SAS Token", test_sas_token)
    run_sample("Async Operations", test_async_operations)
    run_sample("Error Handling", test_error_handling)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    for name, status, err in results:
        icon = "✅" if status == "PASS" else "❌"
        line = f"  {icon} {name}"
        if err:
            line += f" — {err[:80]}"
        print(line)
    print(f"\n{passed}/{passed + failed} passed")

    if failed:
        exit(1)


if __name__ == "__main__":
    main()
