# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, ContainerProxy
from azure.cosmos._routing import routing_range as routing_range
from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos import _base


@pytest.mark.cosmosEmulator
class TestRoutingMapEndToEnd(unittest.TestCase):
    """Routing Map Functionalities end-to-end Tests.
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    configs = test_config.TestConfig
    client: cosmos_client.CosmosClient = None
    created_database: DatabaseProxy = None
    created_container: ContainerProxy = None
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID
    TEST_COLLECTION_ID = configs.TEST_SINGLE_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_database.get_container_client(cls.TEST_COLLECTION_ID)
        cls.collection_link = cls.created_container.container_link

    def test_read_partition_key_ranges(self):
        """Verifies that _ReadPartitionKeyRanges returns the expected number
        of partition key ranges for a single-partition container."""
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))
        self.assertEqual(1, len(partition_key_ranges))

    def test_routing_map_provider(self):
        """Verifies that the PartitionKeyRangeCache returns overlapping ranges
        consistent with the raw _ReadPartitionKeyRanges result. The cache may
        include extra change-feed metadata fields (e.g. _lsn), so we only
        assert that every field from the expected ranges is present and equal."""
        partition_key_ranges = list(self.client.client_connection._ReadPartitionKeyRanges(self.collection_link))

        routing_mp = PartitionKeyRangeCache(self.client.client_connection)
        overlapping_partition_key_ranges = routing_mp.get_overlapping_ranges(
            self.collection_link,
            routing_range.Range("", "FF", True, False),
            {})
        self.assertEqual(len(overlapping_partition_key_ranges), len(partition_key_ranges))

        # The extra _lsn field in overlapping_partition_key_ranges is appearing because modified code is now using the change
        # feed to fetch partition key ranges, while _ReadPartitionKeyRanges uses the standard read feed.
        # Verify that all fields from expected partition_key_ranges exist in actual results
        # and have the same values, allowing additional change feed metadata fields
        # PKRange namedtuple retains id, minInclusive, maxExclusive, parents.
        # Verify these core fields match the service response. ``parents`` is
        # stored as a tuple of strings on PKRange and may be absent on the raw
        # service dict for never-split ranges; normalise both sides.
        pk_range_fields = ('id', 'minInclusive', 'maxExclusive')
        for actual, expected in zip(overlapping_partition_key_ranges, partition_key_ranges):
            for key in pk_range_fields:
                self.assertIn(key, actual, f"Expected key '{key}' not found in actual range")
                self.assertEqual(actual[key], expected[key],
                                 f"Value mismatch for key '{key}': expected {expected[key]}, got {actual[key]}")
            actual_parents = tuple(actual.get('parents') or ())
            expected_parents = tuple(expected.get('parents') or ())
            self.assertEqual(actual_parents, expected_parents,
                             f"parents mismatch: expected {expected_parents}, got {actual_parents}")

    def test_change_feed_etag_stored_after_initial_load(self):
        """Verifies that when the SDK fetches partition key ranges for the first time
        using the change feed, it stores the server's ETag on the cached routing map.
        This ETag acts as a bookmark so future refreshes can request only the changes
        since this point, rather than re-fetching everything."""
        routing_mp = PartitionKeyRangeCache(self.client.client_connection)
        collection_id = _base.GetResourceIdOrFullNameFromLink(self.collection_link)

        # Initial load
        routing_map = routing_mp.get_routing_map(self.collection_link, feed_options={})

        self.assertIsNotNone(routing_map, "Routing map should be returned on initial load")
        self.assertIsNotNone(routing_map.change_feed_etag,
                             "Change feed ETag should be stored after initial load")
        self.assertTrue(len(routing_map.change_feed_etag) > 0,
                        "Change feed ETag should not be empty")

        # Verify the map is in the cache
        cached_map = routing_mp._collection_routing_map_by_item.get(collection_id)
        self.assertIs(cached_map, routing_map, "Routing map should be cached by collection ID")

    def test_warm_cache_returns_same_object(self):
        """Verifies that once a routing map is cached, repeated calls to get_routing_map
        return the exact same Python object without making any additional service calls.
        This confirms the lock-free fast path works correctly — the common case (cache hit)
        has zero overhead."""
        routing_mp = PartitionKeyRangeCache(self.client.client_connection)

        result1 = routing_mp.get_routing_map(self.collection_link, feed_options={})
        result2 = routing_mp.get_routing_map(self.collection_link, feed_options={})

        self.assertIs(result1, result2, "Second call should return the same cached object (identity)")

    def test_force_refresh_returns_valid_map(self):
        """Verifies that force_refresh=True re-fetches partition key ranges from the
        real Cosmos service and returns a valid, complete routing map. This is the code
        path taken when a partition split (410/1002 error) forces the SDK to update its
        cached view of the container's partitions."""
        routing_mp = PartitionKeyRangeCache(self.client.client_connection)

        # Initial load
        initial_map = routing_mp.get_routing_map(self.collection_link, feed_options={})
        self.assertIsNotNone(initial_map)

        # Force refresh — simulates what the 410 retry policy does
        refreshed_map = routing_mp.get_routing_map(
            self.collection_link,
            feed_options={},
            force_refresh=True,
            previous_routing_map=initial_map
        )

        self.assertIsNotNone(refreshed_map, "Force refresh should return a valid routing map")
        self.assertIsNotNone(refreshed_map.change_feed_etag,
                             "Refreshed map should have a change feed ETag")

        # Ranges should still be complete
        ranges = list(refreshed_map._orderedPartitionKeyRanges)
        self.assertGreaterEqual(len(ranges), 1, "Refreshed map should have at least 1 range")
        self.assertEqual(ranges[0]['minInclusive'], '',
                         "First range should start at empty string")
        self.assertEqual(ranges[-1]['maxExclusive'], 'FF',
                         "Last range should end at FF")

    def test_get_overlapping_ranges_uses_cached_map(self):
        """Verifies that get_overlapping_ranges populates the routing map cache on its
        first call, and that subsequent calls reuse the same cached map instance without
        replacing it. This confirms that the SmartRoutingMapProvider on the real client
        correctly caches and reuses routing maps across multiple lookups."""
        # Use the real client's routing map provider (SmartRoutingMapProvider)
        provider = self.client.client_connection._routing_map_provider
        collection_id = _base.GetResourceIdOrFullNameFromLink(self.collection_link)

        # Clear the cache for this collection to start fresh
        provider._collection_routing_map_by_item.pop(collection_id, None)

        # First call populates cache
        ranges1 = provider.get_overlapping_ranges(
            self.collection_link,
            [routing_range.Range("", "FF", True, False)],
            {})
        self.assertGreaterEqual(len(ranges1), 1)

        # Verify cache is now populated
        cached_map = provider._collection_routing_map_by_item.get(collection_id)
        self.assertIsNotNone(cached_map, "Cache should be populated after get_overlapping_ranges")

        # Second call should use the same cached map
        ranges2 = provider.get_overlapping_ranges(
            self.collection_link,
            [routing_range.Range("", "FF", True, False)],
            {})
        self.assertEqual(len(ranges1), len(ranges2))

        # Cache object should be the same instance
        cached_map_after = provider._collection_routing_map_by_item.get(collection_id)
        self.assertIs(cached_map, cached_map_after,
                      "Cache should not be replaced on a second call without force_refresh")


if __name__ == "__main__":
    unittest.main()
