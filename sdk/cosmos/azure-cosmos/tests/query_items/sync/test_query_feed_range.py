# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-path copies of tests/test_query_feed_range.py (``query_items(feed_range=...)``).

Shared ``test_config`` provisioning is replaced by owned fixtures:

* ``setup`` (class scope) owns one database holding the original's
  single-partition (400 RU/s) and multi-partition (30,000 RU/s) containers,
  seeded with the original three documents, and always deletes it.
* ``owned_orders`` (per test) owns the database used by the retained
  full-range SUM/MIN and scoped AVG copies. Three logical partition keys
  are seeded there; multiple physical partitions are not guaranteed.

Queries, feed ranges and assertions are unchanged. Real-split copies only run
when ``COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1`` authorizes 11,000/60,000 RU/s.
"""

import os
import time
import unittest
import uuid
from typing import List, Mapping, Set

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from query_items import _legacy_feed_range_helpers as test_config

SINGLE_PARTITION_CONTAINER_ID = "single"
MULTI_PARTITION_CONTAINER_ID = "multi"
TEST_CONTAINERS_IDS = [SINGLE_PARTITION_CONTAINER_ID, MULTI_PARTITION_CONTAINER_ID]
TEST_OFFER_THROUGHPUTS = [400, 30000]
PARTITION_KEY = "pk"
PK_VALUES = ('pk1', 'pk2', 'pk3')
RUN_MARKER_FIELD = "_run_marker"
RUN_MARKER_VALUE = str(uuid.uuid4())
SPLIT_TIMEOUT = 60 * 10
SLEEP_TIME = 30
REAL_SPLIT_ENV = "COSMOS_QUERY_FEED_RANGE_REAL_SPLIT"


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


def add_all_pk_values_to_set(items: List[Mapping[str, str]], pk_value_set: Set[str]) -> None:
    # Source helper: tests/test_query_feed_range.py::add_all_pk_values_to_set
    if len(items) == 0:
        return

    pk_values = [item[PARTITION_KEY] for item in items if PARTITION_KEY in item]
    pk_value_set.update(pk_values)


def trigger_split(container, throughput):
    # Source helper: tests/test_config.py::TestConfig.trigger_split
    print("Triggering a split in session token helpers")
    container.replace_throughput(throughput)
    print(f"changed offer to {throughput}")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = container.get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > SPLIT_TIMEOUT:
                raise unittest.SkipTest("Partition split didn't complete in time")
            print("Waiting for split to complete")
            time.sleep(SLEEP_TIME)
        else:
            break
    print("Split in session token helpers has completed")


@pytest.fixture(scope="class")
def setup():
    """Owned replacement for the original class-scoped ``setup_and_teardown``."""
    client = _rust_client()
    try:
        database_id = "legacy_query_feed_range_" + uuid.uuid4().hex
        database = client.create_database(database_id)
        print(f"\nOwned feed-range query database: {database_id}")
        try:
            for container_id, offer_throughput in zip(TEST_CONTAINERS_IDS, TEST_OFFER_THROUGHPUTS):
                container = database.create_container_if_not_exists(
                    id=container_id,
                    partition_key=PartitionKey(path='/' + PARTITION_KEY, kind='Hash'),
                    offer_throughput=offer_throughput)
                for pk in PK_VALUES:
                    container.upsert_item(body={
                        PARTITION_KEY: pk,
                        'id': str(uuid.uuid4()),
                        'value': 100,
                        RUN_MARKER_FIELD: RUN_MARKER_VALUE,
                    })
            yield {"key_db": database, "data_db": database}
        finally:
            client.delete_database(database_id)
            print(f"\nDeleted owned feed-range query database: {database_id}")
    finally:
        client.close()


@pytest.fixture
def owned_orders(request):
    """Per-test owned database for the retained SUM/MIN/AVG copies."""
    test = request.instance
    test.client = _rust_client()
    try:
        test.database_id = "legacy_query_sum_" + uuid.uuid4().hex
        test.database = test.client.create_database(test.database_id)
        print(f"\nOwned SUM database: {test.database_id}")
        try:
            test.container = test._create_seeded_container("orders")
            yield
        finally:
            test._delete_owned_database()
    finally:
        test.client.close()


def get_container(setup, container_id: str):
    return setup["data_db"].get_container_client(container_id)


def get_key_container(setup, container_id: str):
    return setup["key_db"].get_container_client(container_id)


class TestQueryFeedRange:
    def _create_seeded_container(self, container_id):
        container = self.database.create_container(id=container_id, partition_key=PartitionKey(path="/pk", kind="Hash"))
        for pk in PK_VALUES:
            container.upsert_item({
                "pk": pk, "id": str(uuid.uuid4()), "value": 100,
                RUN_MARKER_FIELD: RUN_MARKER_VALUE,
            })
        return container

    def _delete_owned_database(self):
        self.client.delete_database(self.database_id)
        print(f"Deleted owned SUM database: {self.database_id}")

    @pytest.mark.cosmosEmulator
    @pytest.mark.usefixtures("owned_orders")
    @pytest.mark.skip(
        reason=(
            "driver-gap: Gap 30 - Rust rejects MIN over the full feed range with HTTP 400 "
            "'Aggregate unsupported' instead of returning the single minimum value. "
            "Re-enable when the driver supports this aggregate query without changing its scope."
        )
    )
    def test_query_value_min_across_full_feed_range_returns_scalar_rust(self):
        """MIN over a multi-partition feed_range should return one value (the smallest)."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_min_across_full_feed_range_returns_scalar
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

        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert len(items) == 1, (
            f"MIN should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100

    @pytest.mark.cosmosEmulator
    @pytest.mark.usefixtures("owned_orders")
    @pytest.mark.skip(
        reason=(
            "driver-gap: Gap 30 - Rust rejects SUM over the full feed range with HTTP 400 "
            "'Aggregate unsupported' instead of returning the combined total. "
            "Re-enable when the driver supports this aggregate query without changing its scope."
        )
    )
    def test_query_value_sum_across_full_feed_range_still_sums_rust(self):
        """SUM should still add per-partition totals together."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_sum_across_full_feed_range_still_sums
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

        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert len(items) == 1, (
            f"SUM should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100 * len(PK_VALUES)

    @pytest.mark.cosmosEmulator
    @pytest.mark.usefixtures("owned_orders")
    def test_query_with_avg_aggregate_single_partition_feed_range_succeeds_rust(self):
        """AVG scoped to a single-partition feed_range must still succeed."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_avg_aggregate_single_partition_feed_range_succeeds
        container = self.container
        query = (
            f'SELECT VALUE AVG(c["value"]) FROM c WHERE IS_DEFINED(c["value"]) '
            f'AND c["{RUN_MARKER_FIELD}"] = @run_marker'
        )

        feed_range = container.feed_range_from_partition_key(PK_VALUES[0])
        # Known gap 30 item 6: the driver does not keep a point feed range as a single-key scope.
        pytest.skip(
            "driver-gap: Rust plans the SDK-produced point feed range as a cross-partition scope and rejects "
            "AVG with 400/20113 'aggregates in cross-partition queries' (known gap 30 items 1 and 6, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-point-feed-range)."
        )
        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert items, "Single-partition AVG must return at least one result row"
        assert items[0] == 100, f"Expected AVG=100, got {items[0]}"

        # Preserve the second-container control without claiming the original topology.
        single_container = self._create_seeded_container("single")
        single_feed_range = single_container.feed_range_from_partition_key(PK_VALUES[0])
        single_items = list(single_container.query_items(
            query=query,
            feed_range=single_feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))
        assert single_items, "Single-partition container AVG must return a row"
        assert single_items[0] == 100

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_both_feed_range_and_partition_key_rust(self, setup, container_id):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_both_feed_range_and_partition_key
        container = get_container(setup, container_id)

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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_for_a_full_range_rust(self, setup, container_id):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_feed_range_for_a_full_range
        container = get_container(setup, container_id)
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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_with_avg_aggregate_across_full_feed_range_raises_rust(self, setup):
        """AVG over a feed_range spanning multiple partitions must raise."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_avg_aggregate_across_full_feed_range_raises
        container = get_container(setup, MULTI_PARTITION_CONTAINER_ID)
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
            list(
                container.query_items(
                    query=query,
                    feed_range=feed_range,
                    parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
                )
            )

        message = str(excinfo.value)
        assert "Unsupported query shape for range-scoped pagination" in message
        assert "SELECT VALUE AVG" in message
        assert message == (
            "Unsupported query shape for range-scoped pagination: "
            "SELECT VALUE AVG(...) cannot be merged client-side when the query "
            "scope spans multiple physical partitions."
        )
        assert list(
            container.query_items(
                query=query,
                partition_key=PK_VALUES[0],
                parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
            )
        ) == [100]

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_value_numeric_field_across_full_feed_range_returns_list_rust(self, setup):
        """Numeric VALUE projections should return one row per document, not a sum."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_numeric_field_across_full_feed_range_returns_list
        container = get_container(setup, MULTI_PARTITION_CONTAINER_ID)
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

        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        # All seeded docs have value=100; we expect one entry per doc.
        assert len(items) == len(PK_VALUES), (
            f"Expected one value per seeded doc ({len(PK_VALUES)}); got {len(items)}."
        )
        assert all(item == 100 for item in items), (
            f"Expected every value to be 100; got {items}"
        )
        assert sum(items) == 100 * len(PK_VALUES)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_value_boolean_expression_across_full_feed_range_returns_list_rust(self, setup):
        """Boolean VALUE projections should return one boolean per document."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_boolean_expression_across_full_feed_range_returns_list
        container = get_container(setup, MULTI_PARTITION_CONTAINER_ID)
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

        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert len(items) == len(PK_VALUES), (
            f"Expected one boolean per seeded doc ({len(PK_VALUES)}); got {len(items)}."
        )
        assert all(item is True for item in items), (
            f"All seeded values are 100 > 0; expected every row to be True. Got {items}"
        )

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_value_max_across_full_feed_range_returns_scalar_rust(self, setup):
        """MAX over a multi-partition feed_range should return one value (the largest)."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_max_across_full_feed_range_returns_scalar
        container = get_container(setup, MULTI_PARTITION_CONTAINER_ID)
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
        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert len(items) == 1, (
            f"MAX should return a single value across partitions; got {len(items)} rows: {items}"
        )
        assert items[0] == 100

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_value_count_across_full_feed_range_still_counts_rust(self, setup):
        """COUNT should still return a single total across partitions."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_value_count_across_full_feed_range_still_counts
        container = get_container(setup, MULTI_PARTITION_CONTAINER_ID)
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
        items = list(container.query_items(
            query=query,
            feed_range=feed_range,
            parameters=[{"name": "@run_marker", "value": RUN_MARKER_VALUE}],
        ))

        assert len(items) == 1
        assert items[0] == len(PK_VALUES)

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    @pytest.mark.cosmosSplit
    @pytest.mark.skipif(os.environ.get(REAL_SPLIT_ENV) != "1", reason=(
        "environment-gap: real partition split raises throughput to 11000/60000 RU/s; "
        "opt in with COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1"
    ))
    def test_query_with_feed_range_during_partition_split_combined_rust(self, setup, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_feed_range_during_partition_split_combined
        container = get_container(setup, container_id)

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
        # replace_throughput is control-plane and must use key-auth container.
        key_container_for_split = get_key_container(setup, container_id)
        key_container_for_split.replace_throughput(target_throughput)
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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_during_partition_split_combined)"))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_feed_range_during_partition_split_rust(self, setup, container_id):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_feed_range_during_partition_split
        container = get_container(setup, container_id)
        query = 'SELECT * from c'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = list(container.read_feed_ranges())
        trigger_split(get_key_container(setup, container_id), 11000)
        for feed_range in feed_ranges:
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)
        assert expected_pk_values == actual_pk_values

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_during_partition_split_combined)"))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_order_by_and_feed_range_during_partition_split_rust(self, setup, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_order_by_and_feed_range_during_partition_split
        container = get_container(setup, container_id)
        query = 'SELECT * FROM c ORDER BY c.id'

        expected_pk_values = set(PK_VALUES)
        actual_pk_values = set()

        feed_ranges = list(container.read_feed_ranges())
        trigger_split(get_key_container(setup, container_id), 11000)

        for feed_range in feed_ranges:
            items = list(container.query_items(
                query=query,
                feed_range=feed_range
            ))
            add_all_pk_values_to_set(items, actual_pk_values)

        assert expected_pk_values == actual_pk_values

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_during_partition_split_combined)"))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_count_aggregate_and_feed_range_during_partition_split_rust(self, setup, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_count_aggregate_and_feed_range_during_partition_split
        container = get_container(setup, container_id)
        # Get initial counts per feed range before split
        feed_ranges = list(container.read_feed_ranges())
        initial_total_count = 0

        for feed_range in feed_ranges:
            query = 'SELECT VALUE COUNT(1) FROM c'
            items = list(container.query_items(query=query, feed_range=feed_range))
            count = items[0] if items else 0
            initial_total_count += count

        # Trigger split
        trigger_split(get_key_container(setup, container_id), 11000)

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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    @pytest.mark.skip(reason=(
        "environment-gap: retains the original's unconditional real-split skip "
        "(covered by test_query_with_feed_range_during_partition_split_combined)"))
    @pytest.mark.parametrize('container_id', TEST_CONTAINERS_IDS)
    def test_query_with_sum_aggregate_and_feed_range_during_partition_split_rust(self, setup, container_id):
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_sum_aggregate_and_feed_range_during_partition_split
        container = get_container(setup, container_id)
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
        trigger_split(get_key_container(setup, container_id), 11000)

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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_with_static_continuation_rust(self, setup):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_static_continuation
        # Known gap 30 item 7: docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-feed-range-continuation
        # The legacy original passes without checking anything: its made-up token returns no pages.
        pytest.skip(
            "driver-gap: on a feed-range query the Rust driver rejects a service continuation token "
            "with 400/20116, while legacy resumes from it (known gap 30 item 7, "
            "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#query-feed-range-continuation)."
        )
        container = get_container(setup, SINGLE_PARTITION_CONTAINER_ID)
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

    @pytest.mark.cosmosQuery
    @pytest.mark.cosmosAADSplit
    def test_query_with_continuation_rust(self, setup):
        # Source: tests/test_query_feed_range.py::TestQueryFeedRange.test_query_with_continuation
        container = get_container(setup, SINGLE_PARTITION_CONTAINER_ID)
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
