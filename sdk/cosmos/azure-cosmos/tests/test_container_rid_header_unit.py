# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Unit tests to verify that the `containerRID` option (which becomes the
`x-ms-cosmos-intended-collection-rid` HTTP header) flows through every
code path that can trigger a partition key range fetch.

"""

import unittest
from typing import Optional, Mapping, Any
from azure.cosmos._routing import routing_range
from azure.cosmos._routing.routing_map_provider import (
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
    """A mock CosmosClientConnection that records the feed_options passed
    to _ReadPartitionKeyRanges so tests can assert on them."""

    def __init__(self, partition_key_ranges=None):
        self.partition_key_ranges = partition_key_ranges or PARTITION_KEY_RANGES
        self.captured_feed_options = None
        self.call_count = 0

    def _ReadPartitionKeyRanges(
        self,
        _collection_link: str,
        feed_options: Optional[Mapping[str, Any]] = None,
        **kwargs
    ):
        self.captured_feed_options = dict(feed_options) if feed_options else {}
        self.call_count += 1
        # Invoke the response_hook if provided (the cache uses it to capture etag)
        response_hook = kwargs.get("response_hook")
        if response_hook:
            response_hook({"etag": "test-etag-1"}, None)
        return iter(self.partition_key_ranges)


class TestContainerRIDHeaderUnit(unittest.TestCase):
    """Verifies that the containerRID feed option (which becomes the
    x-ms-cosmos-intended-collection-rid HTTP header) flows correctly through
    format_pk_range_options, PartitionKeyRangeCache, SmartRoutingMapProvider,
    response_hook chaining, cache staleness detection, and the incremental-
    to-full-load fallback path."""

    # ----- format_pk_range_options (sanitizer) -----

    def test_format_pk_range_options_containerRID_passes_through(self):
        """Only allowlisted keys like containerRID should survive sanitization;
        unknown keys must be stripped."""
        result = _base.format_pk_range_options({"containerRID": CONTAINER_RID, "somethingElse": 123})
        assert result["containerRID"] == CONTAINER_RID
        assert "somethingElse" not in result

    def test_format_pk_range_options_missing_returns_empty(self):
        """When the caller does not supply any allowlisted key, the sanitized
        result must be empty — whether the input contains unknown keys or is
        itself empty."""
        assert _base.format_pk_range_options({"somethingElse": 123}) == {}
        assert _base.format_pk_range_options({}) == {}

    def test_format_pk_range_options_excludedLocations_passes_through(self):
        """Both containerRID and excludedLocations are allowlisted and must
        survive sanitization together."""
        result = _base.format_pk_range_options({
            "containerRID": CONTAINER_RID,
            "excludedLocations": ["West US"]
        })
        assert result["containerRID"] == CONTAINER_RID
        assert result["excludedLocations"] == ["West US"]

    # ----- PartitionKeyRangeCache -----

    def test_initial_load_passes_containerRID(self):
        """On a cold cache, the containerRID from the caller's feed_options
        must be forwarded to _ReadPartitionKeyRanges so the service knows
        which physical container to query."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            {"containerRID": CONTAINER_RID}
        )
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID

    def test_cache_hit_does_not_call_service(self):
        """A second lookup against the same collection must be served entirely
        from the in-memory cache — no additional service call."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options = {"containerRID": CONTAINER_RID}
        cache.get_overlapping_ranges(COLLECTION_LINK, [routing_range.Range("", "FF", True, False)], feed_options)
        assert client.call_count == 1
        cache.get_overlapping_ranges(COLLECTION_LINK, [routing_range.Range("", "3F", True, False)], feed_options)
        assert client.call_count == 1, "Cache hit should not trigger another service call"

    # ----- End-to-end: SmartRoutingMapProvider -> Cache -> _ReadPartitionKeyRanges -----

    def test_end_to_end_containerRID_and_pk_range_flag(self):
        """Verifies the full path: SmartRoutingMapProvider delegates to
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
        provider.get_overlapping_ranges(COLLECTION_LINK, ranges, {"containerRID": CONTAINER_RID})
        assert client.call_count >= 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        assert client.captured_feed_options.get("_internal_pk_range_fetch") is True

    def test_end_to_end_without_containerRID_omits_header(self):
        """When the caller does not supply containerRID, it must not appear
        in the feed_options that reach _ReadPartitionKeyRanges."""
        client = CapturingMockClient()
        provider = SmartRoutingMapProvider(client)
        provider.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            {}
        )
        assert "containerRID" not in client.captured_feed_options

    def test_force_refresh_preserves_containerRID(self):
        """A force_refresh (triggered by split/merge errors) must re-send
        containerRID to the service so the correct physical container is
        queried again."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        feed_options = {"containerRID": CONTAINER_RID}
        previous_map = cache.get_routing_map(COLLECTION_LINK, feed_options)
        assert client.call_count == 1
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID
        cache.get_routing_map(
            COLLECTION_LINK,
            feed_options,
            force_refresh=True,
            previous_routing_map=previous_map,
        )
        # In this mock setup, incremental refresh has no split/merge deltas and
        # falls back to a full refresh, so force-refresh performs two reads.
        assert client.call_count == 3
        assert client.captured_feed_options.get("containerRID") == CONTAINER_RID

    # ----- Cache staleness detection -----

    def _make_cache_with_map(self, collection_id, etag):
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        range_tuples = [(r, True) for r in PARTITION_KEY_RANGES]
        routing_map = CollectionRoutingMap.CompleteRoutingMap(range_tuples, collection_id, etag)
        cache._collection_routing_map_by_item[collection_id] = routing_map
        return cache, routing_map

    def _make_previous_map(self, collection_id, etag):
        range_tuples = [(r, True) for r in PARTITION_KEY_RANGES]
        return CollectionRoutingMap.CompleteRoutingMap(range_tuples, collection_id, etag)

    def test_cache_staleness_false_when_no_previous_map(self):
        """Without a previous routing map to compare against, the cache
        cannot be considered stale — it may simply be the first load."""
        cache, _ = self._make_cache_with_map(COLLECTION_LINK, "etag-1")
        assert cache._is_cache_stale(COLLECTION_LINK, None) is False

    def test_cache_staleness_false_when_cache_is_empty(self):
        """If the cache has no entry for this collection, staleness is
        irrelevant — the caller will do a full load regardless."""
        cache = PartitionKeyRangeCache(CapturingMockClient())
        previous_map = self._make_previous_map(COLLECTION_LINK, "etag-1")
        assert cache._is_cache_stale(COLLECTION_LINK, previous_map) is False

    def test_cache_staleness_true_when_etags_match(self):
        """When the cached map's ETag matches the caller's previous map,
        the cache is stale — the caller already saw this version and is
        asking for a newer one (e.g. after a 410 split error)."""
        cache, _ = self._make_cache_with_map(COLLECTION_LINK, "etag-1")
        previous_map = self._make_previous_map(COLLECTION_LINK, "etag-1")
        assert cache._is_cache_stale(COLLECTION_LINK, previous_map) is True

    def test_cache_staleness_false_when_etags_differ(self):
        """When the cached map has a different (newer) ETag, the cache is
        fresh — another thread already refreshed it."""
        cache, _ = self._make_cache_with_map(COLLECTION_LINK, "etag-2")
        previous_map = self._make_previous_map(COLLECTION_LINK, "etag-1")
        assert cache._is_cache_stale(COLLECTION_LINK, previous_map) is False

    # ----- Incremental-to-full-load fallback and recursion guard -----

    def test_full_load_removes_stale_if_none_match_header(self):
        """When _fetch_routing_map falls back to a full load (no previous map),
        any leftover IfNoneMatch header from an earlier incremental attempt must
        be removed. Otherwise the service would return a delta instead of the
        complete set of partition key ranges."""
        captured_headers = []

        class HeaderCapturingClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                captured_headers.append(dict(kwargs.get('headers', {})))
                response_hook = kwargs.get("response_hook")
                if response_hook:
                    response_hook({"etag": "etag-full"}, None)
                return iter(PARTITION_KEY_RANGES)

        client = HeaderCapturingClient()
        cache = PartitionKeyRangeCache(client)

        # Simulate a full load where kwargs already contain a stale IfNoneMatch
        # (this is the scenario where a recursive fallback inherits kwargs)
        stale_headers = {
            http_constants.HttpHeaders.IfNoneMatch: "stale-etag-should-be-removed"
        }
        cache.get_routing_map(COLLECTION_LINK, {}, headers=stale_headers)

        assert len(captured_headers) == 1
        assert http_constants.HttpHeaders.IfNoneMatch not in captured_headers[0], (
            "IfNoneMatch must be removed on full load to prevent the service "
            "returning a delta instead of the complete set of ranges"
        )

    def test_full_load_with_incomplete_ranges_returns_none(self):
        """When a full load (no previous routing map) returns ranges with gaps,
        CompleteRoutingMap returns None. The method must return None immediately
        without retrying — there is no incremental state to fall back from, and
        repeating the identical request would produce the same result."""

        class IncompleteRangesClient:
            """Returns ranges with a gap — CompleteRoutingMap will return None."""
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                response_hook = kwargs.get("response_hook")
                if response_hook:
                    response_hook({"etag": "etag-incomplete"}, None)
                # Gap: missing the range covering 3F-7F
                return iter([
                    {"id": "0", "minInclusive": "", "maxExclusive": "3F"},
                    {"id": "2", "minInclusive": "7F", "maxExclusive": "FF"},
                ])

        client = IncompleteRangesClient()
        cache = PartitionKeyRangeCache(client)

        result = cache._fetch_routing_map(
            COLLECTION_LINK,
            _base.GetResourceIdOrFullNameFromLink(COLLECTION_LINK),
            None,  # full load (no previous map)
            {},
        )
        assert result is None, (
            "Full load with incomplete ranges must return None "
            "instead of retrying infinitely"
        )

    def test_incremental_fallback_to_full_load_succeeds(self):
        """When an incremental (change-feed) update fails because a returned
        child range references a parent that does not exist in the cached map,
        the code must fall back to a full load. This test verifies that the
        fallback succeeds and produces a complete routing map."""
        call_count = [0]

        class FallbackClient:
            def _ReadPartitionKeyRanges(self, _collection_link, feed_options=None, **kwargs):
                call_count[0] += 1
                response_hook = kwargs.get("response_hook")
                if response_hook:
                    response_hook({"etag": f"etag-{call_count[0]}"}, None)

                if call_count[0] == 1:
                    # First call: incremental — return a child whose parent doesn't exist
                    return iter([
                        {"id": "3", "minInclusive": "3F", "maxExclusive": "5F",
                         "parents": ["NONEXISTENT"]},
                    ])
                else:
                    # Second call: full load fallback — return complete ranges
                    return iter(PARTITION_KEY_RANGES)

        client = FallbackClient()
        cache = PartitionKeyRangeCache(client)

        # Build a previous map to trigger the incremental path
        range_tuples = [(r, True) for r in PARTITION_KEY_RANGES]
        previous_map = CollectionRoutingMap.CompleteRoutingMap(
            range_tuples, COLLECTION_LINK, "etag-old")

        result = cache._fetch_routing_map(
            COLLECTION_LINK,
            _base.GetResourceIdOrFullNameFromLink(COLLECTION_LINK),
            previous_map,
            {}
        )
        assert result is not None, "Fallback to full load should succeed"
        assert call_count[0] == 2, "Should have called service twice: incremental + full fallback"

    # ----- response_hook chaining -----

    def test_upstream_response_hook_is_called(self):
        """When the caller passes a response_hook, it must be invoked with the
        service response headers — even though the cache also uses an internal
        hook to capture the ETag."""
        upstream_calls = []
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            {"containerRID": CONTAINER_RID},
            response_hook=lambda headers, body: upstream_calls.append(headers)
        )
        assert client.call_count == 1
        assert len(upstream_calls) == 1
        assert "etag" in upstream_calls[0]

    def test_no_upstream_hook_still_works(self):
        """The cache must function correctly when no response_hook is supplied
        by the caller."""
        client = CapturingMockClient()
        cache = PartitionKeyRangeCache(client)
        result = cache.get_overlapping_ranges(
            COLLECTION_LINK,
            [routing_range.Range("", "FF", True, False)],
            {"containerRID": CONTAINER_RID}
        )
        assert client.call_count == 1
        assert len(result) == len(PARTITION_KEY_RANGES)


if __name__ == "__main__":
    unittest.main()
