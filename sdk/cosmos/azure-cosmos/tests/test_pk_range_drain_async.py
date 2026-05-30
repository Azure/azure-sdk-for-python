# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async integration tests for the /pkranges change-feed drain loop in
``aio.PartitionKeyRangeCache._fetch_routing_map``.

Mirrors ``test_pk_range_drain.py`` for the async provider: scripts an
``async`` generator from ``_ReadPartitionKeyRanges`` to emit multiple pages
with distinct ETags and asserts on ETag propagation, real-wire 304
preservation (empty page + unchanged ETag), the empty-page terminator, the
ETag-didn't-advance warning, the 503 safety bound, and clean propagation of
mid-drain non-304 errors.
"""

# pylint: disable=protected-access

import logging
import sys
import unittest
from unittest.mock import MagicMock

import pytest

from azure.cosmos._routing.aio.routing_map_provider import PartitionKeyRangeCache
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


def _make_complete_routing_map(collection_id="coll1", etag='"etag-prev"'):
    ranges = [(_full_range(), True)]
    return CollectionRoutingMap.CompleteRoutingMap(ranges, collection_id, etag)


class _AsyncPageScript:
    """Scripted async ``_ReadPartitionKeyRanges`` side-effect for the drain loop.

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

    Records the ``If-None-Match`` header seen on each call.
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
                "AsyncPageScript exhausted on call #{}; only {} scripted entries.".format(
                    self.calls, len(self.script)
                )
            )
        entry = self.script[self.calls]
        self.calls += 1

        kind = entry[0]
        if kind == "raise":
            _, status_code, message = entry
            async def raising_gen():
                raise CosmosHttpResponseError(status_code=status_code, message=message)
                yield  # pragma: no cover
            return raising_gen()

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

            async def async_gen():
                for r in ranges_list:
                    yield r
            return async_gen()

        raise AssertionError("Unknown _AsyncPageScript entry: {!r}".format(entry))


def _make_scripted_async_client(script):
    client = MagicMock()
    script_obj = _AsyncPageScript(script)
    client._ReadPartitionKeyRanges = MagicMock(side_effect=script_obj)
    return client, script_obj


# =========================================================
# Tests
# =========================================================

@pytest.mark.cosmosEmulator
class TestPkRangeDrainAsync(unittest.IsolatedAsyncioTestCase):
    """Async drain-loop integration tests for PartitionKeyRangeCache."""

    async def test_drain_propagates_etag_across_pages_async(self):
        """Three pages with distinct etags drain into one complete map."""
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("page", page2, '"etag-2"'),
            ("page", page3, '"etag-3"'),
            # Real-wire 304 terminator: empty body + unchanged ETag header.
            ("page", [], '"etag-3"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-3"')
        self.assertEqual(script.calls, 4)
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

    async def test_real_wire_304_via_empty_page_preserves_previous_map_async(self):
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

        client, script = _make_scripted_async_client([
            # Real-wire 304: empty body + unchanged ETag header.
            ("page", [], '"etag-prev"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
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
    async def test_real_wire_304_does_not_emit_routing_map_warnings_async(self):
        """Regression pin: real-wire 304 must not emit any WARNING from the
        routing-map module. Mirrors the sync test -- guards against any future
        reintroduction of a defensive ``status_code == 304`` branch that
        would leave ``seen_any_etag=False`` and trip the 'no ETag observed'
        warning.
        """
        previous_map = _make_complete_routing_map(etag='"etag-prev"')

        client, _ = _make_scripted_async_client([
            ("page", [], '"etag-prev"'),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertNoLogs(
            "azure.cosmos._routing", level=logging.WARNING
        ):
            await cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="coll1",
                previous_routing_map=previous_map,
                feed_options={},
            )

    async def test_empty_page_terminates_drain_async(self):
        """An empty page (no ranges, no new etag) ends the drain cleanly."""
        page1 = [_full_range("0", "", "FF")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("page", [], None),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-1"')
        self.assertEqual(script.calls, 2)

    async def test_evaluate_drain_page_literal_304_terminates_async(self):
        """Unit-pin the literal HTTP 304 termination predicate (async path).

        ``evaluate_drain_page`` is shared between sync and async drain loops.
        Same contract as the sync test: peer SDKs (.NET/Java/Go) terminate
        on a literal ``304 Not Modified`` regardless of payload, and so do
        we. This pins the predicate from the async test file so the async
        drain's reliance on it is visible from the async test bundle.
        """
        from azure.cosmos._routing._routing_map_provider_common import (
            evaluate_drain_page,
            _DrainPageDecision,
        )

        decision, new_etag, _next_inm, _seen = evaluate_drain_page(
            page_ranges=[_full_range("0", "", "FF")],
            page_new_etag='"etag-1"',
            current_if_none_match='"etag-0"',
            new_etag='"etag-0"',
            seen_any_etag=True,
            collection_link="dbs/db1/colls/coll1",
            status_code=http_constants.StatusCodes.NOT_MODIFIED,
        )

        self.assertEqual(decision, _DrainPageDecision.STOP_DRAINED)
        self.assertEqual(new_etag, '"etag-1"')

    async def test_literal_304_on_first_page_terminates_without_ranges_async(self):
        """Status 304 on the very first page short-circuits the async drain."""
        seed_page = [_full_range("0", "", "FF")]
        client, _ = _make_scripted_async_client([
            ("page", seed_page, '"etag-seed"'),
            ("page", [], None),
        ])
        cache = PartitionKeyRangeCache(client)
        previous_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        client, script = _make_scripted_async_client([
            ("page", [], '"etag-seed"', 304),
        ])
        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertEqual(script.calls, 1)
        self.assertIsNotNone(routing_map)

    async def test_empty_page_with_advanced_etag_terminates_and_bumps_etag_async(self):
        """Empty page with advanced etag still terminates and persists the new etag.

        The drain loop's termination decision combines two signals -- content
        emptiness and etag advancement. ``test_empty_page_terminates_drain_async``
        above pins the (a) "both signals say stop" path. This test pins the
        adjacent corner case (b) "etag advanced but page is empty": the loop
        must still terminate cleanly *and* persist the new etag for the next
        drain. That contract isn't obvious from reading the loop alone, and
        it's exactly the kind of predicate a future cleanup might accidentally
        invert.
        """
        page1 = [_full_range("0", "", "FF")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("page", [], '"etag-new"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
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

    async def test_etag_did_not_advance_with_items_warns_and_terminates_async(self):
        """Same etag echoed twice with non-empty page → warning + terminate."""
        page1 = [_full_range("0", "", "AA")]
        page2 = [_full_range("1", "AA", "FF")]

        client, _ = _make_scripted_async_client([
            ("page", page1, '"etag-stuck"'),
            ("page", page2, '"etag-stuck"'),
        ])

        cache = PartitionKeyRangeCache(client)

        with self.assertLogs(
            "azure.cosmos._routing", level="WARNING"
        ) as logs:
            routing_map = await cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll1",
                collection_id="coll1",
                previous_routing_map=None,
                feed_options={},
            )

        self.assertIsNotNone(routing_map)
        self.assertTrue(
            any("ETag did not advance" in msg for msg in logs.output),
            "Expected an 'ETag did not advance' warning, got: {!r}".format(logs.output),
        )

    async def test_safety_bound_exhaustion_raises_503_and_skips_cache_async(self):
        """Safety bound exhaustion raises 503 and leaves the cache untouched."""
        script_entries = [
            ("page", [_full_range(str(i), format(i, "04X"), format(i + 1, "04X"))],
             '"etag-{}"'.format(i))
            for i in range(101)
        ]

        client, script = _make_scripted_async_client(script_entries)
        cache = PartitionKeyRangeCache(client)

        with self.assertLogs(
            "azure.cosmos._routing", level="WARNING"
        ) as logs:
            with self.assertRaises(CosmosHttpResponseError) as ctx:
                await cache._fetch_routing_map(
                    collection_link="dbs/db1/colls/coll1",
                    collection_id="coll1",
                    previous_routing_map=None,
                    feed_options={},
                )

        self.assertEqual(
            ctx.exception.status_code,
            http_constants.StatusCodes.SERVICE_UNAVAILABLE,
        )
        self.assertEqual(script.calls, 100)
        self.assertTrue(
            any("safety bound" in msg.lower() for msg in logs.output),
            "Expected a 'safety bound' warning, got: {!r}".format(logs.output),
        )
        self.assertNotIn("coll1", cache._collection_routing_map_by_item)

    async def test_mid_drain_non_304_error_propagates_without_caching_async(self):
        """A 500-class error mid-drain propagates without poisoning the cache."""
        page1 = [_full_range("0", "", "AA")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("raise", 500, "Internal Server Error"),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertRaises(CosmosHttpResponseError) as ctx:
            await cache._fetch_routing_map(
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
