# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.aio.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.documents as documents
import azure.cosmos.partition_key as partition_key
import uuid

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
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


async def create_items(container, size):
    print('Creating Items')

    for i in range(1, size):
        c = str(uuid.uuid4())
        item_definition = {'id': 'item' + c,
                                'address': {'street': '1 Microsoft Way'+c,
                                        'city': 'Redmond'+c,
                                        'state': 'WA',
                                        'zip code': 98052
                                        }
                                }

        await container.create_item(body=item_definition)


async def read_change_feed(container):
    print('\nReading Change Feed from the beginning\n')

    # For a particular Partition Key Range we can use partition_key_range_id]
    # 'is_start_from_beginning = True' will read from the beginning of the history of the container
    # If no is_start_from_beginning is specified, the read change feed loop will pickup the items that happen while the loop / process is active
    response = container.query_items_change_feed(is_start_from_beginning=True)

    # Because the asynchronous client returns an asynchronous iterator object for methods using queries,
    # we do not need to await the function. However, attempting to cast this object into a list directly 
    # will throw an error; instead, iterate over the result using an async for loop like shown here
    async for doc in response:
        print(doc)

    print('\nFinished reading all the change feed\n')


async def run_sample():
    async with cosmos_client.CosmosClient(HOST, MASTER_KEY) as client:
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
                    partition_key=partition_key.PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
                )
                print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            except exceptions.CosmosResourceExistsError:
                raise RuntimeError("Container with id '{}' already exists".format(CONTAINER_ID))

            await create_items(container, 100)
            await read_change_feed(container)

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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
