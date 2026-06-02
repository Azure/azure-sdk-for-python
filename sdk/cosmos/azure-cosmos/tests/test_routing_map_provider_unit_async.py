# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests for PartitionKeyRangeCache:
  - Concurrent access (double-checked locking with asyncio)
  - Empty change feed response (304 Not Modified / zero ranges from incremental update)
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import pytest

from azure.cosmos._routing.aio.routing_map_provider import (
    PartitionKeyRangeCache,
)
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos._routing._routing_map_provider_common import (
    process_fetched_ranges,
    _IncrementalMergeFailed,
    _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS,
)
from azure.cosmos import http_constants
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos._gone_retry_policy_base import _PartitionKeyRangeGoneRetryPolicyBase


# =========================================================
# Test-only tolerant shim for evaluate_drain_page
# =========================================================
# Production wires ``_internal_response_status_capture`` via ``_Request`` so
# ``evaluate_drain_page`` always receives a concrete HTTP status. These unit
# tests use lightweight MagicMock side_effects that bypass ``_Request`` and
# therefore leave the sidecar at ``[None]``. Rather than retrofit every mock
# to populate the sidecar, default an unknown status to ``304`` (Not Modified)
# so the drain terminates after the first page -- which is exactly the
# termination signal each existing mock relies on (data on the data path,
# ``iter([])`` on the INM-match path).
#
# This shim is the *only* test-side concession to the strict status contract
# introduced in commit a1e27a57bd; production code is unchanged.
# pylint: disable=wrong-import-position
import azure.cosmos._routing._routing_map_provider_common as _drain_common  # noqa: E402
import azure.cosmos._routing.routing_map_provider as _sync_provider_module  # noqa: E402
import azure.cosmos._routing.aio.routing_map_provider as _async_provider_module  # noqa: E402

_ORIGINAL_EVALUATE_DRAIN_PAGE = _drain_common.evaluate_drain_page


def _tolerant_evaluate_drain_page(*, page_new_etag, current_if_none_match,
                                   new_etag, seen_any_etag, status_code):
    if status_code is None:
        status_code = 304
    return _ORIGINAL_EVALUATE_DRAIN_PAGE(
        page_new_etag=page_new_etag,
        current_if_none_match=current_if_none_match,
        new_etag=new_etag,
        seen_any_etag=seen_any_etag,
        status_code=status_code,
    )


_drain_common.evaluate_drain_page = _tolerant_evaluate_drain_page
_sync_provider_module.evaluate_drain_page = _tolerant_evaluate_drain_page
_async_provider_module.evaluate_drain_page = _tolerant_evaluate_drain_page


async def _empty_async_gen():
    """Empty async generator used as the INM-match (304) response in mocks."""
    if False:
        yield  # pragma: no cover


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

    async def test_fetch_routing_map_empty_full_load_raises_503_after_budget_async(self):
        """A full load that repeatedly returns zero ranges should retry up
        to the budget and then raise ``CosmosHttpResponseError(503)``
        instead of returning ``None``."""
        client = _make_mock_async_client(ranges=[], response_etag='"etag"')

        cache = PartitionKeyRangeCache(client)

        # Patch ``asyncio.sleep`` so the retry loop's backoffs do not slow
        # this unit test down.
        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache._fetch_routing_map(
                    collection_link="dbs/db1/colls/coll1",
                    collection_id="dbs/db1/colls/coll1",
                    previous_routing_map=None,
                    feed_options={}
                )
        self.assertEqual(ctx.exception.status_code, 503)


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
        last_etag = {'v': None}

        def read_pk_ranges_retry_then_success(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            call_count['n'] += 1
            seen_if_none_match.append(inm)

            if response_hook:
                response_hook({http_constants.HttpHeaders.ETag: '"etag-inc"'}, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update({http_constants.HttpHeaders.ETag: '"etag-inc"'})
            last_etag['v'] = '"etag-inc"'

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

    # ==========================================================================
    # Provider retry-loop behavior tests (mocked integration path).
    #
    # These exercise the async provider's fetch/retry loop with mocked
    # ``/pkranges`` payloads: transient inconsistencies either recover on
    # retry or surface as HTTP 503; ``ValueError("Ranges overlap")`` never
    # leaks to callers.
    # ==========================================================================

    async def test_fetch_routing_map_recovers_after_transient_overlap_async(self):
        """An inconsistent ``/pkranges`` snapshot followed by a consistent
        one should populate the cache cleanly on the second attempt."""
        # First call: stale parent + children missing parent reference → triggers _OverlapDetected.
        bad_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10',   'minInclusive': '80', 'maxExclusive': 'A0'},  # stale parent
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90'},  # missing parents=['10']
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0'},  # missing parents=['10']
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]
        # Second call: same logical topology, but with the lineage metadata correctly
        # propagated — gateway has now rotated to a consistent snapshot.
        good_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90', 'parents': ['10']},
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0', 'parents': ['10']},
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]

        responses = [bad_payload, good_payload]
        call_count = {'n': 0}
        last_etag = {'v': None}

        client = MagicMock()

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            payload = responses[call_count['n']] if call_count['n'] < len(responses) else good_payload
            call_count['n'] += 1
            etag = '"etag-{}"'.format(call_count['n'])
            headers = {http_constants.HttpHeaders.ETag: etag}
            last_etag['v'] = etag
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in payload:
                    yield r

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
        cache = PartitionKeyRangeCache(client)

        # Patch asyncio.sleep so the test does not actually wait the backoff.
        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            result = await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        self.assertIsNotNone(
            result,
            "Cache should populate after the transient overlap clears on retry."
        )
        self.assertEqual(
            call_count['n'], 2,
            "Expected exactly one retry: one failed fetch + one successful fetch."
        )
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        # Post-fix expected ordering: L, 10/0, 10/1, R (the stale parent '10'
        # is correctly filtered on the consistent retry payload).
        self.assertEqual(ids, ['L', '10/0', '10/1', 'R'])

    async def test_fetch_routing_map_surfaces_503_after_persistent_overlap_async(self):
        """Persistent inconsistent snapshots across every retry must surface
        as HTTP 503, not as empty results from ``get_overlapping_ranges``."""
        bad_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10',   'minInclusive': '80', 'maxExclusive': 'A0'},
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90'},
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0'},
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]
        call_count = {'n': 0}
        last_etag = {'v': None}
        client = MagicMock()

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            call_count['n'] += 1
            etag = '"etag-bad"'
            headers = {http_constants.HttpHeaders.ETag: etag}
            last_etag['v'] = etag
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in bad_payload:
                    yield r

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
        cache = PartitionKeyRangeCache(client)

        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        self.assertEqual(
            ctx.exception.status_code, http_constants.StatusCodes.SERVICE_UNAVAILABLE,
            "Persistent overlap must surface as HTTP 503 (transient), not as a bare ValueError "
            "or as a silent empty-result return."
        )
        # We should have exhausted the full retry budget (3 attempts by default).
        self.assertEqual(
            call_count['n'], _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS,
            "Should have made exactly _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS fetch attempts before giving up."
        )

    async def test_fetch_routing_map_recovers_after_transient_gap_async(self):
        """A gap snapshot followed by a consistent one should populate the
        cache cleanly on the second attempt."""
        bad_payload = [
            {'id': 'L', 'minInclusive': '',   'maxExclusive': '80'},
            {'id': 'R', 'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]
        good_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90'},
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0'},
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]

        responses = [bad_payload, good_payload]
        call_count = {'n': 0}
        last_etag = {'v': None}

        client = MagicMock()

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            payload = responses[call_count['n']] if call_count['n'] < len(responses) else good_payload
            call_count['n'] += 1
            etag = '"etag-{}"'.format(call_count['n'])
            headers = {http_constants.HttpHeaders.ETag: etag}
            last_etag['v'] = etag
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in payload:
                    yield r

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
        cache = PartitionKeyRangeCache(client)

        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            result = await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        self.assertIsNotNone(
            result,
            "Async cache should populate after the transient gap clears on retry."
        )
        self.assertEqual(call_count['n'], 2, "Expected exactly one retry.")
        ids = [r['id'] for r in result._orderedPartitionKeyRanges]
        self.assertEqual(ids, ['L', '10/0', '10/1', 'R'])

    async def test_fetch_routing_map_surfaces_503_after_persistent_gap_async(self):
        """A persistent gap across the retry budget must surface as
        ``CosmosHttpResponseError(503)``."""
        bad_payload = [
            {'id': 'L', 'minInclusive': '',   'maxExclusive': '80'},
            {'id': 'R', 'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]
        call_count = {'n': 0}
        last_etag = {'v': None}
        client = MagicMock()

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            call_count['n'] += 1
            etag = '"etag-bad"'
            headers = {http_constants.HttpHeaders.ETag: etag}
            last_etag['v'] = etag
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in bad_payload:
                    yield r

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
        cache = PartitionKeyRangeCache(client)

        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        self.assertEqual(ctx.exception.status_code, http_constants.StatusCodes.SERVICE_UNAVAILABLE)
        self.assertEqual(call_count['n'], _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS)

    async def test_incremental_overlap_converts_to_incremental_merge_failed_async(self):
        """An overlap raised during incremental merge must convert to
        ``_IncrementalMergeFailed`` so the standard fallback (retry
        incremental, then full refresh) takes over; a bare ``ValueError``
        must never escape to the caller."""

        # Existing cached map: '0' covers ['', '80'] and '1' covers ['80', 'FF'].
        previous_map = CollectionRoutingMap.CompleteRoutingMap(
            [
                ({'id': '0', 'minInclusive': '',   'maxExclusive': '80'}, True),
                ({'id': '1', 'minInclusive': '80', 'maxExclusive': 'FF'}, True),
            ],
            'coll1', '"etag-prev"'
        )

        # Delta:
        #   - '0' re-declared with the same span (resolves via the existing
        #     ``known_range_info_by_id`` lookup — no parents needed).
        #   - '2' with ``parents=['1']`` and a span that overlaps '0'. The
        #     parent-resolution loop succeeds because '1' is in the cache,
        #     so we reach ``try_combine``. Once '1' is removed as the gone
        #     parent, the merged map is { '0' ('', '80'), '2' ('40', 'FF') }
        #     — '0' overlaps '2' on ['40', '80'], so ``is_complete_set_of_range``
        #     raises ``ValueError("Ranges overlap: ...")`` from inside
        #     ``try_combine``.
        bad_delta = [
            {'id': '0', 'minInclusive': '',   'maxExclusive': '80'},
            {'id': '2', 'minInclusive': '40', 'maxExclusive': 'FF', 'parents': ['1']},
        ]

        # The wrapper around try_combine must absorb the ValueError and convert
        # it to _IncrementalMergeFailed for the caller's retry loop.
        with self.assertRaises(_IncrementalMergeFailed):
            process_fetched_ranges(
                bad_delta, previous_map, 'coll1', 'dbs/db1/colls/coll1', '"etag-new"'
            )

    async def test_fetch_routing_map_mixed_overlap_and_gap_signals_share_retry_budget_async(self):
        """``_OverlapDetected`` and ``_GapDetected`` share one retry counter.
        Alternating snapshots must still raise 503 once the budget is
        exhausted; the budget is not per-signal-type."""
        # Overlap payload: stale parent '10' coexists with its children that
        # lack a ``parents`` reference. Triggers ``_OverlapDetected``.
        overlap_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10',   'minInclusive': '80', 'maxExclusive': 'A0'},
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90'},
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0'},
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]
        # Gap payload: ['80', 'A0') is missing entirely. Triggers ``_GapDetected``.
        gap_payload = [
            {'id': 'L', 'minInclusive': '',   'maxExclusive': '80'},
            {'id': 'R', 'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]

        responses = [overlap_payload, gap_payload, overlap_payload]
        call_count = {'n': 0}
        last_etag = {'v': None}

        client = MagicMock()

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers_in = kwargs.get('headers') or {}
            inm = headers_in.get(http_constants.HttpHeaders.IfNoneMatch)
            if inm is not None and inm == last_etag['v']:
                return _empty_async_gen()
            payload = responses[call_count['n']] if call_count['n'] < len(responses) else overlap_payload
            call_count['n'] += 1
            etag = '"etag-mixed-{}"'.format(call_count['n'])
            headers = {http_constants.HttpHeaders.ETag: etag}
            last_etag['v'] = etag
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in payload:
                    yield r

            return async_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)
        cache = PartitionKeyRangeCache(client)

        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache.get_routing_map("dbs/db1/colls/coll1", feed_options={})

        self.assertEqual(
            ctx.exception.status_code, http_constants.StatusCodes.SERVICE_UNAVAILABLE,
            "Alternating overlap/gap signals must still surface as HTTP 503 once "
            "the shared budget is exhausted."
        )
        self.assertEqual(
            call_count['n'], _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS,
            "Overlap and gap signals must share one retry budget; alternating "
            "between them must NOT extend the total number of attempts."
        )

    async def test_fetch_routing_map_preserves_existing_cache_entry_when_force_refresh_surfaces_503_async(self):
        """A 503 raised by ``_fetch_routing_map`` during a forced refresh
        must not corrupt the cached routing map. Subsequent reads should
        still see the previously-cached entry."""
        # Pre-populate the shared cache with a known-good routing map.
        cached_map = _make_complete_routing_map("dbs/db1/colls/coll1", '"etag-cached"')
        cache = PartitionKeyRangeCache(MagicMock())
        cache._collection_routing_map_by_item["dbs/db1/colls/coll1"] = cached_map

        # Wire the client to return an inconsistent (overlap) snapshot every
        # time -- forces the retry loop to exhaust its budget and raise 503.
        bad_payload = [
            {'id': 'L',    'minInclusive': '',   'maxExclusive': '80'},
            {'id': '10',   'minInclusive': '80', 'maxExclusive': 'A0'},
            {'id': '10/0', 'minInclusive': '80', 'maxExclusive': '90'},
            {'id': '10/1', 'minInclusive': '90', 'maxExclusive': 'A0'},
            {'id': 'R',    'minInclusive': 'A0', 'maxExclusive': 'FF'},
        ]

        def fake_read_pk_ranges(collection_link, options, response_hook=None, **kwargs):
            headers = {http_constants.HttpHeaders.ETag: '"etag-bad"'}
            if response_hook:
                response_hook(headers, None)
            capture_headers = kwargs.get('_internal_response_headers_capture')
            if capture_headers is not None:
                capture_headers.update(headers)

            async def async_gen():
                for r in bad_payload:
                    yield r

            return async_gen()

        cache._document_client._ReadPartitionKeyRanges = MagicMock(side_effect=fake_read_pk_ranges)

        async def _no_sleep(_seconds):
            return None

        with patch(
            'azure.cosmos._routing.aio.routing_map_provider.asyncio.sleep',
            new=_no_sleep,
        ):
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache.get_routing_map(
                    "dbs/db1/colls/coll1",
                    feed_options={},
                    force_refresh=True,
                    previous_routing_map=cached_map,
                )

        self.assertEqual(ctx.exception.status_code, http_constants.StatusCodes.SERVICE_UNAVAILABLE)

        # Critical invariant: the previously-cached map must still be reachable
        # via the same key. A 503 from a forced refresh must never evict good
        # cache state -- otherwise every transient gateway blip would force the
        # next reader to pay a cold-start cost.
        self.assertIs(
            cache._collection_routing_map_by_item.get("dbs/db1/colls/coll1"), cached_map,
            "Cached routing map must be preserved after a 503 from forced refresh -- "
            "transient inconsistencies must not evict good cache state."
        )
        self.assertEqual(
            cache._collection_routing_map_by_item["dbs/db1/colls/coll1"].change_feed_etag,
            '"etag-cached"',
            "Cached ETag must remain the pre-503 value (no partial overwrite)."
        )


if __name__ == "__main__":
    unittest.main()
