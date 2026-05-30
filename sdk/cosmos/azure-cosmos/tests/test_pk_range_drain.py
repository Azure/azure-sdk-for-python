# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync integration tests for the /pkranges change-feed drain loop in
``PartitionKeyRangeCache._fetch_routing_map``.

These tests exercise the bounded multi-page drain introduced to fix the
unbounded refresh bug for containers with >~8K partition key ranges. They
mock ``_ReadPartitionKeyRanges`` so a single ``_fetch_routing_map`` call
emits multiple pages, each with its own ETag, and assert on:

  * ETag propagation across pages (per-page ``If-None-Match`` advances).
  * ``304 Not Modified`` on the first fetch preserves the previous map.
  * Empty page terminates the drain cleanly.
  * ETag-didn't-advance-with-items terminates the drain and logs a warning.
  * Safety-bound exhaustion raises HTTP 503 and does NOT poison the cache.
  * Mid-drain non-304 errors propagate without poisoning the cache.
"""

import logging
import unittest
from unittest.mock import MagicMock

import pytest

from azure.cosmos._routing.routing_map_provider import PartitionKeyRangeCache
from azure.cosmos._routing.collection_routing_map import CollectionRoutingMap
from azure.cosmos import http_constants
from azure.cosmos.exceptions import CosmosHttpResponseError


# =========================================================
# Helpers
# =========================================================

def _full_range(range_id="0", min_inclusive="", max_exclusive="FF"):
    return {
        "id": range_id,
        "minInclusive": min_inclusive,
        "maxExclusive": max_exclusive,
    }


def _split_full_range_into(n):
    """Return ``n`` non-overlapping ranges spanning ``""`` → ``FF``.

    The shape mirrors what the service emits when a container has been split
    into ``n`` physical partitions; ``process_fetched_ranges`` is happy with
    any structurally-contiguous list ending at ``FF``.
    """
    if n <= 0:
        return []
    # Build evenly spaced 2-hex-digit boundaries.
    step = 0xFF // n
    boundaries = [""]
    for i in range(1, n):
        boundaries.append(format(i * step, "02X"))
    boundaries.append("FF")
    return [
        _full_range(str(i), boundaries[i], boundaries[i + 1])
        for i in range(n)
    ]


def _make_complete_routing_map(collection_id="coll1", etag='"etag-prev"'):
    ranges = [(_full_range(), True)]
    return CollectionRoutingMap.CompleteRoutingMap(ranges, collection_id, etag)


class _PageScript:
    """Scripted ``_ReadPartitionKeyRanges`` side-effect for the drain loop.

    Each entry is one of:
      * ``('page', ranges_list, etag_value)`` -- emit a page + ETag header.
      * ``('raise_304',)`` -- raise ``CosmosHttpResponseError(304)``.
      * ``('raise', status_code, message)`` -- raise another HTTP error.

    The script records the ``If-None-Match`` header it saw on each call so
    tests can assert that the drain loop advanced the etag correctly.
    """

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.if_none_match_seen = []

    def __call__(self, collection_link, options, response_hook=None, **kwargs):  # noqa: ARG002
        in_headers = kwargs.get("headers", {}) or {}
        self.if_none_match_seen.append(
            in_headers.get(http_constants.HttpHeaders.IfNoneMatch)
        )

        if self.calls >= len(self.script):
            raise AssertionError(
                "PageScript exhausted on call #{}; only {} scripted entries.".format(
                    self.calls, len(self.script)
                )
            )
        entry = self.script[self.calls]
        self.calls += 1

        kind = entry[0]
        if kind == "raise_304":
            raise CosmosHttpResponseError(status_code=304, message="Not Modified")
        if kind == "raise":
            _, status_code, message = entry
            raise CosmosHttpResponseError(status_code=status_code, message=message)
        if kind == "page":
            _, ranges_list, etag_value = entry
            capture = kwargs.get("_internal_response_headers_capture")
            if capture is not None and etag_value is not None:
                capture[http_constants.HttpHeaders.ETag] = etag_value
            return iter(ranges_list)
        raise AssertionError("Unknown _PageScript entry: {!r}".format(entry))


def _make_scripted_client(script):
    client = MagicMock()
    script_obj = _PageScript(script)
    client._ReadPartitionKeyRanges = MagicMock(side_effect=script_obj)
    return client, script_obj


# =========================================================
# Tests
# =========================================================

@pytest.mark.cosmosEmulator
class TestPkRangeDrainSync(unittest.TestCase):
    """Sync drain-loop integration tests for PartitionKeyRangeCache."""

    def test_drain_propagates_etag_across_pages(self):
        """Three pages with distinct etags drain into one complete map.

        The drain loop must send the previous page's etag as ``If-None-Match``
        on each subsequent call, and the resulting routing map must contain
        the union of all ranges with the final etag.
        """
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("page", page2, '"etag-2"'),
            ("page", page3, '"etag-3"'),
            ("raise_304",),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-3"')
        self.assertEqual(script.calls, 4)
        # Drain starts with no If-None-Match, then advances to each prior etag.
        self.assertEqual(
            script.if_none_match_seen,
            [None, '"etag-1"', '"etag-2"', '"etag-3"'],
        )

    def test_first_fetch_304_preserves_previous_map(self):
        """A 304 on the first drain call returns the previous map untouched."""
        previous_map = _make_complete_routing_map(etag='"etag-prev"')

        client, script = _make_scripted_client([
            ("raise_304",),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIs(routing_map, previous_map)
        self.assertEqual(script.calls, 1)
        self.assertEqual(script.if_none_match_seen, ['"etag-prev"'])

    def test_empty_page_terminates_drain(self):
        """An empty page (no ranges, no new etag) ends the drain cleanly."""
        page1 = _split_full_range_into(2)

        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("page", [], None),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-1"')
        self.assertEqual(script.calls, 2)

    def test_etag_did_not_advance_with_items_warns_and_terminates(self):
        """Server returning the same etag twice with non-empty page logs a
        warning and terminates the drain to avoid an infinite loop."""
        page1 = [_full_range("0", "", "AA")]
        page2 = [_full_range("1", "AA", "FF")]

        # Page 2 echoes the same etag as page 1 -- protocol anomaly.
        client, _ = _make_scripted_client([
            ("page", page1, '"etag-stuck"'),
            ("page", page2, '"etag-stuck"'),
        ])

        cache = PartitionKeyRangeCache(client)

        with self.assertLogs(
            "azure.cosmos._routing.routing_map_provider", level="WARNING"
        ) as logs:
            routing_map = cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="coll1",
                previous_routing_map=None,
                feed_options={},
            )

        self.assertIsNotNone(routing_map)
        # The warning text mentions the stuck etag.
        self.assertTrue(
            any("ETag did not advance" in msg for msg in logs.output),
            "Expected an 'ETag did not advance' warning, got: {!r}".format(logs.output),
        )

    def test_safety_bound_exhaustion_raises_503_and_skips_cache(self):
        """If the drain never terminates within 100 pages, raise 503 and do
        NOT update the cache (incomplete maps must never reach
        ``process_fetched_ranges``)."""
        # Script 101 unique-etag pages so the loop runs to its bound.
        script_entries = [
            ("page", [_full_range(str(i), format(i, "04X"), format(i + 1, "04X"))],
             '"etag-{}"'.format(i))
            for i in range(101)
        ]

        client, script = _make_scripted_client(script_entries)
        cache = PartitionKeyRangeCache(client)

        with self.assertLogs(
            "azure.cosmos._routing.routing_map_provider", level="WARNING"
        ) as logs:
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                cache._fetch_routing_map(
                    collection_link="dbs/db1/colls/coll1",
                    collection_id="coll1",
                    previous_routing_map=None,
                    feed_options={},
                )

        self.assertEqual(
            ctx.exception.status_code,
            http_constants.StatusCodes.SERVICE_UNAVAILABLE,
        )
        # We stopped at the safety bound, not later.
        self.assertEqual(script.calls, 100)
        self.assertTrue(
            any("safety bound" in msg.lower() for msg in logs.output),
            "Expected a 'safety bound' warning, got: {!r}".format(logs.output),
        )
        # Cache must be untouched -- no entry was inserted for this collection.
        self.assertNotIn("coll1", cache._collection_routing_map_by_item)

    def test_mid_drain_non_304_error_propagates_without_caching(self):
        """A 500-class error in the middle of a drain propagates and leaves
        the cache untouched."""
        page1 = [_full_range("0", "", "AA")]

        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("raise", 500, "Internal Server Error"),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertRaises(CosmosHttpResponseError) as ctx:
            cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="coll1",
                previous_routing_map=None,
                feed_options={},
            )

        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(script.calls, 2)
        self.assertNotIn("coll1", cache._collection_routing_map_by_item)


if __name__ == "__main__":
    unittest.main()
