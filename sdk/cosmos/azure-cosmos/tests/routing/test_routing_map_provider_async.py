# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio  # pylint: disable=do-not-import-asyncio
import unittest

import pytest

from azure.cosmos import _base, http_constants
from azure.cosmos._routing import routing_range as routing_range
from azure.cosmos._routing.aio.routing_map_provider import CollectionRoutingMap
from azure.cosmos._routing.aio.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos.exceptions import CosmosHttpResponseError

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
        from azure.cosmos._routing.aio.routing_map_provider import (
            _shared_routing_map_cache,
            _shared_inflight_fetches,
            _shared_cache_lock,
        )
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()
            _shared_inflight_fetches.clear()

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
        # The cache uses a small per-collection lock to make sure that even
        # under concurrent `force_refresh=True` storms (e.g. lots of 410
        # responses arriving at once), the cache state stays consistent and
        # no caller gets back garbage.
        #
        # We do not assert that exactly one fetch happens — the production
        # code allows the first refresh to populate, and subsequent contending
        # refreshes may either skip (if they see the new ETag) or proceed.
        # The contract this test pins down is the weaker but essential one:
        # nothing crashes, nothing corrupts, and every caller gets back a
        # valid routing map.
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges
        # A gate so we can force contention: refreshes will all pile up
        # waiting here, then we open the gate and let them race.
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

        # === Step 1: populate the cache with a known initial map. Let the
        # gate be open so this initial load isn't slow.
        fetch_event.set()
        initial_map = await provider.get_routing_map(collection_link, feed_options={})
        self.assertEqual(call_count['count'], 1)
        # === Step 2: close the gate so subsequent fetches will block,
        # giving the concurrent callers time to all queue up.
        fetch_event.clear()

        async def refresh_fn():
            return await provider.get_routing_map(
                collection_link, feed_options={},
                force_refresh=True, previous_routing_map=initial_map
            )

        # === Step 3: launch 5 concurrent refresh coroutines. With the gate
        # closed, they'll all pile up at the lock and/or the fetch event.
        tasks = [asyncio.create_task(refresh_fn()) for _ in range(5)]

        # Yield so they all reach their parked state before we release.
        await asyncio.sleep(0.1)
        # Now open the gate and let them all proceed.
        fetch_event.set()

        results = await asyncio.gather(*tasks)

        # === Step 4: contract — every coroutine got back a non-None result.
        # Concurrency didn't corrupt anyone's view of the cache.
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Coroutine {i} got None")

    async def test_cache_never_none_during_refresh_async(self):
        """Fast-path readers should never see None in the cache during a refresh.

        The cache entry is atomically replaced, never deleted.
        """
        # Important property for fast-path readers: the cache slot is
        # ALWAYS either the old map or the new map — it is never
        # transiently set to None while a refresh is in flight.
        #
        # If the refresh code did `del cache[key]; cache[key] = new_map`,
        # there would be a window where a concurrent fast-path reader could
        # observe `None` and incorrectly conclude the cache is cold, which
        # would trigger a redundant fetch storm. The fix uses atomic
        # replacement, so readers always see a valid map.
        #
        # We verify this by spinning a reader coroutine that polls the
        # cache slot continuously while a refresh runs, and asserting it
        # never once observed None.
        original_ranges = self.partition_key_ranges
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    # A small artificial delay so the refresher is provably
                    # in flight while the reader is polling.
                    await asyncio.sleep(0.05)
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, f'"etag-{call_count["count"]}"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # === Step 1: populate the cache so the reader has something
        # non-None to observe between refresh windows.
        initial_map = await provider.get_routing_map(collection_link, feed_options={})
        self.assertIsNotNone(initial_map)

        # === Step 2: set up the reader. It polls the cache as fast as the
        # loop will let it, counting any None observations as failures.
        none_seen = {'count': 0}
        stop_event = asyncio.Event()

        async def reader_fn():
            while not stop_event.is_set():
                cached = provider._collection_routing_map_by_item.get(collection_id)
                if cached is None:
                    none_seen['count'] += 1
                # Yield so this loop doesn't monopolise the event loop.
                await asyncio.sleep(0)

        async def refresher_fn():
            await provider.get_routing_map(
                collection_link, feed_options={},
                force_refresh=True, previous_routing_map=initial_map
            )

        # === Step 3: start the reader, then do the refresh, then stop the reader.
        reader_task = asyncio.create_task(reader_fn())
        await refresher_fn()
        stop_event.set()
        await reader_task

        # === Step 4: contract — the reader saw the slot transition from
        # old map to new map without ever observing a None intermediate.
        self.assertEqual(none_seen['count'], 0,
                         "Cache entry should never be None during a refresh — it should be atomically replaced")

    async def test_cache_populated_when_originating_caller_is_cancelled_async(self):
        """Cancelling the originating caller mid-fetch must NOT prevent the cache write.

        Reproduces the failure mode where a customer's ``asyncio.wait_for``
        deadline expires while the routing-map fetch is in flight. The fetch
        task runs independently of the caller, owns the cache assignment, and
        completes successfully so the cache ends up populated.
        """
        # The bug this test pins down: in the old code, the routing-map fetch
        # ran on the customer's call stack. If the customer wrapped their call
        # in `asyncio.wait_for(..., timeout=2)` and the timeout fired mid-fetch,
        # the CancelledError tore down the fetch, skipped the cache-write line
        # that lived right after the `await`, and the cache stayed empty. Every
        # retry repeated the same doomed sequence.
        #
        # The fix: move the fetch + cache-write into a shared task per
        # collection, and have callers wait on it through `asyncio.shield`. Now
        # when the caller is cancelled, only the *waiter* unwinds — the task
        # itself keeps running on the event loop, finishes the fetch, and
        # writes the result into the cache before returning.
        #
        # This test reproduces the cancellation, then verifies the cache *does*
        # get populated once the gated fetch completes — even though nobody is
        # awaiting it anymore.
        original_ranges = self.partition_key_ranges
        # A gate we control: the fetch will block here until we set the event.
        # This lets us guarantee the fetch is still in flight at the moment
        # the customer's deadline fires.
        fetch_gate = asyncio.Event()
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    # Park here — simulates a slow HTTP round trip the customer
                    # won't wait long enough for.
                    await fetch_gate.wait()
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"slow-etag"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # === Step 1: customer's wait_for fires before the fetch can complete.
        # Without the fix this is where the publish would be lost forever.
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(
                provider.get_routing_map(collection_link, feed_options={}),
                timeout=0.05,
            )

        # === Step 2: at this instant the cache MUST still be empty.
        # The fetch is gated — it hasn't run to completion yet, so the
        # in-flight task hasn't had a chance to write to the cache. If anything
        # were in the cache here it would mean the fetch shortcut something,
        # and the test wouldn't actually be exercising the fix.
        self.assertIsNone(provider._collection_routing_map_by_item.get(collection_id))

        # === Step 3: let the gated fetch complete.
        # The originating caller is long gone (raised TimeoutError above), but
        # the shared task is still alive on the event loop. We open the gate
        # so it can finish its work, then poll until the cache slot fills in.
        fetch_gate.set()
        for _ in range(100):
            if provider._collection_routing_map_by_item.get(collection_id) is not None:
                break
            await asyncio.sleep(0.01)

        # === Step 4: cache must now be populated — this is the fix in action.
        # Even though the caller that triggered the fetch was cancelled, the
        # task survived, the publish ran inside the task, and the routing map
        # made it into the cache.
        populated = provider._collection_routing_map_by_item.get(collection_id)
        self.assertIsNotNone(populated,
                             "Cache must be populated after the gated fetch completes")
        self.assertEqual(len(list(populated._orderedPartitionKeyRanges)), len(original_ranges))
        self.assertEqual(call_count['count'], 1,
                         "Exactly one fetch should have been issued")

        # === Step 5: the customer's retry now hits a populated cache.
        # No new HTTP fetch. The whole point of the fix — the second attempt
        # gets the work that the first attempt's fetch finished after timeout.
        result = await provider.get_routing_map(collection_link, feed_options={})
        self.assertIs(result, populated)
        self.assertEqual(call_count['count'], 1)

    async def test_cache_populated_when_cancelled_with_timeout_kwarg_async(self):
        """Caller cancellation + timeout kwarg still results in cache population."""
        # This is the previous test's companion. It pins down the same fix
        # behaviour (cache must still populate after the originating caller is
        # cancelled) but covers the case where the customer *also* passed a
        # `timeout=N` keyword argument — i.e. both timeout mechanisms are in
        # play at once:
        #
        #   - the asyncio cancellation (from wait_for), AND
        #   - the kwargs timeout (a plain Python kwarg the HTTP layer reads).
        #
        # The kwargs timeout still gets forwarded to the underlying call (we
        # verify the mock saw it). The point is that even in this combined
        # scenario, the shared-task fix still wins: the task keeps
        # running after the caller times out, finishes the fetch, and the
        # cache ends up populated.
        original_ranges = self.partition_key_ranges
        fetch_gate = asyncio.Event()
        call_count = {'count': 0}
        # We capture the timeout the mock client actually saw, to prove the
        # kwargs path is intact end-to-end (not silently dropped before reaching
        # the underlying read).
        seen_timeout_kwarg = {'value': None}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                # Record what the cache layer actually forwarded.
                seen_timeout_kwarg['value'] = kwargs.get('timeout')

                async def _gen():
                    # Gate again — fetch won't complete until we say so.
                    await fetch_gate.wait()
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"slow-timeout-etag"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # === Step 1: customer call dies via wait_for cancellation.
        # Note both timeouts are present: the inner kwargs `timeout=0.001`
        # (which the cache forwards to the mock) AND the outer
        # `wait_for(..., timeout=0.05)` that asynchronously cancels the caller.
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(
                provider.get_routing_map(collection_link, feed_options={}, timeout=0.001),
                timeout=0.05,
            )

        # Sanity-check: the cache layer really did forward the kwargs timeout
        # down to the underlying read. If this is None it means the kwargs
        # path is broken, regardless of whether the cache populates.
        self.assertEqual(seen_timeout_kwarg['value'], 0.001)
        # Cache still empty — fetch is gated, hasn't published yet.
        self.assertIsNone(provider._collection_routing_map_by_item.get(collection_id))

        # === Step 2: let the gated fetch finish, then poll.
        fetch_gate.set()
        for _ in range(100):
            if provider._collection_routing_map_by_item.get(collection_id) is not None:
                break
            await asyncio.sleep(0.01)

        # === Step 3: cache must be populated. Same property as the previous
        # test — the orphaned task lived past the caller's cancellation.
        populated = provider._collection_routing_map_by_item.get(collection_id)
        self.assertIsNotNone(populated)
        self.assertEqual(call_count['count'], 1)

        # === Step 4: retry hits the populated cache, no second fetch.
        result = await provider.get_routing_map(collection_link, feed_options={})
        self.assertIs(result, populated)
        self.assertEqual(call_count['count'], 1)

    async def test_concurrent_cold_cache_callers_share_a_single_fetch_async(self):
        """Concurrent cold-cache callers must coalesce onto one fetch task."""
        # This pins down the "one shared task per container, not one per
        # caller" property. The bug it guards against: if every
        # cold-cache caller spawned its own fetch task, 10 simultaneous
        # callers would each fire their own HTTP request at the gateway — a
        # gateway-side stampede.
        #
        # The fix uses an in-flight-fetches dict: the first caller creates the
        # task and stores it; later callers find it there and join the same
        # task instead of starting a new one.
        #
        # We verify both halves of the property:
        #   1. The mock is called exactly ONCE even though 10 callers arrived
        #      cold and concurrently.
        #   2. All 10 callers receive the SAME routing-map object (proving
        #      they really joined one task, didn't each get their own copy).
        original_ranges = self.partition_key_ranges
        # Gate the fetch so all 10 callers have time to arrive and join the
        # in-flight task before any of them can succeed. Without the gate,
        # the first caller might finish so quickly that the others arrive
        # AFTER the task is done — which would be a different (cache-hit)
        # code path, not the shared-task path we're testing here.
        fetch_gate = asyncio.Event()
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    await fetch_gate.wait()
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"shared-etag"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"

        async def caller():
            return await provider.get_routing_map(collection_link, feed_options={})

        # Fire all 10 callers as concurrent tasks. Each one independently
        # finds the cache empty and goes down the slow path; the in-flight
        # dict is what makes them coalesce.
        tasks = [asyncio.create_task(caller()) for _ in range(10)]
        # Yield so every caller has a chance to enter the slow path and
        # either create the in-flight task (one of them) or find it and
        # join (the other nine). Without this yield we'd race the
        # gate-set below and might not get the contention we're testing.
        await asyncio.sleep(0.05)
        # Now let the (single) fetch complete.
        fetch_gate.set()
        results = await asyncio.gather(*tasks)

        # Critical assertion: the mock was called ONCE, not 10 times.
        # This is the whole point of the in-flight dict.
        self.assertEqual(call_count['count'], 1,
                         "All 10 concurrent cold-cache callers should share one fetch")
        # And every caller got the same object back — proving they all
        # awaited the same shared task, not 10 separately-scheduled fetches
        # that happened to return equivalent data.
        first = results[0]
        self.assertIsNotNone(first)
        for r in results[1:]:
            self.assertIs(r, first, "All callers should observe the same routing map object")

    async def test_waiter_joining_after_originator_cancelled_gets_result_async(self):
        """A waiter that joins after the originating caller is cancelled still receives the fetched map."""
        # The trickiest property of the shared-task fix: the originating caller
        # (the one who created the in-flight task) can be cancelled at any
        # point, but a *later* caller arriving while the fetch is still
        # running must successfully join that same task and receive its
        # result. The cancellation of the originator can't take the task
        # down with it (that's what `asyncio.shield` guarantees).
        #
        # Scenario walked through:
        #   1. Originator starts → registers the in-flight task → parks.
        #   2. Originator is cancelled before the fetch can finish.
        #   3. A NEW caller (the "waiter") arrives. The fetch is still
        #      running on the loop. The waiter finds the task in the
        #      in-flight dict and awaits it.
        #   4. We open the fetch gate. The task completes successfully.
        #   5. The waiter wakes up with the routing map.
        #
        # The mock must show ONE call total — the waiter joined, didn't
        # start a fresh fetch.
        original_ranges = self.partition_key_ranges
        fetch_gate = asyncio.Event()
        call_count = {'count': 0}

        class SlowClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1

                async def _gen():
                    await fetch_gate.wait()
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"join-etag"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(SlowClient())
        collection_link = "dbs/db/colls/container"

        # === Step 1: kick off the originator as its own task so we can
        # cancel it explicitly without bringing down the test coroutine.
        originator = asyncio.create_task(
            provider.get_routing_map(collection_link, feed_options={})
        )
        # Yield twice — once for the originator to be scheduled, once for
        # it to enter the slow path and register the in-flight task in the
        # dict. If we cancel before that registration happens, the waiter
        # below won't find anything to join and will start its own fetch.
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        # === Step 2: cancel the originator. The shared task it created
        # should keep running on the event loop (still parked on the gate).
        originator.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await originator

        # === Step 3: a NEW caller arrives — the waiter. The originator is
        # gone, but the in-flight task is still alive. The waiter should
        # find that task and join it.
        waiter = asyncio.create_task(
            provider.get_routing_map(collection_link, feed_options={})
        )
        # Yield so the waiter has time to enter the slow path and find the
        # already-registered in-flight task.
        await asyncio.sleep(0.01)
        # === Step 4: now let the gated fetch complete. The waiter is
        # awaiting on the shared task; when the task finishes, the waiter
        # wakes up with the result.
        fetch_gate.set()
        result = await waiter

        # === Step 5: the waiter received a real routing map (not None,
        # not an exception inherited from the cancelled originator).
        self.assertIsNotNone(result)
        # And critically: only ONE underlying fetch happened. The waiter
        # joined the originator's task, didn't start a separate one.
        self.assertEqual(call_count['count'], 1,
                         "Waiter should join the in-flight task, not start a new fetch")
        self.assertEqual(len(list(result._orderedPartitionKeyRanges)), len(original_ranges))

    async def test_failed_fetch_clears_inflight_slot_so_next_caller_retries_async(self):
        """When a fetch fails, the in-flight slot is freed and the next caller can retry."""
        # The shared-task fix relies on the `finally` block inside the fetch
        # task to remove its entry from the in-flight dict — REGARDLESS of
        # whether the fetch succeeded or raised. If a failed fetch left a
        # dead task in the dict, the next caller would find that dead task
        # and await it forever (or get back the same stale exception).
        #
        # This test simulates the failure case:
        #   1. First fetch raises CosmosHttpResponseError (simulated 500).
        #   2. The caller sees the exception propagate out — expected.
        #   3. The in-flight dict slot must be EMPTY now, so a fresh attempt
        #      can be registered.
        #   4. A second caller arrives, finds an empty slot, registers a
        #      brand-new fetch, and that one succeeds.
        original_ranges = self.partition_key_ranges
        call_count = {'count': 0}

        class FlakyClient:
            """First call raises, second call returns valid ranges."""
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                attempt = call_count['count']

                async def _gen():
                    if attempt == 1:
                        # Simulate the kind of transient backend error that
                        # would cause the fetch task to raise — and bring the
                        # whole publish path down with it.
                        raise CosmosHttpResponseError(status_code=500, message="simulated transient failure")
                    TestRoutingMapProviderAsync._capture_internal_headers(kwargs, '"retry-etag"')
                    for r in original_ranges:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(FlakyClient())
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)
        # The in-flight dict is keyed by (loop_id, collection_id) so the same
        # cache can be safely reused across different event loops.
        inflight_key = (id(asyncio.get_running_loop()), collection_id)

        # === Step 1: first call. Mock raises; expect the exception to
        # propagate out to us (the awaiting caller).
        with self.assertRaises(CosmosHttpResponseError):
            await provider.get_routing_map(collection_link, feed_options={})

        # === Step 2: the critical assertion. The failed task's `finally`
        # block should have removed itself from the in-flight dict. If this
        # fails, the next caller would be stuck awaiting a dead task.
        self.assertNotIn(inflight_key, provider._inflight_fetches,
                         "Failed fetch should free the in-flight slot")

        # === Step 3: a fresh caller arrives. Because the slot is empty,
        # they register a brand-new fetch — that's `call_count` going to 2.
        # And this attempt succeeds.
        result = await provider.get_routing_map(collection_link, feed_options={})
        self.assertIsNotNone(result)
        self.assertEqual(call_count['count'], 2,
                         "Second attempt should issue a brand-new fetch")

    async def test_inflight_slot_freed_after_successful_fetch_async(self):
        """The in-flight slot must be empty after a successful fetch completes."""
        # The companion to the previous test: cleanup must also happen on
        # the SUCCESS path. If it only happened on failure, every successful
        # fetch would leave a stale `done` task in the in-flight dict, and
        # the dict would grow unbounded over the lifetime of the client.
        #
        # We do exactly one successful fetch, then check the dict is empty.
        provider = PartitionKeyRangeCache(
            TestRoutingMapProviderAsync.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)
        inflight_key = (id(asyncio.get_running_loop()), collection_id)

        # Do a normal, successful fetch.
        await provider.get_routing_map(collection_link, feed_options={})
        # Slot must be cleaned up. If this fails it means the `finally` block
        # is only running on the failure path, not on success.
        self.assertNotIn(inflight_key, provider._inflight_fetches,
                         "Successful fetch should free the in-flight slot")


if __name__ == "__main__":
    unittest.main()
