# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timezone

from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
import azure.cosmos.documents as documents
import azure.cosmos.partition_key as partition_key
import uuid

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https:#azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to consume the Change Feed and iterate on the results.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


async def create_items(container, size, partition_key_value):
    print("Creating Items with partition key value: {}".format(partition_key_value))

    for i in range(size):
        c = str(uuid.uuid4())
        item_definition = {'id': 'item' + c,
                           'address': {'street': '1 Microsoft Way' + c,
                                       'city': 'Redmond' + c,
                                       'state': partition_key_value,
                                       'zip code': 98052
                                       }
                           }

        await container.create_item(body=item_definition)

async def clean_up(container):
    print('\nClean up the container\n')

    async for item in container.query_items(query='SELECT * FROM c'):
        # Deleting the current item
        await container.delete_item(item, partition_key=item['address']['state'])

async def read_change_feed(container):
    print('\nReading Change Feed from the beginning\n')

    # For a particular Partition Key Range we can use partition_key_range_id]
    # 'is_start_from_beginning = True' will read from the beginning of the history of the container
    # If no is_start_from_beginning is specified, the read change feed loop will pickup the items that happen while the loop / process is active
    await create_items(container, 10, 'WA')
    response_iterator = container.query_items_change_feed(is_start_from_beginning=True)

    # Because the asynchronous client returns an asynchronous iterator object for methods using queries,
    # we do not need to await the function. However, attempting to cast this object into a list directly
    # will throw an error; instead, iterate over the result using an async for loop like shown here
    async for doc in response_iterator:
        print(doc)

    print('\nFinished reading all the change feed\n')


async def read_change_feed_with_start_time(container):
    print('\nReading Change Feed from the start time\n')
    # You can read change feed from a specific time.
    # You must pass in a datetime object for the start_time field.

    # Create items
    await create_items(container, 10, 'WA')
    start_time = datetime.now(timezone.utc)
    time = start_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    print('\nReading Change Feed from start time of {}\n'.format(time))
    await create_items(container, 5, 'CA')
    await create_items(container, 5, 'OR')

    # Read change feed from the beginning
    response_iterator = container.query_items_change_feed(start_time="Beginning")
    async for doc in response_iterator:
        print(doc)

    # Read change feed from a start time
    response_iterator = container.query_items_change_feed(start_time=start_time)
    async for doc in response_iterator:
        print(doc)

async def read_change_feed_with_partition_key(container):
    print('\nReading Change Feed from the beginning of the partition key\n')
    # Create items
    await create_items(container, 10, 'WA')
    await create_items(container, 5, 'CA')
    await create_items(container, 5, 'OR')

    # Read change feed with partition key with LatestVersion mode.
    # Should only return change feed for the created items with 'CA' partition key
    response_iterator = container.query_items_change_feed(start_time="Beginning", partition_key="CA")
    async for doc in response_iterator:
        print(doc)

async def read_change_feed_with_continuation(container):
    print('\nReading Change Feed from the continuation\n')
    # Create items
    await create_items(container, 10, 'WA')
    response_iterator = container.query_items_change_feed(start_time="Beginning")
    async for doc in response_iterator:
        print(doc)
    continuation_token = container.client_connection.last_response_headers['etag']

    # Create additional items
    await create_items(container, 5, 'CA')
    await create_items(container, 5, 'OR')

    # You can read change feed from a specific continuation token.
    # You must pass in a valid continuation token.
    # From our continuation token above, you will get all items created after the continuation
    response_iterator = container.query_items_change_feed(continuation=continuation_token)
    async for doc in response_iterator:
        print(doc)

async def read_change_feed_with_all_versions_and_delete_mode(container):
    print('\nReading Change Feed with AllVersionsAndDeletes mode\n')
    # Read the initial change feed with 'AllVersionsAndDeletes' mode.
    # This initial call was made to store a point in time in a 'continuation' token
    response_iterator = container.query_items_change_feed(mode="AllVersionsAndDeletes")
    async for doc in response_iterator:
        print(doc)
    continuation_token = container.client_connection.last_response_headers['etag']

    # Read all change feed with 'AllVersionsAndDeletes' mode after create items from a continuation
    await create_items(container, 10, 'CA')
    await create_items(container, 10, 'OR')
    response_iterator = container.query_items_change_feed(mode="AllVersionsAndDeletes", continuation=continuation_token)
    async for doc in response_iterator:
        print(doc)

    # Read all change feed with 'AllVersionsAndDeletes' mode after delete items from a continuation
    await clean_up(container)
    response_iterator = container.query_items_change_feed(mode="AllVersionsAndDeletes", continuation=continuation_token)
    async for doc in response_iterator:
        print(doc)

async def read_change_feed_with_all_versions_and_delete_mode_with_partition_key(container):
    print('\nReading Change Feed with AllVersionsAndDeletes mode from the partition key\n')

    # Read the initial change feed with 'AllVersionsAndDeletes' mode with partition key('CA').
    # This initial call was made to store a point in time and 'partition_key' in a 'continuation' token
    response_iterator = container.query_items_change_feed(mode="AllVersionsAndDeletes", partition_key="CA")
    async for doc in response_iterator:
        print(doc)
    continuation_token = container.client_connection.last_response_headers['etag']

    await create_items(container, 10, 'CA')
    await create_items(container, 10, 'OR')
    # Read change feed 'AllVersionsAndDeletes' mode with 'CA' partition key value from the previous continuation.
    # Should only print the created items with 'CA' partition key value
    response_iterator = container.query_items_change_feed(mode='AllVersionsAndDeletes', continuation=continuation_token)
    async for doc in response_iterator:
        print(doc)
    continuation_token = container.client_connection.last_response_headers['etag']

    await clean_up(container)
    # Read change feed 'AllVersionsAndDeletes' mode with 'CA' partition key value from the previous continuation.
    # Should only print the deleted items with 'CA' partition key value
    response_iterator = container.query_items_change_feed(mode='AllVersionsAndDeletes', continuation=continuation_token)
    async for doc in response_iterator:
        print(doc)

async def run_sample():
    async with CosmosClient(HOST, MASTER_KEY) as client:
        # Delete pre-existing database
        try:
            await client.delete_database(DATABASE_ID)
        except exceptions.CosmosResourceNotFoundError:
            pass

        try:
            # setup database for this sample
            try:
                db = await client.create_database(id=DATABASE_ID)
            except exceptions.CosmosResourceExistsError:
                raise RuntimeError("Database with id '{}' already exists".format(DATABASE_ID))

            # setup container for this sample
            try:
                container = await db.create_container(
                    id=CONTAINER_ID,
                    partition_key=partition_key.PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash),
                    offer_throughput = 11000
                )
                print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            except exceptions.CosmosResourceExistsError:
                raise RuntimeError("Container with id '{}' already exists".format(CONTAINER_ID))

            # Read change feed from beginning
            await read_change_feed(container)
            await clean_up(container)

            # Read Change Feed from timestamp
            await read_change_feed_with_start_time(container)
            await clean_up(container)

            # Read Change Feed from continuation
            await read_change_feed_with_continuation(container)
            await clean_up(container)

            # Read Change Feed by partition_key
            await read_change_feed_with_partition_key(container)
            await clean_up(container)

            # Read change feed with 'AllVersionsAndDeletes' mode after create/delete item
            await read_change_feed_with_all_versions_and_delete_mode(container)
            await clean_up(container)

            # Read change feed with 'AllVersionsAndDeletes' mode with partition key for create/delete items.
            await read_change_feed_with_all_versions_and_delete_mode_with_partition_key(container)
            await clean_up(container)

            # cleanup database after sample
            try:
                await client.delete_database(db)
            except exceptions.CosmosResourceNotFoundError:
                pass

        except exceptions.CosmosHttpResponseError as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))

        finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    asyncio.run(run_sample())