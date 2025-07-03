# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import pytest
import test_config
import unittest
import uuid

from azure.cosmos import CosmosClient
from itertools import combinations
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
    document_definitions = [{PARTITION_KEY: pk, 'id': str(uuid.uuid4())} for pk in PK_VALUES]
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
class TestQueryFeedRange():
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
                enable_cross_partition_query=True,
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
                enable_cross_partition_query=True,
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
                enable_cross_partition_query=True,
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
            enable_cross_partition_query=True,
            feed_range=feed_range
        ))
        add_all_pk_values_to_set(items, actual_pk_values)
        assert expected_pk_values.issubset(actual_pk_values)

if __name__ == "__main__":
    unittest.main()
