# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests for PartitionKeyRangeCache:
  - Concurrent access (double-checked locking with asyncio)
  - Empty change feed response (304 Not Modified / zero ranges from incremental update)
"""

import asyncio
import unittest
from unittest.mock import MagicMock

import pytest

from azure.cosmos.aio import CosmosClient  # noqa: F401 - needed to resolve circular imports
from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos import http_constants
from azure.cosmos._gone_retry_policy_base import _PartitionKeyRangeGoneRetryPolicyBase



def _make_complete_routing_map(collection_id="coll1", etag='"etag-1"'):
    """Create a minimal but complete CollectionRoutingMap for testing."""
    ranges = [
        ({'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}, True)
    ]
    return CollectionRoutingMap.CompleteRoutingMap(ranges, collection_id, etag)


def _make_mock_async_client(ranges, response_etag='"etag-resp"', include_etag_header=True):
    """Create a mock async client whose _ReadPartitionKeyRanges returns an
    async iterator over the given ranges and invokes the response_hook."""
    client = MagicMock()

    def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
        headers = ({http_constants.HttpHeaders.ETag: response_etag} if include_etag_header else {})
        if response_hook:
            response_hook(headers, None)
        capture_headers = kwargs.get('_internal_response_headers_capture')
        if capture_headers is not None:
            capture_headers.update(headers)

        async def async_gen():
            for r in ranges:
                yield r

        return async_gen()

    client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
    return client


@pytest.mark.cosmosEmulator
class TestRoutingMapProviderUnitAsync(unittest.IsolatedAsyncioTestCase):
    """Async unit tests for PartitionKeyRangeCache."""


    async def test_concurrent_initial_load_only_fetches_once_async(self):
        """When multiple coroutines concurrently call get_routing_map on an empty
        cache, only ONE should call _ReadPartitionKeyRanges. The others should
        find the map populated by the first coroutine (double-checked lock)."""
        full_range = {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}
        call_count = {'n': 0}

        client = MagicMock()

        def slow_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1

            async def slow_gen():
                await asyncio.sleep(0.1)  # Simulate slow network
                yield full_range

            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag-slow"'}, None)
            return slow_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=slow_read_pk_ranges)

        cache = PartitionKeyRangeCache(client)

        # Launch 5 concurrent coroutines that all try to load the same collection
        async def worker():
            return await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        results = await asyncio.gather(*[worker() for _ in range(5)])

        # All coroutines should have gotten a valid routing map
        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Coroutine {i} should have gotten a routing map")

        # All coroutines should return the SAME object (identity check)
        for i in range(1, 5):
            self.assertIs(results[0], results[i],
                          f"Coroutine {i} should return the same cached object as coroutine 0")

        # _ReadPartitionKeyRanges should have been called exactly once
        self.assertEqual(call_count['n'], 1,
                         f"Expected 1 fetch call (double-checked lock), got {call_count['n']}")

    async def test_concurrent_access_different_collections_independent_async(self):
        """Concurrent get_routing_map calls for DIFFERENT collections should
        not block each other — each collection has its own lock."""
        call_log = {'coll_a': 0, 'coll_b': 0}

        client = MagicMock()

        def read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            if 'coll_a' in collection_link:
                call_log['coll_a'] += 1
            else:
                call_log['coll_b'] += 1

            async def gen():
                await asyncio.sleep(0.05)
                yield {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}

            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag"'}, None)
            return gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges)

        cache = PartitionKeyRangeCache(client)

        result_a, result_b = await asyncio.gather(
            cache.get_routing_map("dbs/db1/colls/coll_a", feed_options={}),
            cache.get_routing_map("dbs/db1/colls/coll_b", feed_options={})
        )

        self.assertIsNotNone(result_a)
        self.assertIsNotNone(result_b)
        self.assertEqual(call_log['coll_a'], 1)
        self.assertEqual(call_log['coll_b'], 1)
        self.assertIsNot(result_a, result_b)

    async def test_concurrent_force_refresh_only_refreshes_once_async(self):
        """When multiple coroutines force_refresh the same collection simultaneously,
        only one should actually fetch — the others see the updated ETag and skip.

        We mock _fetch_routing_map directly to isolate the locking logic from
        the change-feed protocol details."""
        call_count = {'n': 0}

        client = MagicMock()
        cache = PartitionKeyRangeCache(client)

        # Pre-populate cache
        initial_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-stale"')
        cache._collection_routing_map_by_item["dbs/db1/colls/coll1"] = initial_map

        refreshed_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-refreshed"')

        async def mock_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):
            call_count['n'] += 1
            await asyncio.sleep(0.1)  # Simulate slow fetch
            return refreshed_map

        cache._fetch_routing_map = mock_fetch

        async def worker():
            return await cache.get_routing_map(
                "dbs/db1/colls/coll1",
                feed_options={},
                force_refresh=True,
                previous_routing_map=initial_map
            )

        results = await asyncio.gather(*[worker() for _ in range(3)])

        for i, r in enumerate(results):
            self.assertIsNotNone(r, f"Coroutine {i} should have gotten a routing map")

        # Only one fetch — the first coroutine refreshes, others see updated ETag
        self.assertEqual(call_count['n'], 1,
                         f"Expected 1 fetch (others skip via stale check), got {call_count['n']}")


    async def test_empty_incremental_response_preserves_existing_map_async(self):
        """When an incremental change feed returns zero ranges (service returned
        304 Not Modified / no changes since the ETag), try_combine with an empty
        list should return the existing map unchanged."""
        initial_map = _make_complete_routing_map("coll1", '"etag-1"')

        result = initial_map.try_combine([], '"etag-2"')

        self.assertIsNotNone(result, "try_combine with empty delta should return a valid map")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0'], "Ranges should be unchanged")
        self.assertEqual(result.change_feed_etag, '"etag-2"', "ETag should be updated")

    async def test_fetch_routing_map_empty_incremental_response_async(self):
        """_fetch_routing_map should succeed when the incremental change feed
        returns zero ranges — the existing map should be preserved with
        the updated ETag."""
        client = _make_mock_async_client(ranges=[], response_etag='"etag-new"')

        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIsNotNone(result, "Should return valid map when incremental response is empty")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['0'], "Ranges should be preserved from previous map")
        self.assertEqual(result.change_feed_etag, '"etag-new"', "ETag should be updated")

    async def test_fetch_routing_map_empty_full_load_returns_none_async(self):
        """_fetch_routing_map should return None when a full load (no previous
        map) returns zero ranges — this means the service returned nothing."""
        client = _make_mock_async_client(ranges=[], response_etag='"etag"')

        cache = PartitionKeyRangeCache(client)

        result = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=None,
            feed_options={}
        )

        self.assertIsNone(result, "Full load with empty ranges should return None")


    async def test_get_previous_routing_map_exact_key_finds_entry_async(self):
        """_get_previous_routing_map should find the cached routing map when
        the collection_link matches the key stored in the cache exactly."""
        mock_client = MagicMock()
        mock_routing_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-1"')

        mock_provider = MagicMock()
        mock_provider._collection_routing_map_by_item = {
            "dbs/db1/colls/coll1": mock_routing_map
        }
        mock_client._routing_map_provider = mock_provider

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/coll1")

        self.assertIs(result, mock_routing_map,
                      "Should return the cached map when the key matches exactly")

    async def test_get_previous_routing_map_normalizes_collection_link_async(self):
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

    async def test_get_previous_routing_map_returns_none_for_missing_async(self):
        """_get_previous_routing_map returns None when the collection is not
        in the cache."""
        mock_client = MagicMock()
        mock_provider = MagicMock()
        mock_provider._collection_routing_map_by_item = {}
        mock_client._routing_map_provider = mock_provider

        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/unknown")
        self.assertIsNone(result)

    async def test_get_previous_routing_map_returns_none_for_none_link_async(self):
        """_get_previous_routing_map returns None when collection_link is None."""
        mock_client = MagicMock()
        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map(None)
        self.assertIsNone(result)

    async def test_get_previous_routing_map_returns_none_when_no_provider_async(self):
        """_get_previous_routing_map returns None when the client has no
        _routing_map_provider attribute."""
        mock_client = MagicMock(spec=[])  # spec=[] means no attributes
        policy = _PartitionKeyRangeGoneRetryPolicyBase(mock_client)
        result = policy._get_previous_routing_map("dbs/db1/colls/coll1")
        self.assertIsNone(result)

    async def test_fetch_routing_map_empty_incremental_response_same_etag_returns_same_object_async(self):
        """Empty incremental response with unchanged ETag should return the
        existing map object without rebuilding."""
        client = _make_mock_async_client(ranges=[], response_etag='"etag-old"')
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIs(result, previous_map)
        self.assertEqual(result.change_feed_etag, '"etag-old"')

    async def test_fetch_routing_map_empty_incremental_response_missing_etag_preserves_previous_async(self):
        """If service omits ETag on an empty incremental response, preserve
        the existing ETag and map instance."""
        client = _make_mock_async_client(ranges=[], include_etag_header=False)
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        with self.assertLogs("azure.cosmos._routing._routing_map_provider_common", level="WARNING") as logs:
            result = await cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="dbs/db1/colls/coll1",
                previous_routing_map=previous_map,
                feed_options={}
            )

        self.assertIs(result, previous_map)
        self.assertEqual(result.change_feed_etag, '"etag-old"')
        self.assertTrue(any("returned no ETag" in message for message in logs.output))

    async def test_fetch_routing_map_fallback_rechains_upstream_response_hook_async(self):
        """Upstream response_hook should be invoked for both incremental and
        full-refresh attempts when incremental merge falls back (async)."""
        client = MagicMock()
        upstream_calls = []
        call_count = {'n': 0}

        def upstream_hook(headers, _):
            upstream_calls.append(dict(headers))

        def read_pk_ranges_with_fallback(collection_link, options, response_hook=None, **kwargs):
            call_count['n'] += 1
            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: f'"etag-{call_count["n"]}"'}, None)

            async def async_gen():
                if call_count['n'] <= 2:
                    yield {
                        'id': '1',
                        'minInclusive': '',
                        'maxExclusive': 'AA',
                        'parents': ['missing-parent']
                    }
                else:
                    yield {'id': '0', 'minInclusive': '', 'maxExclusive': 'FF'}

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=read_pk_ranges_with_fallback)
        cache = PartitionKeyRangeCache(client)
        previous_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-old"')

        result = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={},
            response_hook=upstream_hook
        )

        self.assertIsNotNone(result)
        self.assertEqual(call_count['n'], 3, "Expected incremental attempt, one retry, then full-refresh fallback")
        self.assertEqual(len(upstream_calls), 3, "Upstream response_hook should run for retry and fallback attempts")

    async def test_fetch_routing_map_incomplete_retry_succeeds_without_full_refresh_async(self):
        """Incomplete incremental update should retry once with same ETag and succeed without full refresh (async)."""
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

            async def async_gen():
                if call_count['n'] == 1:
                    yield {'id': '9', 'minInclusive': '', 'maxExclusive': 'AA', 'parents': ['missing-parent']}
                else:
                    yield {'id': '2', 'minInclusive': '', 'maxExclusive': '03', 'parents': ['0']}
                    yield {'id': '3', 'minInclusive': '03', 'maxExclusive': '05', 'parents': ['0']}
                    yield {'id': '4', 'minInclusive': '', 'maxExclusive': '02', 'parents': ['2']}
                    yield {'id': '5', 'minInclusive': '02', 'maxExclusive': '03', 'parents': ['2']}

            return async_gen()

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

        result = await cache._fetch_routing_map(
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

    async def test_fetch_routing_map_cascading_single_delta_split_merges_incrementally_async(self):
        """Cascading split deltas should merge incrementally without full refresh (async).

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

            async def async_gen():
                if call_count['n'] == 1:
                    # 1st call: incremental payload with a cascading parent chain in one delta.
                    yield {'id': '2', 'minInclusive': '', 'maxExclusive': '03', 'parents': ['0']}
                    yield {'id': '3', 'minInclusive': '03', 'maxExclusive': '05', 'parents': ['0']}
                    yield {'id': '4', 'minInclusive': '', 'maxExclusive': '02', 'parents': ['2']}
                    yield {'id': '5', 'minInclusive': '02', 'maxExclusive': '03', 'parents': ['2']}
                else:
                    return

            return async_gen()

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

        result = await cache._fetch_routing_map(
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
