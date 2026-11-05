# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the async change-feed start-time test, which seeds items with upsert_item.

The fixture owns a unique database and provides the original key-auth (control-plane)
and data-plane database proxies, both Rust-backed. The test body is unchanged.
"""
import unittest
import uuid
from asyncio import sleep
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id


@pytest_asyncio.fixture()
async def setup():
    database_id = unique_database_id("upsert-change-feed-async")
    # Closed decision: Rust owns endpoint discovery and multi-write routing
    # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). Rust-backed clients reject the
    # original's multiple_write_locations argument (even False), so it is omitted.
    # Key-auth client for control-plane operations (create/delete containers)
    key_client = CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust")
    await key_client.__aenter__()
    # Data-plane client (AAD when configured, else key auth)
    data_client = create_data_client_async(_backend="rust")
    await data_client.__aenter__()
    try:
        key_db = await key_client.create_database(database_id)
        try:
            yield {
                "key_db": key_db,
                "data_db": data_client.get_database_client(database_id),
                "is_emulator": TestSettings.is_emulator
            }
        finally:
            await key_client.delete_database(database_id)
    finally:
        await data_client.close()
        await key_client.close()

def round_time():
    # Round now down to whole seconds: change feed start_time is second-granular, so
    # sub-second values would make the start_time checks flaky.
    utc_now = datetime.now(timezone.utc)
    return utc_now - timedelta(microseconds=utc_now.microsecond)

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestChangeFeedAsync:
    """Rust-path copy of tests/test_change_feed_async.py::TestChangeFeedAsync."""

    @pytest.mark.asyncio
    async def test_query_change_feed_with_start_time_rust(self, setup):
        # Source: tests/test_change_feed_async.py::TestChangeFeedAsync.test_query_change_feed_with_start_time
        # start_time must select only changes at or after that instant; a future time
        # returns nothing; a non-UTC time is normalized to UTC. Without it, timezone or
        # start-position bugs would slip through.
        container_id = "query_change_feed_start_time_test_" + str(uuid.uuid4())
        created_collection_ref = await setup["key_db"].create_container(
            container_id,
            PartitionKey(path="/pk")
        )
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)
        batchSize = 50

        async def create_random_items(container, batch_size):
            created_ids = set()
            for _ in range(batch_size):
                # Generate a Random partition key
                partition_key = 'pk' + str(uuid.uuid4())

                # Generate a random item
                item = {
                    'id': 'item' + str(uuid.uuid4()),
                    'pk': partition_key,
                    'content': 'This is some random content',
                }

                try:
                    # Create the item in the container
                    await container.upsert_item(item)
                    created_ids.add(item['id'])
                except exceptions.CosmosHttpResponseError as e:
                    pytest.fail(str(e))
            return created_ids

        try:
            # Create first batch of random items
            first_batch_ids = await create_random_items(created_collection, batchSize)

            # wait for 1 second and record the time, then wait another second
            await sleep(1)
            start_time = round_time()
            # Use an equivalent instant in a non-UTC timezone to validate SDK timezone normalization.
            not_utc_time = start_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
            await sleep(1)

            # now create another batch of items
            second_batch_ids = await create_random_items(created_collection, batchSize)

            # now query change feed based on start time
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=start_time)]
            change_feed_ids = {item['id'] for item in change_feed_iter}

            # start_time is second-granular; boundary writes from the first batch can be included.
            assert second_batch_ids.issubset(change_feed_ids)
            assert change_feed_ids.issubset(first_batch_ids.union(second_batch_ids))

            # negative test: pass in a valid time in the future
            future_time = start_time + timedelta(hours=1)
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=future_time)]
            # A future time should return 0
            assert len(change_feed_iter) == 0

            # test a date that is not utc, will be converted to utc by sdk
            change_feed_iter = [i async for i in created_collection.query_items_change_feed(start_time=not_utc_time)]
            change_feed_non_utc_ids = {item['id'] for item in change_feed_iter}
            assert change_feed_non_utc_ids == change_feed_ids
        finally:
            await setup["key_db"].delete_container(created_collection_ref.id)


if __name__ == '__main__':
    unittest.main()
