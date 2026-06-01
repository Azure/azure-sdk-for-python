# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Sync integration tests for the /pkranges change-feed drain loop in
``PartitionKeyRangeCache._fetch_routing_map``.

These tests exercise the multi-page drain introduced to fix the
unbounded refresh bug for containers with >~8K partition key ranges. They
mock ``_ReadPartitionKeyRanges`` so a single ``_fetch_routing_map`` call
emits multiple pages, each with its own ETag, and assert on:

  * ETag propagation across pages (per-page ``If-None-Match`` advances).
  * Real-wire ``304 Not Modified`` (empty page + unchanged ETag) on the first
    fetch preserves the previous map.
  * Empty page terminates the drain cleanly.
  * Mid-drain non-304 errors propagate without poisoning the cache.
"""

# pylint: disable=protected-access

import logging
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
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
        """An empty body materializes as HTTP 304 in the mock helper (mirrors
        the real gateway's wire shape for a drained change feed), so the drain
        terminates via the literal-304 predicate -- the same predicate peer
        SDKs (.NET / Java / Go) use. This pins that the helper's empty->304
        mapping reaches the production termination decision.
        """
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
            page_new_etag='"etag-1"',
            current_if_none_match='"etag-0"',
            new_etag='"etag-0"',
            seen_any_etag=True,
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
        """Empty body + new ETag header is the canonical "304 with fresh etag"
        wire shape (the gateway tells us the routing map is fully drained and
        hands us a new continuation anchor for the next refresh). The mock
        helper materializes the empty body as status 304, so this exercises
        the literal-304 termination branch -- pinning that (a) the drain
        terminates, (b) the new etag is persisted on the returned routing map
        so the next drain starts from the right anchor, and (c) the request
        carried the prior etag as ``If-None-Match``. Matches the .NET / Java /
        Go termination semantics.
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

    def test_per_page_transient_failure_is_retried_within_page_call(self):
        """A transient 503 during page 2 is absorbed by the per-page retry
        layer; the drain loop completes without restarting from page 1.

        In production, ``_ReadPartitionKeyRanges`` returns an ``ItemPaged``
        and each ``by_page()`` fetch is wrapped in ``_retry_utility.Execute``
        inside ``base_execution_context._fetch_items_helper_no_retries``.
        So a transient retryable status (503) on page 2 is retried by the
        per-request retry policy *inside* the page call, and the drain loop
        only ever sees the final outcome of each page. This test pins that
        contract: pages 1, 3 succeed on first attempt, page 2 succeeds on
        the retry, and the final routing map reflects all three pages with
        no whole-drain restart.
        """
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        # Underlying script: the 503 between page1 and page2 is absorbed by
        # the per-page retry wrapper below, so the drain loop never sees it.
        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("raise", 503, "Service Unavailable"),  # page 2, attempt 1
            ("page", page2, '"etag-2"'),            # page 2, attempt 2 (retry)
            ("page", page3, '"etag-3"'),
            ("page", [], '"etag-3"'),               # 304 / empty terminator
        ])

        underlying_side_effect = client._ReadPartitionKeyRanges.side_effect
        retry_attempts = [0]

        def with_per_page_retry(*args, **kwargs):
            """Mirrors what ``_retry_utility.Execute`` +
            ``_ServiceUnavailableRetryPolicy`` do for a retryable 503: one
            retry per page call, transparent to the caller."""
            try:
                return underlying_side_effect(*args, **kwargs)
            except CosmosHttpResponseError as e:
                if e.status_code == 503:
                    retry_attempts[0] += 1
                    return underlying_side_effect(*args, **kwargs)
                raise

        client._ReadPartitionKeyRanges = MagicMock(side_effect=with_per_page_retry)

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
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
        # And the only call the drain loop's outer try/except saw was the
        # successful retry -- the 503 never surfaced.
        self.assertEqual(client._ReadPartitionKeyRanges.call_count, 4)

    # =========================================================
    # Gap-coverage tests (option B): merge-failure cascades,
    # cascading splits, concurrency, missing-ETag handling.
    # =========================================================

    def test_drain_without_etag_headers_terminates_and_preserves_previous_etag(self):
        """Server omits ETag header entirely -- drain still terminates cleanly
        and the previous ETag is preserved on the returned routing map.

        Peer SDKs (.NET v3 ``PartitionKeyRangeCache.cs``, Java
        ``RxPartitionKeyRangeCache.java``) both trust the gateway to emit an
        ETag and have no defensive cap when one is missing; .NET nulls out
        the continuation, Java reads it as null. Python's behavior is
        slightly safer: ``process_fetched_ranges`` preserves the previous
        ETag and logs a WARNING. This test pins that contract so a future
        refactor cannot silently swap to nullification (which would force a
        full re-drain on the next refresh).
        """
        previous_map = _make_complete_routing_map(
            collection_id="coll-noetag", etag='"etag-prev"'
        )

        # Single empty page with no ETag header. Empty body auto-maps to 304
        # in the helper, so the drain terminates immediately via the literal-
        # 304 predicate -- but ``seen_any_etag`` stays False because the
        # response carried no ETag.
        client, script = _make_scripted_client([
            ("page", [], None),
        ])

        cache = PartitionKeyRangeCache(client)
        with self.assertLogs(
            "azure.cosmos._routing._routing_map_provider_common",
            level=logging.WARNING,
        ) as log_ctx:
            routing_map = cache._fetch_routing_map(
                collection_link="dbs/db1/colls/coll-noetag",
                collection_id="coll-noetag",
                previous_routing_map=previous_map,
                feed_options={},
            )

        self.assertEqual(script.calls, 1)
        # Previous map (and its ETag) is preserved; no defensive cap fires.
        self.assertIs(routing_map, previous_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-prev"')
        # WARNING was emitted exactly once for the missing-ETag case.
        no_etag_warnings = [
            m for m in log_ctx.output if "returned no ETag" in m
        ]
        self.assertEqual(len(no_etag_warnings), 1)

    def test_parent_not_found_falls_back_to_full_refresh(self):
        """Incremental merge with unknown parent IDs -> retry -> full refresh.

        The page's child ranges declare parents that are not present in the
        cached map. ``process_fetched_ranges`` raises ``_IncrementalMergeFailed``
        from the parents-not-found branch. The provider then:
          1. Retries the incremental fetch once with the same previous map.
          2. On the second incremental failure, sets ``current_previous_map=None``
             and falls back to a full refresh.
          3. The full refresh succeeds and returns a complete map.

        This pins the multi-layered fallback chain end-to-end, including the
        boundary where the provider transitions from incremental retry to
        full-refresh recovery. Without this test, a future refactor of the
        retry cascade could silently collapse to "fail on first incremental
        error" with no failing test signal.
        """
        previous_map = _make_complete_routing_map(
            collection_id="coll-parent", etag='"etag-prev"'
        )
        # Child range claims parent "ghost-parent" which is NOT in previous_map
        # (whose only range is id "0"). process_fetched_ranges will fail on
        # parents-not-found.
        orphan_child = _full_range("child", "", "FF")
        orphan_child["parents"] = ["ghost-parent"]

        # The full-refresh page is a complete, parent-free range set.
        full_refresh_ranges = _split_full_range_into(2)

        client, script = _make_scripted_client([
            # Drain attempt 1 (incremental): orphan child -> raises -> retry.
            ("page", [orphan_child], '"etag-bad-1"'),
            ("page", [], '"etag-bad-1"'),
            # Drain attempt 2 (incremental retry): same outcome -> fall back.
            ("page", [orphan_child], '"etag-bad-2"'),
            ("page", [], '"etag-bad-2"'),
            # Drain attempt 3 (full refresh, previous_map=None): clean ranges.
            ("page", full_refresh_ranges, '"etag-full"'),
            ("page", [], '"etag-full"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-parent",
            collection_id="coll-parent",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        # Final map came from the full-refresh path.
        self.assertEqual(routing_map.change_feed_etag, '"etag-full"')
        # All six scripted entries were consumed: 2 attempts x 2 pages
        # (incremental) + 2 pages (full refresh).
        self.assertEqual(script.calls, 6)

    def test_overlap_in_second_page_falls_back_to_full_refresh(self):
        """Incremental merge with overlapping ranges -> retry -> full refresh.

        ``try_combine`` raises ``ValueError("Ranges overlap...")`` when the
        merged range set is not a clean partition cover (e.g. two split
        children that both claim the same byte range due to an out-of-order or
        duplicated split notification). ``process_fetched_ranges`` translates
        this into ``_IncrementalMergeFailed``; the provider then retries
        incrementally and falls back to a full refresh.

        Distinct from the parent-not-found test above: that one fires at
        L461 (parents-not-found), this one fires at L479 (overlap from
        ``try_combine``). Both must independently trigger the same recovery
        cascade.
        """
        # Previous map: single range A covering the full PK space.
        previous_map = _make_complete_routing_map(
            collection_id="coll-overlap", etag='"etag-prev"'
        )

        # Two split children that BOTH claim parent "0" (the only range in
        # previous_map) but their ranges OVERLAP: B covers ["", "AA") and C
        # covers ["80", "FF"). 0x80 < 0xAA, so the merged set is not a clean
        # partition -> try_combine raises ValueError("Ranges overlap").
        child_b = _full_range("child-b", "", "AA")
        child_b["parents"] = ["0"]
        child_c = _full_range("child-c", "80", "FF")
        child_c["parents"] = ["0"]
        overlapping_page = [child_b, child_c]

        full_refresh_ranges = _split_full_range_into(2)

        client, script = _make_scripted_client([
            # Drain attempt 1 (incremental): overlap -> raises -> retry.
            ("page", overlapping_page, '"etag-overlap-1"'),
            ("page", [], '"etag-overlap-1"'),
            # Drain attempt 2 (incremental retry): same outcome -> fall back.
            ("page", overlapping_page, '"etag-overlap-2"'),
            ("page", [], '"etag-overlap-2"'),
            # Drain attempt 3 (full refresh, previous_map=None): clean ranges.
            ("page", full_refresh_ranges, '"etag-full"'),
            ("page", [], '"etag-full"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-overlap",
            collection_id="coll-overlap",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-full"')
        self.assertEqual(script.calls, 6)

    def test_cascading_splits_in_single_page_resolve(self):
        """Cascading splits (A->B+C, then B->D+E) in a single page resolve in
        two passes via the ``unresolved``/``progress_made`` queue.

        The page is intentionally ordered ``[D, E, B, C]`` so that on pass 1
        the merge loop encounters D and E *before* B is known. D and E
        declare parent B (not in the prior map), so they cannot resolve.
        B and C resolve via parent A. Pass 2 then resolves D and E because
        B is now in ``known_range_info_by_id``. This pins the inner
        breadth-first resolution loop in ``process_fetched_ranges``.
        """
        # Prior map: single range A covering the full PK space.
        previous_map = _make_complete_routing_map(
            collection_id="coll-cascading", etag='"etag-prev"'
        )

        # B and C split from A; D and E then split from B -- all in one page.
        b = _full_range("B", "", "55")
        b["parents"] = ["0"]
        c = _full_range("C", "55", "FF")
        c["parents"] = ["0"]
        d = _full_range("D", "", "33")
        d["parents"] = ["B"]
        e = _full_range("E", "33", "55")
        e["parents"] = ["B"]
        # Ordering forces the two-pass behavior: D/E come before B in the
        # iteration order.
        cascading_page = [d, e, b, c]

        client, script = _make_scripted_client([
            ("page", cascading_page, '"etag-cascading"'),
            ("page", [], '"etag-cascading"'),
        ])

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll-cascading",
            collection_id="coll-cascading",
            previous_routing_map=previous_map,
            feed_options={},
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(routing_map.change_feed_etag, '"etag-cascading"')
        self.assertEqual(script.calls, 2)
        # Final map covers the full PK space via the leaf ranges D, E, C
        # (A and B are gone after the cascading split).
        # pylint: disable=protected-access
        final_ids = sorted(routing_map._rangeById.keys())
        self.assertEqual(final_ids, ["C", "D", "E"])

    def test_concurrent_drains_for_same_collection_serialize(self):
        """N concurrent ``get_routing_map`` calls for the same collection
        result in exactly ONE ``_fetch_routing_map`` invocation; all callers
        receive the same map object.

        Pins the per-collection lock in ``get_routing_map``: without it, a
        cold-cache burst from a worker pool would thunder N parallel /pkranges
        drains. A future refactor that accidentally removed the lock (or
        widened the fast-path read past the cache check) would surface here.
        """
        # We're testing the lock around _fetch_routing_map -- mock it
        # directly. This isolates the locking contract from the drain loop.
        client = MagicMock()
        provider = PartitionKeyRangeCache(client)

        fetch_count = [0]
        complete_map = _make_complete_routing_map(
            collection_id="coll-serialize", etag='"etag-serialize"'
        )

        def slow_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):  # noqa: ARG001
            fetch_count[0] += 1
            # Hold the lock long enough that queued callers definitely
            # observe the same cached result on lock release.
            time.sleep(0.05)
            return complete_map

        provider._fetch_routing_map = MagicMock(side_effect=slow_fetch)

        N = 8
        barrier = threading.Barrier(N)

        def caller():
            barrier.wait(timeout=5)
            return provider.get_routing_map(
                collection_link="dbs/db1/colls/coll-serialize",
                feed_options={},
            )

        with ThreadPoolExecutor(max_workers=N) as ex:
            futures = [ex.submit(caller) for _ in range(N)]
            results = [f.result(timeout=10) for f in futures]

        # The per-collection lock serialized the burst: exactly one fetch
        # ran; the other N-1 callers hit the post-lock cache check.
        self.assertEqual(fetch_count[0], 1)
        # All callers received the same cached map object (identity check).
        self.assertTrue(all(r is complete_map for r in results))

    def test_concurrent_drains_for_different_collections_do_not_serialize(self):
        """Two concurrent ``get_routing_map`` calls for DIFFERENT collections
        do NOT serialize against each other.

        Pins the lock GRANULARITY: a future refactor that replaced the
        per-collection lock with a single global lock would force unrelated
        collection refreshes to queue, hurting throughput. The test uses a
        shared barrier *inside* the fetch to prove both fetches were live at
        the same time -- a global lock would deadlock the barrier.
        """
        client = MagicMock()
        provider = PartitionKeyRangeCache(client)

        map_a = _make_complete_routing_map(collection_id="coll-A", etag='"etag-A"')
        map_b = _make_complete_routing_map(collection_id="coll-B", etag='"etag-B"')

        # Both fetches must enter before either exits. If a global lock
        # serialized them, the second fetch would not enter until the first
        # released -- and the barrier would time out.
        in_fetch_barrier = threading.Barrier(2, timeout=5)

        def selective_fetch(collection_link, collection_id, previous_routing_map, feed_options, **kwargs):  # noqa: ARG001
            in_fetch_barrier.wait()
            return map_a if "coll-A" in collection_link else map_b

        provider._fetch_routing_map = MagicMock(side_effect=selective_fetch)

        start_barrier = threading.Barrier(2)

        def caller(collection_link):
            start_barrier.wait(timeout=5)
            return provider.get_routing_map(
                collection_link=collection_link, feed_options={},
            )

        with ThreadPoolExecutor(max_workers=2) as ex:
            f_a = ex.submit(caller, "dbs/db1/colls/coll-A")
            f_b = ex.submit(caller, "dbs/db1/colls/coll-B")
            result_a = f_a.result(timeout=10)
            result_b = f_b.result(timeout=10)

        # Both fetches ran (no global serialization swallowed one of them).
        self.assertEqual(provider._fetch_routing_map.call_count, 2)
        # Each caller received the map for its own collection.
        self.assertIs(result_a, map_a)
        self.assertIs(result_b, map_b)

    def test_caller_headers_not_mutated_by_drain_loop(self):
        """Drain loop must never mutate the caller's ``headers`` dict.

        Regression guard: the drain loop receives an arbitrary ``kwargs``
        dict from upstream and forwards it (via shallow-copy + per-iter
        header dict-copy) to every ``_ReadPartitionKeyRanges`` call. It must
        not leak per-iter mutations -- ``If-None-Match`` overrides, sidecar
        captures, or ``prepare_fetch_options_and_headers`` additions
        (``A-IM``, page-size, populate-stats, etc.) -- back into the
        caller's dict. A regression here would silently poison the next
        outbound request from the same caller (e.g. a stale
        ``If-None-Match`` carried into an unrelated read).
        """
        page1 = [_full_range("0", "", "55")]
        page2 = [_full_range("1", "55", "AA")]
        page3 = [_full_range("2", "AA", "FF")]

        client, script = _make_scripted_client([
            ("page", page1, '"etag-1"'),
            ("page", page2, '"etag-2"'),
            ("page", page3, '"etag-3"'),
            ("page", [], '"etag-3"'),
        ])

        # Sentinel headers from the caller -- snapshot up front so we can
        # diff against the post-drain state.
        caller_headers = {"X-Custom-Marker": "value", "Authorization": "Bearer x"}
        caller_headers_snapshot = dict(caller_headers)

        cache = PartitionKeyRangeCache(client)
        routing_map = cache._fetch_routing_map(
            collection_link="dbs/db1/colls/coll1",
            collection_id="coll1",
            previous_routing_map=None,
            feed_options={},
            headers=caller_headers,
        )

        self.assertIsNotNone(routing_map)
        self.assertEqual(script.calls, 4)
        # Caller's dict identity AND contents are unchanged after the drain.
        self.assertEqual(caller_headers, caller_headers_snapshot)
        self.assertNotIn(http_constants.HttpHeaders.IfNoneMatch, caller_headers)
        self.assertNotIn(http_constants.HttpHeaders.AIM, caller_headers)
        # Per-page ``If-None-Match`` did still get sent to the wire on every
        # call after the first -- proving the drain DID set the header on
        # the outbound request, just not on the caller's dict.
        self.assertEqual(
            script.if_none_match_seen,
            [None, '"etag-1"', '"etag-2"', '"etag-3"'],
        )


if __name__ == "__main__":
    unittest.main()
