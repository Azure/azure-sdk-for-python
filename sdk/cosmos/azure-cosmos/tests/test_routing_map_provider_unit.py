# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync unit tests for PartitionKeyRangeCache:
  - Concurrent access (double-checked locking)
  - Empty change feed response (304 Not Modified / zero ranges from incremental update)
"""

import threading
import time
import unittest
from unittest.mock import MagicMock

import pytest

from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos import http_constants
from azure.cosmos._gone_retry_policy_base import _PartitionKeyRangeGoneRetryPolicyBase


# =========================================================
# Helpers
# =========================================================

def _make_complete_routing_map(collection_id="coll1", etag='"etag-1"'):
    """Create a minimal but complete CollectionRoutingMap for testing."""
    ranges = [
        ({'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}, True)
    ]
    return CollectionRoutingMap.CompleteRoutingMap(ranges, collection_id, etag)


def _make_mock_client(ranges, response_etag='"etag-resp"', include_etag_header=True):
    """Create a mock client whose _ReadPartitionKeyRanges returns the given ranges
    and whose response_hook receives the given etag."""
    client = MagicMock()

    def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
        headers = ({http_constants.HttpHeaders.ETag: response_etag} if include_etag_header else {})
        # Older call sites pass response_hook; current provider passes internal header capture.
        if response_hook:
            response_hook(headers, None)
        capture_headers = kwargs.get('_internal_response_headers_capture')
        if capture_headers is not None:
            capture_headers.update(headers)
        return iter(ranges)

    client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
    return client


# =========================================================
# Test Class
# =========================================================

@pytest.mark.cosmosEmulator
class TestRoutingMapProviderUnit(unittest.TestCase):
    """Sync unit tests for PartitionKeyRangeCache."""

    def test_get_overlapping_ranges_returns_empty_when_routing_map_is_none(self):
        """Sync parity: return [] when routing map is unavailable instead of crashing."""
        cache = PartitionKeyRangeCache(MagicMock())
        cache.get_routing_map = MagicMock(return_value=None)

        result = cache.get_overlapping_ranges(
            "dbs/db1/colls/coll1",
            [MagicMock()],
            feed_options={}
        )

        self.assertEqual(result, [])
        cache.get_routing_map.assert_called_once()

    def test_concurrent_initial_load_only_fetches_once(self):
        """When multiple threads concurrently call get_routing_map on an empty
        cache, only ONE thread should call _ReadPartitionKeyRanges. The others
        should find the map populated by the first thread (double-checked lock)."""
        full_range = {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}
        call_count = {'n': 0}
        barrier = threading.Barrier(5, timeout=10)

        client = MagicMock()

        def slow_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1
            # Simulate slow network call so other threads pile up on the lock
            time.sleep(0.1)
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag-slow"'}, None)
            return iter([full_range])

        client._ReadPartitionKeyRanges = MagicMock(side_effect=slow_read_pk_ranges)

        cache = PartitionKeyRangeCache(client)
        results = [None] * 5
        errors = []

        def worker(idx):
            try:
                barrier.wait()  # All threads start at the same time
                result = cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})
                results[idx] = result
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        self.assertEqual(errors, [], f"Worker threads raised errors: {errors}")

        # All threads should have gotten a valid routing map
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Thread {i} should have gotten a routing map")

        # All threads should return the SAME object (identity check)
        for i in range(1, 5):
            self.assertIs(results[0], results[i],
                          f"Thread {i} should return the same cached object as thread 0")

        # _ReadPartitionKeyRanges should have been called exactly once
        self.assertEqual(call_count['n'], 1,
                         f"Expected 1 fetch call (double-checked lock), got {call_count['n']}")

    def test_concurrent_access_different_collections_independent(self):
        """Concurrent get_routing_map calls for DIFFERENT collections should
        not block each other — each collection has its own lock."""
        call_log = {'coll_a': 0, 'coll_b': 0}
        barrier = threading.Barrier(2, timeout=10)

        client = MagicMock()

        def read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            # Track which collection was fetched
            if 'coll_a' in collection_link:
                call_log['coll_a'] += 1
            else:
                call_log['coll_b'] += 1
            time.sleep(0.05)
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag"'}, None)
            return iter([{'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}])

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges)

        cache = PartitionKeyRangeCache(client)
        results = {}
        errors = []

        def worker(coll_link):
            try:
                barrier.wait()
                r = cache.get_routing_map(coll_link, feed_options={})
                results[coll_link] = r
            except Exception as e:
                errors.append(e)

        t1 = threading.Thread(target=worker, args=("dbs/db1/colls/coll_a",))
        t2 = threading.Thread(target=worker, args=("dbs/db1/colls/coll_b",))
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        self.assertEqual(errors, [])
        self.assertIsNotNone(results.get("dbs/db1/colls/coll_a"))
        self.assertIsNotNone(results.get("dbs/db1/colls/coll_b"))

        # Both collections should have been fetched independently
        self.assertEqual(call_log['coll_a'], 1)
        self.assertEqual(call_log['coll_b'], 1)

        # They should be different objects (different collections)
        self.assertIsNot(results["dbs/db1/colls/coll_a"], results["dbs/db1/colls/coll_b"])

    def test_concurrent_force_refresh_only_refreshes_once(self):
        """When multiple threads force_refresh the same collection simultaneously,
        only one should actually fetch — the second thread's double-check inside
        the lock should see the updated map and skip the fetch.

        We mock _fetch_routing_map directly to isolate the locking logic from
        the change-feed protocol details."""
        call_count = {'n': 0}
        barrier = threading.Barrier(3, timeout=10)

        client = MagicMock()
        cache = PartitionKeyRangeCache(client)

        # Pre-populate cache so force_refresh has something to compare against
        initial_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-stale"')
        cache._collection_routing_map_by_item["dbs/db1/colls/coll1"] = initial_map

        refreshed_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-refreshed"')

        original_fetch = cache._fetch_routing_map

        def mock_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):
            call_count['n'] += 1
            time.sleep(0.1)  # Simulate slow fetch
            return refreshed_map

        cache._fetch_routing_map = mock_fetch

        results = [None] * 3
        errors = []

        def worker(idx):
            try:
                barrier.wait()
                r = cache.get_routing_map(
                    "dbs/db1/colls/coll1",
                    feed_options={},
                    force_refresh=True,
                    previous_routing_map=initial_map
                )
                results[idx] = r
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        self.assertEqual(errors, [])

        # All threads should get a valid result
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Thread {i} should have gotten a routing map")

        # Only one fetch should have occurred — the first thread refreshes,
        # the other threads see the updated ETag and skip
        self.assertEqual(call_count['n'], 1,
                         f"Expected 1 fetch (others skip via stale check), got {call_count['n']}")


    def test_empty_incremental_response_preserves_existing_map(self):
        """When an incremental change feed returns zero ranges (service returned
        304 Not Modified / no changes since the ETag), try_combine with an empty
        list should return the existing map unchanged."""
        initial_map = _make_complete_routing_map("coll1", '"etag-1"')

        # try_combine with empty list and same etag
        result = initial_map.try_combine([], '"etag-2"')

        self.assertIsNotNone(result, "try_combine with empty delta should return a valid map")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0'], "Ranges should be unchanged")
        self.assertEqual(result.change_feed_etag, '"etag-2"', "ETag should be updated")

    def test_fetch_routing_map_empty_incremental_response(self):
        """_fetch_routing_map should succeed when the incremental change feed
        returns zero ranges — the existing map should be preserved with
        the updated ETag."""
        full_range = {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}

        client = MagicMock()

        def read_pk_ranges_empty(collection_link, options, response_hook=None, **kwargs):
            headers = {http_constants.HttpHeaders.ETag: '"etag-new"'}
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)
            return iter([])  # Empty — no changes

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_empty)

        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIsNotNone(result, "Should return valid map when incremental response is empty")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0'], "Ranges should be preserved from previous map")
        self.assertEqual(result.change_feed_etag, '"etag-new"', "ETag should be updated")

    def test_fetch_routing_map_empty_full_load_returns_none(self):
        """_fetch_routing_map should return None when a full load (no previous
        map) returns zero ranges — this means the service returned nothing."""
        client = MagicMock()

        def read_pk_ranges_empty(collection_link, options, response_hook=None, **kwargs):
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag"'}, None)
            return iter([])  # No ranges at all

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_empty)

        cache = PartitionKeyRangeCache(client)

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=None,  # Full load
            feed_options={}
        )

        self.assertIsNone(result, "Full load with empty ranges should return None")


    def test_get_previous_routing_map_exact_key_finds_entry(self):
        """_get_previous_routing_map should find the cached routing map when
        the collection_link matches the key stored in the cache exactly."""
        mock_client = MagicMock()
        mock_routing_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-1"')

        # Wire up the mock so _routing_map_provider._collection_routing_map_by_item exists
        mock_provider = MagicMock()
        mock_provider._collection_routing_map_by_item = {
            "dbs/db1/colls/coll1": mock_routing_map
        }
        mock_client._routing_map_provider = mock_provider

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/coll1")

        self.assertIs(result, mock_routing_map,
                      "Should return the cached map when the key matches exactly")

    def test_get_previous_routing_map_normalizes_collection_link(self):
        """_get_previous_routing_map normalizes collection_link before cache lookup.
        Equivalent links with leading/trailing slashes should resolve to the
        same cached routing map entry."""
        mock_client = MagicMock()
        mock_routing_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-1"')

        mock_provider = MagicMock()
        mock_provider._collection_routing_map_by_item = {
            "dbs/db1/colls/coll1": mock_routing_map  # stored with clean key
        }
        mock_client._routing_map_provider = mock_provider

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)

        # Trailing slash — should hit after normalization
        result = policy._get_previous_routing_map("dbs/db1/colls/coll1/")
        self.assertIs(result, mock_routing_map)

        # Leading slash — should also hit after normalization
        result = policy._get_previous_routing_map("/dbs/db1/colls/coll1")
        self.assertIs(result, mock_routing_map)

        # Both leading and trailing slashes should still resolve
        result = policy._get_previous_routing_map("/dbs/db1/colls/coll1/")
        self.assertIs(result, mock_routing_map)

    def test_get_previous_routing_map_returns_none_for_missing(self):
        """_get_previous_routing_map returns None when the collection is not
        in the cache."""
        mock_client = MagicMock()
        mock_provider = MagicMock()
        mock_provider._collection_routing_map_by_item = {}
        mock_client._routing_map_provider = mock_provider

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/unknown")
        self.assertIsNone(result)

    def test_get_previous_routing_map_returns_none_for_none_link(self):
        """_get_previous_routing_map returns None when collection_link is None."""
        mock_client = MagicMock()
        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map(None)
        self.assertIsNone(result)

    def test_get_previous_routing_map_returns_none_when_no_provider(self):
        """_get_previous_routing_map returns None when the client has no
        _routing_map_provider attribute."""
        mock_client = MagicMock(spec=[])  # spec=[] means no attributes
        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/coll1")
        self.assertIsNone(result)

    def test_extract_collection_info_returns_link_and_rid_from_request_headers(self):
        """_extract_collection_info should return collection link + RID when
        intended collection RID header is present and cache lookup succeeds."""
        mock_client = MagicMock()
        rid = "rid-123"
        collection_link = "dbs/db1/colls/coll1"
        mock_client._container_properties_cache = {
            rid: {"container_link": collection_link}
        }

        request = MagicMock()
        request.headers = {http_constants.HttpHeaders.IntendedCollectionRID: rid}

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client, None, None, None, request)
        extracted_link, extracted_rid = policy._extract_collection_info()

        self.assertEqual(extracted_link, collection_link)
        self.assertEqual(extracted_rid, rid)

    def test_extract_collection_info_returns_none_when_request_args_missing(self):
        """_extract_collection_info should return (None, None) when no request
        argument is present in policy args."""
        mock_client = MagicMock()
        mock_client._container_properties_cache = {}

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        extracted_link, extracted_rid = policy._extract_collection_info()

        self.assertIsNone(extracted_link)
        self.assertIsNone(extracted_rid)

    def test_extract_collection_info_returns_rid_even_when_cache_miss(self):
        """_extract_collection_info should still return RID from headers even
        when cache has no matching container entry."""
        mock_client = MagicMock()
        mock_client._container_properties_cache = {}
        rid = "rid-missing"

        request = MagicMock()
        request.headers = {http_constants.HttpHeaders.IntendedCollectionRID: rid}

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client, None, None, None, request)
        extracted_link, extracted_rid = policy._extract_collection_info()

        self.assertIsNone(extracted_link)
        self.assertEqual(extracted_rid, rid)

    def test_fetch_routing_map_empty_incremental_response_same_etag_returns_same_object(self):
        """Empty incremental response with unchanged ETag should return the
        existing map object without rebuilding."""
        client = _make_mock_client(ranges=[], response_etag='"etag-old"')
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIs(result, previous_map, "No-op incremental refresh should reuse existing map instance")
        self.assertEqual(result.change_feed_etag, '"etag-old"')

    def test_fetch_routing_map_empty_incremental_response_missing_etag_preserves_previous(self):
        """If service omits ETag on an empty incremental response, preserve
        the existing ETag and map instance."""
        client = _make_mock_client(ranges=[], include_etag_header=False)
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        with self.assertLogs("azure.cosmos._routing._routing_map_provider_common", level="WARNING") as logs:
            result = cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="dbs/db1/colls/coll1",
                previous_routing_map=previous_map,
                feed_options={}
            )

        self.assertIs(result, previous_map)
        self.assertEqual(result.change_feed_etag, '"etag-old"')
        self.assertTrue(any("returned no ETag" in message for message in logs.output))

    def test_fetch_routing_map_fallback_rechains_upstream_response_hook(self):
        """Upstream response_hook should be invoked for both incremental and
        full-refresh attempts when incremental merge falls back."""
        client = MagicMock()
        upstream_calls = []
        call_count = {'n': 0}

        def upstream_hook(headers, _):
            upstream_calls.append(dict(headers))

        def read_pk_ranges_with_fallback(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: f'"etag-{call_count["n"]}"'}, None)

            if call_count['n'] <= 2:
                return iter([
                    {
                        'id': '1',
                        'minInclusive': '',
                        'maxExclusive': 'AA',
                        'parents': ['missing-parent']
                    }
                ])
            return iter([{'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}])

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_with_fallback)
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={},
            response_hook=upstream_hook
        )

        self.assertIsNotNone(result)
        self.assertEqual(call_count['n'], 3, "Expected incremental attempt, one retry, then full-refresh fallback")
        self.assertEqual(len(upstream_calls), 3, "Upstream response_hook should run for retry and fallback attempts")

    def test_fetch_routing_map_incomplete_retry_succeeds_without_full_refresh(self):
        """Incomplete incremental update should retry once with the same ETag and succeed without full refresh."""
        client = MagicMock()
        call_count = {'n': 0}
        seen_if_none_match = []

        def read_pk_ranges_retry_then_success(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1
            headers = kwargs.get('headers', {})
            seen_if_none_match.append(headers.get(http_constants.HttpHeaders.IfNoneMatch))

            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag-inc"'}, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update({http_constants.HttpHeaders.ETag: '"etag-inc"'})

            # First incremental attempt is incomplete (missing parent), second resolves.
            if call_count['n'] == 1:
                return iter([
                    {'id': '9', 'minInclusive': '', 'maxExclusive': 'AA', 'parents': ['missing-parent']}
                ])

            return iter([
                {'id': '2', 'minInclusive': '', 'maxExclusive': '03', 'parents': ['0']},
                {'id': '3', 'minInclusive': '03', 'maxExclusive': '05', 'parents': ['0']},
                {'id': '4', 'minInclusive': '', 'maxExclusive': '02', 'parents': ['2']},
                {'id': '5', 'minInclusive': '02', 'maxExclusive': '03', 'parents': ['2']},
            ])

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_retry_then_success)
        cache = PartitionKeyRangeCache(client)
        previous_map = CollectionRoutingMap.CompleteRoutingMap(
            [
                ({'id': '0', 'minInclusive': '', 'maxExclusive': '05'}, True),
                ({'id': '1', 'minInclusive': '05', 'maxExclusive': 'FF'}, True),
            ],
            "dbs/db1/colls/coll1",
            '"etag-old"'
        )

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(result)
        self.assertEqual(call_count['n'], 2, "Expected one incremental retry and no full refresh")
        self.assertEqual(seen_if_none_match, ['"etag-old"', '"etag-old"'])
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['4', '5', '3', '1'])

    def test_fetch_routing_map_cascading_single_delta_split_merges_incrementally(self):
        """Cascading split deltas should merge incrementally without full refresh.

        Scenario (single incremental delta):
        - Previous map has ranges: 0 (""-"05"), 1 ("05"-"FF")
        - Delta includes: 2/3 split 0, and 4/5 split 2 in the same payload.

        Parent links are resolved transitively within the same delta, so
        parent "2" is resolvable after "2" is introduced from parent "0".
        """
        client = MagicMock()
        call_count = {'n': 0}

        def read_pk_ranges_cascading(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: f'"etag-{call_count["n"]}"'}, None)

            # 1st call: incremental payload with a cascading parent chain in one delta.
            if call_count['n'] == 1:
                return iter([
                    {'id': '2', 'minInclusive': '', 'maxExclusive': '03', 'parents': ['0']},
                    {'id': '3', 'minInclusive': '03', 'maxExclusive': '05', 'parents': ['0']},
                    {'id': '4', 'minInclusive': '', 'maxExclusive': '02', 'parents': ['2']},
                    {'id': '5', 'minInclusive': '02', 'maxExclusive': '03', 'parents': ['2']},
                ])

            return iter([])

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_cascading)
        cache = PartitionKeyRangeCache(client)

        previous_map = CollectionRoutingMap.CompleteRoutingMap(
            [
                ({'id': '0', 'minInclusive': '', 'maxExclusive': '05'}, True),
                ({'id': '1', 'minInclusive': '05', 'maxExclusive': 'FF'}, True),
            ],
            "dbs/db1/colls/coll1",
            '"etag-old"'
        )

        result = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIsNotNone(result)
        self.assertEqual(call_count['n'], 1, "Expected single incremental fetch for cascading split")

        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['4', '5', '3', '1'])
        self.assertEqual(result.change_feed_etag, '"etag-old"')


if __name__ == "__main__":
    unittest.main()
