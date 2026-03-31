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
        if response_hook:
            headers = ({http_constants.HttpHeaders.ETag: response_etag} if include_etag_header else {})
            response_hook(headers, None)

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

        result = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="dbs/db1/colls/coll1",
            previous_routing_map=previous_map,
            feed_options={}
        )

        self.assertIs(result, previous_map)
        self.assertEqual(result.change_feed_etag, '"etag-old"')

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
                if call_count['n'] == 1:
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
        self.assertEqual(call_count['n'], 2, "Expected incremental attempt and full-refresh fallback")
        self.assertEqual(len(upstream_calls), 2, "Upstream response_hook should run for both attempts")


if __name__ == "__main__":
    unittest.main()
