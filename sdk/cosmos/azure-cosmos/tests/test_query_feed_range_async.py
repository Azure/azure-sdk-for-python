# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
from unittest import mock

import pytest
import pytest_asyncio
import test_config
import unittest
import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from typing import List, Mapping, Set

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
TEST_NAME = "Query FeedRange "
SINGLE_PARTITION_CONTAINER_ID = TEST_NAME + CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID
MULTI_PARTITION_CONTAINER_ID = TEST_NAME + CONFIG.TEST_MULTI_PARTITION_CONTAINER_ID
TEST_CONTAINERS_IDS = [SINGLE_PARTITION_CONTAINER_ID, MULTI_PARTITION_CONTAINER_ID]
TEST_OFFER_THROUGHPUTS = [CONFIG.THROUGHPUT_FOR_1_PARTITION, CONFIG.THROUGHPUT_FOR_5_PARTITIONS]
PARTITION_KEY = CONFIG.TEST_CONTAINER_PARTITION_KEY
PK_VALUES = ('pk1', 'pk2', 'pk3')
async def add_all_pk_values_to_set_async(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)

@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    print("Setup: This runs before any tests")
    document_definitions = [{PARTITION_KEY: pk, 'id': str(uuid.uuid4()), 'value': 100} for pk in PK_VALUES]
    database = CosmosClient(HOST, KEY).get_database_client(DATABASE_ID)

    for container_id, offer_throughput in zip(TEST_CONTAINERS_IDS, TEST_OFFER_THROUGHPUTS):
        # Delete container if it exists to ensure clean state
        try:
            await database.delete_container(container_id)
            print(f"Deleted existing container: {container_id}")
        except Exception as e:
            print(f"Container {container_id} doesn't exist, creating new: {e}")

        # Create fresh container
        container = await database.create_container(
            id=container_id,
            partition_key=PartitionKey(path='/' + PARTITION_KEY, kind='Hash'),
            offer_throughput=offer_throughput)

        # Insert test data
        for document_definition in document_definitions:
            await container.upsert_item(body=document_definition)

        print(f"Created container {container_id} with {len(document_definitions)} documents")

    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

async def get_container(container_id: str):
    client = CosmosClient(HOST, KEY)
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(container_id)

@pytest.mark.cosmosQuery
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestQueryFeedRangeAsync:
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_for_all_partitions_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()
        async for feed_range in container.read_feed_ranges():
            items = [item async for item in
                (container.query_items(
                    query=query,
                    feed_range=feed_range
                )
            )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)
        assert expected_pk_values == actual_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_for_partition_key_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * from c'

        for pk_value in PK_VALUES:
            expected_pk_values = {pk_value}
            actual_pk_values = set()

            feed_range = await container.feed_range_from_partition_key(pk_value)
            items = [item async for item in
                (container.query_items(
                    query=query,
                    feed_range=feed_range
                )
            )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)
            assert expected_pk_values == actual_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_both_feed_range_and_partition_key_async(self, container_id):
        container = await get_container(container_id)

        expected_error_message = "'feed_range' and 'partition_key' are exclusive parameters, please only set one of them."
        query = 'SELECT * from c'
        partition_key = PK_VALUES[0]
        feed_range = await container.feed_range_from_partition_key(partition_key)
        with pytest.raises(ValueError) as e:
            items = [item async for item in
             (container.query_items(
                 query=query,
                 feed_range=feed_range,
                 partition_key=partition_key
             )
             )]
        assert str(e.value) == expected_error_message

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_for_a_full_range_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()
        new_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(new_range)
        items = [item async for item in
             (container.query_items(
                 query=query,
                 feed_range=feed_range
             )
         )]
        await add_all_pk_values_to_set_async(items, actual_pk_values)
        assert expected_pk_values.issubset(actual_pk_values)

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_async_during_back_to_back_partition_splits_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        # Get feed ranges before any splits
        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]

        # Trigger two consecutive splits
        await test_config.TestConfig.trigger_split_async(container, 11000)
        await test_config.TestConfig.trigger_split_async(container, 24000)

        # Query using the original feed ranges, the SDK should handle the splits
        for feed_range in feed_ranges:
            items = [item async for item in
                     (container.query_items(
                         query=query,
                         feed_range=feed_range
                     )
                     )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_async_during_partition_split_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        await test_config.TestConfig.trigger_split_async(container, 11000)
        for feed_range in feed_ranges:
            items = [item async for item in
                     (container.query_items(
                         query=query,
                         feed_range=feed_range
                     )
                     )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)
        assert expected_pk_values == actual_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_order_by_and_feed_range_async_during_partition_split_async(self, container_id):
        container = await get_container(container_id)
        query = 'SELECT * FROM c ORDER BY c.id'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        await test_config.TestConfig.trigger_split_async(container, 11000)

        for feed_range in feed_ranges:
            items = [item async for item in
                     (container.query_items(
                         query=query,
                         feed_range=feed_range
                     )
                     )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_count_aggregate_and_feed_range_async_during_partition_split_async(self, container_id):
        container = await get_container(container_id)
        # Get initial counts per feed range before split
        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        print(f"BEFORE SPLIT: Number of feed ranges: {len(feed_ranges)}")
        initial_total_count = 0

        for i, feed_range in enumerate(feed_ranges):
            query = 'SELECT VALUE COUNT(1) FROM c'
            items = [item async for item in container.query_items(query=query, feed_range=feed_range)]
            count = items[0] if items else 0
            print(f"Feed range {i} count BEFORE split: {count}")
            initial_total_count += count

        print(f"Total count BEFORE split: {initial_total_count}")

        # Trigger split
        await test_config.TestConfig.trigger_split_async(container, 11000)

        # Query with aggregate after split using original feed ranges
        post_split_total_count = 0
        for i, feed_range in enumerate(feed_ranges):
            query = 'SELECT VALUE COUNT(1) FROM c'
            items = [item async for item in container.query_items(query=query, feed_range=feed_range)]
            count = items[0] if items else 0
            print(f"Original feed range {i} count AFTER split: {count}")
            post_split_total_count += count

        print(f"Total count AFTER split using OLD ranges: {post_split_total_count}")
        print(f"Expected: {len(PK_VALUES)}")

        assert initial_total_count == post_split_total_count
        assert post_split_total_count == len(PK_VALUES)

        # Verify counts match (no data loss during split)
        print(f"Initial total count: {initial_total_count}, Post-split total count: {post_split_total_count}")
        assert initial_total_count == post_split_total_count
        print(f"len(PK_VALUES): {len(PK_VALUES)}, Post-split total count: {post_split_total_count}")
        assert post_split_total_count == len(PK_VALUES)

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_sum_aggregate_and_feed_range_async_during_partition_split_async(self, container_id):
        container = await get_container(container_id)
        # Get initial sums per feed range before split
        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        initial_total_sum = 0
        expected_total_sum = len(PK_VALUES) * 100

        for feed_range in feed_ranges:
            query = 'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])'
            items = [item async for item in container.query_items(query=query, feed_range=feed_range)]
            # The result for a SUM query on an empty set of rows is `undefined`.
            # The query returns no result pages in this case.
            current_sum = items[0] if items else 0
            initial_total_sum += current_sum

        # Trigger split
        await test_config.TestConfig.trigger_split_async(container, 11000)

        # Query with aggregate after split using original feed ranges
        post_split_total_sum = 0
        for feed_range in feed_ranges:
            query = 'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])'
            items = [item async for item in container.query_items(query=query, feed_range=feed_range)]
            current_sum = items[0] if items else 0
            post_split_total_sum += current_sum

        # Verify sums match (no data loss during split)
        assert initial_total_sum == post_split_total_sum
        assert post_split_total_sum == expected_total_sum


    async def test_query_with_static_continuation_async(self):
        container = await get_container(SINGLE_PARTITION_CONTAINER_ID)
        query = 'SELECT * from c'

        # verify continuation token does not have any impact
        for i in range(10):
            query_by_page = container.query_items(
                query=query,
                feed_range={
                    'Range': {'isMaxInclusive': False, 'isMinInclusive': True,
                              'max': '1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE',
                              'min': '0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'}},
                max_item_count=1,
                continuation='-RID:~a0NPAOszCpOChB4AAAAAAA==#RT:1#TRC:2#ISV:2#IEO:65567#QCF:8').by_page()
            async for page in query_by_page:
                items = [item async for item in page]
                assert len(items) > 0

    async def test_query_with_continuation_async(self):
        container = await get_container(SINGLE_PARTITION_CONTAINER_ID)
        query = 'SELECT * from c'

        # go through all feed ranges using pagination
        feed_ranges = container.read_feed_ranges()
        async for feed in feed_ranges:
            query_kwargs = {
                "query": query,
                "feed_range": feed,
                "priority": "Low",
                "max_item_count": 1
            }
            query_results = container.query_items(**query_kwargs)
            pager = query_results.by_page()
            first_page = await pager.__anext__()
            items = [item async for item in first_page]
            assert len(items) > 0
            continuation_token = pager.continuation_token
            # use that continuation token to restart the query, and drain it from there
            query_kwargs = {
                "query": query,
                "feed_range": feed,
                "continuation": continuation_token,
                "priority": "Low",
                "max_item_count": 2
            }
            query_results = container.query_items(**query_kwargs)
            pager = query_results.by_page(continuation_token=continuation_token)
            async for new_page in pager:
                items = [item async for item in new_page]
                assert len(items) > 0

if __name__ == "__main__":
    unittest.main()
