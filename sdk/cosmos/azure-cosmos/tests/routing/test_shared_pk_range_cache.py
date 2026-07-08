# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import gc
import threading
import unittest

import pytest

import azure.cosmos._routing.routing_map_provider as rmp
from azure.cosmos._routing.routing_range import Range, PKRange
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing.routing_map_provider import (
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
class TestSharedPartitionKeyRangeCache(unittest.TestCase):

    def tearDown(self):
        _reset_shared_cache_state()

    def test_same_endpoint_shares_cache(self):
        c1 = MockClient("https://account1.documents.azure.com:443/")
        c2 = MockClient("https://account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        self.assertIs(cache1._collection_routing_map_by_item,
                      cache2._collection_routing_map_by_item)

    def test_different_endpoints_isolated(self):
        c1 = MockClient("https://account1.documents.azure.com:443/")
        c2 = MockClient("https://account2.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        self.assertIsNot(cache1._collection_routing_map_by_item,
                         cache2._collection_routing_map_by_item)

    def test_shared_cache_populated_by_first_client(self):
        c1 = MockClient("https://account1.documents.azure.com:443/")
        c2 = MockClient("https://account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        pk_ranges = [{"id": "0", "minInclusive": "", "maxExclusive": "FF"}]
        crm = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in pk_ranges], "test-collection"
        )
        cache1._collection_routing_map_by_item["test-collection"] = crm
        self.assertIn("test-collection", cache2._collection_routing_map_by_item)
        self.assertIs(cache2._collection_routing_map_by_item["test-collection"], crm)

    def test_clear_cache_resets_for_endpoint(self):
        c1 = MockClient("https://account1.documents.azure.com:443/")
        c2 = MockClient("https://account1.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        original_dict = cache1._collection_routing_map_by_item
        cache1._collection_routing_map_by_item["coll1"] = "dummy"
        cache1.clear_cache()
        self.assertNotIn("coll1", cache1._collection_routing_map_by_item)
        # .clear() preserves the dict identity - all clients still share the same object
        self.assertIs(cache1._collection_routing_map_by_item, original_dict)
        self.assertIs(cache2._collection_routing_map_by_item, original_dict)

    def test_clear_cache_does_not_affect_other_endpoints(self):
        c1 = MockClient("https://account1.documents.azure.com:443/")
        c2 = MockClient("https://account2.documents.azure.com:443/")
        cache1 = PartitionKeyRangeCache(c1)
        cache2 = PartitionKeyRangeCache(c2)
        cache1._collection_routing_map_by_item["coll1"] = "data1"
        cache2._collection_routing_map_by_item["coll2"] = "data2"
        cache1.clear_cache()
        self.assertNotIn("coll1", cache1._collection_routing_map_by_item)
        self.assertIn("coll2", cache2._collection_routing_map_by_item)


    def test_pkrange_dict_access(self):
        """PKRange supports dict-style [key] access."""
        pkr = PKRange(id="1", minInclusive="00", maxExclusive="FF", parents=("0",))
        self.assertEqual(pkr["id"], "1")
        self.assertEqual(pkr["minInclusive"], "00")
        self.assertEqual(pkr.get("parents"), ("0",))
        self.assertEqual(pkr.get("_rid", "default"), "default")
        self.assertIn("id", pkr)
        self.assertNotIn("_rid", pkr)

    def test_pkrange_contains_truthy_presence_for_parents(self):
        """``"parents" in pkr`` follows truthy-presence semantics.

        The most common production case is a PKR that has never split
        (``parents=()``), where ``"parents" in pkr`` must report False so
        callers that previously consumed raw service dicts (where the field
        was simply absent when empty) keep working unchanged.
        """
        pkr_no_parents = PKRange(id="0", minInclusive="", maxExclusive="FF", parents=())
        self.assertNotIn("parents", pkr_no_parents)

        pkr_with_parents = PKRange(id="2", minInclusive="40", maxExclusive="80", parents=("0", "1"))
        self.assertIn("parents", pkr_with_parents)

    def test_pkrange_status_and_throughput_fraction_fields_roundtrip(self):
        """``status`` and ``throughputFraction`` are the non-routing PKR fields
        retained in the cache for forward-compat (e.g. filtering non-online
        ranges or future RU-share-aware logic).

        Confirms back-compat (default ``None`` => not present) and that
        explicit values flow through dict-style access and ``__contains__``.
        """
        pkr_default = PKRange(id="0", minInclusive="", maxExclusive="FF", parents=())
        self.assertIsNone(pkr_default.status)
        self.assertIsNone(pkr_default.throughputFraction)
        self.assertNotIn("status", pkr_default)
        self.assertNotIn("throughputFraction", pkr_default)

        pkr_online = PKRange(
            id="1", minInclusive="00", maxExclusive="80", parents=(),
            status="online", throughputFraction=0.5,
        )
        self.assertEqual(pkr_online.status, "online")
        self.assertEqual(pkr_online["status"], "online")
        self.assertIn("status", pkr_online)
        self.assertEqual(pkr_online.throughputFraction, 0.5)
        self.assertEqual(pkr_online["throughputFraction"], 0.5)
        self.assertIn("throughputFraction", pkr_online)

    def test_pkrange_in_collection_routing_map(self):
        """CollectionRoutingMap works with PKRange namedtuples."""
        pk_ranges = [
            PKRange(id="0", minInclusive="", maxExclusive="80", parents=()),
            PKRange(id="1", minInclusive="80", maxExclusive="FF", parents=()),
        ]
        crm = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in pk_ranges], "test"
        )
        self.assertIsNotNone(crm)
        overlapping = crm.get_overlapping_ranges(Range("", "FF", True, False))
        self.assertEqual(len(overlapping), 2)

    def test_range_has_slots(self):
        r = Range("00", "FF", True, False)
        # __slots__ is verified by the absence of __dict__. sys.getsizeof() is
        # intentionally not asserted because it is not a stable cross-version
        # / cross-platform contract.
        self.assertFalse(hasattr(r, "__dict__"))

    def test_range_skips_upper_when_already_uppercase(self):
        original = "05C1C9CD673398"
        r = Range(original, original, True, False)
        self.assertIs(r.min, original)

    def test_range_applies_upper_when_lowercase(self):
        r = Range("05c1c9cd", "05c1d9cd", True, False)
        self.assertEqual(r.min, "05C1C9CD")


@pytest.mark.cosmosEmulator
class TestSharedPartitionKeyRangeCacheLifecycle(unittest.TestCase):
    """Refcount and release() lifecycle tests for the process-global cache."""

    def tearDown(self):
        _reset_shared_cache_state()

    def _refcount(self, endpoint):
        return _shared_cache_refcounts.get(endpoint, 0)

    def test_construct_increments_refcount(self):
        ep = "https://lifecycle1.documents.azure.com:443/"
        self.assertEqual(self._refcount(ep), 0)
        c1 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 1)
        c2 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 2)
        # Keep references alive until end of test so refcount checks above
        # observe the constructed-but-not-released state.
        _ = (c1, c2)

    def test_release_decrements_refcount(self):
        ep = "https://lifecycle2.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        c2 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 2)
        c1.release()
        self.assertEqual(self._refcount(ep), 1)
        c2.release()
        self.assertEqual(self._refcount(ep), 0)

    def test_release_evicts_at_zero(self):
        ep = "https://lifecycle3.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        # All four dicts have an entry for the endpoint.
        self.assertIn(ep, _shared_routing_map_cache)
        self.assertIn(ep, _shared_collection_locks)
        self.assertIn(ep, _shared_locks_locks)
        self.assertIn(ep, _shared_cache_refcounts)
        c1.release()
        # After last release, all four are evicted.
        self.assertNotIn(ep, _shared_routing_map_cache)
        self.assertNotIn(ep, _shared_collection_locks)
        self.assertNotIn(ep, _shared_locks_locks)
        self.assertNotIn(ep, _shared_cache_refcounts)

    def test_release_does_not_evict_with_other_clients(self):
        ep = "https://lifecycle4.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        c2 = PartitionKeyRangeCache(MockClient(ep))
        c1.release()
        # Refcount drops to 1, entries remain for c2.
        self.assertEqual(self._refcount(ep), 1)
        self.assertIn(ep, _shared_routing_map_cache)
        # c2 still references the same shared dict (identity preserved).
        self.assertIs(c2._collection_routing_map_by_item,
                      _shared_routing_map_cache[ep])

    def test_release_is_idempotent(self):
        """Sequential double-release on the same instance does not double-decrement."""
        ep = "https://lifecycle5.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        c2 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 2)
        c1.release()
        c1.release()  # second call must be a no-op
        c1.release()
        self.assertEqual(self._refcount(ep), 1)
        # c2's entries must remain.
        self.assertIn(ep, _shared_routing_map_cache)
        # Keep c2 alive until the assertion above runs.
        _ = c2

    def test_concurrent_release_does_not_double_decrement(self):
        """TOCTOU regression: two threads racing release() decrement at most once.

        Without the fix to move the ``_released`` check inside the shared
        cache lock, two concurrent callers (e.g. ``__exit__`` racing
        ``__del__``) can both pass the early-return guard before either
        sets the flag, producing a double decrement.
        """
        ep = "https://lifecycle6.documents.azure.com:443/"
        # Hold an extra refcount via c_keep so a double-decrement bug would
        # observably wrong-evict the endpoint (refcount would go to -1 and
        # the entry would be popped).
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
        # c_keep still references the same shared dict.
        self.assertIs(c_keep._collection_routing_map_by_item,
                      _shared_routing_map_cache[ep])

    def test_del_fallback_releases(self):
        """``__del__`` decrements refcount when client teardown was skipped."""
        ep = "https://lifecycle7.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 1)
        del c1
        gc.collect()
        # __del__ runs release() → refcount hits 0 → endpoint evicted.
        self.assertEqual(self._refcount(ep), 0)
        self.assertNotIn(ep, _shared_routing_map_cache)

    def test_clear_cache_does_not_change_refcount(self):
        ep = "https://lifecycle8.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        before = self._refcount(ep)
        c1.clear_cache()
        self.assertEqual(self._refcount(ep), before)
        # Endpoint still present.
        self.assertIn(ep, _shared_routing_map_cache)

    def test_reentrant_release_during_init_does_not_deadlock(self):
        """Acquires ``_shared_cache_lock`` on a single thread and calls
        ``release()`` from inside that critical section. A non-reentrant
        ``Lock`` would deadlock here; an ``RLock`` returns cleanly.
        """
        ep = "https://reentry1.documents.azure.com:443/"
        c1 = PartitionKeyRangeCache(MockClient(ep))
        self.assertEqual(self._refcount(ep), 1)

        # Explicit ``Any`` value type so the static checker doesn't infer
        # ``dict[str, bool | None]`` from the initial values and then flag
        # the ``Exception`` assignment in the exception arm as a type error.
        result: dict = {"done": False, "error": None}

        def reenter():
            try:
                # Acquire the shared lock first to mimic the ``__init__``
                # critical section, then call ``release()`` from inside it
                # to simulate the GC-driven ``__del__`` path. A non-reentrant
                # Lock deadlocks here; an RLock returns cleanly.
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
            "the lock must be a threading.RLock (see module-level comment)."
        )
        self.assertIsNone(result["error"])
        self.assertTrue(result["done"])
        # Refcount must have decremented exactly once.
        self.assertEqual(self._refcount(ep), 0)
        self.assertNotIn(ep, _shared_routing_map_cache)

    def test_init_under_gc_triggered_by_dict_op_does_not_deadlock(self):
        """Reproduces the GC re-entry chain that requires
        ``_shared_cache_lock`` to be an ``RLock``.

        A ``PartitionKeyRangeCache`` that participates in a reference cycle
        can only be collected by cyclic GC. When another instance is
        constructed against the same endpoint, the dict op inside
        ``__init__``'s critical section can trigger cyclic GC, which
        sweeps the cycled instance and runs its ``__del__`` ->
        ``release()`` on the same thread, re-acquiring the lock.

        To force the chain deterministically: build a cache in a reference
        cycle, drop the outer reference, swap ``_shared_routing_map_cache``
        for a dict whose ``__contains__`` calls ``gc.collect()``, then
        construct a second cache in a worker thread with a short timeout.
        ``Lock`` deadlocks the worker; ``RLock`` returns in milliseconds.
        """
        class _GcTriggeringDict(dict):
            """``__contains__`` runs cyclic GC so collection of the
            unreachable cycle happens inside the init lock block.
            """
            def __contains__(self, key):  # type: ignore[override]
                gc.collect()
                return super().__contains__(key)

        ep = "https://reentry-gc.documents.azure.com:443/"

        # Build a cache in a reference cycle and drop the outer reference;
        # only cyclic GC can collect it now.
        cache_in_cycle = PartitionKeyRangeCache(MockClient(ep))
        cache_in_cycle._cycle_self = cache_in_cycle  # type: ignore[attr-defined]
        del cache_in_cycle

        # Disable automatic gen-0/1/2 collection so the only collection
        # opportunity is the explicit gc.collect() inside __contains__.
        gc.disable()
        original_cache_dict = rmp._shared_routing_map_cache
        rmp._shared_routing_map_cache = _GcTriggeringDict(original_cache_dict)
        try:
            # Construct a second cache in a worker thread with a short
            # timeout. Lock deadlocks; RLock completes in milliseconds.
            outcome: dict = {"done": False, "error": None}

            def _construct():
                try:
                    outcome["instance"] = PartitionKeyRangeCache(MockClient(ep))
                    outcome["done"] = True
                except Exception as e:  # pylint: disable=broad-except
                    outcome["error"] = e

            worker = threading.Thread(
                target=_construct, name="gc-reentry-worker", daemon=True,
            )
            worker.start()
            worker.join(timeout=3.0)

            self.assertFalse(
                worker.is_alive(),
                "PartitionKeyRangeCache(...) deadlocked when cyclic GC "
                "fired inside the init critical section; "
                "_shared_cache_lock must be a threading.RLock.",
            )
            self.assertIsNone(outcome["error"], f"Construction errored: {outcome['error']}")
            self.assertTrue(outcome["done"])
        finally:
            rmp._shared_routing_map_cache = original_cache_dict
            gc.enable()


if __name__ == "__main__":
    unittest.main()
