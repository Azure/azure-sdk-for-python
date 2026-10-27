# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async discovered/key-scoped queries with owned 400/30,000 RU/s containers.

Both parity columns preserve the original data and container configurations.
Owned key-auth fixtures replace shared provisioning, not the test body.
"""

import os
import uuid
from typing import List, Mapping, Set

import pytest
import pytest_asyncio

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient

TEST_CONTAINERS_IDS = ["single", "multi"]
TEST_OFFER_THROUGHPUTS = [400, 30000]
PARTITION_KEY = "pk"
PK_VALUES = ('pk1', 'pk2', 'pk3')
RUN_MARKER_FIELD = "_run_marker"
RUN_MARKER_VALUE = str(uuid.uuid4())


async def add_all_pk_values_to_set_async(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)


@pytest_asyncio.fixture
async def setup_and_teardown_async(request, container_id):
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database_id = "legacy_query_ranges_async_" + uuid.uuid4().hex
        database = await client.create_database(database_id)
        print(f"\nOwned async feed-range query database: {database_id}")
        try:
            container = await database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/" + PARTITION_KEY, kind="Hash"),
                offer_throughput=TEST_OFFER_THROUGHPUTS[TEST_CONTAINERS_IDS.index(container_id)],
            )
            for pk in PK_VALUES:
                await container.upsert_item({
                    PARTITION_KEY: pk, "id": str(uuid.uuid4()), "value": 100,
                    RUN_MARKER_FIELD: RUN_MARKER_VALUE,
                })
            request.instance.data_db = database
            yield
        finally:
            request.instance.data_db = None
            await client.delete_database(database_id)
            print(f"\nDeleted owned async feed-range query database: {database_id}")


@pytest.mark.cosmosQuery
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestQueryFeedRangeAsync:
    data_db = None

    def get_container(self, container_id: str):
        return self.data_db.get_container_client(container_id)

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_for_all_partitions_async_rust(self, container_id):
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_for_all_partitions_async
        container = self.get_container(container_id)
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
    async def test_query_with_feed_range_for_partition_key_async_rust(self, container_id):
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_for_partition_key_async
        container = self.get_container(container_id)
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
