# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import random
import time
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey, ContainerProxy
from azure.cosmos.exceptions import CosmosHttpResponseError
from unittest.mock import patch, MagicMock
from azure.cosmos import http_constants
from azure.cosmos import _base


def run_queries(container, iterations):
    ret_list = []
    for i in range(iterations):
        curr = str(random.randint(0, 10))
        query = 'SELECT * FROM c WHERE c.attr1=' + curr + ' order by c.attr1'
        qlist = list(container.query_items(query=query, enable_cross_partition_query=True))
        ret_list.append((curr, qlist))
    for ret in ret_list:
        curr = ret[0]
        if len(ret[1]) != 0:
            for results in ret[1]:
                attr_number = results['attr1']
                assert str(attr_number) == curr  # verify that all results match their randomly generated attributes
        print("validation succeeded for all query results")


@pytest.mark.cosmosSplit
class TestPartitionSplitQuery(unittest.TestCase):
    database: DatabaseProxy = None
    container: ContainerProxy = None
    client: cosmos_client.CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    throughput = 400
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Single-partition-container-without-throughput"
    MAX_TIME = 60 * 10  # 10 minutes for the test to complete, should be enough for partition split to complete

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.container = cls.database.create_container(
            id=cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=cls.throughput)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.database.delete_container(cls.container.id)
        except CosmosHttpResponseError:
            pass

    def test_partition_split_query(self):
        for i in range(100):
            body = test_config.get_test_item()
            self.container.create_item(body=body)

        start_time = time.time()
        print("created items, changing offer to 11k and starting queries")
        self.container.replace_throughput(11000)
        offer_time = time.time()
        print("changed offer to 11k")
        print("--------------------------------")
        print("now starting queries")

        run_queries(self.container, 100)  # initial check for queries before partition split
        print("initial check succeeded, now reading offer until replacing is done")
        offer = self.container.get_throughput()
        while True:
            if time.time() - start_time > self.MAX_TIME:  # timeout test at 10 minutes
                self.skipTest("Partition split didn't complete in time")
            if offer.properties['content'].get('isOfferReplacePending', False):
                time.sleep(30)  # wait for the offer to be replaced, check every 30 seconds
                offer = self.container.get_throughput()
            else:
                print("offer replaced successfully, took around {} seconds".format(time.time() - offer_time))
                run_queries(self.container, 100)  # check queries work post partition split
                self.assertTrue(offer.offer_throughput > self.throughput)
                return

    def test_incremental_merge_preserves_stable_partitions(self):
        """
        Validates the incremental merge logic when a SINGLE partition splits.

        Specifically tests the scenario where:
        - Initial state: 1 partition (< 10k RU/s)
        - After split: 2 partitions (1 parent splits into 2 children)
        - Validation: Both new partitions have parent references

        This test ensures that when ALL partitions split, the incremental merge
        correctly handles the transition without any stable partitions to preserve.
        """
        container = self.database.create_container(
            id='single_partition_split_test_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400  # Single physical partition
        )

        try:
            # Insert data
            for i in range(50):
                item = {'id': f'item_{i}', 'pk': f'pk_{i % 2}', 'value': i}
                container.create_item(item)

            # Verify: We start with 1 partition
            initial_pk_ranges = list(container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            ))
            print(f"Initial partition count: {len(initial_pk_ranges)}")
            assert len(initial_pk_ranges) == 1, \
                f"Expected 1 partition at 400 RU/s, got {len(initial_pk_ranges)}"

            # Force initial routing map cache by running a query
            run_queries(container, 1)

            # Trigger split (1 -> 2 partitions)
            container.replace_throughput(11000)
            pending = True
            while pending:
                offer = container.get_throughput()
                pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
                if pending:
                    time.sleep(5)

            # Run queries to trigger routing map refresh
            run_queries(container, 1)

            # Verify: Split created 2 partitions using _ReadPartitionKeyRanges
            post_split_pk_ranges = list(container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            ))
            print(f"Post-split partition count: {len(post_split_pk_ranges)}")

            assert len(post_split_pk_ranges) == 2, \
                f"Expected 2 partitions after split, got {len(post_split_pk_ranges)}"

            # Verify: Access routing map
            provider = container.client_connection._routing_map_provider
            # The routing map is cached by collection link
            cached_map = provider._collection_routing_map_by_item.get(
                container.container_link
            )

            current_ranges = list(cached_map._orderedPartitionKeyRanges)

            # When a single partition splits, both children will have 'parents'
            child_partitions = [r for r in current_ranges if r.get('parents')]
            stable_partitions = [r for r in current_ranges if not r.get('parents')]

            # This validates ALL partitions split (both have parent references)
            assert len(child_partitions) == 2, \
                f"Expected 2 child partitions with parents, got {len(child_partitions)}"
            assert len(stable_partitions) == 0, \
                f"Expected 0 stable partitions (all split), got {len(stable_partitions)}"

            print(f"Validated: Single partition split into {len(child_partitions)} children")

            # Verify final throughput
            final_offer = container.get_throughput()
            assert final_offer.offer_throughput == 11000

        finally:
            self.database.delete_container(container.id)

    def test_incremental_merge_handles_split_partitions(self):
        """
        Validates the incremental merge logic when SOME partitions split.

        Specifically tests BOTH branches in _get_routing_map_with_change_feed:
        - Initial state: 2 partitions (11k RU/s)
        - After split: 3 partitions (1 stable + 2 new from split)
        - Validation:
          1. `if parents:` branch - New child partitions inherit parent's range_info
          2. `else:` branch - Stable partition preserves its original range_info

        This test ensures that during a PARTIAL split, the incremental merge correctly:
        - Handles new child partitions (with parent references)
        - Preserves unchanged partitions (without parent references)
        """
        container = self.database.create_container(
            id='partial_split_test_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000  # 2 physical partitions
        )

        try:
            # Insert data
            for i in range(200):
                item = {'id': f'item_{i}', 'pk': f'pk_{i % 2}', 'value': i}
                container.create_item(item)

            # Verify: We start with 2 partitions
            initial_pk_ranges = list(container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            ))
            print(f"Initial partition count: {len(initial_pk_ranges)}")
            assert len(initial_pk_ranges) == 2, \
                f"Expected 2 partitions at 11k RU/s, got {len(initial_pk_ranges)}"

            # Force initial routing map cache
            run_queries(container, 1)

            # Trigger split (2 -> 3 partitions: 1 stable + 2 from split)
            container.replace_throughput(25000)
            pending = True
            while pending:
                offer = container.read_offer()
                pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
                if pending:
                    time.sleep(5)

            # Run queries to trigger routing map refresh
            run_queries(container, 1)

            # Verify: Split created 3 partitions
            post_split_pk_ranges = list(container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            ))
            print(f"Post-split partition count: {len(post_split_pk_ranges)}")

            assert len(post_split_pk_ranges) == 3, \
                f"Expected 3 partitions after partial split, got {len(post_split_pk_ranges)}"

            # Verify: Access routing map and validate both code paths
            provider = container.client_connection._routing_map_provider
            cached_map = provider._collection_routing_map_by_item.get(
                container.container_link
            )

            current_ranges = list(cached_map._orderedPartitionKeyRanges)
            child_partitions = [r for r in current_ranges if r.get('parents')]
            stable_partitions = [r for r in current_ranges if not r.get('parents')]

            # This validates BOTH code paths
            # Test the `if parents:` branch
            assert len(child_partitions) == 2, \
                  f"Expected 2 child partitions from split, got {len(child_partitions)}"

            # Test the `else:` branch
            assert len(stable_partitions) == 1, \
                    f"Expected 1 stable partition (unchanged), got {len(stable_partitions)}"

            # Verify parent references on children
            for child in child_partitions:
                parents = child.get('parents', [])
                assert len(parents) > 0, f"Child {child['id']} has empty parents"
                print(f"Child partition {child['id']} has parent {parents[0]}")

            print(f"Validated: {len(stable_partitions)} stable + {len(child_partitions)} split partitions")

            # Verify final throughput
            final_offer = container.get_throughput()
            assert final_offer.offer_throughput == 25000

        finally:
            self.database.delete_container(container.id)

    def test_incremental_change_feed_only_affects_target_collection(self):
        """
        Validates that incremental change feed updates are collection-scoped.

        Scenario:
        - Create 2 containers: container_A and container_B
        - Both start with 1 partition (400 RU/s)
        - Run queries on both to populate routing map cache
        - Split ONLY container_A (400 → 11000 RU/s)
        - Verify:
          1. container_A's routing map is refreshed (2 partitions)
          2. container_B's routing map is unchanged (1 partition)
          3. container_B's cache is NOT invalidated
        """
        container_a = self.database.create_container(
            id='container_a_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        container_b = self.database.create_container(
            id='container_b_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            # Insert data into both containers
            for i in range(50):
                container_a.create_item({'id': f'a_{i}', 'pk': f'pk_{i}', 'value': i})
                container_b.create_item({'id': f'b_{i}', 'pk': f'pk_{i}', 'value': i})

            # Force routing map cache population for BOTH containers
            run_queries(container_a, 1)
            run_queries(container_b, 1)

            # Verify initial state: Both have 1 partition
            provider = container_a.client_connection._routing_map_provider
            collection_id_a = _base.GetResourceIdOrFullNameFromLink(container_a.container_link)
            collection_id_b = _base.GetResourceIdOrFullNameFromLink(container_b.container_link)

            map_a_before = provider._collection_routing_map_by_item.get(collection_id_a)
            map_b_before = provider._collection_routing_map_by_item.get(collection_id_b)

            assert map_a_before is not None, "Container A should have cached routing map"
            assert map_b_before is not None, "Container B should have cached routing map"

            ranges_a_before = list(map_a_before._orderedPartitionKeyRanges)
            ranges_b_before = list(map_b_before._orderedPartitionKeyRanges)

            assert len(ranges_a_before) == 1, f"Expected 1 partition in A, got {len(ranges_a_before)}"
            assert len(ranges_b_before) == 1, f"Expected 1 partition in B, got {len(ranges_b_before)}"

            # Store container B's original routing map object reference
            map_b_object_id = id(map_b_before)

            print(f"Before split - Container A: {len(ranges_a_before)} partitions")
            print(f"Before split - Container B: {len(ranges_b_before)} partitions")
            print(f"Container B routing map object ID: {map_b_object_id}")

            # Split only Container A
            container_a.replace_throughput(11000)
            pending = True
            while pending:
                offer = container_a.get_throughput()
                pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
                if pending:
                    time.sleep(5)

            # Wait for physical partition ranges to reflect the split.
            split_convergence_deadline = time.time() + 300
            physical_count = 0
            while time.time() < split_convergence_deadline:
                physical_ranges = list(container_a.client_connection._ReadPartitionKeyRanges(
                    container_a.container_link
                ))
                physical_count = len(physical_ranges)
                if physical_count == 2:
                    break
                time.sleep(5)

            assert physical_count == 2, \
                f"Container A physical partitions did not converge to 2 after split, got {physical_count}"

            # Trigger and wait for routing-map cache refresh for container A.
            cached_count = 0
            current_map = map_a_before
            while time.time() < split_convergence_deadline:
                provider = container_a.client_connection._routing_map_provider
                refreshed_map = provider.get_routing_map(
                    collection_link=container_a.container_link,
                    feed_options={},
                    force_refresh=True,
                    previous_routing_map=current_map,
                )
                current_map = refreshed_map or current_map
                cached_count = len(list(current_map._orderedPartitionKeyRanges)) if current_map else 0
                if cached_count == 2:
                    break
                time.sleep(5)

            # Also run queries on container B to verify cache wasn't invalidated
            run_queries(container_b, 1)

            # Verify post-split state
            provider = container_a.client_connection._routing_map_provider
            map_a_after = provider._collection_routing_map_by_item.get(collection_id_a)
            map_b_after = provider._collection_routing_map_by_item.get(collection_id_b)

            assert map_a_after is not None, "Container A should still have cached routing map"
            assert map_b_after is not None, "Container B should still have cached routing map"

            ranges_a_after = list(map_a_after._orderedPartitionKeyRanges)
            ranges_b_after = list(map_b_after._orderedPartitionKeyRanges)

            print(f"After split - Container A: {len(ranges_a_after)} partitions")
            print(f"After split - Container B: {len(ranges_b_after)} partitions")

            # Validate container A was updated
            assert len(ranges_a_after) == 2, \
                f"Container A should have 2 partitions after split, got {len(ranges_a_after)} (physical={physical_count}, cached={cached_count})"

            # Validate container B remained unchanged
            assert len(ranges_b_after) == 1, \
                f"Container B should still have 1 partition, got {len(ranges_b_after)}"

            # Verify container B's cache wasn't cleared/recreated
            # The routing map object should be the SAME instance
            map_b_after_object_id = id(map_b_after)
            assert map_b_object_id == map_b_after_object_id, \
                f"Container B's routing map was recreated (cache invalidated). " \
                f"Before: {map_b_object_id}, After: {map_b_after_object_id}"

            # Verify the partition IDs haven't changed for container B
            assert ranges_b_before[0]['id'] == ranges_b_after[0]['id'], \
                "Container B's partition ID changed unexpectedly"

            print("Validated: Incremental change feed only affected container A")
            print("Container B's routing map remained untouched (same object reference)")

        finally:
            self.database.delete_container(container_a.id)
            self.database.delete_container(container_b.id)

    def test_routing_map_provider_fallback_on_incomplete_merge(self):
        """
        Validates that routing_map_provider falls back to full refresh
        when incremental merge produces incomplete range coverage.
        """
        container = self.database.create_container(
            id='test_fallback_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            # Insert data
            for i in range(20):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link

            # Get initial routing map
            initial_map = provider.get_routing_map(
                collection_link=collection_link,
                feed_options={}
            )

            assert initial_map is not None
            initial_ranges = list(initial_map._orderedPartitionKeyRanges)
            assert len(initial_ranges) == 1

            # Simulate a corrupted incremental update by creating incomplete ranges
            parent_id = initial_ranges[0]['id']

            # Create child ranges with a GAP (incomplete coverage)
            corrupted_child_1 = {
                'id': 'corrupted_1',
                'minInclusive': '',
                'maxExclusive': '80',
                'parents': [parent_id]
            }

            # Gap from '80' to '90' - missing coverage!
            corrupted_child_2 = {
                'id': 'corrupted_2',
                'minInclusive': '90',  # Should be '80'
                'maxExclusive': 'FF',
                'parents': [parent_id]
            }

            # Test try_combine with corrupted data
            combined_map = initial_map.try_combine(
                [(corrupted_child_1, True), (corrupted_child_2, True)],
                new_change_feed_etag="corrupted_etag"
            )

            # Should return None due to incomplete coverage
            assert combined_map is None, \
                "try_combine should return None for incomplete range set"

            print("Validated: try_combine correctly rejects incomplete ranges")

            # Now verify the routing_map_provider's fallback behavior
            # Clear cache to force a fresh fetch
            provider._collection_routing_map_by_item.clear()

            # This should trigger the full refresh fallback path
            refreshed_map = provider.get_routing_map(
                collection_link=collection_link,
                feed_options={}
            )

            # Should successfully retrieve the routing map via full refresh
            assert refreshed_map is not None, \
                "Routing map should be retrieved via full refresh fallback"

            refreshed_ranges = list(refreshed_map._orderedPartitionKeyRanges)
            assert len(refreshed_ranges) == 1, \
                f"Expected 1 partition after fallback, got {len(refreshed_ranges)}"

            # Verify completeness
            assert refreshed_ranges[0]['minInclusive'] == ''
            assert refreshed_ranges[0]['maxExclusive'] == 'FF'

            print("✓ Validated: routing_map_provider successfully fell back to full refresh")

            # Verify queries still work after fallback
            query_results = list(container.query_items(
                query='SELECT * FROM c',
                enable_cross_partition_query=True
            ))

            assert len(query_results) == 20, \
                f"Expected 20 items after fallback, got {len(query_results)}"

            print("Validated: Queries work correctly after fallback")

        finally:
            self.database.delete_container(container.id)

    def test_etag_staleness_detection_across_all_scenarios(self):
        """Verifies that the cache correctly detects whether a refresh is needed by
        comparing ETags. The ETag is a version stamp from the change feed — when two
        maps have the same ETag, it means nobody has refreshed yet (stale). This test
        checks all four scenarios:

        1. No previous map provided -> not stale (nothing to compare against)
        2. ETags match -> stale (nobody refreshed since the caller last looked)
        3. ETags differ -> not stale (another thread already refreshed)
        4. Cache is empty -> not stale (empty cache is handled separately as initial load)
        """
        container = self.database.create_container(
            id='test_stale_etag_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            cached_map = provider._collection_routing_map_by_item.get(collection_id)
            assert cached_map is not None

            # Case 1: previous_routing_map is None -> should return False
            assert provider._is_cache_stale(collection_id, None) is False, \
                "_is_cache_stale should return False when previous_routing_map is None"

            # Case 2: ETags match -> should return True (cache is stale)
            assert provider._is_cache_stale(collection_id, cached_map) is True, \
                "_is_cache_stale should return True when ETags match"

            # Case 3: ETags differ -> should return False (already refreshed)
            fake_previous = MagicMock()
            fake_previous.change_feed_etag = "fake-different-etag-12345"
            assert provider._is_cache_stale(collection_id, fake_previous) is False, \
                "_is_cache_stale should return False when ETags differ"

            # Case 4: Cache is empty -> should return False
            provider._collection_routing_map_by_item.clear()
            real_previous = MagicMock()
            real_previous.change_feed_etag = cached_map.change_feed_etag
            assert provider._is_cache_stale(collection_id, real_previous) is False, \
                "_is_cache_stale should return False when cache is empty"

            print("Validated: _is_cache_stale ETag comparison logic works correctly")

        finally:
            self.database.delete_container(container.id)

    def test_full_refresh_fallback_stops_infinite_recursion(self):
        """Verifies that the SDK does not recurse infinitely when a full refresh from
        the service returns an incomplete set of partition ranges.

        When a full load is performed (previous_routing_map=None) and the service
        returns gapped ranges, _fetch_routing_map must return None immediately —
        there is no incremental state to fall back from, and repeating the
        identical request would produce the same result."""
        container = self.database.create_container(
            id='test_fallback_guard_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            # Create an incomplete range set that will cause CompleteRoutingMap to fail
            incomplete_range = {
                'id': 'incomplete_0',
                'minInclusive': '',
                'maxExclusive': '80',  # Gap from 80 to FF
            }

            def mock_read_ranges(*args, **kwargs):
                return iter([incomplete_range])

            with patch.object(
                    container.client_connection,
                    '_ReadPartitionKeyRanges',
                    side_effect=mock_read_ranges
            ):
                # Full load with incomplete ranges should return None immediately
                result = provider._fetch_routing_map(
                    collection_link=collection_link,
                    collection_id=collection_id,
                    previous_routing_map=None,
                    feed_options={},
                )

                # Should return None instead of recursing infinitely
                assert result is None, \
                    "_fetch_routing_map should return None when full load produces incomplete ranges"

            print("Validated: full load with incomplete ranges returns None without recursion")

        finally:
            self.database.delete_container(container.id)

    def test_pk_range_fetch_sets_recursion_prevention_flag(self):
        """Verifies that when the SDK fetches partition key ranges, it sets a special
        flag (_internal_pk_range_fetch) in the request options.

        This flag exists to break a specific infinite loop: if the PK range fetch itself
        gets a 410 (partition gone) error, the retry logic would normally try to refresh
        the routing map — which would call the PK range fetch again — creating an endless
        cycle. The flag tells the retry logic to skip the refresh and let the 410 propagate."""
        container = self.database.create_container(
            id='test_pk_flag_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link

            captured_options = {}
            original_read = container.client_connection._ReadPartitionKeyRanges

            def spy_read_ranges(*args, **kwargs):
                if len(args) > 1:
                    captured_options.update(args[1])
                return original_read(*args, **kwargs)

            with patch.object(
                    container.client_connection,
                    '_ReadPartitionKeyRanges',
                    side_effect=spy_read_ranges
            ):
                # Clear cache to force a fresh fetch
                provider._collection_routing_map_by_item.clear()

                routing_map = provider.get_routing_map(
                    collection_link=collection_link,
                    feed_options={}
                )

                assert routing_map is not None
                assert captured_options.get("_internal_pk_range_fetch") is True, \
                    "_internal_pk_range_fetch flag should be set in options"

            print("Validated: _internal_pk_range_fetch flag is correctly set")

        finally:
            self.database.delete_container(container.id)

    def test_cached_map_returned_without_lock(self):
        """Verifies that when the routing map is already cached and no refresh is needed,
        get_routing_map returns it immediately without acquiring the per-collection lock.

        This is important for performance: in a read-heavy workload, every query needs to
        look up the routing map. If every lookup acquired a lock, threads would contend
        unnecessarily. The fast path (dict lookup without locking) avoids this. This test
        also confirms that force_refresh=True correctly bypasses the fast path and does
        acquire the lock."""
        container = self.database.create_container(
            id='test_fast_path_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            # Verify cache is populated
            cached_map = provider._collection_routing_map_by_item.get(collection_id)
            assert cached_map is not None

            # Spy on _get_lock_for_collection to verify it's NOT called on the fast path
            lock_call_count = {'count': 0}
            original_get_lock = provider._get_lock_for_collection

            def spy_get_lock(*args, **kwargs):
                lock_call_count['count'] += 1
                return original_get_lock(*args, **kwargs)

            with patch.object(provider, '_get_lock_for_collection', side_effect=spy_get_lock):
                # This should hit the fast path — no lock acquisition
                result = provider.get_routing_map(
                    collection_link=collection_link,
                    feed_options={}
                )

                assert result is cached_map, "Should return the same cached map object"
                assert lock_call_count['count'] == 0, \
                    "Lock should NOT be acquired on the fast path"

            # Now verify that force_refresh DOES acquire the lock
            lock_call_count['count'] = 0
            with patch.object(provider, '_get_lock_for_collection', side_effect=spy_get_lock):
                result = provider.get_routing_map(
                    collection_link=collection_link,
                    feed_options={},
                    force_refresh=True
                )
                assert result is not None
                assert lock_call_count['count'] == 1, \
                    "Lock SHOULD be acquired when force_refresh=True"

            print("Validated: Lock-free fast path works correctly")

        finally:
            self.database.delete_container(container.id)

    def test_upstream_response_hook_preserved_during_routing_map_fetch(self):
        """Verifies that when a caller passes a response_hook callback, it is still
        invoked even though _fetch_routing_map also installs its own internal hook to
        capture the change feed ETag.

        Without proper hook chaining, either the caller's hook would be silently dropped,
        or the SDK would crash with 'got multiple values for keyword argument'. This test
        confirms both hooks are called and both receive the response headers."""
        container = self.database.create_container(
            id='test_hook_chain_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            # Clear cache to force a fetch
            provider._collection_routing_map_by_item.clear()

            upstream_headers_captured = {}

            def upstream_hook(headers, body):
                upstream_headers_captured.update(headers)

            # Call get_routing_map with an upstream response_hook in kwargs
            result = provider.get_routing_map(
                collection_link=collection_link,
                feed_options={},
                response_hook=upstream_hook
            )

            assert result is not None, "Routing map should be returned"

            # The internal hook should have captured the ETag (used for change_feed_etag)
            assert result.change_feed_etag is not None, \
                "Internal capture hook should have captured the ETag"

            # The upstream hook should also have been called with headers
            assert len(upstream_headers_captured) > 0, \
                "Upstream response_hook should have been called with headers"

            print("Validated: response_hook chaining works correctly")

        finally:
            self.database.delete_container(container.id)

    def test_stale_etag_header_removed_on_full_refresh_fallback(self):
        """Verifies that when an incremental update fails and the SDK falls back to a
        full refresh, the stale If-None-Match header is removed from the request.

        Current behavior includes one incremental retry before full refresh.
        This test forces both incremental attempts to be incomplete, then verifies
        the final full-refresh call drops If-None-Match."""
        container = self.database.create_container(
            id='test_etag_cleanup_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(10):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            captured_headers_list = []
            original_read = container.client_connection._ReadPartitionKeyRanges

            call_count = {'count': 0}

            def spy_read_ranges(*args, **kwargs):
                call_count['count'] += 1
                # Capture the headers from kwargs
                headers = kwargs.get('headers', {})
                captured_headers_list.append(headers.copy())

                if call_count['count'] <= 2:
                    # First two calls are incremental attempts; return a child
                    # with a missing parent so merge is incomplete and fallback
                    # path is exercised.
                    fake_child = {
                        'id': f'child_{call_count["count"]}',
                        'minInclusive': '',
                        'maxExclusive': 'FF',
                        'parents': ['nonexistent_parent']
                    }
                    return iter([fake_child])
                # Third call should be full-load fallback.
                return original_read(*args, **kwargs)

            cached_map = provider._collection_routing_map_by_item.get(collection_id)
            assert cached_map is not None
            assert cached_map.change_feed_etag is not None

            with patch.object(
                    container.client_connection,
                    '_ReadPartitionKeyRanges',
                    side_effect=spy_read_ranges
            ):
                # Force refresh with the stale map to trigger incremental path
                result = provider.get_routing_map(
                    collection_link=collection_link,
                    feed_options={},
                    force_refresh=True,
                    previous_routing_map=cached_map
                )

                assert result is not None

                # Verify 3 calls: incremental + incremental retry + full fallback.
                assert call_count['count'] == 3, \
                    f"Expected 3 calls to _ReadPartitionKeyRanges, got {call_count['count']}"

                # First two calls should be incremental and include IfNoneMatch.
                first_headers = captured_headers_list[0]
                assert http_constants.HttpHeaders.IfNoneMatch in first_headers, \
                    "First call (incremental) should have IfNoneMatch header"

                second_headers = captured_headers_list[1]
                assert http_constants.HttpHeaders.IfNoneMatch in second_headers, \
                    "Second call (incremental retry) should have IfNoneMatch header"

                # Third call is full-load fallback and should drop IfNoneMatch.
                third_headers = captured_headers_list[2]
                assert http_constants.HttpHeaders.IfNoneMatch not in third_headers, \
                    "Third call (full load fallback) should NOT have IfNoneMatch header"

            print("Validated: IfNoneMatch header is correctly cleaned up on fallback")

        finally:
            self.database.delete_container(container.id)

    def test_targeted_refresh_with_stale_map_keeps_queries_working(self):
        """Verifies the end-to-end targeted refresh path: the SDK caches a routing map,
        then force-refreshes it using the old map as a reference (simulating what the 410
        retry policy does after a partition split), and confirms that queries still return
        correct results afterward.

        This is the most important refresh path in production — it's how the SDK recovers
        from partition splits without disrupting the user's queries."""
        container = self.database.create_container(
            id='test_force_refresh_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(20):
                container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link
            collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

            # Capture the current map as the "stale" previous map
            stale_map = provider._collection_routing_map_by_item.get(collection_id)
            assert stale_map is not None
            original_etag = stale_map.change_feed_etag

            # Force refresh with the stale map — simulates what the gone retry policy does
            refreshed_map = provider.get_routing_map(
                collection_link=collection_link,
                feed_options={},
                force_refresh=True,
                previous_routing_map=stale_map
            )

            assert refreshed_map is not None
            assert len(list(refreshed_map._orderedPartitionKeyRanges)) >= 1

            # Verify queries still work after force refresh
            results = list(container.query_items(
                query='SELECT * FROM c',
                enable_cross_partition_query=True
            ))
            assert len(results) == 20, \
                f"Expected 20 items after force refresh, got {len(results)}"

            print("Validated: Force refresh with previous_routing_map works correctly")

        finally:
            self.database.delete_container(container.id)

if __name__ == "__main__":
    unittest.main()
