# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async integration tests for the /pkranges change-feed drain loop in
``aio.PartitionKeyRangeCache._fetch_routing_map``.

Mirrors ``test_pk_range_drain.py`` for the async provider: scripts an
``async`` generator from ``_ReadPartitionKeyRanges`` to emit multiple pages
with distinct ETags and asserts on ETag propagation, real-wire 304
preservation (empty page + unchanged ETag), the empty-page terminator, and
clean propagation of mid-drain non-304 errors.
"""

# pylint: disable=protected-access

import asyncio
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
        """An empty body materializes as HTTP 304 in the mock helper (mirrors
        the real gateway's wire shape for a drained change feed), so the drain
        terminates via the literal-304 predicate -- the same predicate peer
        SDKs (.NET / Java / Go) use. Async mirror of the sync test.
        """
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
            page_new_etag='"etag-1"',
            current_if_none_match='"etag-0"',
            new_etag='"etag-0"',
            seen_any_etag=True,
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
        """Empty body + new ETag header is the canonical "304 with fresh etag"
        wire shape. The mock helper materializes the empty body as status 304,
        so this exercises the literal-304 termination branch -- pinning that
        (a) the drain terminates, (b) the new etag is persisted on the
        returned routing map so the next drain starts from the right anchor,
        and (c) the request carried the prior etag as ``If-None-Match``.
        Async mirror of the sync test.
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

    async def test_per_page_transient_failure_is_retried_within_page_call_async(self):
        """A transient 503 during page 2 is absorbed by the per-page retry
        layer; the drain loop completes without restarting from page 1.

        Production async path: ``_ReadPartitionKeyRanges`` returns an
        ``AsyncItemPaged`` and each ``by_page()`` fetch is wrapped in
        ``_retry_utility.ExecuteAsync`` inside
        ``aio.base_execution_context._fetch_items_helper_no_retries``. So a
        transient retryable status (503) on page 2 is retried by the
        per-request retry policy *inside* the page call, and the drain loop
        only ever sees the final outcome of each page. This test pins that
        contract for the async drain.
        """
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("raise", 503, "Service Unavailable"),  # page 2, attempt 1
            ("page", page2, '"etag-2"'),            # page 2, attempt 2 (retry)
            ("page", page3, '"etag-3"'),
            ("page", [], '"etag-3"'),               # 304 / empty terminator
        ])

        underlying_side_effect = client._ReadPartitionKeyRanges.side_effect
        retry_attempts = [0]

        def with_per_page_retry_async(*args, **kwargs):
            """Mirrors ``_retry_utility.ExecuteAsync`` +
            ``_ServiceUnavailableRetryPolicy``: a 503 raised while
            materializing the page is retried once, transparently to the
            drain loop. Returns a fresh async generator so the caller's
            ``async for`` sees a clean iteration."""
            async def retried_gen():
                try:
                    inner = underlying_side_effect(*args, **kwargs)
                    async for item in inner:
                        yield item
                except CosmosHttpResponseError as e:
                    if e.status_code != 503:
                        raise
                    retry_attempts[0] += 1
                    inner = underlying_side_effect(*args, **kwargs)
                    async for item in inner:
                        yield item
            return retried_gen()

        client._ReadPartitionKeyRanges = MagicMock(side_effect=with_per_page_retry_async)

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
        )

        # Drain completed and the final routing map carries page 3's etag.
        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-3"')
        # One retry was absorbed by the per-page wrapper (page 2's 503).
        self.assertEqual(retry_attempts[0], 1)
        # 5 underlying script invocations: page1, page2-attempt1 (503),
        # page2-attempt2 (success), page3, 304-terminator.
        self.assertEqual(script.calls, 5)
        # IfNoneMatch was preserved across the retry: both page-2 attempts
        # saw '"etag-1"', proving the drain loop did NOT restart from page 1
        # (which would have started with None) and did NOT advance to
        # '"etag-2"' prematurely (which would mean it processed page 2
        # before the retry).
        self.assertEqual(
            script.if_none_match_seen,
            [None, '"etag-1"', '"etag-1"', '"etag-2"', '"etag-3"'],
        )
        # And the drain loop's outer try/except saw 4 successful page calls
        # -- the 503 was absorbed inside the per-page retry wrapper.
        self.assertEqual(client._ReadPartitionKeyRanges.call_count, 4)

    # =========================================================
    # Gap-coverage tests (option B): async mirrors of the sync
    # merge-failure cascades, cascading splits, concurrency,
    # and missing-ETag handling.
    # =========================================================

    async def test_drain_without_etag_headers_terminates_and_preserves_previous_etag_async(self):
        """Async mirror: server omits ETag header -> previous ETag preserved
        and termination still fires via the literal-304 predicate. See sync
        twin for full rationale."""
        previous_map = _make_complete_routing_map(
            collection_id="coll-noetag", etag='"etag-prev"'
        )

        client, script = _make_scripted_async_client([
            ("page", [], None),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertLogs(
            "azure.cosmos._routing._routing_map_provider_common",
            level=logging.WARNING,
        ) as log_ctx:
            routing_map = await cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll-noetag",
                collection_id="coll-noetag",
                previous_routing_map=previous_map,
                feed_options={},
            )

        self.assertEqual(script.calls, 1)
        self.assertIs(routing_map, previous_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-prev"')
        no_etag_warnings = [
            m for m in log_ctx.output if "returned no ETag" in m
        ]
        self.assertEqual(len(no_etag_warnings), 1)

    async def test_parent_not_found_falls_back_to_full_refresh_async(self):
        """Async mirror: parents-not-found -> retry -> full refresh succeeds.
        See sync twin for full rationale."""
        previous_map = _make_complete_routing_map(
            collection_id="coll-parent", etag='"etag-prev"'
        )
        orphan_child = _full_range("child", "", "FF")
        orphan_child["parents"] = ["ghost-parent"]

        full_refresh_ranges = [
            _full_range("0", "", "55"),
            _full_range("1", "55", "FF"),
        ]

        client, script = _make_scripted_async_client([
            ("page", [orphan_child], '"etag-bad-1"'),
            ("page", [], '"etag-bad-1"'),
            ("page", [orphan_child], '"etag-bad-2"'),
            ("page", [], '"etag-bad-2"'),
            ("page", full_refresh_ranges, '"etag-full"'),
            ("page", [], '"etag-full"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-parent",
            collection_id="coll-parent",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-full"')
        self.assertEqual(script.calls, 6)

    async def test_overlap_in_second_page_falls_back_to_full_refresh_async(self):
        """Async mirror: overlap from try_combine -> retry -> full refresh.
        See sync twin for full rationale."""
        previous_map = _make_complete_routing_map(
            collection_id="coll-overlap", etag='"etag-prev"'
        )

        child_b = _full_range("child-b", "", "AA")
        child_b["parents"] = ["0"]
        child_c = _full_range("child-c", "80", "FF")
        child_c["parents"] = ["0"]
        overlapping_page = [child_b, child_c]

        full_refresh_ranges = [
            _full_range("0", "", "55"),
            _full_range("1", "55", "FF"),
        ]

        client, script = _make_scripted_async_client([
            ("page", overlapping_page, '"etag-overlap-1"'),
            ("page", [], '"etag-overlap-1"'),
            ("page", overlapping_page, '"etag-overlap-2"'),
            ("page", [], '"etag-overlap-2"'),
            ("page", full_refresh_ranges, '"etag-full"'),
            ("page", [], '"etag-full"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-overlap",
            collection_id="coll-overlap",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-full"')
        self.assertEqual(script.calls, 6)

    async def test_cascading_splits_in_single_page_resolve_async(self):
        """Async mirror: cascading splits A->B+C and B->D+E in a single page
        resolve in two passes. See sync twin for full rationale."""
        previous_map = _make_complete_routing_map(
            collection_id="coll-cascading", etag='"etag-prev"'
        )

        b = _full_range("B", "", "55")
        b["parents"] = ["0"]
        c = _full_range("C", "55", "FF")
        c["parents"] = ["0"]
        d = _full_range("D", "", "33")
        d["parents"] = ["B"]
        e = _full_range("E", "33", "55")
        e["parents"] = ["B"]
        cascading_page = [d, e, b, c]

        client, script = _make_scripted_async_client([
            ("page", cascading_page, '"etag-cascading"'),
            ("page", [], '"etag-cascading"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-cascading",
            collection_id="coll-cascading",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-cascading"')
        self.assertEqual(script.calls, 2)
        # pylint: disable=protected-access
        final_ids = sorted(routing_map._rangeById.keys())
        self.assertEqual(final_ids, ["C", "D", "E"])

    async def test_concurrent_drains_for_same_collection_serialize_async(self):
        """Async mirror: N concurrent ``get_routing_map`` calls for the same
        collection result in exactly ONE ``_fetch_routing_map`` invocation.

        Distinct from the sync test because the async provider keys per-
        collection locks on ``(loop_id, collection_id)`` rather than just
        ``collection_id`` -- a regression in the async key derivation would
        not surface in the sync test.
        """
        client = MagicMock()
        provider = PartitionKeyRangeCache(client)

        fetch_count = [0]
        complete_map = _make_complete_routing_map(
            collection_id="coll-serialize", etag='"etag-serialize"'
        )

        async def slow_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):  # noqa: ARG001
            fetch_count[0] += 1
            # Hold long enough that queued coroutines observe the cached
            # result on lock release.
            await asyncio.sleep(0.05)
            return complete_map

        provider._fetch_routing_map = MagicMock(side_effect=slow_fetch)

        N = 8
        results = await asyncio.gather(*[
            provider.get_routing_map(
                collection_link="dbs/db1/colls/coll-serialize",
                feed_options={},
            )
            for _ in range(N)
        ])

        self.assertEqual(fetch_count[0], 1)
        self.assertTrue(all(r is complete_map for r in results))

    async def test_concurrent_drains_for_different_collections_do_not_serialize_async(self):
        """Async mirror: two concurrent ``get_routing_map`` calls for
        DIFFERENT collections do NOT serialize. Uses a shared barrier-like
        counted ``asyncio.Event`` (avoids ``asyncio.Barrier`` for Python 3.10
        compatibility)."""
        client = MagicMock()
        provider = PartitionKeyRangeCache(client)

        map_a = _make_complete_routing_map(collection_id="coll-A", etag='"etag-A"')
        map_b = _make_complete_routing_map(collection_id="coll-B", etag='"etag-B"')

        entered = 0
        both_in = asyncio.Event()

        async def selective_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):  # noqa: ARG001
            nonlocal entered
            entered += 1
            if entered == 2:
                both_in.set()
            # If a global lock serialized the two fetches, the second would
            # never enter and this wait would time out.
            await asyncio.wait_for(both_in.wait(), timeout=5)
            return map_a if "coll-A" in collection_link else map_b

        provider._fetch_routing_map = MagicMock(side_effect=selective_fetch)

        result_a, result_b = await asyncio.gather(
            provider.get_routing_map(
                collection_link="dbs/db1/colls/coll-A", feed_options={},
            ),
            provider.get_routing_map(
                collection_link="dbs/db1/colls/coll-B", feed_options={},
            ),
        )

        self.assertEqual(provider._fetch_routing_map.call_count, 2)
        self.assertIs(result_a, map_a)
        self.assertIs(result_b, map_b)

    async def test_caller_headers_not_mutated_by_drain_loop_async(self):
        """Async mirror: drain loop must never mutate the caller's headers.

        Regression guard for the async provider's drain loop. See the sync
        ``test_caller_headers_not_mutated_by_drain_loop`` for the full
        rationale; both providers shallow-copy ``kwargs`` per iteration and
        deep-copy the ``headers`` dict per iteration so that per-page
        ``If-None-Match`` overrides and ``prepare_fetch_options_and_headers``
        additions (``A-IM``, page-size, populate-stats) never leak back into
        the caller's dict.
        """
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        client, script = _make_scripted_async_client([
            ("page", page1, '"etag-1"'),
            ("page", page2, '"etag-2"'),
            ("page", page3, '"etag-3"'),
            ("page", [], '"etag-3"'),
        ])

        caller_headers = {"X-Custom-Marker": "value", "Authorization": "Bearer x"}
        caller_headers_snapshot = dict(caller_headers)

        cache = PartitionKeyRangeCache(client)
        routing_map = await cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
            headers=caller_headers,
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(script.calls, 4)
        self.assertEqual(caller_headers, caller_headers_snapshot)
        self.assertNotIn(http_constants.HttpHeaders.IfNoneMatch, caller_headers)
        self.assertNotIn(http_constants.HttpHeaders.AIM, caller_headers)
        self.assertEqual(
            script.if_none_match_seen,
            [None, '"etag-1"', '"etag-2"', '"etag-3"'],
        )


if __name__ == "__main__":
    unittest.main()
