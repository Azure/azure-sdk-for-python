# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async integration tests for the /pkranges change-feed drain loop in
``aio.PartitionKeyRangeCache._fetch_routing_map``.

Mirrors ``test_pk_range_drain.py`` for the async provider: scripts an
``async`` generator from ``_ReadPartitionKeyRanges`` to emit multiple pages
with distinct ETags and asserts on ETag propagation, 304 preservation, the
empty-page terminator, the ETag-didn't-advance warning, the 503 safety
bound, and clean propagation of mid-drain non-304 errors.
"""

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
      * ``('raise_304',)`` -- raise ``CosmosHttpResponseError(304)``.
      * ``('raise', status_code, message)`` -- raise another HTTP error.

    Records the ``If-None-Match`` header seen on each call.
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
                "AsyncPageScript exhausted on call #{}; only {} scripted entries.".format(
                    self.calls, len(self.script)
                )
            )
        entry = self.script[self.calls]
        self.calls += 1

        kind = entry[0]
        if kind == "raise_304":
            # The caller does ``async for item in pk_range_generator``. We need
            # the raise to surface from that consumption. Returning a generator
            # that raises on first iteration achieves that.
            async def raising_gen_304():
                raise CosmosHttpResponseError(status_code=304, message="Not Modified")
                yield  # pragma: no cover -- unreachable but makes this an async generator
            return raising_gen_304()

        if kind == "raise":
            _, status_code, message = entry
            async def raising_gen():
                raise CosmosHttpResponseError(status_code=status_code, message=message)
                yield  # pragma: no cover
            return raising_gen()

        if kind == "page":
            _, ranges_list, etag_value = entry
            capture = kwargs.get("_internal_response_headers_capture")
            if capture is not None and etag_value is not None:
                capture[http_constants.HttpHeaders.ETag] = etag_value

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
            ("raise_304",),
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

    async def test_first_fetch_304_preserves_previous_map_async(self):
        """A 304 on the first drain call returns the previous map untouched."""
        previous_map = _make_complete_routing_map(etag='"etag-prev"')

        client, script = _make_scripted_async_client([
            ("raise_304",),
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
            "azure.cosmos._routing.aio.routing_map_provider", level="WARNING"
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
            "azure.cosmos._routing.aio.routing_map_provider", level="WARNING"
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
