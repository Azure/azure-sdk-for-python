# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Async unit tests for the shared partition key range cache.

Async counterparts of the cache-sharing tests in test_shared_pk_range_cache.py,
validating that the async PartitionKeyRangeCache shares routing maps correctly.
PKRange and Range data structure tests are not duplicated here since they are
the same class in both sync and async paths.
"""

import gc
import threading
import unittest

import pytest

import azure.cosmos._routing.aio.routing_map_provider as rmp_async
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing.aio.routing_map_provider import (
    PartitionKeyRangeCache,
    _shared_routing_map_cache,
    _shared_cache_lock,
    _shared_collection_locks,
    _shared_locks_locks,
    _shared_cache_refcounts,
)


class MockClient:
    def __init__(self, url_connection):
        self.url_connection = url_connection


def _reset_shared_cache_state():
    """Wipe all four shared-cache globals so successive tests start clean."""
    with _shared_cache_lock:
        _shared_routing_map_cache.clear()
        _shared_collection_locks.clear()
        _shared_locks_locks.clear()
        _shared_cache_refcounts.clear()


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
class TestSharedPartitionKeyRangeCacheAsync(unittest.IsolatedAsyncioTestCase):

    def tearDown(self):
        _reset_shared_cache_state()

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
        _reset_shared_cache_state()

    def _refcount(self, endpoint):
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
        # Keep c2 alive until the assertion above runs.
        _ = c2

    async def test_concurrent_release_does_not_double_decrement_async(self):
        """TOCTOU regression: concurrent release() decrements at most once.

        Mirrors the sync lifecycle guard for the async module's shared cache.
        """

        ep = "https://async-lifecycle5.documents.azure.com:443/"
        c_keep = PartitionKeyRangeCache(MockClient(ep))
        c_target = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 2)

        barrier = threading.Barrier(2)

        def go():
            barrier.wait()
            c_target.release()

        threads = [threading.Thread(target=go) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        # Refcount must still be 1 (only c_keep alive).
        self.assertEqual(self._refcount(ep), 1)
        self.assertIn(ep, _shared_routing_map_cache)
        self.assertIs(c_keep._collection_routing_map_by_item, _shared_routing_map_cache[ep])

    async def test_del_fallback_releases_async(self):
        """``__del__`` decrements refcount when explicit release is skipped."""

        ep = "https://async-lifecycle6.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 1)
        del c1
        gc.collect()
        self.assertEqual(self._refcount(ep), 0)
        self.assertNotIn(ep, _shared_routing_map_cache)

    async def test_clear_cache_does_not_change_refcount_async(self):
        ep = "https://async-lifecycle4.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        before = self._refcount(ep)
        c1.clear_cache()
        self.assertEqual(self._refcount(ep), before)
        self.assertIn(ep, _shared_routing_map_cache)

    async def test_reentrant_release_during_init_does_not_deadlock_async(self):
        """Acquires the async module's ``_shared_cache_lock`` on a single
        thread and calls ``release()`` from inside that critical section.
        A non-reentrant ``Lock`` would deadlock here; an ``RLock`` returns
        cleanly.
        """
        ep = "https://async-reentry1.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 1)

        # Explicit ``Any`` value type so the static checker doesn't infer
        # ``dict[str, bool | None]`` and reject the ``Exception`` assignment.
        result: dict = {"done": False, "error": None}

        def reenter():
            try:
                with _shared_cache_lock:
                    c1.release()
                result["done"] = True
            except Exception as exc:  # pylint: disable=broad-except
                result["error"] = exc

        worker = threading.Thread(target=reenter)
        worker.start()
        worker.join(timeout=5)

        self.assertFalse(
            worker.is_alive(),
            "Reentrant release() under _shared_cache_lock deadlocked; "
            "the async module's lock must be a threading.RLock."
        )
        self.assertIsNone(result["error"])
        self.assertTrue(result["done"])
        self.assertEqual(self._refcount(ep), 0)
        self.assertNotIn(ep, _shared_routing_map_cache)

    async def test_init_under_gc_triggered_by_dict_op_does_not_deadlock_async(self):
        """Reproduces the GC re-entry chain that requires the async module's
        ``_shared_cache_lock`` to be an ``RLock``.

        The async ``PartitionKeyRangeCache`` has the same ``__init__`` ->
        dict op -> cyclic GC -> ``__del__`` -> ``release()`` shape as the
        sync version, so a non-reentrant ``Lock`` would deadlock identically
        the moment cyclic GC fires inside the init critical section against
        any cache that participates in a reference cycle. The async module
        uses ``threading.RLock`` (not ``asyncio.Lock``) precisely so this
        sync-only re-entry path stays safe while remaining usable from
        coroutines.
        """
        class _GcTriggeringDict(dict):
            def __contains__(self, key):  # type: ignore[override]
                gc.collect()
                return super().__contains__(key)

        ep = "https://async-reentry-gc.documents.azure.com:443/"

        # Build a cache in a reference cycle and drop the outer reference;
        # only cyclic GC can collect it now.
        cache_in_cycle = PartitionKeyRangeCache(MockClient(ep))
        cache_in_cycle._cycle_self = cache_in_cycle  # type: ignore[attr-defined]
        del cache_in_cycle

        gc.disable()
        original_cache_dict = rmp_async._shared_routing_map_cache
        rmp_async._shared_routing_map_cache = _GcTriggeringDict(original_cache_dict)
        try:
            outcome: dict = {"done": False, "error": None}

            def _construct():
                try:
                    outcome["instance"] = PartitionKeyRangeCache(MockClient(ep))
                    outcome["done"] = True
                except Exception as e:  # pylint: disable=broad-except
                    outcome["error"] = e

            worker = threading.Thread(
                target=_construct, name="gc-reentry-worker-async", daemon=True,
            )
            worker.start()
            worker.join(timeout=3.0)

            self.assertFalse(
                worker.is_alive(),
                "Async PartitionKeyRangeCache(...) deadlocked when cyclic "
                "GC fired inside the init critical section; the async "
                "module's _shared_cache_lock must be a threading.RLock.",
            )
            self.assertIsNone(outcome["error"], f"Construction errored: {outcome['error']}")
            self.assertTrue(outcome["done"])
        finally:
            rmp_async._shared_routing_map_cache = original_cache_dict
            gc.enable()


if __name__ == "__main__":
    unittest.main()
