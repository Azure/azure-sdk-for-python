# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original discovered/key-scoped range queries with owned 400/30,000 RU/s containers.

Both parity columns preserve the original data and container configurations.
Owned key-auth fixtures replace shared provisioning, not the test body.
"""

import os
import uuid
from typing import List, Mapping, Set

import pytest

from azure.cosmos import CosmosClient, PartitionKey

TEST_CONTAINERS_IDS = ["single", "multi"]
TEST_OFFER_THROUGHPUTS = [400, 30000]
PARTITION_KEY = "pk"
PK_VALUES = ('pk1', 'pk2', 'pk3')
RUN_MARKER_FIELD = "_run_marker"
RUN_MARKER_VALUE = str(uuid.uuid4())


def add_all_pk_values_to_set(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)


@pytest.fixture
def setup(container_id):
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database_id = "legacy_query_ranges_" + uuid.uuid4().hex
        database = client.create_database(database_id)
        print(f"\nOwned feed-range query database: {database_id}")
        try:
            container = database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/" + PARTITION_KEY, kind="Hash"),
                offer_throughput=TEST_OFFER_THROUGHPUTS[TEST_CONTAINERS_IDS.index(container_id)],
            )
            for pk in PK_VALUES:
                container.upsert_item({
                    PARTITION_KEY: pk, "id": str(uuid.uuid4()), "value": 100,
                    RUN_MARKER_FIELD: RUN_MARKER_VALUE,
                })
            yield {"data_db": database}
        finally:
            client.delete_database(database_id)
            print(f"\nDeleted owned feed-range query database: {database_id}")


def get_container(setup, container_id: str):
    return setup["data_db"].get_container_client(container_id)


@pytest.mark.cosmosQuery
class TestQueryFeedRange:
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_for_all_partitions_rust(self, setup, container_id):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_feed_range_for_all_partitions
        container = get_container(setup, container_id)
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
    def test_query_with_feed_range_for_partition_key_rust(self, setup, container_id):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_feed_range_for_partition_key
        container = get_container(setup, container_id)
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
