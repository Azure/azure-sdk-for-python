# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests to verify that the `containerRID` option (which becomes the
`x-ms-cosmos-intended-collection-rid` HTTP header) flows through every
async code path that can trigger a partition key range fetch.

"""

import unittest
from typing import Optional, Mapping, Any, Dict
from azure.cosmos._routing import routing_range
from azure.cosmos._routing.aio.routing_map_provider import (
    PartitionKeyRangeCache,
    SmartRoutingMapProvider,
)
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos import _base, http_constants


# =====================================================================
# Shared test fixtures
# =====================================================================

COLLECTION_LINK = "dbs/mydb/colls/mycoll"
CONTAINER_RID = "XkwmAA=="  # cspell:disable-line

PARTITION_KEY_RANGES = [
    {"id": "0", "minInclusive": "", "maxExclusive": "3F"},
    {"id": "1", "minInclusive": "3F", "maxExclusive": "7F"},
    {"id": "2", "minInclusive": "7F", "maxExclusive": "FF"},
]


class CapturingMockClient:
    """A mock async CosmosClientConnection that records the feed_options
    passed to _ReadPartitionKeyRanges so tests can assert on them.

    _ReadPartitionKeyRanges returns an async iterator (matching the real
    async client behavior)."""

    def __init__(self, partition_key_ranges=None):
        self.partition_key_ranges = partition_key_ranges or PARTITION_KEY_RANGES
        self.captured_feed_options = None
        self.call_count = 0

    @staticmethod
    def _capture_internal_headers(kwargs, etag):
        captured_headers = kwargs.get('_internal_response_headers_capture')
        if captured_headers is not None:
            captured_headers.clear()
            captured_headers.update({'ETag': etag})

    async def _ReadPartitionKeyRanges(
        self,
        collection_link: str,
        feed_options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ):
        self.captured_feed_options = dict(feed_options) if feed_options else {}
        self.call_count += 1
        CapturingMockClient._capture_internal_headers(kwargs, '"test-etag-1"')
        response_hook = kwargs.get("response_hook")
        if response_hook:
            response_hook({"etag": "test-etag-1"}, None)
        for item in self.partition_key_ranges:
            yield item


class TestContainerRIDHeaderUnitAsync(unittest.IsolatedAsyncioTestCase):
    """Verifies that the containerRID feed option (which becomes the
    x-ms-cosmos-intended-collection-rid HTTP header) flows correctly through
    the async PartitionKeyRangeCache, SmartRoutingMapProvider, and the
    incremental-to-full-load fallback path.
    """

    # ----- PartitionKeyRangeCache -----

    async def test_initial_load_passes_containerRID_async(self):
        """On a cold cache, the containerRID from the caller's feed_options
        must be forwarded to _ReadPartitionKeyRanges so the service knows
        which physical container to query."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        await cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            feed_options
        )
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID

    async def test_cache_hit_does_not_call_service_async(self):
        """A second lookup against the same collection must be served entirely
        from the in-memory cache — no additional service call."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        await cache.get_overlapping_ranges(
            COLLECTION_LINK, [routing_range.Range("", "FF", True, False)], feed_options)
        assert client.call_count == 1
        await cache.get_overlapping_ranges(
            COLLECTION_LINK, [routing_range.Range("", "3F", True, False)], feed_options)
        assert client.call_count == 1, "Cache hit should not trigger another service call"


    async def test_end_to_end_containerRID_and_pk_range_flag_async(self):
        """Verifies the full async path: SmartRoutingMapProvider delegates to
        PartitionKeyRangeCache, which adds the internal pk-range-fetch flag
        and forwards the caller's containerRID to _ReadPartitionKeyRanges.
        Uses multiple disjoint ranges to also verify that containerRID
        survives when the provider resolves several ranges in one call."""
        client = CapturingMockClient()
        provider = SmartRoutingMapProvider(client)
        ranges = [
            routing_range.Range("", "1A", True, False),
            routing_range.Range("5C", "5D", True, False),
            routing_range.Range("8E", "8F", True, False),
        ]
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        await provider.get_overlapping_ranges(
            COLLECTION_LINK, ranges, feed_options)
        assert client.call_count >= 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        assert client.captured_feed_options.get("_internal_pk_range_fetch") is True

    async def test_end_to_end_without_containerRID_omits_header_async(self):
        """When the caller does not supply containerRID, it must not appear
        in the feed_options that reach _ReadPartitionKeyRanges."""
        client = CapturingMockClient()
        provider = SmartRoutingMapProvider(client)
        feed_options: Dict[str, Any] = {}
        await provider.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            feed_options
        )
        assert "containerRID" not in client.captured_feed_options

    async def test_incremental_refresh_preserves_containerRID_async(self):
        """A force_refresh (triggered by split/merge errors) must re-send
        containerRID to the service so the correct physical container is
        queried again."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        previous_map = await cache.get_routing_map(COLLECTION_LINK, feed_options)
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        await cache.get_routing_map(
            COLLECTION_LINK,
            feed_options,
            force_refresh=True,
            previous_routing_map=previous_map,
        )
        # The mock returns the same ranges (no split/merge deltas), so the
        # incremental merge succeeds in a single fetch without falling back
        # to a full refresh.
        assert client.call_count == 2
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID

    async def test_incremental_retry_after_split_preserves_containerRID_async(self):
        """When an incremental refresh encounters unresolvable parent ranges,
        the routing map provider retries the incremental fetch once
        (_INCOMPLETE_ROUTING_MAP_MAX_RETRIES=1). On the retry, if the ranges
        resolve successfully, containerRID must still flow through."""
        # Post-split ranges reference parents not in the original map
        split_ranges = [
            {"id": "3", "minInclusive": "", "maxExclusive": "1F", "parents": ["99"]},
            {"id": "4", "minInclusive": "1F", "maxExclusive": "3F", "parents": ["99"]},
        ]

        class SplitMockClient:
            def __init__(self):
                self.captured_feed_options = None
                self.call_count = 0

            @staticmethod
            def _capture_internal_headers(kwargs, etag):
                captured_headers = kwargs.get('_internal_response_headers_capture')
                if captured_headers is not None:
                    captured_headers.clear()
                    captured_headers.update({'ETag': etag})

            async def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                self.captured_feed_options = dict(feed_options) if feed_options else {}
                self.call_count += 1
                SplitMockClient._capture_internal_headers(kwargs, '"test-etag-1"')
                # First call: initial load returns original ranges
                # Second call: incremental returns split ranges with unknown parents,
                #              raising _IncrementalMergeFailed (caught → retry incremental, count 0→1)
                # Third call: incremental retry succeeds with resolvable ranges
                items = split_ranges if self.call_count == 2 else PARTITION_KEY_RANGES
                for item in items:
                    yield item

        client = SplitMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        previous_map = await cache.get_routing_map(COLLECTION_LINK, feed_options)
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        await cache.get_routing_map(
            COLLECTION_LINK,
            feed_options,
            force_refresh=True,
            previous_routing_map=previous_map,
        )
        # Incremental fetch hits unresolvable parents → retries once → succeeds:
        # 1 initial + 1 failed incremental + 1 successful retry = 3 calls.
        assert client.call_count == 3
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID

    async def test_full_refresh_fallback_after_exhausted_retries_preserves_containerRID_async(self):
        """When incremental retries are exhausted (_INCOMPLETE_ROUTING_MAP_MAX_RETRIES=1),
        the routing map provider falls back to a full refresh (current_previous_map=None).
        containerRID must still flow through on the full refresh call."""
        # Post-split ranges reference parents not in the original map
        split_ranges = [
            {"id": "3", "minInclusive": "", "maxExclusive": "1F", "parents": ["99"]},
            {"id": "4", "minInclusive": "1F", "maxExclusive": "3F", "parents": ["99"]},
        ]

        class FullRefreshMockClient:
            def __init__(self):
                self.captured_feed_options = None
                self.call_count = 0

            @staticmethod
            def _capture_internal_headers(kwargs, etag):
                captured_headers = kwargs.get('_internal_response_headers_capture')
                if captured_headers is not None:
                    captured_headers.clear()
                    captured_headers.update({'ETag': etag})

            async def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                self.captured_feed_options = dict(feed_options) if feed_options else {}
                self.call_count += 1
                FullRefreshMockClient._capture_internal_headers(kwargs, '"test-etag-1"')
                # Call 1: initial load → good ranges
                # Call 2: incremental → split ranges (unresolvable) → retry (count 0→1)
                # Call 3: incremental retry → split ranges again (still unresolvable)
                #         → retries exhausted → fall back to full refresh (previous_map=None)
                # Call 4: full refresh → good ranges → success
                items = split_ranges if self.call_count in (2, 3) else PARTITION_KEY_RANGES
                for item in items:
                    yield item

        client = FullRefreshMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        previous_map = await cache.get_routing_map(COLLECTION_LINK, feed_options)
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        await cache.get_routing_map(
            COLLECTION_LINK,
            feed_options,
            force_refresh=True,
            previous_routing_map=previous_map,
        )
        # 1 initial + 1 failed incremental + 1 failed retry + 1 full refresh = 4 calls.
        assert client.call_count == 4
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID


    async def test_full_load_removes_stale_if_none_match_header_async(self):
        """When async _fetch_routing_map falls back to a full load (no previous
        map), any leftover IfNoneMatch header from an earlier incremental attempt
        must be removed. Otherwise, the service would return a delta instead of
        the complete set of partition key ranges."""
        captured_headers = []

        class HeaderCapturingClient:
            async def _ReadPartitionKeyRanges(self, collection_link, feed_options=None, **kwargs):
                captured_headers.append(dict(kwargs.get('headers', {})))
                CapturingMockClient._capture_internal_headers(kwargs, '"etag-full"')
                for item in PARTITION_KEY_RANGES:
                    yield item

        client = HeaderCapturingClient()
        cache = PartitionKeyRangeCache(client)

        stale_headers = {
            http_constants.HttpHeaders.IfNoneMatch: "stale-etag-should-be-removed"
        }
        await cache.get_routing_map(COLLECTION_LINK, {}, headers=stale_headers)

        assert len(captured_headers) == 1
        assert http_constants.HttpHeaders.IfNoneMatch not in captured_headers[0], (
            "IfNoneMatch must be removed on full load to prevent the service "
            "returning a delta instead of the complete set of ranges"
        )

    async def test_full_load_with_incomplete_ranges_returns_none_async(self):
        """When a full load (no previous routing map) returns ranges with gaps,
        CompleteRoutingMap returns None. The method must return None immediately
        without retrying — there is no incremental state to fall back from, and
        repeating the identical request would produce the same result."""

        class IncompleteRangesClient:
            async def _ReadPartitionKeyRanges(self, collection_link, feed_options=None, **kwargs):
                response_hook = kwargs.get("response_hook")
                if response_hook:
                    response_hook({"etag": "etag-incomplete"}, None)
                # Gap: missing the range covering 3F-7F
                for item in [
                    {"id": "0", "minInclusive": "", "maxExclusive": "3F"},
                    {"id": "2", "minInclusive": "7F", "maxExclusive": "FF"},
                ]:
                    yield item

        client = IncompleteRangesClient()
        cache = PartitionKeyRangeCache(client)

        result = await cache._fetch_routing_map(
            COLLECTION_LINK,
            _base.GetResourceIdOrFullNameFromLink(COLLECTION_LINK),
            None,  # full load (no previous map)
            {},
        )
        assert result is None, (
            "Full load with incomplete ranges must return None "
            "instead of retrying infinitely"
        )

    async def test_incremental_fallback_to_full_load_succeeds_async(self):
        """When an incremental (change-feed) update fails because a returned
        child range references a parent that does not exist in the cached map,
        the code must fall back to a full load. This test verifies that the
        fallback succeeds and produces a complete routing map."""
        call_count = [0]

        class FallbackClient:
            async def _ReadPartitionKeyRanges(self, collection_link, feed_options=None, **kwargs):
                call_count[0] += 1
                CapturingMockClient._capture_internal_headers(kwargs, f'"etag-{call_count[0]}"')

                if call_count[0] == 1:
                    # First call: incremental — return a child whose parent doesn't exist
                    yield {"id": "3", "minInclusive": "3F", "maxExclusive": "5F",
                           "parents": ["NONEXISTENT"]}
                else:
                    # Second call: full load fallback — return complete ranges
                    for item in PARTITION_KEY_RANGES:
                        yield item

        client = FallbackClient()
        cache = PartitionKeyRangeCache(client)

        # Build a previous map to trigger the incremental path
        range_tuples = [(r, True) for r in PARTITION_KEY_RANGES]
        previous_map = CollectionRoutingMap.CompleteRoutingMap(
            range_tuples, COLLECTION_LINK, "etag-old")

        result = await cache._fetch_routing_map(
            COLLECTION_LINK,
            _base.GetResourceIdOrFullNameFromLink(COLLECTION_LINK),
            previous_map,
            {}
        )
        assert result is not None, "Fallback to full load should succeed"
        assert call_count[0] == 2, "Should have called service twice: incremental + full fallback"


    async def test_upstream_response_hook_is_called_async(self):
        """When the caller passes a response_hook, it must be invoked with the
        service response headers — even though the cache also uses an internal
        hook to capture the ETag."""
        upstream_calls = []
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        await cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            feed_options,
            response_hook=lambda headers, body: upstream_calls.append(headers)
        )
        assert client.call_count == 1
        assert len(upstream_calls) == 1
        assert "etag" in upstream_calls[0]

    async def test_no_upstream_hook_still_works_async(self):
        """The cache must function correctly when no response_hook is supplied
        by the caller."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options: Dict[str, Any] = {"containerRID": CONTAINER_RID}
        result = await cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            feed_options
        )
        assert client.call_count == 1
        assert len(result) == len(PARTITION_KEY_RANGES)


if __name__ == "__main__":
    unittest.main()
