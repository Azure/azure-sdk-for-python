# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import time

import pytest
import test_config
import unittest
import uuid

from azure.cosmos import CosmosClient, exceptions
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
def add_all_pk_values_to_set(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)

@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    print("Setup: This runs before any tests")
    document_definitions = [{PARTITION_KEY: pk, 'id': str(uuid.uuid4()), 'value': 100} for pk in PK_VALUES]
    database = CosmosClient(HOST, KEY).get_database_client(DATABASE_ID)

    for container_id, offer_throughput in zip(TEST_CONTAINERS_IDS, TEST_OFFER_THROUGHPUTS):
        container = database.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path='/' + PARTITION_KEY, kind='Hash'),
            offer_throughput=offer_throughput)
        for document_definition in document_definitions:
            container.upsert_item(body=document_definition)
    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

def get_container(container_id: str):
    client = CosmosClient(HOST, KEY)
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(container_id)

@pytest.mark.cosmosQuery
class TestQueryFeedRange:
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_for_all_partitions(self, container_id):
        container = get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()
        iter_feed_ranges = list(container.read_feed_ranges())
        for feed_range in iter_feed_ranges:
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)
        assert actual_pk_values == expected_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_for_partition_key(self, container_id):
        container = get_container(container_id)
        query = 'SELECT * from c'

        for pk_value in PK_VALUES:
            expected_pk_values = {pk_value}
            actual_pk_values = set()

            feed_range = container.feed_range_from_partition_key(pk_value)
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)
            assert actual_pk_values == expected_pk_values

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_both_feed_range_and_partition_key(self, container_id):
        container = get_container(container_id)

        expected_error_message = "'feed_range' and 'partition_key' are exclusive parameters, please only set one of them."
        query = 'SELECT * from c'
        partition_key = PK_VALUES[0]
        feed_range = container.feed_range_from_partition_key(partition_key)
        with pytest.raises(ValueError) as e:
            list(container.query_items(
                query=query,
                feed_range=feed_range,
                partition_key=partition_key
            ))
        assert str(e.value) == expected_error_message

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_for_a_full_range(self, container_id):
        container = get_container(container_id)
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
        items = list(container.query_items(
            query=query,
            feed_range=feed_range
        ))
        add_all_pk_values_to_set(items, actual_pk_values)
        assert expected_pk_values.issubset(actual_pk_values)

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_during_partition_split_combined(self, container_id):
        container = get_container(container_id)

        # Differentiate behavior based on container type
        if container_id == SINGLE_PARTITION_CONTAINER_ID:
            # Single partition: starts at 400 RU/s, increase to trigger split
            target_throughput = 11000
            print(f"Single-partition container: increasing from ~400 to {target_throughput}")
        else:  # MULTI_PARTITION_CONTAINER_ID
            # Multi-partition: starts at 30000 RU/s, increase further to trigger more splits
            target_throughput = 60000
            print(f"Multi-partition container: increasing from 30000 to {target_throughput}")

        # Get feed ranges before split
        feed_ranges_before_split = list(container.read_feed_ranges())
        print(f"BEFORE SPLIT: Number of feed ranges: {len(feed_ranges_before_split)}")

        # Get initial counts and sums before split
        initial_count = 0
        initial_sum = 0

        for feed_range in feed_ranges_before_split:
            count_items = list(container.query_items(
                query='SELECT VALUE COUNT(1) FROM c',
                feed_range=feed_range
            ))
            initial_count += count_items[0] if count_items else 0

            sum_items = list(container.query_items(
                query='SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])',
                feed_range=feed_range
            ))
            initial_sum += sum_items[0] if sum_items else 0

        print(f"Initial count: {initial_count}, Initial sum: {initial_sum}")

        # verify we have some data
        assert initial_count > 0, "Container should have at least some documents"

        # Collect all PK values before split
        expected_pk_values = set()
        for feed_range in feed_ranges_before_split:
            items = list(container.query_items(query='SELECT * FROM c', feed_range=feed_range))
            add_all_pk_values_to_set(items, expected_pk_values)

        print(f"Found {len(expected_pk_values)} unique partition keys before split")

        # Trigger split
        # test_config.TestConfig.trigger_split(container, target_throughput)
        container.replace_throughput(target_throughput)
        # wait for the split to begin
        time.sleep(20)

        # Test 1: Basic query with stale feed ranges (SDK should handle split)
        actual_pk_values = set()
        query = 'SELECT * from c'

        for feed_range in feed_ranges_before_split:
            items = list(container.query_items(query=query, feed_range=feed_range))
            add_all_pk_values_to_set(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values, f"Expected {len(expected_pk_values)} PKs, got {len(actual_pk_values)}"
        print("Test 1 (basic query with stale feed ranges) passed")

        # Test 2: Order by query with stale feed ranges
        actual_pk_values_order_by = set()
        query_order_by = 'SELECT * FROM c ORDER BY c.id'

        for feed_range in feed_ranges_before_split:
            items = list(container.query_items(query=query_order_by, feed_range=feed_range))
            add_all_pk_values_to_set(items, actual_pk_values_order_by)

        assert expected_pk_values == actual_pk_values_order_by, f"Expected {len(expected_pk_values)} PKs, got {len(actual_pk_values_order_by)}"
        print("Test 2 (order by query with stale feed ranges) passed")

        # Test 3: Count aggregate query with stale feed ranges
        post_split_count = 0
        query_count = 'SELECT VALUE COUNT(1) FROM c'

        for i, feed_range in enumerate(feed_ranges_before_split):
            items = list(container.query_items(query=query_count, feed_range=feed_range))
            count = items[0] if items else 0
            print(f"Feed range {i} count AFTER split: {count}")
            post_split_count += count

        print(f"Total count AFTER split: {post_split_count}, Expected: {initial_count}")
        assert initial_count == post_split_count, f"Count mismatch: before={initial_count}, after={post_split_count}"
        print("Test 3 (count aggregate with stale feed ranges) passed")

        # Test 4: Sum aggregate query with stale feed ranges
        post_split_sum = 0
        query_sum = 'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])'

        for feed_range in feed_ranges_before_split:
            items = list(container.query_items(query=query_sum, feed_range=feed_range))
            current_sum = items[0] if items else 0
            post_split_sum += current_sum

        print(f"Total sum AFTER split: {post_split_sum}, Expected: {initial_sum}")
        assert initial_sum == post_split_sum, f"Sum mismatch: before={initial_sum}, after={post_split_sum}"
        print("Test 4 (sum aggregate with stale feed ranges) passed")

    @pytest.mark.skip(reason="Covered by test_query_with_feed_range_during_partition_split_combined")
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_during_partition_split(self, container_id):
        container = get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = list(container.read_feed_ranges())
        test_config.TestConfig.trigger_split(container, 11000)
        for feed_range in feed_ranges:
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)
        assert expected_pk_values == actual_pk_values

    @pytest.mark.skip(reason="Covered by test_query_with_feed_range_during_partition_split_combined")
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_order_by_and_feed_range_during_partition_split(self, container_id):
        container = get_container(container_id)
        query = 'SELECT * FROM c ORDER BY c.id'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = list(container.read_feed_ranges())
        test_config.TestConfig.trigger_split(container, 11000)

        for feed_range in feed_ranges:
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values

    @pytest.mark.skip(reason="Covered by test_query_with_feed_range_during_partition_split_combined")
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_count_aggregate_and_feed_range_during_partition_split(self, container_id):
        container = get_container(container_id)
        # Get initial counts per feed range before split
        feed_ranges = list(container.read_feed_ranges())
        initial_total_count = 0

        for feed_range in feed_ranges:
            query = 'SELECT VALUE COUNT(1) FROM c'
            items = list(container.query_items(query=query, feed_range=feed_range))
            count = items[0] if items else 0
            initial_total_count += count

        # Trigger split
        test_config.TestConfig.trigger_split(container, 11000)

        # Query with aggregate after split using original feed ranges
        post_split_total_count = 0
        for feed_range in feed_ranges:
            query = 'SELECT VALUE COUNT(1) FROM c'
            items = list(container.query_items(query=query, feed_range=feed_range))
            count = items[0] if items else 0
            post_split_total_count += count

        # Verify counts match (no data loss during split)
        assert initial_total_count == post_split_total_count
        assert post_split_total_count == len(PK_VALUES)

    @pytest.mark.skip(reason="Covered by test_query_with_feed_range_during_partition_split_combined")
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_sum_aggregate_and_feed_range_during_partition_split(self, container_id):
        container = get_container(container_id)
        # Get initial sums per feed range before split
        feed_ranges = list(container.read_feed_ranges())
        initial_total_sum = 0
        expected_total_sum = len(PK_VALUES) * 100

        for feed_range in feed_ranges:
            query = 'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])'
            items = list(container.query_items(query=query, feed_range=feed_range))
            # The result for a SUM query on an empty set of rows is `undefined`.
            # The query returns no result pages in this case.
            current_sum = items[0] if items else 0
            initial_total_sum += current_sum

        # Trigger split
        test_config.TestConfig.trigger_split(container, 11000)

        # Query with aggregate after split using original feed ranges
        post_split_total_sum = 0
        for feed_range in feed_ranges:
            query = 'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])'
            items = list(container.query_items(query=query, feed_range=feed_range))
            current_sum = items[0] if items else 0
            post_split_total_sum += current_sum

        # Verify sums match (no data loss during split)
        assert initial_total_sum == post_split_total_sum
        assert post_split_total_sum == expected_total_sum

    def test_query_with_static_continuation(self):
        container = get_container(SINGLE_PARTITION_CONTAINER_ID)
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
            for page in query_by_page:
                items = list(page)
                assert len(items) > 0

    def test_query_with_continuation(self):
        container = get_container(SINGLE_PARTITION_CONTAINER_ID)
        query = 'SELECT * from c'

        # go through all feed ranges using pagination
        feed_ranges = container.read_feed_ranges()
        for feed in feed_ranges:
            query_kwargs = {
                "query": query,
                "feed_range": feed,
                "priority": "Low",
                "max_item_count": 1
            }
            query_results = container.query_items(**query_kwargs)
            pager = query_results.by_page()
            first_page = next(pager)
            items = list(first_page)
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
            for new_page in pager:
                items = list(new_page)
                assert len(items) > 0

if __name__ == "__main__":
    unittest.main()
