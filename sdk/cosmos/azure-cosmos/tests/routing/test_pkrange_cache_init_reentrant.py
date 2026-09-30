# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Regression tests for GC re-entry during ``PartitionKeyRangeCache.__init__``.

These tests cover the partial-clear + re-entrant ``release()`` path that
previously caused a KeyError.
"""

from __future__ import annotations

import gc
import threading
import unittest

import pytest

from azure.cosmos._routing.routing_map_provider import (
    PartitionKeyRangeCache,
    _shared_routing_map_cache,
    _shared_cache_lock,
    _shared_collection_locks,
    _shared_locks_locks,
    _shared_cache_refcounts,
)


_ENDPOINT = "https://pkrange-init-reentry.documents.azure.com:443/"


class _MockClient:
    """Minimal mock client with a cycle slot used by the regression setup."""

    def __init__(self, url):
        self.url_connection = url
        self.cycle_ref = None


def _reset_shared_state():
    """Reset all four shared-cache globals."""
    gc.collect()
    with _shared_cache_lock:
        _shared_routing_map_cache.clear()
        _shared_collection_locks.clear()
        _shared_locks_locks.clear()
        _shared_cache_refcounts.clear()


@pytest.mark.cosmosEmulator
class TestPartitionKeyRangeCacheInitReentrant(unittest.TestCase):
    """Deterministic regression for the GC re-entry KeyError."""

    def setUp(self):
        _reset_shared_state()
        gc.disable()  # only the test's monkey-patched Lock() triggers GC
        self._real_lock = threading.Lock

    def tearDown(self):
        threading.Lock = self._real_lock  # type: ignore[assignment]
        gc.enable()
        _reset_shared_state()

    def _make_orphan_in_cycle(self):
        """Build a cycle-pinned cache instance collectible only by cyclic GC."""
        client = _MockClient(_ENDPOINT)
        cache = PartitionKeyRangeCache(client)
        # Cycle: client.cycle_ref -> cache -> cache._document_client -> client
        client.cycle_ref = cache

    def test_init_survives_reentrant_release_via_gc_during_lock_alloc(self):
        """Constructor should not raise when GC re-enters ``release()``."""
        # Create an orphan in a cycle so GC owns finalization.
        self._make_orphan_in_cycle()
        self.assertEqual(
            _shared_cache_refcounts.get(_ENDPOINT), 1,
            "precondition: orphan creation must register refcount == 1",
        )

        # Simulate historical partial cleanup that cleared only one dict.
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()

        # Force cyclic GC on the first ``threading.Lock()`` call in next init.
        real_lock = self._real_lock
        fired = {"count": 0}

        def gc_triggering_lock(*args, **kwargs):
            if fired["count"] == 0:
                fired["count"] += 1
                gc.collect()
            return real_lock(*args, **kwargs)

        threading.Lock = gc_triggering_lock  # type: ignore[assignment]
        try:
            # Construct a new cache; this used to raise KeyError.
            new_client = _MockClient(_ENDPOINT)
            cache = PartitionKeyRangeCache(new_client)
        finally:
            threading.Lock = real_lock  # type: ignore[assignment]

        # Ensure this test actually exercised the GC-triggered path.
        self.assertGreaterEqual(
            fired["count"], 1,
            "test invariant: the monkey-patched Lock() must have fired GC "
            "at least once during __init__",
        )

        # New cache must bind to entries currently in shared registries.
        self.assertIs(
            cache._collection_routing_map_by_item,
            _shared_routing_map_cache[_ENDPOINT],
            "new cache must bind to the routing-map dict currently in the registry",
        )
        self.assertIs(
            cache._collection_locks,
            _shared_collection_locks[_ENDPOINT],
            "new cache must bind to the collection-locks dict currently in the registry",
        )
        self.assertIs(
            cache._locks_lock,
            _shared_locks_locks[_ENDPOINT],
            "new cache must bind to the meta-lock currently in the registry",
        )

        # Refcount should be one live cache after orphan release + new init.
        self.assertEqual(
            _shared_cache_refcounts[_ENDPOINT], 1,
            "refcount must be 1 (orphan released by GC, new cache added one)",
        )

    def test_init_setdefault_never_clobbers_live_inner_dicts(self):
        """``setdefault`` init should preserve uncleared shared entries."""
        cache1 = PartitionKeyRangeCache(_MockClient(_ENDPOINT))
        original_inner = cache1._collection_routing_map_by_item
        original_locks = cache1._collection_locks
        original_meta = cache1._locks_lock

        # Partial clear: drop only the routing-map dict.
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()

        cache2 = PartitionKeyRangeCache(_MockClient(_ENDPOINT))

        # cache2 should get a new routing map dict but reuse uncleared entries.
        self.assertIsNot(
            cache2._collection_routing_map_by_item, original_inner,
            "cleared routing-map dict must be replaced",
        )
        self.assertIs(
            cache2._collection_locks, original_locks,
            "uncleared collection-locks dict must be reused (no clobbering)",
        )
        self.assertIs(
            cache2._locks_lock, original_meta,
            "uncleared meta-lock must be reused (no clobbering)",
        )

        # Refcount should reflect both live instances.
        self.assertEqual(
            _shared_cache_refcounts[_ENDPOINT], 2,
            "live refcount must be preserved across partial-clear + reconstruct",
        )

        # Keep both alive until the assertions above run.
        _ = (cache1, cache2)


if __name__ == "__main__":
    unittest.main()

