# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

from azure.cosmos._routing import routing_range as routing_range
from azure.cosmos._routing.routing_map_provider import CollectionRoutingMap
from azure.cosmos._routing.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos import http_constants

from typing import Optional, Mapping, Any
from unittest.mock import MagicMock
import threading

@pytest.mark.cosmosEmulator
class TestRoutingMapProvider(unittest.TestCase):
    @staticmethod
    def _capture_internal_headers(kwargs, etag):
        captured_headers = kwargs.get('_internal_response_headers_capture')
        if captured_headers is not None:
            captured_headers.clear()
            captured_headers.update({'ETag': etag})

    class MockedCosmosClientConnection(object):

        def __init__(self, partition_key_ranges):
            self.partition_key_ranges = partition_key_ranges
            self.url_connection = "https://mock-test.documents.azure.com:443/"

        def _ReadPartitionKeyRanges(self, _collection_link: str, _feed_options: Optional[Mapping[str, Any]] = None, **kwargs):
            TestRoutingMapProvider._capture_internal_headers(kwargs, '"test-etag-1"')
            return self.partition_key_ranges

    def tearDown(self):
        from azure.cosmos._routing.routing_map_provider import _shared_routing_map_cache, _shared_cache_lock
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()

    def setUp(self):
        self.partition_key_ranges = [{u'id': u'0', u'minInclusive': u'', u'maxExclusive': u'05C1C9CD673398'},
                                     {u'id': u'1', u'minInclusive': u'05C1C9CD673398',
                                      u'maxExclusive': u'05C1D9CD673398'},
                                     {u'id': u'2', u'minInclusive': u'05C1D9CD673398',
                                      u'maxExclusive': u'05C1E399CD6732'},
                                     {u'id': u'3', u'minInclusive': u'05C1E399CD6732',
                                      u'maxExclusive': u'05C1E9CD673398'},
                                     {u'id': u'4', u'minInclusive': u'05C1E9CD673398', u'maxExclusive': u'FF'}]
        self.smart_routing_map_provider = self.instantiate_smart_routing_map_provider(self.partition_key_ranges)

        partitionRangeWithInfo = map(lambda r: (r, True), self.partition_key_ranges)
        self.cached_collection_routing_map = CollectionRoutingMap.CompleteRoutingMap(partitionRangeWithInfo,
                                                                                     'sample collection id')

    def instantiate_smart_routing_map_provider(self, partition_key_ranges):
        client = TestRoutingMapProvider.MockedCosmosClientConnection(partition_key_ranges)
        return SmartRoutingMapProvider(client)

    def test_full_range(self):
        # query range is the whole partition key range
        pkRange = routing_range.Range("", "FF", True, False)
        overlapping_partition_key_ranges = self.get_overlapping_ranges([pkRange])
        self.assertEqual(len(overlapping_partition_key_ranges), len(self.partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, self.partition_key_ranges)

        pkRange = routing_range.Range("", "FF", False, False)
        overlapping_partition_key_ranges = self.get_overlapping_ranges([pkRange])
        self.assertEqual(overlapping_partition_key_ranges, self.partition_key_ranges)
        self.assertEqual(self.cached_collection_routing_map.get_overlapping_ranges([pkRange]),
                         self.partition_key_ranges)

    def test_empty_ranges(self):
        # query range is the whole partition key range
        pkRange = routing_range.Range("", "FF", True, False)
        overlapping_partition_key_ranges = self.get_overlapping_ranges([pkRange])
        self.assertEqual(len(overlapping_partition_key_ranges), len(self.partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, self.partition_key_ranges)

        # query range list is empty
        overlapping_partition_key_ranges = self.get_overlapping_ranges([])
        self.assertEqual(len(overlapping_partition_key_ranges), 0)

        # validate the overlaping partition key ranges results for empty ranges is empty
        empty_start_range = routing_range.Range("", "", False, True)
        empty_end_range = routing_range.Range("FF", "FF", False, True)
        empty_range = routing_range.Range("AA", "AA", False, True)
        self.validate_empty_query_ranges([empty_range], [empty_start_range], [empty_end_range],
                                         [empty_start_range, empty_range], [empty_start_range, empty_end_range],
                                         [empty_range, empty_end_range],
                                         [empty_range, empty_range, empty_end_range])

    def test_bad_overlapping_query_ranges(self):
        # they share AA point
        r1 = routing_range.Range("", "AA", True, True)
        r2 = routing_range.Range("AA", "FF", True, False)

        def func_one_point_overlap():
            self.smart_routing_map_provider.get_overlapping_ranges("sample collection id", [r1, r2])

        self.assertRaises(ValueError, func_one_point_overlap)

        # overlapping range
        r1 = routing_range.Range("", "AB", True, False)
        r2 = routing_range.Range("AA", "FA", True, False)

        def func_overlap():
            self.smart_routing_map_provider.get_overlapping_ranges("sample collection id", [r1, r2])

        self.assertRaises(ValueError, func_overlap)

        r1 = routing_range.Range("AB", "AC", True, False)
        r1 = routing_range.Range("AA", "AB", True, False)

        def func_non_sorted():
            self.smart_routing_map_provider.get_overlapping_ranges("sample collection id", [r1, r2])

        self.assertRaises(ValueError, func_overlap)

    def test_empty_ranges_are_thrown_away(self):
        e1 = routing_range.Range("", "", True, False)
        r1 = routing_range.Range("", "AB", True, False)
        e2 = routing_range.Range("AB", "AB", True, False)
        r2 = routing_range.Range("AB", "AC", True, False)
        e3 = routing_range.Range("AC", "AC", True, False)
        e4 = routing_range.Range("AD", "AD", True, False)

        self.validate_overlapping_ranges_results([e1, r1, e2, r2, e3, e4], self.get_overlapping_ranges([r1, r2]))
        self.validate_against_cached_collection_results([e1, r1, e2, r2, e3, e4])

    def test_simple(self):
        r = routing_range.Range("AB", "AC", True, False)
        self.validate_against_cached_collection_results([r])

        ranges = [
            routing_range.Range("0000000040", "0000000045", True, False),
            routing_range.Range("0000000045", "0000000046", True, False),
            routing_range.Range("0000000046", "0000000050", True, False)
        ]
        self.validate_against_cached_collection_results(ranges)

    def test_simple_boundary(self):
        ranges = [

            routing_range.Range("05C1C9CD673398", "05C1D9CD673398", True, False),
        ]
        self.validate_against_cached_collection_results(ranges)
        self.validate_overlapping_ranges_results(ranges, self.partition_key_ranges[1:2])

    def test_two_adjacent_boundary(self):
        ranges = [
            # self.partition_key_ranges[1]
            routing_range.Range("05C1C9CD673398", "05C1D9CD673398", True, False),

            # self.partition_key_ranges[2]
            routing_range.Range("05C1D9CD673398", "05C1D9CD673399", True, False),
        ]
        self.validate_against_cached_collection_results(ranges)
        self.validate_overlapping_ranges_results(ranges, self.partition_key_ranges[1:3])

    def test_two_ranges_in_one_partition_key_range(self):
        # two ranges fall in the same partition key range
        ranges = [
            routing_range.Range("05C1C9CD673400", "05C1C9CD673401", True, False),
            routing_range.Range("05C1C9CD673402", "05C1C9CD673403", True, False),

        ]
        self.validate_against_cached_collection_results(ranges)
        self.validate_overlapping_ranges_results(ranges, self.partition_key_ranges[1:2])

    def test_complex(self):
        ranges = [
            # all are covered by self.partition_key_ranges[1]
            routing_range.Range("05C1C9CD673398", "05C1D9CD673391", True, False),
            routing_range.Range("05C1D9CD673391", "05C1D9CD673392", True, False),
            routing_range.Range("05C1D9CD673393", "05C1D9CD673395", True, False),
            routing_range.Range("05C1D9CD673395", "05C1D9CD673395", True, False),
            # all are covered by self.partition_key_ranges[4]]
            routing_range.Range("05C1E9CD673398", "05C1E9CD673401", True, False),
            routing_range.Range("05C1E9CD673402", "05C1E9CD673403", True, False),
            # empty range
            routing_range.Range("FF", "FF", True, False),
        ]
        self.validate_against_cached_collection_results(ranges)
        self.validate_overlapping_ranges_results(ranges, [self.partition_key_ranges[1], self.partition_key_ranges[4]])

    def validate_against_cached_collection_results(self, queryRanges):
        # validates the results of smart routing map provider against the results of cached collection map
        overlapping_partition_key_ranges = self.get_overlapping_ranges(queryRanges)
        self.assertEqual(overlapping_partition_key_ranges,
                         self.cached_collection_routing_map.get_overlapping_ranges(queryRanges))

    def validate_overlapping_ranges_results(self, queryRanges, expected_overlapping_partition_key_ranges):
        overlapping_partition_key_ranges = self.get_overlapping_ranges(queryRanges)
        self.assertEqual(overlapping_partition_key_ranges, expected_overlapping_partition_key_ranges)

    def validate_empty_query_ranges(self, *queryRangesList):
        for queryRanges in queryRangesList:
            self.validate_overlapping_ranges_results(queryRanges, [])

    def get_overlapping_ranges(self, queryRanges):
        return self.smart_routing_map_provider.get_overlapping_ranges("dbs/db/colls/container", queryRanges)

    def test_get_routing_map_caches_on_first_call(self):
        """Initial call to get_routing_map fetches from service and caches the result."""
        provider = PartitionKeyRangeCache(
            TestRoutingMapProvider.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"

        result = provider.get_routing_map(collection_link, feed_options={})

        self.assertIsNotNone(result)
        self.assertEqual(len(list(result._orderedPartitionKeyRanges)), 5)
        # Verify it's cached
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)
        self.assertIn(collection_id, provider._collection_routing_map_by_item)

    def test_fetch_routing_map_preserves_user_response_hook_and_internal_etag_capture(self):
        """User response_hook should still be invoked while internal header capture sets map ETag."""
        hook_calls = []
        expected_internal_etag = '"internal-etag"'

        class HookAwareClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProvider._capture_internal_headers(kwargs, expected_internal_etag)
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'ETag': '"user-hook-etag"'}, None)
                return self.partition_key_ranges

            def __init__(self, partition_key_ranges):
                self.partition_key_ranges = partition_key_ranges

        provider = PartitionKeyRangeCache(HookAwareClient(self.partition_key_ranges))
        collection_link = "dbs/db/colls/container"

        def user_hook(headers, _):
            hook_calls.append(headers.get('ETag'))

        result = provider.get_routing_map(collection_link, feed_options={}, response_hook=user_hook)

        self.assertIsNotNone(result)
        self.assertEqual(result.change_feed_etag, expected_internal_etag)
        self.assertEqual(hook_calls, ['"user-hook-etag"'])

    def test_get_routing_map_returns_cached_on_second_call(self):
        """Second call returns the same cached object without re-fetching."""
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"test-etag-1"')
                return original_ranges

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        result1 = provider.get_routing_map(collection_link, feed_options={})
        result2 = provider.get_routing_map(collection_link, feed_options={})

        self.assertIs(result1, result2, "Second call should return the exact same cached object")
        self.assertEqual(call_count['count'], 1, "Service should only be called once")

    def test_get_routing_map_force_refresh(self):
        """force_refresh=True causes a re-fetch even when cache is populated.

        The force_refresh path passes the previous routing map as the base for an
        incremental update. We simulate a split of range '0' into '5' and '6',
        so the incremental merge succeeds, resulting in 2 total service calls:
        1. Initial load
        2. Incremental update (force_refresh)
        """
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        # Simulate a split: range '0' splits into '5' and '6'
        split_ranges = [
            {'id': '5', 'minInclusive': '', 'maxExclusive': '05C1B9CD673398', 'parents': ['0']},
            {'id': '6', 'minInclusive': '05C1B9CD673398', 'maxExclusive': '05C1C9CD673398', 'parents': ['0']},
        ]

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')
                if call_count['count'] == 1:
                    return original_ranges
                return split_ranges

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        result1 = provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)

        result2 = provider.get_routing_map(
            collection_link, feed_options={},
            force_refresh=True, previous_routing_map=result1
        )
        self.assertEqual(call_count['count'], 2, "force_refresh should trigger one incremental fetch")
        self.assertIsNotNone(result2)
        # Verify the split was applied: should now have 6 ranges (original 5 minus '0' plus '5' and '6')
        self.assertEqual(len(list(result2._orderedPartitionKeyRanges)), 6)

    def test_is_cache_stale_etag_logic(self):
        """_is_cache_stale returns correct results for all ETag scenarios."""
        provider = PartitionKeyRangeCache(
            TestRoutingMapProvider.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # Populate cache
        cached_map = provider.get_routing_map(collection_link, feed_options={})

        # Case 1: None previous -> False
        self.assertFalse(provider._is_cache_stale(collection_id, None))

        # Case 2: Same ETag → True (stale)
        self.assertTrue(provider._is_cache_stale(collection_id, cached_map))

        # Case 3: Different ETag -> False (already refreshed by someone else)
        mock_map = MagicMock()
        mock_map.change_feed_etag = "completely-different-etag"
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map))

        # Case 4: Empty cache -> False
        provider._collection_routing_map_by_item.clear()
        mock_map2 = MagicMock()
        mock_map2.change_feed_etag = cached_map.change_feed_etag
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map2))

    def test_fetch_routing_map_full_load_with_incomplete_ranges_returns_none(self):
        """When a full load (previous_routing_map=None) returns gapped ranges, returns None immediately."""
        incomplete_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'}  # Gap from 80 to FF
        ]

        class IncompleteClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"incomplete-etag"')
                return incomplete_ranges

        provider = PartitionKeyRangeCache(IncompleteClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=None,
            feed_options={},
        )
        self.assertIsNone(result, "Should return None when full load produces incomplete ranges")

    def test_fetch_routing_map_incremental_with_parents(self):
        """Incremental update correctly merges child ranges that reference a parent."""
        # Build initial map with 2 ranges
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        # Simulate change feed returning children of range '0'
        delta_ranges = [
            {'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']},
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']}
        ]

        class DeltaClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"etag-2"')
                return delta_ranges

        provider = PartitionKeyRangeCache(DeltaClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result)
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3, "Should have 3 ranges: 2 children + 1 unchanged")
        self.assertEqual(ranges[0]['id'], '2')
        self.assertEqual(ranges[1]['id'], '3')
        self.assertEqual(ranges[2]['id'], '1')

    def test_fetch_routing_map_cleans_if_none_match_on_fallback(self):
        """When falling back from incremental to full load, stale IfNoneMatch is removed."""
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-old"'
        )

        captured_headers_list = []
        call_count = {'count': 0}
        full_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}
        ]

        class HeaderCapturingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                headers = kwargs.get('headers', {})
                captured_headers_list.append(headers.copy())
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                if call_count['count'] <= 2:
                    # Return a child with missing parent to force incremental retry,
                    # then full-load fallback.
                    return [{'id': '99', 'minInclusive': '', 'maxExclusive': 'FF', 'parents': ['MISSING']}]
                return full_ranges

        provider = PartitionKeyRangeCache(HeaderCapturingClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(captured_headers_list), 3)

        # First call (incremental) should have IfNoneMatch
        self.assertIn(http_constants.HttpHeaders.IfNoneMatch, captured_headers_list[0])

        # Second call is incremental retry, so it should still carry IfNoneMatch.
        self.assertIn(http_constants.HttpHeaders.IfNoneMatch, captured_headers_list[1])

        # Third call is full-load fallback and must clear stale IfNoneMatch.
        self.assertNotIn(http_constants.HttpHeaders.IfNoneMatch, captured_headers_list[2])

    def test_fetch_routing_map_merge_parents0_evicted_later_parent_cached(self):
        """Merge where parents[0] is an evicted grandparent but a later parent IS in cache.

        Scenario:
        - Range '1' split into '1A' and '1B' (SDK processed this earlier, evicted '1')
        - Cache has: {0, 1A, 1B, 2}
        - Now '1A' and '1B' merge into '3' with parents=['1', '1A', '1B']
        - parents[0]='1' is NOT in cache (evicted grandparent)
        - parents[1]='1A' IS in cache -> should find it and succeed incrementally
        """
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1A', 'minInclusive': '40', 'maxExclusive': '60'},
            {'id': '1B', 'minInclusive': '60', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-B"'
        )

        # Merge delta: '1A' and '1B' merge into '3', parents includes evicted '1'
        delta_ranges = [
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['1', '1A', '1B']}
        ]
        call_count = {'count': 0}

        class MergeClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"etag-C"')
                return delta_ranges

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result, "Should succeed incrementally — parents[1] is in cache")
        self.assertEqual(call_count['count'], 1, "Should only call service once (no fallback needed)")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3)
        ids = [r['id'] for r in ranges]
        self.assertEqual(ids, ['0', '3', '2'])

    def test_fetch_routing_map_merge_all_parents_cached(self):
        """Merge where all parents are in cache — validates first-match range_info inheritance.

        Scenario:
        - Cache has: {0, 1, 2} with distinct range_info values
        - Ranges '0' and '1' merge into '3' with parents=['0', '1']
        - Both '0' and '1' are in cache -> should pick '0' (first match) range_info
        """
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1', 'minInclusive': '40', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(initial_ranges[0], 'info_0'), (initial_ranges[1], 'info_1'), (initial_ranges[2], 'info_2')],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        delta_ranges = [
            {'id': '3', 'minInclusive': '', 'maxExclusive': '80', 'parents': ['0', '1']}
        ]

        class MergeClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"etag-2"')
                return delta_ranges

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result, "Should succeed incrementally with all parents in cache")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]['id'], '3')
        self.assertEqual(ranges[1]['id'], '2')
        # range_info should be inherited from the first cached parent ('0' → 'info_0')
        self.assertEqual(result._orderedPartitionInfo[0], 'info_0')
        # Stable range '2' should keep its original range_info
        self.assertEqual(result._orderedPartitionInfo[1], 'info_2')

    def test_fetch_routing_map_two_rapid_splits_all_parents_missing(self):
        """Two rapid splits where the intermediate range was never cached.

        Scenario:
        - SDK cache has: {0, 1, 2} with etag="etag-ANCIENT"
        - Meanwhile on the service:
          1. Range '1' split into '1A' and '1B'
          2. Range '1A' split again into '1A-i' and '1A-ii'
        - Delta returns '1A-i' with parents=['1A'], '1A-ii' with parents=['1A'], '1B' with parents=['1']
        - '1B' has parent '1' -> found in cache
        - '1A-i' has parent '1A' -> NOT found (intermediate, never cached) → falls back to full refresh

        This scenario validates that when none of a range's parents are in cache,
        the code correctly falls back to a full refresh.
        """
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1', 'minInclusive': '40', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-ANCIENT"'
        )

        call_count = {'count': 0}
        # Delta from two rapid splits: '1A' was intermediate (never cached)
        delta_ranges = [
            {'id': '1B', 'minInclusive': '60', 'maxExclusive': '80', 'parents': ['1']},
            {'id': '1A-i', 'minInclusive': '40', 'maxExclusive': '50', 'parents': ['1A']},
            {'id': '1A-ii', 'minInclusive': '50', 'maxExclusive': '60', 'parents': ['1A']}
        ]
        # Full refresh returns the final state
        full_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1A-i', 'minInclusive': '40', 'maxExclusive': '50'},
            {'id': '1A-ii', 'minInclusive': '50', 'maxExclusive': '60'},
            {'id': '1B', 'minInclusive': '60', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]

        class RapidSplitClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                if call_count['count'] == 1:
                    return delta_ranges
                return full_ranges

        provider = PartitionKeyRangeCache(RapidSplitClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result, "Should succeed via full refresh fallback")
        self.assertEqual(
            call_count['count'],
            3,
            "Should call service three times (incremental + incremental retry + full fallback)",
        )
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 5)
        ids = [r['id'] for r in ranges]
        self.assertEqual(ids, ['0', '1A-i', '1A-ii', '1B', '2'])

    def test_fetch_routing_map_merge_range_info_from_correct_parent(self):
        """Verifies range_info is inherited from the first CACHED parent, not necessarily parents[0].

        Scenario:
        - Cache has: {0, 1A, 1B, 2} with range_info='info_1A' for '1A' and 'info_1B' for '1B'
        - Merge: '1A' and '1B' into '3' with parents=['1', '1A', '1B']
        - parents[0]='1' not in cache, parents[1]='1A' is in cache
        - range_info should be 'info_1A' (from '1A', the first cached parent)
        """
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1A', 'minInclusive': '40', 'maxExclusive': '60'},
            {'id': '1B', 'minInclusive': '60', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(initial_ranges[0], 'info_0'),
             (initial_ranges[1], 'info_1A'),
             (initial_ranges[2], 'info_1B'),
             (initial_ranges[3], 'info_2')],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        delta_ranges = [
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['1', '1A', '1B']}
        ]

        class MergeClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProvider._capture_internal_headers(kwargs, '"etag-2"')
                return delta_ranges

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=initial_map,
            feed_options={}
        )

        self.assertIsNotNone(result)
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3)
        self.assertEqual(ranges[0]['id'], '0')
        self.assertEqual(ranges[1]['id'], '3')
        self.assertEqual(ranges[2]['id'], '2')
        # range_info for '3' should come from '1A' (first cached parent), not '1' (evicted)
        self.assertEqual(result._orderedPartitionInfo[1], 'info_1A')

    def test_force_refresh_without_previous_map_triggers_targeted_fetch(self):
        """force_refresh=True without previous_routing_map should still trigger a targeted fetch.

        This guards the 410 path where collection_link is known but previous_routing_map
        is not available. The refresh must not become a no-op when cache already exists.
        """
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')
                return original_ranges

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        # Initial load
        result1 = provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)
        self.assertIsNotNone(result1)

        # force_refresh=True without previous_routing_map should still fetch once.
        result2 = provider.get_routing_map(
            collection_link, feed_options={},
            force_refresh=True
        )
        self.assertEqual(call_count['count'], 2, "force_refresh=True without previous_routing_map should trigger fetch")
        self.assertIsNotNone(result2)

    def test_concurrent_refresh_serialized_by_lock(self):
        """Under concurrent force_refresh calls, the per-collection lock serializes refreshes.

        Verifies that threads don't corrupt the cache and all get a valid result.
        With `and`, only the first thread that finds the cache stale actually fetches.
        Subsequent threads see the updated ETag and skip the redundant fetch.
        """
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges
        fetch_event = threading.Event()

        class SlowCountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                # Simulate a slow service call to widen the contention window
                fetch_event.wait(timeout=2)
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')
                return original_ranges

        provider = PartitionKeyRangeCache(SlowCountingClient())
        collection_link = "dbs/db/colls/container"

        # Populate cache with initial map
        fetch_event.set()  # Let the initial load go fast
        initial_map = provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)
        fetch_event.clear()  # Now make subsequent fetches slow

        results = [None] * 5
        errors = []

        def thread_fn(idx):
            try:
                results[idx] = provider.get_routing_map(
                    collection_link, feed_options={},
                    force_refresh=True, previous_routing_map=initial_map
                )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=thread_fn, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()

        # Give threads time to all start and contend on the lock
        import time
        time.sleep(0.2)
        # Release the slow fetch
        fetch_event.set()

        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Threads raised errors: {errors}")
        # All threads should get a non-None result
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Thread {i} got None")

    def test_cache_never_none_during_refresh(self):
        """Fast-path readers should never see None in the cache during a refresh.

        The cache entry is atomically replaced, never deleted. This test verifies
        that concurrent readers always see either the old valid map or the new valid map.
        """
        original_ranges = self.partition_key_ranges
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                import time
                time.sleep(0.1)  # Simulate network delay
                TestRoutingMapProvider._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                return original_ranges

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # Populate cache
        initial_map = provider.get_routing_map(collection_link, feed_options={})
        self.assertIsNotNone(initial_map)

        none_seen = {'count': 0}
        stop_event = threading.Event()

        def reader_fn():
            """Continuously reads the cache and checks it's never None."""
            while not stop_event.is_set():
                cached = provider._collection_routing_map_by_item.get(collection_id)
                if cached is None:
                    none_seen['count'] += 1

        def refresher_fn():
            """Triggers a force refresh."""
            provider.get_routing_map(
                collection_link, feed_options={},
                force_refresh=True, previous_routing_map=initial_map
            )

        reader = threading.Thread(target=reader_fn)
        refresher = threading.Thread(target=refresher_fn)

        reader.start()
        refresher.start()
        refresher.join(timeout=10)
        stop_event.set()
        reader.join(timeout=5)

        self.assertEqual(none_seen['count'], 0,
                         "Cache entry should never be None during a refresh — it should be atomically replaced")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
