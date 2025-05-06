# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import uuid
import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic throughput bucket operations at the client, database, container and item levels.
#
# 1. Setting throughput buckets at the Client Level
#
# 2. Setting Throughput Buckets at the Item Level
#    2.1 - Read Item
#    2.2 - Create Item
#
# 3. Multi-Bucket Usage
#    3.1 - Create and Delete Item with Separate Buckets
#    3.2 - Create Client and Create Item with Separate Buckets
#    3.3 - Create, Upsert, and Delete Item with Separate Buckets
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Databases and Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

# Applies throughput bucket 1 to all requests from a client application
async def create_client_with_throughput_bucket(host=HOST, master_key=MASTER_KEY):
    async with CosmosClient(host, master_key, throughput_bucket=1) as client:
        pass

# Applies throughput bucket 2 for read item requests
async def container_read_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)
    created_container = await database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))
    created_document = await created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

    await created_container.read_item(
         item=created_document['id'],
         partition_key="mypk",
         throughput_bucket=2)

    await database.delete_container(created_container.id)

# Applies throughput bucket 3 for create item requests
async def container_create_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    created_container = await database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))

    await created_container.create_item(
        body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
        throughput_bucket=3)

    await database.delete_container(created_container.id)

# Applies throughput bucket 3 for create item requests and bucket 4 for delete item requests
async def container_create_and_delete_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    created_container = await database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))

    created_item = await created_container.create_item(
        body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
        throughput_bucket=3)

    await created_container.delete_item(
        created_item['id'],
        partition_key='mypk',
        throughput_bucket=4)

    await database.delete_container(created_container.id)

# Applies throughput bucket 1 to all requests from a client application, and bucket 2 to create item requests
async def create_client_and_item_with_throughput_bucket(host=HOST, master_key=MASTER_KEY):
    async with CosmosClient(host, master_key,
        throughput_bucket=1) as client:

        database = client.get_database_client(DATABASE_ID)

        created_container = await database.create_container(
            str(uuid.uuid4()),
            PartitionKey(path="/pk"))

        await created_container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=2)

        await database.delete_container(created_container.id)

# Applies throughput bucket 3 for create item requests, bucket 4 for upsert item requests, and bucket 5 for delete item
async def container_create_upsert_and_delete_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    created_container = await database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))

    created_item = await created_container.create_item(
        body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
        throughput_bucket=3)

    # add items for partition key 1
    for i in range(1, 3):
        await created_container.upsert_item(
            dict(id="item{}".format(i), pk='mypk', throughput_bucket=4))

    await created_container.delete_item(
        created_item['id'],
        partition_key='mypk',
        throughput_bucket=5)
    database.delete_container(created_container.id)

async def run_sample():
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY} ) as client:
        await client.create_database_if_not_exists(id=DATABASE_ID)
        try:
            # creates client
            await create_client_with_throughput_bucket()

            # reads an item from a container
            await container_read_item_throughput_bucket(client)

            # writes an item to a container
            await container_create_item_throughput_bucket(client)

            # creates and deletes an item to a container
            await container_create_and_delete_item_throughput_bucket(client)

            # creates a client and item with separate throughput buckets
            await create_client_and_item_with_throughput_bucket()

            # creates an item, upserts multiple items, and deletes an item all on separate throughput buckets
            await container_create_upsert_and_delete_item_throughput_bucket(client)

        except exceptions.CosmosHttpResponseError as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))

        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    asyncio.run(run_sample())
