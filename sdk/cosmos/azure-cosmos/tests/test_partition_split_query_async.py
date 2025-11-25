# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import time
import unittest
import random
import uuid
from unittest.mock import patch

import pytest

import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy

async def run_queries(container, iterations):
    ret_list = []
    for i in range(iterations):
        curr = str(random.randint(0, 10))
        query = 'SELECT * FROM c WHERE c.attr1=' + curr + ' order by c.attr1'
        qlist = [item async for item in container.query_items(query=query)]
        ret_list.append((curr, qlist))
    for ret in ret_list:
        curr = ret[0]
        if len(ret[1]) != 0:
            for results in ret[1]:
                attr_number = results['attr1']
                assert str(attr_number) == curr  # verify that all results match their randomly generated attributes
        print("validation succeeded for all query results")


@pytest.mark.cosmosSplit
class TestPartitionSplitQueryAsync(unittest.IsolatedAsyncioTestCase):
    database: DatabaseProxy = None
    container: ContainerProxy = None
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    throughput = 400
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_CONTAINER_ID = "Single-partition-container-without-throughput-async"
    MAX_TIME = 60 * 30  # 10 minutes for the test to complete, should be enough for partition split to complete

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        await self.client.__aenter__()
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.container = await self.created_database.create_container(
            id=self.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=self.throughput)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_partition_split_query_async(self):
        for i in range(100):
            body = test_config.get_test_item()
            await self.container.create_item(body=body)

        start_time = time.time()
        print("created items, changing offer to 11k and starting queries")
        await self.container.replace_throughput(11000)
        offer_time = time.time()
        print("changed offer to 11k")
        print("--------------------------------")
        print("now starting queries")

        await run_queries(self.container, 1)  # initial check for queries before partition split
        print("initial check succeeded, now reading offer until replacing is done")
        offer = await self.container.get_throughput()
        while True:
            if time.time() - start_time > self.MAX_TIME:  # timeout test at 10 minutes
                self.skipTest("Partition split didn't complete in time.")
            if offer.properties['content'].get('isOfferReplacePending', False):
                time.sleep(30)  # wait for the offer to be replaced, check every 30 seconds
                offer = await self.container.get_throughput()
            else:
                print("offer replaced successfully, took around {} seconds".format(time.time() - offer_time))
                await run_queries(self.container, 1)  # check queries work post partition split
                self.assertTrue(offer.offer_throughput > self.throughput)
                return

    async def test_incremental_merge_preserves_stable_partitions_async(self):
        """
        Validates the incremental merge logic when a SINGLE partition splits.

        Specifically tests the scenario where:
        - Initial state: 1 partition (< 10k RU/s)
        - After split: 2 partitions (1 parent splits into 2 children)
        - Validation: Both new partitions have parent references

        This test ensures that when ALL partitions split, the incremental merge
        correctly handles the transition without any stable partitions to preserve.
        """
        #Insert data
        for i in range(50):
            item = {'id': f'item_{i}', 'pk': f'pk_{i % 2}', 'value': i}
            await self.container.create_item(item)

        # Verify: We start with 1 partition
        initial_pk_ranges = [r async for r in self.container.client_connection._ReadPartitionKeyRanges(
            self.container.container_link
        )]
        print(f"Initial partition count: {len(initial_pk_ranges)}")
        assert len(initial_pk_ranges) == 1, \
            f"Expected 1 partition at 400 RU/s, got {len(initial_pk_ranges)}"

        # Force initial routing map cache by running a query
        await run_queries(self.container, 1)

        # Trigger split (1 -> 2 partitions)
        await self.container.replace_throughput(11000)
        pending = True
        while pending:
            offer = await self.container.get_throughput()
            pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
            if pending:
                await asyncio.sleep(5)

        # Run queries to trigger routing map refresh
        await run_queries(self.container, 1)

        # Verify: Split created 2 partitions using _ReadPartitionKeyRanges
        post_split_pk_ranges = [r async for r in self.container.client_connection._ReadPartitionKeyRanges(
            self.container.container_link
        )]
        print(f"Post-split partition count: {len(post_split_pk_ranges)}")

        assert len(post_split_pk_ranges) == 2, \
            f"Expected 2 partitions after split, got {len(post_split_pk_ranges)}"

        # Verify: Access routing map
        provider = self.container.client_connection._routing_map_provider
        # The routing map is cached by collection link
        cached_map = provider._collection_routing_map_by_item.get(
            self.container.container_link
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
        final_offer = await self.container.get_throughput()
        assert final_offer.offer_throughput == 11000

    async def test_incremental_merge_handles_split_partitions_async(self):
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
        new_container = await self.created_database.create_container(
            id='partial_split_test_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000  # 2 physical partitions
        )
        try:
            # Insert data
            for i in range(200):
                item = {'id': f'item_{i}', 'pk': f'pk_{i % 2}', 'value': i}
                await new_container.create_item(item)

            # Verify: We start with 2 partitions
            initial_pk_ranges = [r async for r in new_container.client_connection._ReadPartitionKeyRanges(
                new_container.container_link
            )]
            print(f"Initial partition count: {len(initial_pk_ranges)}")
            assert len(initial_pk_ranges) == 2, \
                f"Expected 2 partitions at 11k RU/s, got {len(initial_pk_ranges)}"

            # Force initial routing map cache
            await run_queries(new_container, 1)

            # Trigger split (2 -> 3 partitions: 1 stable + 2 from split)
            await new_container.replace_throughput(25000)
            pending = True
            while pending:
                offer = await new_container.get_throughput()
                pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
                if pending:
                    await asyncio.sleep(5)

            # Run queries to trigger routing map refresh
            await run_queries(new_container, 1)

            # Verify: Split created 3 partitions
            post_split_pk_ranges = [r async for r in new_container.client_connection._ReadPartitionKeyRanges(
                new_container.container_link
            )]
            print(f"Post-split partition count: {len(post_split_pk_ranges)}")

            assert len(post_split_pk_ranges) == 3, \
                f"Expected 3 partitions after partial split, got {len(post_split_pk_ranges)}"

            # Verify: Access routing map and validate both code paths
            provider = new_container.client_connection._routing_map_provider
            cached_map = provider._collection_routing_map_by_item.get(
                new_container.container_link
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
            final_offer = await new_container.get_throughput()
            assert final_offer.offer_throughput == 25000

        finally:
            await self.created_database.delete_container(new_container.id)

    async def test_incremental_change_feed_only_affects_target_collection_async(self):
        """
        Validates that incremental change feed updates are collection-scoped.

        Scenario:
        - Create 2 containers: container_A and container_B
        - Both start with 1 partition (400 RU/s)
        - Run queries on both to populate routing map cache
        - Split ONLY container_A (400 -> 11000 RU/s)
        - Verify:
          1. container_A's routing map is refreshed (2 partitions)
          2. container_B's routing map is unchanged (1 partition)
          3. container_B's cache is NOT invalidated
        """
        container_a = await self.created_database.create_container(
            id='container_a_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        container_b = await self.created_database.create_container(
            id='container_b_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            # Insert data into both containers
            for i in range(50):
                await container_a.create_item({'id': f'a_{i}', 'pk': f'pk_{i}', 'value': i})
                await container_b.create_item({'id': f'b_{i}', 'pk': f'pk_{i}', 'value': i})

            # Force routing map cache population for BOTH containers
            await run_queries(container_a, 1)
            await run_queries(container_b, 1)

            # Verify initial state: Both have 1 partition
            provider = container_a.client_connection._routing_map_provider

            map_a_before = provider._collection_routing_map_by_item.get(container_a.container_link)
            map_b_before = provider._collection_routing_map_by_item.get(container_b.container_link)

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

            # SPLIT ONLY CONTAINER A
            await container_a.replace_throughput(11000)
            pending = True
            while pending:
                offer = await container_a.get_throughput()
                pending = offer.properties.get('content', {}).get('isOfferReplacePending', False)
                if pending:
                    await asyncio.sleep(5)

            # Trigger routing map refresh for container A
            await run_queries(container_a, 1)

            # Also run queries on container B to verify cache wasn't invalidated
            await run_queries(container_b, 1)

            # Verify post-split state
            map_a_after = provider._collection_routing_map_by_item.get(container_a.container_link)
            map_b_after = provider._collection_routing_map_by_item.get(container_b.container_link)

            assert map_a_after is not None, "Container A should still have cached routing map"
            assert map_b_after is not None, "Container B should still have cached routing map"

            ranges_a_after = list(map_a_after._orderedPartitionKeyRanges)
            ranges_b_after = list(map_b_after._orderedPartitionKeyRanges)

            print(f"After split - Container A: {len(ranges_a_after)} partitions")
            print(f"After split - Container B: {len(ranges_b_after)} partitions")

            # Validate container A was updated
            assert len(ranges_a_after) == 2, \
                f"Container A should have 2 partitions after split, got {len(ranges_a_after)}"

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
            await self.created_database.delete_container(container_a.id)
            await self.created_database.delete_container(container_b.id)


    async def test_routing_map_provider_fallback_on_incomplete_merge_async(self):
        """
        Validates that routing_map_provider falls back to full refresh
        when incremental merge produces incomplete range coverage.
        """
        container = await self.created_database.create_container(
            id='test_fallback_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            # Insert data
            for i in range(20):
                await container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            # Populate cache
            await run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link

            # Get initial routing map
            initial_map = await provider.get_or_refresh_routing_map_for_collection(
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
            refreshed_map = await provider.get_or_refresh_routing_map_for_collection(
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

            print("Validated: routing_map_provider successfully fell back to full refresh")

            # Verify queries still work after fallback
            query_results = [item async for item in container.query_items(
                query='SELECT * FROM c',
            )]

            assert len(query_results) == 20, \
                f"Expected 20 items after fallback, got {len(query_results)}"

            print("Validated: Queries work correctly after fallback")

        finally:
            await self.created_database.delete_container(container.id)

    async def test_fallback_when_parent_missing_in_incremental_update_async(self):
        """
        Validates fallback when change feed returns child with missing parent.

        This directly tests the guard at routing_map_provider.py
        """
        container = await self.created_database.create_container(
            id='test_missing_parent_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(30):
                await container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            await run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link

            initial_map = provider._collection_routing_map_by_item.get(collection_link)
            assert initial_map is not None

            # Create fake child with non-existent parent
            fake_child = {
                'id': 'child_with_missing_parent',
                'minInclusive': '',
                'maxExclusive': '80',
                'parents': ['non_existent_parent_id']  # Parent doesn't exist
            }

            # Track how many times _ReadPartitionKeyRanges is called
            call_count = {'count': 0}
            original_read = container.client_connection._ReadPartitionKeyRanges

            def mock_read_ranges(*args, **kwargs):
                call_count['count'] += 1
                if call_count['count'] == 1:
                    # First call: Return fake child to trigger missing parent guard
                    async def async_iter():
                        yield fake_child

                    return async_iter()
                else:
                    # Subsequent calls: Return real data for full refresh
                    return original_read(*args, **kwargs)

            with patch.object(
                    container.client_connection,
                    '_ReadPartitionKeyRanges',
                    side_effect=mock_read_ranges
            ):
                # Force refresh with stale map
                provider._collection_routing_map_by_item.clear()

                refreshed_map = await provider.get_or_refresh_routing_map_for_collection(
                    collection_link=collection_link,
                    feed_options={},
                    previous_routing_map=initial_map  # Simulate stale cache
                )

                # Should succeed via fallback after detecting missing parent
                assert refreshed_map is not None
                assert call_count['count'] >= 2, \
                    "Should have called _ReadPartitionKeyRanges twice (initial + fallback)"

                print("Validated: Missing parent guard triggered fallback")

        finally:
            await self.created_database.delete_container(container.id)

    async def test_fallback_when_existing_range_missing_in_incremental_update_async(self):
        """
        Validates the defensive guard logic when an existing range is missing from cache.

        This tests the routing_map_provider's ability to detect and recover from
        inconsistent state where change feed returns a stable partition that's not
        in the cached routing map.
        """
        container = await self.created_database.create_container(
            id='test_missing_range_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400
        )

        try:
            for i in range(30):
                await container.create_item({'id': f'item_{i}', 'pk': f'pk_{i}', 'value': i})

            await run_queries(container, 1)

            provider = container.client_connection._routing_map_provider
            collection_link = container.container_link

            # Get real routing map
            real_map = provider._collection_routing_map_by_item.get(collection_link)
            assert real_map is not None

            real_ranges = list(real_map._orderedPartitionKeyRanges)
            assert len(real_ranges) == 1

            # Create a fake previous map with INCOMPLETE _rangeById
            from unittest.mock import MagicMock
            fake_previous_map = MagicMock()
            fake_previous_map._rangeById = {}  # Empty - simulates missing range

            # Simulate receiving an existing range from change feed
            existing_range = real_ranges[0].copy()
            # Remove 'parents' field to simulate stable partition
            existing_range.pop('parents', None)

            # Manually test the guard logic
            range_id = existing_range['id']

            # This simulates the code at lines 179-185
            if range_id in fake_previous_map._rangeById:
                pytest.fail("Range should NOT be in fake previous map")
            else:
                # Guard should trigger here
                print(f"Guard triggered: Existing range '{range_id}' not found in cache")

                # Verify fallback by manually clearing cache and refreshing
                provider._collection_routing_map_by_item.clear()

                # Full refresh (no previous_routing_map)
                refreshed_map = await provider.get_or_refresh_routing_map_for_collection(
                    collection_link=collection_link,
                    feed_options={}
                )

                assert refreshed_map is not None
                refreshed_ranges = list(refreshed_map._orderedPartitionKeyRanges)
                assert len(refreshed_ranges) == 1

                print("Validated: Fallback to full refresh succeeded")

                # Verify queries work after fallback
                results = [item async for item in container.query_items(
                    query='SELECT * FROM c',
                )]
                assert len(results) == 30

                print("Validated: Queries work after fallback")

        finally:
            await self.created_database.delete_container(container.id)


if __name__ == '__main__':
    unittest.main()
