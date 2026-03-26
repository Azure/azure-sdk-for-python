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

    These mirror the sync tests in test_routing_map_provider.py but use the
    async code paths.
    """

    class MockedCosmosClientConnection(object):
        """Mock that returns partition key ranges as an async generator."""

        def __init__(self, partition_key_ranges):
            self.partition_key_ranges = partition_key_ranges

        def _ReadPartitionKeyRanges(self, _collection_link: str,
                                    _feed_options: Optional[Mapping[str, Any]] = None, **kwargs):
            response_hook = kwargs.get('response_hook')
            if response_hook:
                response_hook({'etag': '"test-etag-1"'}, None)

            ranges = self.partition_key_ranges

            async def _gen():
                for r in ranges:
                    yield r

            return _gen()

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
    # New: PartitionKeyRangeCache (async) caching tests
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

    async def test_get_routing_map_returns_cached_on_second_call_async(self):
        """Second call returns the same cached object without re-fetching."""
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': '"test-etag-1"'}, None)

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
        """force_refresh=True causes a re-fetch even when cache is populated."""
        call_count = {'count': 0}
        original_ranges = self.partition_key_ranges

        class CountingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': f'"test-etag-{call_count["count"]}"'}, None)

                async def _gen():
                    for r in original_ranges:
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
        self.assertEqual(call_count['count'], 2, "force_refresh should trigger a second fetch")
        self.assertIsNotNone(result2)

    async def test_is_cache_stale_etag_logic_async(self):
        """_is_cache_stale returns correct results for all ETag scenarios."""
        provider = PartitionKeyRangeCache(
            TestRoutingMapProviderAsync.MockedCosmosClientConnection(self.partition_key_ranges)
        )
        collection_link = "dbs/db/colls/container"
        from azure.cosmos import _base
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        cached_map = await provider.get_routing_map(collection_link, feed_options={})

        # Case 1: None previous → False
        self.assertFalse(provider._is_cache_stale(collection_id, None))

        # Case 2: Same ETag → True (stale)
        self.assertTrue(provider._is_cache_stale(collection_id, cached_map))

        # Case 3: Different ETag → False (already refreshed)
        mock_map = MagicMock()
        mock_map.change_feed_etag = "completely-different-etag"
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map))

        # Case 4: Empty cache → False
        provider._collection_routing_map_by_item.clear()
        mock_map2 = MagicMock()
        mock_map2.change_feed_etag = cached_map.change_feed_etag
        self.assertFalse(provider._is_cache_stale(collection_id, mock_map2))

    async def test_fetch_routing_map_fallback_recursion_guard_async(self):
        """When a full load returns an incomplete map, returns None instead of recursing."""
        incomplete_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'}  # Gap from 80 to FF
        ]

        class IncompleteClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': '"incomplete-etag"'}, None)

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
        self.assertIsNone(result, "Should return None when full load returns an incomplete map")

    async def test_fetch_routing_map_full_load_with_incomplete_ranges_returns_none_async(self):
        """When a full load (previous_routing_map=None) returns gapped ranges, returns None immediately."""
        incomplete_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'}  # Gap from 80 to FF
        ]

        class IncompleteClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': '"incomplete-etag"'}, None)

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
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': '"etag-2"'}, None)

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

    async def test_fetch_routing_map_incremental_missing_parent_falls_back_async(self):
        """When incremental update has a child referencing a missing parent, falls back to full refresh."""
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        call_count = {'count': 0}
        delta_ranges = [
            {'id': '5', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['NONEXISTENT']}
        ]
        full_ranges = [
            {'id': '5', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '6', 'minInclusive': '40', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]

        class FallbackClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': f'"etag-{call_count["count"]}"'}, None)
                data = delta_ranges if call_count['count'] == 1 else full_ranges

                async def _gen():
                    for r in data:
                        yield r

                return _gen()

        provider = PartitionKeyRangeCache(FallbackClient())
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
        self.assertEqual(call_count['count'], 2, "Should have called service twice (incremental + fallback)")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 3)

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
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': f'"etag-{call_count["count"]}"'}, None)
                data = ([{'id': '99', 'minInclusive': '', 'maxExclusive': 'FF',
                          'parents': ['MISSING']}] if call_count['count'] == 1 else full_ranges)

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
        self.assertEqual(len(captured_headers_list), 2)

        # First call (incremental) should have IfNoneMatch
        self.assertIn(http_constants.HttpHeaders.IfNoneMatch, captured_headers_list[0])

        # Second call (full load fallback) should NOT have IfNoneMatch
        self.assertNotIn(http_constants.HttpHeaders.IfNoneMatch, captured_headers_list[1])

    async def test_fetch_routing_map_incremental_existing_range_no_parents_async(self):
        """Incremental update correctly handles an existing range reappearing without parents (metadata update)."""
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        # Range '1' reappears with no parents (metadata update) + range '0' splits
        delta_ranges = [
            {'id': '2', 'minInclusive': '', 'maxExclusive': '40', 'parents': ['0']},
            {'id': '3', 'minInclusive': '40', 'maxExclusive': '80', 'parents': ['0']},
            {'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'},  # no parents — stable
        ]

        class DeltaClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': '"etag-2"'}, None)

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
        self.assertEqual(len(ranges), 3)
        self.assertEqual(ranges[0]['id'], '2')
        self.assertEqual(ranges[1]['id'], '3')
        self.assertEqual(ranges[2]['id'], '1')

    async def test_fetch_routing_map_incremental_unknown_range_no_parents_falls_back_async(self):
        """Incremental update with an unknown range ID and no parents (merge scenario) falls back to full refresh."""
        initial_ranges = [
            {'id': '0', 'minInclusive': '', 'maxExclusive': '40'},
            {'id': '1', 'minInclusive': '40', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]
        initial_map = CollectionRoutingMap.CompleteRoutingMap(
            [(r, True) for r in initial_ranges],
            'dbs/db/colls/container',
            '"etag-1"'
        )

        call_count = {'count': 0}
        # Range '7' is brand new with no parents — simulates a merge of '0' and '1'
        delta_ranges = [
            {'id': '7', 'minInclusive': '', 'maxExclusive': '80'},  # no parents, not in cache
        ]
        full_ranges = [
            {'id': '7', 'minInclusive': '', 'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '80', 'maxExclusive': 'FF'}
        ]

        class MergeClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count['count'] += 1
                response_hook = kwargs.get('response_hook')
                if response_hook:
                    response_hook({'etag': f'"etag-{call_count["count"]}"'}, None)
                data = delta_ranges if call_count['count'] == 1 else full_ranges

                async def _gen():
                    for r in data:
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

        self.assertIsNotNone(result, "Should succeed via full refresh fallback after merge detection")
        self.assertEqual(call_count['count'], 2, "Should have called service twice (incremental + fallback)")
        ranges = list(result._orderedPartitionKeyRanges)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0]['id'], '7')
        self.assertEqual(ranges[1]['id'], '2')


if __name__ == "__main__":
    unittest.main()
