# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid
from azure.cosmos import CosmosClient, ContainerProxy, PartitionKey
import azure.cosmos.exceptions as exceptions
import config
# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://learn.microsoft.com/azure/cosmos-db/nosql/quickstart-portal#create-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the synchronous read_items API for Azure Cosmos DB
# ----------------------------------------------------------------------------------------------------------

# Use the default emulator settings
HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = "read_items_sync_db"
CONTAINER_ID = "read_items_sync_container"


def create_items(container: ContainerProxy, num_items: int) -> list:
    """Helper function to create items in the container and return a list for read_items."""
    print(f"Creating {num_items} items...")
    items_to_read = []
    for i in range(num_items):
        doc_id = f"item_{i}_{uuid.uuid4()}"
        # For this sample, the partition key is the same as the item id
        pk_value = doc_id
        item_body = {'id': doc_id, 'data': i}
        container.create_item(body=item_body)
        items_to_read.append((doc_id, pk_value))
    print(f"{num_items} items created.")
    return items_to_read


def demonstrate_read_items(container: ContainerProxy) -> None:
    """Demonstrates various scenarios for the read_items API."""
    print("\n--- 1. Basic read_items usage with a non-existent item ---")
    items_to_read = create_items(container, 5)
    # Add a non-existent item to the list to show it's ignored in the result
    items_to_read.append(("non_existent_item", "non_existent_pk"))

    read_results = container.read_items(items=items_to_read)
    print(f"Successfully read {len(read_results)} items out of {len(items_to_read)} requested.")
    for item in read_results:
        print(f"  - Read item with id: {item.get('id')}")

    print("\n--- 2. Reading a large number of items to show concurrency ---")
    # This demonstrates how read_items handles concurrency and query chunking.
    # The SDK will split the 1100 items into multiple backend queries.
    large_items_list = create_items(container, 1100)
    large_read_results = container.read_items(items=large_items_list)
    print(f"Successfully read {len(large_read_results)} items.")
    headers = large_read_results.get_response_headers()
    if headers:
        print(f"Aggregated request charge for large read: {headers.get('x-ms-request-charge')}")

    print("\n--- 3. Using a response_hook to capture results and headers ---")
    hook_captured_data = {}

    def response_hook(hook_headers, results):
        """A simple hook to capture the aggregated headers and the final result list."""
        print("Response hook called!")
        hook_captured_data['hook_headers'] = hook_headers
        hook_captured_data['results'] = results
        hook_captured_data['call_count'] = hook_captured_data.get('call_count', 0) + 1

    items_for_hook = create_items(container, 10)
    hook_results = container.read_items(
        items=items_for_hook,
        response_hook=response_hook
    )

    print(f"Response hook was called {hook_captured_data.get('call_count', 0)} time(s).")
    if 'hook_headers' in hook_captured_data:
        print(f"Aggregated request charge from hook: {hook_captured_data['hook_headers'].get('x-ms-request-charge')}")
    print(f"Result list from hook is the same as returned list: {hook_captured_data['results'] is hook_results}")


def run_sample():
    """A synchronous sample for the read_items API."""
    client = CosmosClient(HOST, {'masterKey': MASTER_KEY})
    db = None
    try:
        # Create a database
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        print(f"Database '{DATABASE_ID}' created or already exists.")

        # Create a container with /id as the partition key
        partition_key = PartitionKey(path="/id")
        container = db.create_container_if_not_exists(
            id=CONTAINER_ID,
            partition_key=partition_key
        )
        print(f"Container '{CONTAINER_ID}' created or already exists.")

        demonstrate_read_items(container)

    except exceptions.CosmosHttpResponseError as e:
        print(f"\nAn HTTP error occurred: {e.message}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if db:
            print("\n--- Cleaning up ---")
            try:
                client.delete_database(db)
                print(f"Database '{DATABASE_ID}' cleaned up.")
            except exceptions.CosmosResourceNotFoundError:
                print(f"Database '{DATABASE_ID}' was not found, cleanup not needed.")


if __name__ == '__main__':
    run_sample()