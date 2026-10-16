# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copied async full-range SUM/MIN and scoped AVG with owned fixtures.

SQL, feed-range construction, parameters, and assertions are preserved.
Both parity columns use this fixture, not the original shared provisioning.
Three logical keys do not establish multiple physical partitions.
"""

import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from query_items import _legacy_feed_range_helpers as test_config

PK_VALUES = ('pk1', 'pk2', 'pk3')
RUN_MARKER_FIELD = "_run_marker"
RUN_MARKER_VALUE = str(uuid.uuid4())


@pytest.mark.cosmosEmulator
class TestQueryFeedRangeAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database_id = "legacy_query_sum_async_" + uuid.uuid4().hex
        self.database = await self.client.create_database(self.database_id)
        self.addAsyncCleanup(self._delete_owned_database)
        print(f"\nOwned async SUM database: {self.database_id}")
        self.container = await self._create_seeded_container("orders")

    async def _create_seeded_container(self, container_id):
        container = await self.database.create_container(
            id=container_id, partition_key=PartitionKey(path="/pk", kind="Hash"),
        )
        for pk in PK_VALUES:
            await container.upsert_item({
                "pk": pk, "id": str(uuid.uuid4()), "value": 100,
                RUN_MARKER_FIELD: RUN_MARKER_VALUE,
            })
        return container

    async def _delete_owned_database(self):
        await self.client.delete_database(self.database_id)
        print(f"Deleted owned async SUM database: {self.database_id}")

    async def test_query_value_min_across_full_feed_range_returns_scalar_async(self):
        """MIN over a multi-partition feed_range should return one value (the smallest)."""
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_min_across_full_feed_range_returns_scalar_async
        container = self.container
        query = (
            f'SELECT VALUE MIN(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        full_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(full_range)

        items = [item async for item in container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]

        assert len(items) == 1, (
            f"MIN should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100

    async def test_query_value_sum_across_full_feed_range_still_sums_async(self):
        """SUM should still add per-partition totals together."""
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_sum_across_full_feed_range_still_sums_async
        container = self.container
        query = (
            f'SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        full_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(full_range)

        items = [item async for item in container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]

        assert len(items) == 1, (
            f"SUM should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100 * len(PK_VALUES)

    async def test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async(self):
        """AVG scoped to a single-partition feed_range must still succeed."""
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async
        container = self.container
        query = (
            f'SELECT VALUE AVG(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        feed_range = await container.feed_range_from_partition_key(PK_VALUES[0])
        items = [item async for item in container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]

        assert items, "Single-partition AVG must return at least one result row"
        assert items[0] == 100, f"Expected AVG=100, got {items[0]}"

        # Preserve the second-container control without claiming the original topology.
        single_container = await self._create_seeded_container("single")
        single_feed_range = await single_container.feed_range_from_partition_key(PK_VALUES[0])
        single_items = [item async for item in single_container.query_items(
            query=query,
            feed_range=single_feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]
        assert single_items, "Single-partition container AVG must return a row"
        assert single_items[0] == 100
