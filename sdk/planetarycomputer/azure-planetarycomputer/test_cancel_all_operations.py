# pylint: disable=line-too-long,useless-suppression
"""
Test cancel_all_operations() scope.

Creates two temporary collections, starts create-item LROs on both,
then calls cancel_all_operations() and checks if operations across
ALL collections get cancelled.

Usage:
    python test_cancel_all_operations.py
"""

import time
from azure.planetarycomputer import PlanetaryComputerProClient
from azure.planetarycomputer.models import (
    StacCollection,
    StacExtensionSpatialExtent,
    StacCollectionTemporalExtent,
    StacExtensionExtent,
    StacItem,
)
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

ENDPOINT = "https://stablegeo.eebtfbh5h4bffxbf.uksouth.geocatalog.spatio.azure.com"

COLLECTION_A = "cancel-test-collection-a"
COLLECTION_B = "cancel-test-collection-b"


def make_item(item_id, collection_id):
    return {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": item_id,
        "collection": collection_id,
        "bbox": [-84.44, 33.62, -84.37, 33.69],
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-84.37, 33.62], [-84.37, 33.69], [-84.44, 33.69], [-84.44, 33.62], [-84.37, 33.62]]],
        },
        "properties": {"datetime": "2021-11-14T16:00:00Z"},
        "links": [
            {
                "rel": "collection",
                "type": "application/json",
                "href": f"./collections/{collection_id}",
            }
        ],
        "assets": {
            "image": {
                "href": "https://naipeuwest.blob.core.windows.net/naip/v002/ga/2021/ga_060cm_2021/33084/m_3308421_se_16_060_20211114.tif",
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
            }
        },
    }


def create_collection(client, collection_id):
    try:
        client.stac.get_collection(collection_id=collection_id)
        print(f"  {collection_id} already exists, deleting...")
        client.stac.begin_delete_collection(collection_id=collection_id).result()
    except ResourceNotFoundError:
        pass

    col = StacCollection(
        id=collection_id,
        description=f"Temp collection for cancel test",
        license="proprietary",
        extent=StacExtensionExtent(
            spatial=StacExtensionSpatialExtent(bounding_box=[[-180, -90, 180, 90]]),
            temporal=StacCollectionTemporalExtent(interval=[[None, None]]),
        ),
        links=[],
        stac_version="1.0.0",
        type="Collection",
    )
    client.stac.begin_create_collection(body=col).result()
    print(f"  Created {collection_id}")


def main():
    credential = DefaultAzureCredential()
    client = PlanetaryComputerProClient(endpoint=ENDPOINT, credential=credential)

    # Step 1: Create two collections
    print("=== Step 1: Create test collections ===")
    create_collection(client, COLLECTION_A)
    create_collection(client, COLLECTION_B)

    # Step 2: Start item create operations on both (use polling=False to not wait)
    print("\n=== Step 2: Start operations on both collections ===")
    for i in range(3):
        for col_id in [COLLECTION_A, COLLECTION_B]:
            item = make_item(f"test-item-{col_id[-1]}-{i}", col_id)
            try:
                poller = client.stac.begin_create_item(collection_id=col_id, body=item, polling=False)
                print(f"  Started create '{item['id']}' in {col_id}")
            except Exception as e:
                print(f"  Error starting '{item['id']}' in {col_id}: {e}")

    # Step 3: Check pending operations (only for our test collections)
    print("\n=== Step 3: Operations before cancel ===")
    test_collections = {COLLECTION_A, COLLECTION_B}

    ops_a = list(client.ingestion.list_operations(collection_id=COLLECTION_A))
    ops_b = list(client.ingestion.list_operations(collection_id=COLLECTION_B))
    print(f"  {COLLECTION_A}: {len(ops_a)} operations")
    for op in ops_a:
        print(f"    {op.id} | status={op.status} | type={op.type}")
    print(f"  {COLLECTION_B}: {len(ops_b)} operations")
    for op in ops_b:
        print(f"    {op.id} | status={op.status} | type={op.type}")

    pending_before = [op for op in ops_a + ops_b if "PENDING" in str(op.status) or "RUNNING" in str(op.status)]
    print(f"\n  Pending/Running across test collections: {len(pending_before)}")

    # Step 4: Cancel all operations
    print("\n=== Step 4: Calling cancel_all_operations() ===")
    client.ingestion.cancel_all_operations()
    print("cancel_all_operations() completed")

    # Step 5: Check operations after cancel (focused on test collections)
    time.sleep(2)
    print("\n=== Step 5: Operations after cancel ===")
    ops_a_after = list(client.ingestion.list_operations(collection_id=COLLECTION_A))
    ops_b_after = list(client.ingestion.list_operations(collection_id=COLLECTION_B))
    print(f"  {COLLECTION_A}: {len(ops_a_after)} operations")
    for op in ops_a_after:
        print(f"    {op.id} | status={op.status} | type={op.type}")
    print(f"  {COLLECTION_B}: {len(ops_b_after)} operations")
    for op in ops_b_after:
        print(f"    {op.id} | status={op.status} | type={op.type}")

    cancelled = [op for op in ops_a_after + ops_b_after if "CANCELED" in str(op.status)]
    print(f"\n  Cancelled across BOTH test collections: {len(cancelled)}")
    if cancelled:
        collections_cancelled = set(op.collection_id for op in cancelled)
        print(f"  Collections with cancelled ops: {collections_cancelled}")
        if len(collections_cancelled) > 1:
            print("  CONFIRMED: cancel_all_operations() affects MULTIPLE collections (catalog-wide)")
        else:
            print("  Only one collection affected")

    # Also check if ops from OTHER collections got cancelled
    all_ops_after = list(client.ingestion.list_operations())
    all_cancelled = [op for op in all_ops_after if "CANCELED" in str(op.status)]
    cancelled_collections = set(op.collection_id for op in all_cancelled)
    print(f"\n  Total CANCELED operations across catalog: {len(all_cancelled)}")
    print(f"  Collections with CANCELED ops: {cancelled_collections}")

    # Step 7: Cleanup
    print("\n=== Step 7: Cleanup ===")
    for col_id in [COLLECTION_A, COLLECTION_B]:
        try:
            client.stac.begin_delete_collection(collection_id=col_id).result()
            print(f"  Deleted {col_id}")
        except Exception as e:
            print(f"  Cleanup {col_id}: {e}")


if __name__ == "__main__":
    main()
