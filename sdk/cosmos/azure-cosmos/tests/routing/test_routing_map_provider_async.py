# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest

from azure.cosmos._routing import routing_range as routing_range
from azure.cosmos._routing.aio.routing_map_provider import CollectionRoutingMap
from azure.cosmos._routing.aio.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos import http_constants

from typing import Optional, Mapping, Any
from unittest.mock import MagicMock


@pytest.mark.cosmosEmulator
class TestRoutingMapProviderAsync(unittest.IsolatedAsyncioTestCase):
    """Async unit tests for PartitionKeyRangeCache and SmartRoutingMapProvider.
    """

    @staticmethod
    def _capture_internal_headers(kwargs, etag):
        captured_headers = kwargs.get('_internal_response_headers_capture')
        if captured_headers is not None:
            captured_headers.clear()
            captured_headers.update({'ETag': etag})

    class MockedCosmosClientConnection(object):
        """Mock that returns partition key ranges as an async generator."""

        def __init__(self, partition_key_ranges):
            self.partition_key_ranges = partition_key_ranges
            self.url_connection = "https://mock-async-test.documents.azure.com:443/"

        def _ReadPartitionKeyRanges(self, _collection_link: str,
                                    _feed_options: Optional[Mapping[str, Any]] = None, **kwargs):
            TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"test-etag-1"')

            ranges = self.partition_key_ranges

            async def _gen():
                for r in ranges:
                    yield r

            return _gen()

    def tearDown(self):
        from azure.cosmos._routing.aio.routing_map_provider import _shared_routing_map_cache, _shared_cache_lock
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()

    def setUp(self):
        self.partition_key_ranges = [
            {u'id': u'0', u'minInclusive': u'', u'maxExclusive': u'05C1C9CD673398'},
            {u'id': u'1', u'minInclusive': u'05C1C9CD673398', u'maxExclusive': u'05C1D9CD673398'},
            {u'id': u'2', u'minInclusive': u'05C1D9CD673398', u'maxExclusive': u'05C1E399CD6732'},
            {u'id': u'3', u'minInclusive': u'05C1E399CD6732', u'maxExclusive': u'05C1E9CD673398'},
            {u'id': u'4', u'minInclusive': u'05C1E9CD673398', u'maxExclusive': u'FF'},
        ]
        self.smart_routing_map_provider = self._instantiate_smart_routing_map_provider(self.partition_key_ranges)

        partitionRangeWithInfo = [(r, True) for r in self.partition_key_ranges]
        self.cached_collection_routing_map = CollectionRoutingMap.CompleteRoutingMap(
            partitionRangeWithInfo, 'sample collection id'
        )

    def _instantiate_smart_routing_map_provider(self, partition_key_ranges):
        client = TestRoutingMapProviderAsync.MockedCosmosClientConnection(partition_key_ranges)
        return SmartRoutingMapProvider(client)

    # ---------------------------------------------------------------
    # SmartRoutingMapProvider.get_overlapping_ranges tests
    # ---------------------------------------------------------------

    async def test_full_range_async(self):
        pkRange = routing_range.Range("", "FF", True, False)
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", [pkRange])
        self.assertEqual(len(overlapping), len(self.partition_key_ranges))
        self.assertEqual(overlapping, self.partition_key_ranges)

    async def test_empty_ranges_async(self):
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", [])
        self.assertEqual(len(overlapping), 0)

    async def test_bad_overlapping_query_ranges_async(self):
        r1 = routing_range.Range("", "AA", True, True)
        r2 = routing_range.Range("AA", "FF", True, False)
        with self.assertRaises(ValueError):
            await self.smart_routing_map_provider.get_overlapping_ranges(
                "sample collection id", [r1, r2])

    async def test_empty_ranges_are_thrown_away_async(self):
        e1 = routing_range.Range("", "", True, False)
        r1 = routing_range.Range("", "AB", True, False)
        e2 = routing_range.Range("AB", "AB", True, False)
        r2 = routing_range.Range("AB", "AC", True, False)
        e3 = routing_range.Range("AC", "AC", True, False)
        e4 = routing_range.Range("AD", "AD", True, False)

        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", [r1, r2])
        overlapping_all = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", [e1, r1, e2, r2, e3, e4])
        self.assertEqual(overlapping_all, overlapping)
        self.assertEqual(overlapping_all,
                         self.cached_collection_routing_map.get_overlapping_ranges([e1, r1, e2, r2, e3, e4]))

    async def test_simple_async(self):
        r = routing_range.Range("AB", "AC", True, False)
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", [r])
        self.assertEqual(overlapping, self.cached_collection_routing_map.get_overlapping_ranges([r]))

    async def test_simple_boundary_async(self):
        ranges = [
            routing_range.Range("05C1C9CD673398", "05C1D9CD673398", True, False),
        ]
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", ranges)
        self.assertEqual(overlapping,
                         self.cached_collection_routing_map.get_overlapping_ranges(ranges))
        self.assertEqual(overlapping, self.partition_key_ranges[1:2])

    async def test_two_adjacent_boundary_async(self):
        ranges = [
            # self.partition_key_ranges[1]
            routing_range.Range("05C1C9CD673398", "05C1D9CD673398", True, False),
            # self.partition_key_ranges[2]
            routing_range.Range("05C1D9CD673398", "05C1D9CD673399", True, False),
        ]
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", ranges)
        self.assertEqual(overlapping,
                         self.cached_collection_routing_map.get_overlapping_ranges(ranges))
        self.assertEqual(overlapping, self.partition_key_ranges[1:3])

    async def test_two_ranges_in_one_partition_key_range_async(self):
        # two ranges fall in the same partition key range
        ranges = [
            routing_range.Range("05C1C9CD673400", "05C1C9CD673401", True, False),
            routing_range.Range("05C1C9CD673402", "05C1C9CD673403", True, False),
        ]
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", ranges)
        self.assertEqual(overlapping,
                         self.cached_collection_routing_map.get_overlapping_ranges(ranges))
        self.assertEqual(overlapping, self.partition_key_ranges[1:2])

    async def test_complex_async(self):
        ranges = [
            routing_range.Range("05C1C9CD673398", "05C1D9CD673391", True, False),
            routing_range.Range("05C1D9CD673391", "05C1D9CD673392", True, False),
            routing_range.Range("05C1D9CD673393", "05C1D9CD673395", True, False),
            routing_range.Range("05C1D9CD673395", "05C1D9CD673395", True, False),
            routing_range.Range("05C1E9CD673398", "05C1E9CD673401", True, False),
            routing_range.Range("05C1E9CD673402", "05C1E9CD673403", True, False),
            routing_range.Range("FF", "FF", True, False),
        ]
        overlapping = await self.smart_routing_map_provider.get_overlapping_ranges(
            "dbs/db/colls/container", ranges)
        expected = [self.partition_key_ranges[1], self.partition_key_ranges[4]]
        self.assertEqual(overlapping, expected)

    # ---------------------------------------------------------------
    # PartitionKeyRangeCache(async) caching tests
    # ---------------------------------------------------------------

    async def test_get_routing_map_caches_on_first_call_async(self):
        """Initial call to get_routing_map fetches from service and caches the result."""
        provider = PartitionKeyRangeCache(
            TestRoutingMapProviderAsync.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"

        result = await provider.get_routing_map(collection_link, feed_options={})

        self.assertIsNotNone(result)
        self.assertEqual(len(list(result._orderedPartitionKeyRanges)), 5)
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)
        self.assertIn(collection_id, provider._collection_routing_map_by_item)

    async def test_fetch_routing_map_preserves_user_response_hook_and_internal_etag_capture_async(self):
        """User response_hook should still fire while internal header capture sets map ETag."""
        hook_calls = []
        expected_internal_etag = '"internal-etag"'

        class HookAwareClient:
            def __init__(self, partition_key_ranges):
                self.partition_key_ranges = partition_key_ranges

            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, expected_internal_etag)
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'ETag': '"user-hook-etag"'}, None)

                async def _gen():
                    for r in self.partition_key_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(HookAwareClient(self.partition_key_ranges))
        collection_link = "dbs/db/colls/container"

        def user_hook(headers, _):
            hook_calls.append(headers.get('ETag'))

        result = await provider.get_routing_map(collection_link, feed_options={}, response_hook=user_hook)

        self.assertIsNotNone(result)
        self.assertEqual(result.change_feed_etag, expected_internal_etag)
        self.assertEqual(hook_calls, ['"user-hook-etag"'])

    async def test_get_routing_map_returns_cached_on_second_call_async(self):
        """Second call returns the same cached object without re-fetching."""
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"test-etag-1"')

                async def _gen():
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        result1 = await provider.get_routing_map(collection_link, feed_options={})
        result2 = await provider.get_routing_map(collection_link, feed_options={})

        self.assertIs(result1, result2, "Second call should return the exact same cached object")
        self.assertEqual(call_count['count'], 1, "Service should only be called once")

    async def test_get_routing_map_force_refresh_async(self):
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
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')

                data = original_ranges if call_count['count'] == 1 else split_ranges

                async def _gen():
                    for r in data:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        result1 = await provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)

        result2 = await provider.get_routing_map(
            collection_link, feed_options={},
            force_refresh=True, previous_routing_map=result1
        )
        self.assertEqual(call_count['count'], 2, "force_refresh should trigger one incremental fetch")
        self.assertIsNotNone(result2)
        # Verify the split was applied: should now have 6 ranges (original 5 minus '0' plus '5' and '6')
        self.assertEqual(len(list(result2._orderedPartitionKeyRanges)), 6)

    async def test_is_cache_stale_etag_logic_async(self):
        """_is_cache_stale returns correct results for all ETag scenarios."""
        provider = PartitionKeyRangeCache(
            TestRoutingMapProviderAsync.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        cached_map = await provider.get_routing_map(collection_link, feed_options={})

        # Case 1: None previous -> False
        self.assertFalse(provider._is_cache_stale(collection_id, None))

        # Case 2: Same ETag -> True (stale)
        self.assertTrue(provider._is_cache_stale(collection_id, cached_map))

        # Case 3: Different ETag -> False (already refreshed)
        mock_map = MagicMock()
        mock_map.change_feed_etag = "completely-different-etag"
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map))

        # Case 4: Empty cache -> False
        provider._collection_routing_map_by_item.clear()
        mock_map2 = MagicMock()
        mock_map2.change_feed_etag = cached_map.change_feed_etag
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map2))

    async def test_fetch_routing_map_full_load_with_incomplete_ranges_returns_none_async(self):
        """When a full load (previous_routing_map=None) returns gapped ranges, returns None immediately."""
        incomplete_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'}  # Gap from 80 to FF
        ]

        class IncompleteClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"incomplete-etag"')

                async def _gen():
                    for r in incomplete_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(IncompleteClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
            collection_link=collection_link,
            collection_id=collection_id,
            previous_routing_map=None,
            feed_options={},
        )
        self.assertIsNone(result, "Should return None when full load produces incomplete ranges")

    async def test_fetch_routing_map_incremental_with_parents_async(self):
        """Incremental update correctly merges child ranges that reference a parent."""
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        delta_ranges = [
            {'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']},
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']}
        ]

        class DeltaClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"etag-2"')

                async def _gen():
                    for r in delta_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(DeltaClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_fetch_routing_map_cleans_if_none_match_on_fallback_async(self):
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
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                data = ([{'id': '99', 'minInclusive': '', 'maxExclusive': 'FF',
                          'parents': ['MISSING']}] if call_count['count'] <= 2 else full_ranges)

                async def _gen():
                    for r in data:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(HeaderCapturingClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_fetch_routing_map_merge_parents0_evicted_later_parent_cached_async(self):
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

        delta_ranges = [
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['1', '1A', '1B']}
        ]
        call_count = {'count': 0}

        class MergeClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"etag-C"')

                async def _gen():
                    for r in delta_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_fetch_routing_map_merge_all_parents_cached_async(self):
        """Merge where all parents are in cache — validates first-match range_info inheritance.

        Scenario:
        - Cache has: {0, 1, 2} with distinct range_info values
        - Ranges '0' and '1' merge into '3' with parents=['0', '1']
        - Both '0' and '1' are in cache → should pick '0' (first match) range_info
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
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"etag-2"')

                async def _gen():
                    for r in delta_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_fetch_routing_map_two_rapid_splits_all_parents_missing_async(self):
        """Two rapid splits where the intermediate range was never cached.

        Scenario:
        - SDK cache has: {0, 1, 2} with etag="etag-ANCIENT"
        - Meanwhile on the service:
          1. Range '1' split into '1A' and '1B'
          2. Range '1A' split again into '1A-i' and '1A-ii'
        - Delta returns '1A-i' with parents=['1A'], '1A-ii' with parents=['1A'], '1B' with parents=['1']
        - '1B' has parent '1' -> found in cache
        - '1A-i' has parent '1A' -> NOT found (intermediate, never cached) → falls back to full refresh
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
        delta_ranges = [
            {'id': '1B', 'minInclusive': '60', 'maxExclusive': '80', 'parents': ['1']},
            {'id': '1A-i', 'minInclusive': '40', 'maxExclusive': '50', 'parents': ['1A']},
            {'id': '1A-ii', 'minInclusive': '50', 'maxExclusive': '60', 'parents': ['1A']}
        ]
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
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                data = delta_ranges if call_count['count'] == 1 else full_ranges

                async def _gen():
                    for r in data:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(RapidSplitClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_fetch_routing_map_merge_range_info_from_correct_parent_async(self):
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
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"etag-2"')

                async def _gen():
                    for r in delta_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(MergeClient())
        from azure.cosmos import _base
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        result = await provider._fetch_routing_map(
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

    async def test_force_refresh_without_previous_map_triggers_targeted_fetch_async(self):
        """force_refresh=True without previous_routing_map should still trigger a targeted fetch.

        This guards the 410 path where collection_link is known but previous_routing_map
        is not available. The refresh must not become a no-op when cache already exists.
        """
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')

                async def _gen():
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(CountingClient())
        collection_link = "dbs/db/colls/container"

        # Initial load
        result1 = await provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)
        self.assertIsNotNone(result1)

        # force_refresh=True without previous_routing_map should still fetch once.
        result2 = await provider.get_routing_map(
            collection_link, feed_options={},
            force_refresh=True
        )
        self.assertEqual(call_count['count'], 2, "force_refresh=True without previous_routing_map should trigger fetch")
        self.assertIsNotNone(result2)

    async def test_concurrent_refresh_serialized_by_lock_async(self):
        """Under concurrent force_refresh calls, the per-collection lock serializes refreshes.

        Verifies that coroutines don't corrupt the cache and all get a valid result.
        """
        import asyncio
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges
        fetch_event = asyncio.Event()

        class SlowCountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    await fetch_event.wait()
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"test-etag-{call_count["count"]}"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowCountingClient())
        collection_link = "dbs/db/colls/container"

        # Populate cache with initial map (let it go fast)
        fetch_event.set()
        initial_map = await provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)
        fetch_event.clear()

        async def refresh_fn():
            return await provider.get_routing_map(
                collection_link, feed_options={},
                force_refresh=True, previous_routing_map=initial_map
            )

        # Launch 5 concurrent refresh coroutines
        tasks = [asyncio.create_task(refresh_fn()) for _ in range(5)]

        await asyncio.sleep(0.1)
        fetch_event.set()

        results = await asyncio.gather(*tasks)

        # All coroutines should get a non-None result
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Coroutine {i} got None")

    async def test_cache_never_none_during_refresh_async(self):
        """Fast-path readers should never see None in the cache during a refresh.

        The cache entry is atomically replaced, never deleted.
        """
        import asyncio
        original_ranges = self.partition_key_ranges
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    await asyncio.sleep(0.05)
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # Populate cache
        initial_map = await provider.get_routing_map(collection_link, feed_options={})
        self.assertIsNotNone(initial_map)

        none_seen = {'count': 0}
        stop_event = asyncio.Event()

        async def reader_fn():
            while not stop_event.is_set():
                cached = provider._collection_routing_map_by_item.get(collection_id)
                if cached is None:
                    none_seen['count'] += 1
                await asyncio.sleep(0)

        async def refresher_fn():
            await provider.get_routing_map(
                collection_link, feed_options={},
                force_refresh=True, previous_routing_map=initial_map
            )

        reader_task = asyncio.create_task(reader_fn())
        await refresher_fn()
        stop_event.set()
        await reader_task

        self.assertEqual(none_seen['count'], 0,
                         "Cache entry should never be None during a refresh — it should be atomically replaced")


if __name__ == "__main__":
    unittest.main()
