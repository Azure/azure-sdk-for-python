# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for the shared partition key range cache.

Async counterparts of the cache-sharing tests in test_shared_pk_range_cache.py,
validating that the async PartitionKeyRangeCache shares routing maps correctly.
PKRange and Range data structure tests are not duplicated here since they are
the same class in both sync and async paths.
"""

import unittest

import pytest

from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing.aio.routing_map_provider import (
    PartitionKeyRangeCache,
    _shared_routing_map_cache,
    _shared_cache_lock,
)


class MockClient:
    def __init__(self, url_connection):
        self.url_connection = url_connection


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestSharedPartitionKeyRangeCacheAsync(unittest.IsolatedAsyncioTestCase):

    def tearDown(self):
        # Wipe ALL four shared-cache globals between unit tests, not just
        # the routing-map dict, so refcount and lock state stay consistent
        # for tests that exercise lifecycle behavior.
        from azure.cosmos._routing.aio.routing_map_provider import (
            _shared_collection_locks,
            _shared_locks_locks,
            _shared_cache_refcounts,
        )
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()
            _shared_collection_locks.clear()
            _shared_locks_locks.clear()
            _shared_cache_refcounts.clear()

    async def test_same_endpoint_shares_cache_async(self):
        """Async: Two caches with the same endpoint share the same dict."""
        c1 = MockClient("https://async-account1.documents.azure.com:443/")
        c2 = MockClient("https://async-account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        self.assertIs(cache1._collection_routing_map_by_item,
                      cache2._collection_routing_map_by_item)

    async def test_different_endpoints_isolated_async(self):
        """Async: Two caches with different endpoints have isolated dicts."""
        c1 = MockClient("https://async-account1.documents.azure.com:443/")
        c2 = MockClient("https://async-account2.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        self.assertIsNot(cache1._collection_routing_map_by_item,
                         cache2._collection_routing_map_by_item)

    async def test_shared_cache_populated_by_first_client_async(self):
        """Async: Data added by one cache is visible to another sharing the same endpoint."""
        c1 = MockClient("https://async-account1.documents.azure.com:443/")
        c2 = MockClient("https://async-account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        pk_ranges = [{"id": "0", "minInclusive": "", "maxExclusive": "FF"}]
        crm = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in pk_ranges], "test-collection"
        )
        cache1._collection_routing_map_by_item["test-collection"] = crm
        self.assertIn("test-collection", cache2._collection_routing_map_by_item)
        self.assertIs(cache2._collection_routing_map_by_item["test-collection"], crm)

    async def test_clear_cache_resets_for_endpoint_async(self):
        """Async: clear_cache() empties the shared dict while preserving identity."""
        c1 = MockClient("https://async-account1.documents.azure.com:443/")
        c2 = MockClient("https://async-account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        original_dict = cache1._collection_routing_map_by_item
        cache1._collection_routing_map_by_item["coll1"] = "dummy"
        cache1.clear_cache()
        self.assertNotIn("coll1", cache1._collection_routing_map_by_item)
        self.assertIs(cache1._collection_routing_map_by_item, original_dict)
        self.assertIs(cache2._collection_routing_map_by_item, original_dict)

    async def test_clear_cache_does_not_affect_other_endpoints_async(self):
        """Async: clear_cache() on one endpoint doesn't affect another."""
        c1 = MockClient("https://async-account1.documents.azure.com:443/")
        c2 = MockClient("https://async-account2.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        cache1._collection_routing_map_by_item["coll1"] = "data1"
        cache2._collection_routing_map_by_item["coll2"] = "data2"
        cache1.clear_cache()
        self.assertNotIn("coll1", cache1._collection_routing_map_by_item)
        self.assertIn("coll2", cache2._collection_routing_map_by_item)




@pytest.mark.cosmosEmulator
class TestSharedPartitionKeyRangeCacheLifecycleAsync(unittest.IsolatedAsyncioTestCase):
    """Async refcount and release() lifecycle tests."""

    def tearDown(self):
        from azure.cosmos._routing.aio.routing_map_provider import (
            _shared_collection_locks,
            _shared_locks_locks,
            _shared_cache_refcounts,
        )
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()
            _shared_collection_locks.clear()
            _shared_locks_locks.clear()
            _shared_cache_refcounts.clear()

    def _refcount(self, endpoint):
        from azure.cosmos._routing.aio.routing_map_provider import _shared_cache_refcounts
        return _shared_cache_refcounts.get(endpoint, 0)

    async def test_construct_and_release_async(self):
        ep = "https://async-lifecycle1.documents.azure.com:443/"
        self.assertEqual(self._refcount(ep), 0)
        c1 = PartitionKeyRangeCache(MockClient(ep))
        c2 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 2)
        c1.release()
        self.assertEqual(self._refcount(ep), 1)
        c2.release()
        self.assertEqual(self._refcount(ep), 0)

    async def test_release_evicts_at_zero_async(self):
        from azure.cosmos._routing.aio.routing_map_provider import (
            _shared_collection_locks,
            _shared_locks_locks,
            _shared_cache_refcounts,
        )
        ep = "https://async-lifecycle2.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        for d in (_shared_routing_map_cache, _shared_collection_locks,
                  _shared_locks_locks, _shared_cache_refcounts):
            self.assertIn(ep, d)
        c1.release()
        for d in (_shared_routing_map_cache, _shared_collection_locks,
                  _shared_locks_locks, _shared_cache_refcounts):
            self.assertNotIn(ep, d)

    async def test_release_is_idempotent_async(self):
        ep = "https://async-lifecycle3.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        c2 = PartitionKeyRangeCache(MockClient(ep))
        c1.release()
        c1.release()
        c1.release()
        self.assertEqual(self._refcount(ep), 1)
        # c2 entry retained
        self.assertIn(ep, _shared_routing_map_cache)
        del c2

    async def test_clear_cache_does_not_change_refcount_async(self):
        ep = "https://async-lifecycle4.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        before = self._refcount(ep)
        c1.clear_cache()
        self.assertEqual(self._refcount(ep), before)
        self.assertIn(ep, _shared_routing_map_cache)


if __name__ == "__main__":
    unittest.main()
