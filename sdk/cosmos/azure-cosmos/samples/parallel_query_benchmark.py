# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""Sample showing how to use max_degree_of_parallelism and max_buffered_item_count
to speed up cross-partition queries with the async Cosmos DB client.

Prerequisites:
    1. An Azure Cosmos account -
       https://azure.microsoft.com/documentation/articles/documentdb-create-account/
    2. Microsoft Azure Cosmos PyPi package -
       https://pypi.python.org/pypi/azure-cosmos/
"""

import asyncio
from azure.cosmos.aio import CosmosClient
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


async def query_items_serial(container):
    """Query items with the default serial execution (degree=0)."""
    print('\n1.1 Cross-partition query - serial (default)\n')

    items = container.query_items(
        query="SELECT * FROM c",
    )
    item_list = [item async for item in items]
    print('Got {} items with serial execution'.format(len(item_list)))


async def query_items_parallel(container):
    """Query items with parallel execution across partitions."""
    print('\n1.2 Cross-partition query - parallel (degree=4)\n')

    # Use max_degree_of_parallelism to fetch from multiple partitions concurrently
    items = container.query_items(
        query="SELECT * FROM c",
        max_degree_of_parallelism=4,
    )
    item_list = [item async for item in items]
    print('Got {} items with degree=4'.format(len(item_list)))


async def query_items_parallel_with_buffer(container):
    """Query items with both parallel execution and a buffered item count."""
    print('\n1.3 Cross-partition query - parallel with buffering\n')

    # max_buffered_item_count controls how many items can be buffered ahead
    # while the consumer processes results
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c.category",
        max_degree_of_parallelism=8,
        max_buffered_item_count=500,
    )
    item_list = [item async for item in items]
    print('Got {} items with degree=8 and buffer=500'.format(len(item_list)))


async def run_sample():
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            db = client.get_database_client(DATABASE_ID)
            container = db.get_container_client(CONTAINER_ID)

            await query_items_serial(container)
            await query_items_parallel(container)
            await query_items_parallel_with_buffer(container)

        except Exception as e:
            print('\nrun_sample has caught an error. {0}'.format(e))

        finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    asyncio.run(run_sample())
