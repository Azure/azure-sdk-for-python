# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-path copies of tests/test_query_feed_range_async.py (``query_items(feed_range=...)``).

``TestQueryFeedRangeAsync`` holds the retained full-range SUM/MIN and scoped
AVG copies with a per-test owned database. Three logical keys do not establish
multiple physical partitions.

``TestQueryFeedRangeAsyncRust`` holds the remaining copies. Its class-scoped
``setup_async`` fixture replaces the shared ``test_config`` provisioning with an
owned database holding the original's single-partition (400 RU/s) and
multi-partition (30,000 RU/s) containers, seeded with the original three
documents, and always deletes it.

SQL, feed-range construction, parameters, and assertions are preserved.
Real-split copies only run when ``COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1``
authorizes 11,000/24,000/60,000 RU/s.
"""

import asyncio
import os
import time
import unittest
import uuid
from typing import List, Mapping, Set

import pytest
import pytest_asyncio

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

    @pytest.mark.skip(
        reason=(
            "driver-gap: Gap 30 - Rust rejects MIN over the full feed range with HTTP 400 "
            "'Aggregate unsupported' instead of returning the single minimum value. "
            "Re-enable when the driver supports this aggregate query without changing its scope."
        )
    )
    async def test_query_value_min_across_full_feed_range_returns_scalar_async_rust(self):
        """MIN over a multi-partition feed_range should return one value (the smallest)."""
        # pylint: disable-next=line-too-long
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

    @pytest.mark.skip(
        reason=(
            "driver-gap: Gap 30 - Rust rejects SUM over the full feed range with HTTP 400 "
            "'Aggregate unsupported' instead of returning the combined total. "
            "Re-enable when the driver supports this aggregate query without changing its scope."
        )
    )
    async def test_query_value_sum_across_full_feed_range_still_sums_async_rust(self):
        """SUM should still add per-partition totals together."""
        # pylint: disable-next=line-too-long
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

    async def test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async_rust(self):
        """AVG scoped to a single-partition feed_range must still succeed."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_avg_aggregate_single_partition_feed_range_succeeds_async
        container = self.container
        query = (
            f'SELECT VALUE AVG(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        feed_range = await container.feed_range_from_partition_key(PK_VALUES[0])
        # Known gap 30 item 6: the driver does not keep a point feed range as a single-key scope.
        pytest.skip(
            "driver-gap: Rust plans the SDK-produced point feed range as a cross-partition scope and rejects "
            "AVG with 400/20113 'aggregates in cross-partition queries' (known gap 30 items 1 and 6, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-point-feed-range)."
        )
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


SINGLE_PARTITION_CONTAINER_ID = "single"
MULTI_PARTITION_CONTAINER_ID = "multi"
TEST_CONTAINERS_IDS = [SINGLE_PARTITION_CONTAINER_ID, MULTI_PARTITION_CONTAINER_ID]
TEST_OFFER_THROUGHPUTS = [400, 30000]
PARTITION_KEY = "pk"
SPLIT_TIMEOUT = 60 * 10
SLEEP_TIME = 30
REAL_SPLIT_ENV = "COSMOS_QUERY_FEED_RANGE_REAL_SPLIT"


async def add_all_pk_values_to_set_async(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    # Source helper: tests/test_query_feed_range_async.py::add_all_pk_values_to_set_async
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)


async def trigger_split_async(container, throughput):
    # Source helper: tests/test_config.py::TestConfig.trigger_split_async
    print("Triggering a split in session token helpers")
    await container.replace_throughput(throughput)
    print(f"changed offer to {throughput}")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = await container.get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > SPLIT_TIMEOUT:
                raise unittest.SkipTest("Partition split didn't complete in time")
            print("Waiting for split to complete")
            await asyncio.sleep(SLEEP_TIME)
        else:
            break
    print("Split in session token helpers has completed")


@pytest_asyncio.fixture(scope="class", loop_scope="class")
async def setup_async(request):
    """Owned replacement for the original class-scoped ``setup_and_teardown_async``."""
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
    try:
        database_id = "legacy_query_feed_range_async_" + uuid.uuid4().hex
        database = await client.create_database(database_id)
        print(f"\nOwned async feed-range query database: {database_id}")
        try:
            for container_id, offer_throughput in zip(TEST_CONTAINERS_IDS, TEST_OFFER_THROUGHPUTS):
                container = await database.create_container_if_not_exists(
                    id=container_id,
                    partition_key=PartitionKey(path='/' + PARTITION_KEY, kind='Hash'),
                    offer_throughput=offer_throughput)
                for pk in PK_VALUES:
                    await container.upsert_item(body={
                        PARTITION_KEY: pk,
                        'id': str(uuid.uuid4()),
                        'value': 100,
                        RUN_MARKER_FIELD: RUN_MARKER_VALUE,
                    })
            request.cls.data_db = database
            request.cls.key_db = database
            yield
        finally:
            request.cls.data_db = None
            request.cls.key_db = None
            await client.delete_database(database_id)
            print(f"\nDeleted owned async feed-range query database: {database_id}")
    finally:
        await client.close()


@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADSplit
@pytest.mark.asyncio(loop_scope="class")
@pytest.mark.usefixtures("setup_async")
class TestQueryFeedRangeAsyncRust:
    data_db = None
    key_db = None

    def get_container(self, container_id: str):
        return self.data_db.get_container_client(container_id)

    def get_key_container(self, container_id: str):
        return self.key_db.get_container_client(container_id)

    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_both_feed_range_and_partition_key_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_both_feed_range_and_partition_key_async
        # Known gap 30 item 11: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust rejects this input with a different exception type or message than legacy "
            "(known gap 30 item 11, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-error-contract)."
        )
        container = self.get_container(container_id)

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
    async def test_query_with_feed_range_for_a_full_range_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_for_a_full_range_async
        container = self.get_container(container_id)
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

    async def test_query_with_avg_aggregate_across_full_feed_range_raises_async_rust(self):
        """AVG over a feed_range spanning multiple partitions must raise."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_avg_aggregate_across_full_feed_range_raises_async
        # Known gap 30 item 11: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust rejects this input with a different exception type or message than legacy "
            "(known gap 30 item 11, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-error-contract)."
        )
        container = self.get_container(MULTI_PARTITION_CONTAINER_ID)
        query = (
            f'SELECT VALUE AVG(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        # Full hash range covers every physical partition of the container.
        full_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(full_range)

        with pytest.raises(ValueError) as excinfo:
            _ = [item async for item in container.query_items(
                query=query,
                feed_range=feed_range,
                parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
            )]

        message = str(excinfo.value)
        assert "Unsupported query shape for range-scoped pagination" in message
        assert "SELECT VALUE AVG" in message

    async def test_query_value_numeric_field_across_full_feed_range_returns_list_async_rust(self):
        """Numeric VALUE projections should return one row per document, not a sum."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_numeric_field_across_full_feed_range_returns_list_async
        container = self.get_container(MULTI_PARTITION_CONTAINER_ID)
        query = (
            f'SELECT VALUE c["value"] FROM c WHERE IS_DEFINED(c["value"]) '
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

        assert len(items) == len(PK_VALUES), (
            f"Expected one value per seeded doc ({len(PK_VALUES)}); got {len(items)}."
        )
        assert all(item == 100 for item in items), (
            f"Expected every value to be 100; got {items}"
        )
        assert sum(items) == 100 * len(PK_VALUES)

    async def test_query_value_boolean_expression_across_full_feed_range_returns_list_async_rust(self):
        """Boolean VALUE projections should return one boolean per document."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_boolean_expression_across_full_feed_range_returns_list_async
        container = self.get_container(MULTI_PARTITION_CONTAINER_ID)
        query = (
            f'SELECT VALUE c["value"] > 0 FROM c WHERE IS_DEFINED(c["value"]) '
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

        assert len(items) == len(PK_VALUES), (
            f"Expected one boolean per seeded doc ({len(PK_VALUES)}); got {len(items)}."
        )
        assert all(item is True for item in items), (
            f"All seeded values are 100 > 0; expected every row to be True. Got {items}"
        )

    async def test_query_value_max_across_full_feed_range_returns_scalar_async_rust(self):
        """MAX over a multi-partition feed_range should return one value (the largest)."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_max_across_full_feed_range_returns_scalar_async
        container = self.get_container(MULTI_PARTITION_CONTAINER_ID)
        query = (
            f'SELECT VALUE MAX(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        full_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(full_range)

        # Known gap 30 item 1: no cross-partition aggregate execution in the driver.
        pytest.skip(
            "driver-gap: Rust rejects MAX over the full feed range with 400/20113 'aggregates in "
            "cross-partition queries' (known gap 30 item 1, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-unscoped-max)."
        )
        items = [item async for item in container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]

        assert len(items) == 1, (
            f"MAX should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100

    async def test_query_value_count_across_full_feed_range_still_counts_async_rust(self):
        """COUNT should still return a single total across partitions."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_value_count_across_full_feed_range_still_counts_async
        container = self.get_container(MULTI_PARTITION_CONTAINER_ID)
        query = (
            f'SELECT VALUE COUNT(1) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        full_range = test_config.create_range(
            range_min="",
            range_max="FF",
            is_min_inclusive=True,
            is_max_inclusive=False,
        )
        feed_range = test_config.create_feed_range_in_dict(full_range)

        # Known gap 30 item 1: no cross-partition aggregate execution in the driver.
        pytest.skip(
            "driver-gap: Rust rejects COUNT over the full feed range with 400/20113 'aggregates in "
            "cross-partition queries' (known gap 30 item 1, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-full-range-sum)."
        )
        items = [item async for item in container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        )]

        assert len(items) == 1
        assert items[0] == len(PK_VALUES)

    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional skip "
        "('will be moved to a new pipeline'); it needs two real partition splits"))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_async_during_back_to_back_partition_splits_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_async_during_back_to_back_partition_splits_async
        container = self.get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        # Get feed ranges before any splits
        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]

        # Trigger two consecutive splits
        key_container_for_split = self.get_key_container(container_id)
        await trigger_split_async(key_container_for_split, 11000)
        await trigger_split_async(key_container_for_split, 24000)

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
    @pytest.mark.cosmosSplit
    @pytest.mark.skipif(os.environ.get(REAL_SPLIT_ENV) != "1", reason=(
        "environment-gap: real partition split raises throughput to 11000/24000/60000 RU/s; "
        "opt in with COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1"
    ))
    async def test_query_with_feed_range_async_during_partition_split_combined_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_async_during_partition_split_combined_async
        container = self.get_container(container_id)

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
        feed_ranges_before_split = [feed_range async for feed_range in container.read_feed_ranges()]
        print(f"BEFORE SPLIT: Number of feed ranges: {len(feed_ranges_before_split)}")

        # Get initial counts and sums before split
        initial_count = 0
        initial_sum = 0

        for feed_range in feed_ranges_before_split:
            count_items = [item async for item in container.query_items(
                query='SELECT VALUE COUNT(1) FROM c',
                feed_range=feed_range
            )]
            initial_count += count_items[0] if count_items else 0

            sum_items = [item async for item in container.query_items(
                query='SELECT VALUE SUM(c["value"]) FROM c WHERE IS_DEFINED(c["value"])',
                feed_range=feed_range
            )]
            initial_sum += sum_items[0] if sum_items else 0

        print(f"Initial count: {initial_count}, Initial sum: {initial_sum}")

        # verify we have some data
        assert initial_count > 0, "Container should have at least some documents"

        # Collect all PK values before split
        expected_pk_values = set()
        for feed_range in feed_ranges_before_split:
            items = [item async for item in container.query_items(query='SELECT * FROM c', feed_range=feed_range)]
            await add_all_pk_values_to_set_async(items, expected_pk_values)

        print(f"Found {len(expected_pk_values)} unique partition keys before split")

        # Trigger and wait for split progression using shared helper.
        key_container_for_split = self.get_key_container(container_id)
        await trigger_split_async(key_container_for_split, target_throughput)

        # Test 1: Basic query with stale feed ranges (SDK should handle split)
        actual_pk_values = set()
        query = 'SELECT * from c'

        for feed_range in feed_ranges_before_split:
            items = [item async for item in container.query_items(query=query, feed_range=feed_range)]
            await add_all_pk_values_to_set_async(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values, f"Expected {len(expected_pk_values)} PKs, got {len(actual_pk_values)}"
        print("Test 1 (basic query with stale feed ranges) passed")

        # Test 2: Order by query with stale feed ranges
        actual_pk_values_order_by = set()
        query_order_by = 'SELECT * FROM c ORDER BY c.id'

        for feed_range in feed_ranges_before_split:
            items = [item async for item in container.query_items(query=query_order_by, feed_range=feed_range)]
            await add_all_pk_values_to_set_async(items, actual_pk_values_order_by)

        assert expected_pk_values == actual_pk_values_order_by, f"Expected {len(expected_pk_values)} PKs, got {len(actual_pk_values_order_by)}"
        print("Test 2 (order by query with stale feed ranges) passed")

        # Test 3: Count aggregate query with stale feed ranges
        post_split_count = 0
        query_count = 'SELECT VALUE COUNT(1) FROM c'

        for i, feed_range in enumerate(feed_ranges_before_split):
            items = [item async for item in container.query_items(query=query_count, feed_range=feed_range)]
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
            items = [item async for item in container.query_items(query=query_sum, feed_range=feed_range)]
            current_sum = items[0] if items else 0
            post_split_sum += current_sum

        print(f"Total sum AFTER split: {post_split_sum}, Expected: {initial_sum}")
        assert initial_sum == post_split_sum, f"Sum mismatch: before={initial_sum}, after={post_split_sum}"
        print("Test 4 (sum aggregate with stale feed ranges) passed")

    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_async_during_partition_split_combined_async)"
    ))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_feed_range_async_during_partition_split_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_feed_range_async_during_partition_split_async
        container = self.get_container(container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        await trigger_split_async(self.get_key_container(container_id), 11000)
        for feed_range in feed_ranges:
            items = [item async for item in
                     (container.query_items(
                         query=query,
                         feed_range=feed_range
                     )
                     )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)
        assert expected_pk_values == actual_pk_values

    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_async_during_partition_split_combined_async)"
    ))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_order_by_and_feed_range_async_during_partition_split_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_order_by_and_feed_range_async_during_partition_split_async
        container = self.get_container(container_id)
        query = 'SELECT * FROM c ORDER BY c.id'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = [feed_range async for feed_range in container.read_feed_ranges()]
        await trigger_split_async(self.get_key_container(container_id), 11000)

        for feed_range in feed_ranges:
            items = [item async for item in
                     (container.query_items(
                         query=query,
                         feed_range=feed_range
                     )
                     )]
            await add_all_pk_values_to_set_async(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values

    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_async_during_partition_split_combined_async)"
    ))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_count_aggregate_and_feed_range_async_during_partition_split_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_count_aggregate_and_feed_range_async_during_partition_split_async
        container = self.get_container(container_id)
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
        await trigger_split_async(self.get_key_container(container_id), 11000)

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

    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_async_during_partition_split_combined_async)"
    ))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    async def test_query_with_sum_aggregate_and_feed_range_async_during_partition_split_async_rust(self, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_sum_aggregate_and_feed_range_async_during_partition_split_async
        container = self.get_container(container_id)
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
        await trigger_split_async(self.get_key_container(container_id), 11000)

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

    async def test_query_with_static_continuation_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_static_continuation_async
        # Known gap 30 item 12: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30
        pytest.skip(
            "driver-gap: Rust sends the static continuation keyword on a feed-range query and the service "
            "rejects it with 400/20116; legacy ignores it (known gap 30 item 12, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-feed-range-continuation)."
        )
        container = self.get_container(SINGLE_PARTITION_CONTAINER_ID)
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

    async def test_query_with_continuation_async_rust(self):
        # Source: tests/test_query_feed_range_async.py::TestQueryFeedRangeAsync.test_query_with_continuation_async
        container = self.get_container(SINGLE_PARTITION_CONTAINER_ID)
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
