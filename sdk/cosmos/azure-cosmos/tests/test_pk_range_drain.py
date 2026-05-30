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
  * Real-wire ``304 Not Modified`` (empty page + unchanged ETag) on the first
    fetch preserves the previous map.
  * Empty page terminates the drain cleanly.
  * ETag-didn't-advance-with-items terminates the drain and logs a warning.
  * Safety-bound exhaustion raises HTTP 503 and does NOT poison the cache.
  * Mid-drain non-304 errors propagate without poisoning the cache.
"""

# pylint: disable=protected-access

import logging
import sys
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
        The wire status is inferred to match production: empty ``ranges_list``
        is treated as the real-wire 304 Not Modified (empty body + unchanged
        ETag header), non-empty as 200. Production never surfaces 304 as an
        exception (see ``_synchronized_request.py`` -- only ``>= 400`` raises)
        so this is the only shape the drain loop ever sees on the wire.
      * ``('page', ranges_list, etag_value, status_code)`` -- same, but with
        an explicit wire status. Use this to model server bugs (e.g. 304 with
        a non-empty body, or 200 with an empty body) when exercising the
        drain loop's defensive branches.
      * ``('raise', status_code, message)`` -- raise another HTTP error.

    The script records the ``If-None-Match`` header it saw on each call so
    tests can assert that the drain loop advanced the etag correctly.
    """

    def __init__(self, script):
        self.script = list(script)
        self.calls = 0
        self.if_none_match_seen = []
        self.a_im_seen = []

    def __call__(self, collection_link, options, response_hook=None, **kwargs):  # noqa: ARG002
        in_headers = kwargs.get("headers", {}) or {}
        self.if_none_match_seen.append(
            in_headers.get(http_constants.HttpHeaders.IfNoneMatch)
        )
        self.a_im_seen.append(
            in_headers.get(http_constants.HttpHeaders.AIM)
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
        if kind == "raise":
            _, status_code, message = entry
            raise CosmosHttpResponseError(status_code=status_code, message=message)
        if kind == "page":
            if len(entry) == 4:
                _, ranges_list, etag_value, status_code = entry
            else:
                _, ranges_list, etag_value = entry
                # Mirror the real wire: empty page == 304 Not Modified,
                # populated page == 200 OK.
                status_code = (
                    http_constants.StatusCodes.NOT_MODIFIED
                    if not ranges_list
                    else http_constants.StatusCodes.OK
                )
            capture = kwargs.get("_internal_response_headers_capture")
            if capture is not None and etag_value is not None:
                capture[http_constants.HttpHeaders.ETag] = etag_value
            status_capture = kwargs.get("_internal_response_status_capture")
            if status_capture is not None:
                status_capture[0] = status_code
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
            # Real-wire 304 terminator: empty body + unchanged ETag header.
            ("page", [], '"etag-3"'),
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
        # Wire-protocol pin: every outgoing /pkranges call must carry the
        # canonical capital-F ``A-IM: Incremental Feed`` literal. The gateway
        # accepts case-insensitive variants per RFC 3229, but the canonical
        # wire form is what every peer SDK ships -- a future cast change or
        # constant rename that flipped the case would silently alter
        # change-feed behavior server-side without this assertion.
        self.assertEqual(
            script.a_im_seen,
            [http_constants.HttpHeaders.IncrementalFeedHeaderValue] * 4,
        )

    def test_real_wire_304_via_empty_page_preserves_previous_map(self):
        """Production shape of a 304 first-fetch preserves the previous map.

        Real-wire 304s never surface as exceptions in production -- the HTTP
        client only raises for ``status >= 400`` (see
        ``_synchronized_request.py:205``). The change-feed read pipeline
        treats 304 as a success-path empty body + unchanged ETag header (see
        ``change_feed_fetcher.py:155-194`` for the canonical pattern). That
        empty page + matching ETag lands on the identity fast-path in
        ``_routing_map_provider_common.py:476-477`` and returns the previous
        map untouched.
        """
        previous_map = _make_complete_routing_map(etag='"etag-prev"')

        client, script = _make_scripted_client([
            # Real-wire 304: empty body + unchanged ETag header.
            ("page", [], '"etag-prev"'),
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

    @unittest.skipIf(
        sys.version_info < (3, 10),
        "assertNoLogs is only available on Python 3.10+",
    )
    def test_real_wire_304_does_not_emit_routing_map_warnings(self):
        """Regression pin: real-wire 304 must not emit any WARNING from the
        routing-map module. The defensive ``except status_code == 304`` branch
        that previously existed left ``seen_any_etag=False`` and tripped the
        'no ETag observed' warning. If anyone reintroduces that branch (or any
        equivalent path that bypasses ``evaluate_drain_page``), this test
        catches it before it lands.
        """
        previous_map = _make_complete_routing_map(etag='"etag-prev"')

        client, _ = _make_scripted_client([
            ("page", [], '"etag-prev"'),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertNoLogs(
            "azure.cosmos._routing", level=logging.WARNING
        ):
            cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="coll1",
                previous_routing_map=previous_map,
                feed_options={},
            )

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

    def test_evaluate_drain_page_literal_304_terminates(self):
        """Unit-pin the literal HTTP 304 termination predicate.

        ``evaluate_drain_page`` is the pure-function termination oracle for
        the drain loop. Peer SDKs (.NET/Java/Go) end the drain on a literal
        ``304 Not Modified`` status. Pin that the predicate ends the drain
        on status 304 even when the page payload is non-empty -- i.e.
        status wins over content, matching peer SDKs literally.
        """
        from azure.cosmos._routing._routing_map_provider_common import (
            evaluate_drain_page,
            _DrainPageDecision,
        )

        decision, new_etag, _next_inm, _seen = evaluate_drain_page(
            page_ranges=[_full_range("0", "", "FF")],  # non-empty body
            page_new_etag='"etag-1"',
            current_if_none_match='"etag-0"',
            new_etag='"etag-0"',
            seen_any_etag=True,
            collection_link="dbs/db1/colls/coll1",
            status_code=http_constants.StatusCodes.NOT_MODIFIED,
        )

        self.assertEqual(decision, _DrainPageDecision.STOP_DRAINED)
        # New etag from the 304 response is still adopted.
        self.assertEqual(new_etag, '"etag-1"')

    def test_literal_304_on_first_page_terminates_without_ranges(self):
        """Status 304 on the very first page short-circuits the drain.

        Models the steady-state case where a refresh is triggered but the
        routing map has not actually changed: gateway returns 304 on the
        first request and we must terminate cleanly without trying to
        build a routing map from zero ranges.
        """
        # Seed a previous map so the fetch path has something to preserve
        # when the 304 short-circuits before any ranges arrive.
        seed_page = _split_full_range_into(3)
        client, _ = _make_scripted_client([
            ("page", seed_page, '"etag-seed"'),
            ("page", [], None),
        ])
        cache = PartitionKeyRangeCache(client)
        previous_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        # Now a refresh that gets an immediate 304.
        client, script = _make_scripted_client([
            ("page", [], '"etag-seed"', 304),
        ])
        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=previous_map,
            feed_options={},
        )

        # Previous map is preserved on a no-op refresh.
        self.assertEqual(script.calls, 1)
        self.assertIsNotNone(routing_map)

    def test_empty_page_with_advanced_etag_terminates_and_bumps_etag(self):
        """Empty page with advanced etag still terminates and persists the new etag.

        The drain loop's termination decision combines two signals -- content
        emptiness and etag advancement. ``test_empty_page_terminates_drain``
        above pins the (a) "both signals say stop" path. This test pins the
        adjacent corner case (b) "etag advanced but page is empty": the loop
        must still terminate cleanly *and* persist the new etag for the next
        drain. That contract isn't obvious from reading the loop alone, and
        it's exactly the kind of predicate a future cleanup might accidentally
        invert.
        """
        page1 = _split_full_range_into(2)

        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("page", [], '"etag-new"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        # New etag is persisted even though the terminating page was empty.
        self.assertEqual(routing_map.change_feed_etag, '"etag-new"')
        self.assertEqual(script.calls, 2)
        # Second request carried the prior etag as If-None-Match.
        self.assertEqual(script.if_none_match_seen, [None, '"etag-1"'])

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
            "azure.cosmos._routing", level="WARNING"
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
            "azure.cosmos._routing", level="WARNING"
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
