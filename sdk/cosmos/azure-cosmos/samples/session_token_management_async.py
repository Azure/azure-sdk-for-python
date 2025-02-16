# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import random
import uuid
from typing import Dict, Any

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions

import asyncio
import config
from azure.identity.aio import DefaultAzureCredential
from azure.cosmos.http_constants import HttpHeaders

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to manage session tokens. By default, the SDK manages session tokens for you. These samples
# are for use cases where you want to manage session tokens yourself.
#
# 1. Storing session tokens in a cache by feed range from the partition key.
#
# 2. Storing session tokens in a cache by feed range from the container.
#
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
CREDENTIAL = DefaultAzureCredential()
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

async def storing_session_tokens_pk(container):
    print('1. Storing session tokens in a cache by feed range from the partition key.')


    cache: Dict[str, Any] = {}

    # Everything below is just a simulation of what could be run on different machines and clients
    # to store session tokens in a cache by feed range from the partition key.
    # The cache is a Dict here for simplicity but in a real-world scenario, it would be some service.
    feed_ranges_and_session_tokens = []
    previous_session_token = ""

    # populating cache with session tokens
    for i in range(5):
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
        target_feed_range = await container.feed_range_from_partition_key(item['pk'])
        response = await container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        # adding everything in the cache in case consolidation is possible
        for feed_range_json, session_token_cache in cache.items():
            feed_range = json.loads(feed_range_json)
            feed_ranges_and_session_tokens.append((feed_range, session_token_cache))
        feed_ranges_and_session_tokens.append((target_feed_range, session_token))
        latest_session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        # only doing this for the key to be immutable
        feed_range_json = json.dumps(target_feed_range)
        cache[feed_range_json] = latest_session_token
        previous_session_token = session_token


async def storing_session_tokens_container_feed_ranges(container):
    print('2. Storing session tokens in a cache by feed range from the container.')

    # The cache is a dictionary here for simplicity but in a real-world scenario, it would be some service.
    cache: Dict[str, Any] = {}

    # Everything below is just a simulation of what could be run on different machines and clients
    # to store session tokens in a cache by feed range from the partition key.
    feed_ranges_and_session_tokens = []
    previous_session_token = ""
    feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]

    # populating cache with session tokens
    for i in range(5):
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'pk': 'A' + str(random.randint(1, 10))
        }
        feed_range_from_pk = await container.feed_range_from_partition_key(item['pk'])
        response = await container.create_item(item, session_token=previous_session_token)
        session_token = response.get_response_headers()[HttpHeaders.SessionToken]
        # adding everything in the cache in case consolidation is possible

        for feed_range_json, session_token_cache in cache.items():
            feed_range = json.loads(feed_range_json)
            feed_ranges_and_session_tokens.append((feed_range, session_token_cache))
        target_feed_range = {}
        for feed_range in feed_ranges:
            if await container.is_feed_range_subset(feed_range, feed_range_from_pk):
                target_feed_range = feed_range
                break
        feed_ranges_and_session_tokens.append((target_feed_range, session_token))
        latest_session_token = await container.get_latest_session_token(feed_ranges_and_session_tokens, target_feed_range)
        # only doing this for the key to be immutable
        feed_range_json = json.dumps(target_feed_range)
        cache[feed_range_json] = latest_session_token
        previous_session_token = session_token


async def run_sample():
    async with CosmosClient(HOST, CREDENTIAL) as client:
        try:
            db = await client.create_database_if_not_exists(id=DATABASE_ID)
            container = await db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey('/pk'))

            # example of storing session tokens in cache by feed range from the partition key
            await storing_session_tokens_pk(container)

            # example of storing session tokens in cache by feed range from the container
            await storing_session_tokens_container_feed_ranges(container)

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
