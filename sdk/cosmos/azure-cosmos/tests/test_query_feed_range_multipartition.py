# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""End-to-end tests for ``query_items(feed_range=...)`` against a feed_range
that overlaps more than one physical partition.

These tests reproduce a customer-reported bug whose two visible symptoms are:

* pages return more than ``max_item_count`` items (the per-partition fan-out
  loop POSTs once per overlapping physical partition and concatenates the
  results into a single logical page), and
* duplicate items appear across pages (only the last overlap's outbound
  continuation is preserved on the wire, so the next page restarts the
  other overlap(s) from offset 0).

Three scenarios are covered:

* ``test_two_partition_feed_range`` — feed_range overlaps two adjacent
  physical partitions (the customer's exact case).
* ``test_three_way_overlap`` — feed_range overlaps three adjacent physical
  partitions; same family of bug, wider fan-out.
* ``test_post_split_resume`` — emit a continuation under one physical
  layout, force a real partition split, then resume with the same
  continuation against the new layout. Slow (``cosmosSplit``).

The tests run against a live Cosmos account (``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` env vars). They are marked ``cosmosQuery`` (and
``cosmosSplit`` for the post-split test). Each one is expected to fail on
the buggy code path and to pass once the fan-out / continuation handling is
fixed.

Async parity lives in ``test_query_feed_range_multipartition_async.py``.
"""

import time
import unittest
import uuid
from typing import Iterable, List, Optional, Tuple

import pytest

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID

# Dedicated container for these tests. Throughput is chosen so the
# container has multiple physical partitions out of the box (no split needed
# for the two/three-overlap tests); the post-split test then forces an
# additional split on top.
REPRO_CONTAINER_ID = "FeedRangeMultiPartition-" + str(uuid.uuid4())
REPRO_PARTITION_KEY = "pk"
REPRO_THROUGHPUT = CONFIG.THROUGHPUT_FOR_5_PARTITIONS  # 30000 → ~5 partitions
REPRO_DOC_COUNT = 200  # spread across partitions; ensures every partition has data

# Customer-reported symptom thresholds:
#   max_item_count=5 → page returns 10 items (under 2-overlap fan-out)
#   page 3 replays page 2's items (duplicate ids)
PAGE_SIZE = 5

# Per-overlap data threshold below which we skip a configuration as not a
# meaningful repro. Need enough docs in each partition to drive ≥ 3 pages
# under PAGE_SIZE = 5, matching the customer's observed setup.
MIN_DOCS_PER_PARTITION = 15


def _client() -> CosmosClient:
    return CosmosClient(HOST, KEY)


def _get_container():
    db = _client().get_database_client(DATABASE_ID)
    return db.get_container_client(REPRO_CONTAINER_ID)


def _sorted_partition_ranges(container) -> List[Tuple[str, str]]:
    """Return current physical partitions' EPK ranges as (min, max) tuples,
    sorted by ``min``. Reads the routing map via ``read_feed_ranges()`` (the
    public surface that returns one dict per current physical partition).
    """
    feed_ranges = list(container.read_feed_ranges())
    pairs: List[Tuple[str, str]] = []
    for fr in feed_ranges:
        r = fr["Range"]
        pairs.append((r["min"], r["max"]))
    pairs.sort(key=lambda p: p[0])
    return pairs


def _count_in_range(container, range_min: str, range_max: str) -> int:
    fr = test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))
    items = list(container.query_items(
        query="SELECT VALUE COUNT(1) FROM c", feed_range=fr))
    return items[0] if items else 0


def _crossing_feed_range(range_min: str, range_max: str):
    """Synthesize a feed_range whose ``[min, max)`` interval spans the union
    of one or more current physical partitions — exactly the shape a
    customer-supplied feed_range takes after the underlying partition has
    been split."""
    return test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))


def _ids_via_per_partition_scan(container, partition_ranges: Iterable[Tuple[str, str]]):
    """Ground-truth set of document ids inside the union of the given physical
    partition ranges. Each partition is queried independently (each call is a
    single-overlap query that does NOT go through the buggy fan-out branch),
    so this is the correct baseline to compare a crossing-feed_range query
    against."""
    ground_truth = set()
    for (mn, mx) in partition_ranges:
        fr = _crossing_feed_range(mn, mx)
        for item in container.query_items(query="SELECT c.id FROM c", feed_range=fr):
            ground_truth.add(item["id"])
    return ground_truth


def _drain_pages(pager) -> Tuple[List[List[dict]], List[str]]:
    """Iterate ``pager`` to exhaustion. Return the per-page item lists (so the
    caller can assert on per-page sizes) and the ordered list of all ids
    encountered (so the caller can assert on duplicates)."""
    pages: List[List[dict]] = []
    all_ids: List[str] = []
    for page in pager:
        items = list(page)
        pages.append(items)
        all_ids.extend(item["id"] for item in items)
    return pages, all_ids


@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    """Create a dedicated container for these tests, populate it with enough
    documents that every physical partition has data on both sides of every
    internal boundary, and tear it down afterwards."""
    client = _client()
    db = client.get_database_client(DATABASE_ID)
    container = db.create_container_if_not_exists(
        id=REPRO_CONTAINER_ID,
        partition_key=PartitionKey(path="/" + REPRO_PARTITION_KEY, kind="Hash"),
        offer_throughput=REPRO_THROUGHPUT)
    # Insert REPRO_DOC_COUNT documents with distinct partition-key values.
    # SHA-based PK hashing distributes these roughly uniformly across the
    # container's physical partitions, so each partition ends up with a few
    # dozen documents — enough to drive multiple pages at PAGE_SIZE=5.
    for i in range(REPRO_DOC_COUNT):
        container.upsert_item({
            REPRO_PARTITION_KEY: f"pk-{i:04d}",
            "id": f"doc-{i:04d}",
            "value": i,
        })
    yield
    try:
        db.delete_container(REPRO_CONTAINER_ID)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.cosmosQuery
class TestFeedRangeMultiPartition:
    """Sync end-to-end tests for feed_range queries that overlap multiple
    physical partitions."""

    # ------------------------------------------------------------------ #
    # Single-partition control (regression guard for the no-fan-out path)
    # ------------------------------------------------------------------ #
    def test_single_partition_feed_range(self):
        """``feed_range`` strictly inside one physical partition's EPK
        range, ``max_item_count=PAGE_SIZE``: every page must contain
        exactly ``PAGE_SIZE`` items (except possibly the last one), no
        duplicates across pages, and the last page's continuation must be
        ``None``.

        This is the path thousands of the customer's other feedRanges
        follow. It does NOT exercise the multi-overlap fan-out branch and
        must remain green both before and after the fix - any regression
        here means the fix broke the single-overlap path.
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if not partitions:
            pytest.skip("Container has no physical partitions")

        # Pick the first partition that holds enough docs to drive
        # multiple PAGE_SIZE pages.
        chosen_pp = None
        for (mn, mx) in partitions:
            if _count_in_range(container, mn, mx) >= MIN_DOCS_PER_PARTITION:
                chosen_pp = (mn, mx)
                break
        if chosen_pp is None:
            pytest.skip("No single partition populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        single = _crossing_feed_range(chosen_pp[0], chosen_pp[1])
        ground_truth = _ids_via_per_partition_scan(container, [chosen_pp])

        pager = container.query_items(
            query="SELECT * FROM c",
            feed_range=single,
            max_item_count=PAGE_SIZE,
        ).by_page()
        pages, all_ids = _drain_pages(pager)

        # Every page except the last one is exactly PAGE_SIZE; the last
        # page is at most PAGE_SIZE.
        for idx, page in enumerate(pages):
            if idx < len(pages) - 1:
                assert len(page) == PAGE_SIZE, (
                    f"page {idx} returned {len(page)} items, expected "
                    f"exactly {PAGE_SIZE} (only the last page is allowed "
                    "to be short on the single-overlap path)")
            else:
                assert len(page) <= PAGE_SIZE

        # No duplicates and full coverage of the partition.
        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"single-partition path returned duplicates: "
            f"{len(all_ids) - len(unique)} duplicate id(s)")
        assert unique == ground_truth, (
            f"single-partition coverage mismatch: returned={len(unique)}, "
            f"ground_truth={len(ground_truth)}, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}")

        # After the last page, the continuation token must be None
        # (composite drained -> caller's loop terminates correctly).
        assert pager.continuation_token in (None, "", b""), (
            f"expected empty continuation after draining all pages; got "
            f"{pager.continuation_token!r}")

    # ------------------------------------------------------------------ #
    # Two-partition feed_range (the customer's exact case)
    # ------------------------------------------------------------------ #
    def test_two_partition_feed_range(self):
        """Construct a feed_range that overlaps two adjacent physical
        partitions and pin down the customer's three symptoms:

          (a) per-page item count ≤ ``max_item_count`` (customer saw 10 on
              ``max_item_count=5`` because the buggy fan-out loop concatenates
              one POST per overlap),
          (b) no duplicate ids across pages (customer saw page 3 replay 5 of
              page 2's items because only the last overlap's outbound
              continuation is preserved),
          (c) the union of ids returned matches the union of ids from
              independent per-partition scans (no missing items).

        On the buggy code path this test is expected to fail on (a) and (b).
        Once the fan-out / continuation handling is fixed it must pass on
        all three.
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with ≥ 2 physical partitions")

        # Find the first adjacent pair where both partitions hold enough docs
        # to drive ≥ 3 pages under PAGE_SIZE = 5 (matching the customer's
        # observed setup).
        chosen = None
        for i in range(len(partitions) - 1):
            p0, p1 = partitions[i], partitions[i + 1]
            if (_count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                    and _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                chosen = (p0, p1)
                break
        if chosen is None:
            pytest.skip("No adjacent partition pair both populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        (p0_min, _), (_, p1_max) = chosen
        crossing = _crossing_feed_range(p0_min, p1_max)
        ground_truth = _ids_via_per_partition_scan(
            container, [chosen[0], chosen[1]])

        pager = container.query_items(
            query="SELECT * FROM c",
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page()
        pages, all_ids = _drain_pages(pager)

        # (a) every page must respect max_item_count
        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size budget violated (max_item_count={PAGE_SIZE}); "
            f"got pages with sizes {[len(p) for p in pages]}; "
            f"oversized pages (index, size): {oversized}. "
            "This is the customer's '10 items per page on max_item_count=5' "
            "symptom.")

        # (b) no duplicates across pages
        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"duplicates across pages: {len(all_ids)} items returned, "
            f"{len(unique)} distinct, "
            f"{len(all_ids) - len(unique)} duplicate(s). "
            "This is the customer's 'page 3 replays 5 items from page 2' "
            "symptom.")

        # (c) no missing items vs ground truth
        assert unique == ground_truth, (
            f"item-set mismatch: returned={len(unique)} ids, "
            f"ground_truth={len(ground_truth)} ids, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}.")

    # ------------------------------------------------------------------ #
    # Three-way overlap (synthetic, wider fan-out)
    # ------------------------------------------------------------------ #
    def test_three_way_overlap(self):
        """Same shape as ``test_two_partition_feed_range`` but with a
        ``feed_range`` that overlaps **three** adjacent physical partitions.
        The buggy fan-out fires three POSTs per page, so per-page sizes can
        reach ``3 × PAGE_SIZE`` and the duplicate-on-resume pattern becomes
        more pronounced. Once the bug is fixed, behaviour must collapse back
        to the same three guarantees as the two-partition test.
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 3:
            pytest.skip("Need a container with ≥ 3 physical partitions")

        chosen: Optional[List[Tuple[str, str]]] = None
        for i in range(len(partitions) - 2):
            triple = partitions[i:i + 3]
            if all(_count_in_range(container, mn, mx) >= MIN_DOCS_PER_PARTITION
                   for mn, mx in triple):
                chosen = triple
                break
        if chosen is None:
            pytest.skip("No three adjacent partitions all populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        assert chosen is not None  # narrows for type checkers; pytest.skip raises
        crossing = _crossing_feed_range(chosen[0][0], chosen[2][1])
        ground_truth = _ids_via_per_partition_scan(container, chosen)

        pager = container.query_items(
            query="SELECT * FROM c",
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page()
        pages, all_ids = _drain_pages(pager)

        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size budget violated; sizes={[len(p) for p in pages]}; "
            f"oversized={oversized}. With 3-way overlap on the buggy code "
            "path, expect pages of up to 3×max_item_count.")

        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"duplicates across pages: {len(all_ids)} returned, "
            f"{len(unique)} distinct, "
            f"{len(all_ids) - len(unique)} duplicate(s).")

        assert unique == ground_truth, (
            f"item-set mismatch: returned={len(unique)}, "
            f"ground_truth={len(ground_truth)}, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}.")

    # ------------------------------------------------------------------ #
    # Post-split resume (slow; requires a real partition split)
    # ------------------------------------------------------------------ #
    @pytest.mark.cosmosSplit
    def test_post_split_resume(self):
        """End-to-end "the routing layout changed underneath a saved
        continuation token" scenario:

          1. Construct a 2-overlap crossing feed_range under the *current*
             routing map; drain page 1 and save the continuation token.
          2. Trigger a real partition split (``trigger_split``) so the
             container's physical partition count grows. The same EPK
             ``{min, max}`` interval now overlaps a different (≥ 2) set of
             physical partitions.
          3. Resume with the saved continuation token + the same
             ``feed_range``. Drain remaining pages.
          4. Assert: combined ids across page 1 + post-split pages are
             unique and equal the union of a fresh per-partition scan over
             the same EPK interval.

        On the buggy code path the saved continuation is a plain backend
        string from whichever overlap was last in the loop; sending that
        token to a different partition layout is undefined. Expect this
        test to fail with either duplicates or wrong rows.
        """
        container = _get_container()
        partitions_before = _sorted_partition_ranges(container)
        if len(partitions_before) < 2:
            pytest.skip("Need a container with ≥ 2 physical partitions")

        chosen = None
        for i in range(len(partitions_before) - 1):
            p0, p1 = partitions_before[i], partitions_before[i + 1]
            if (_count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                    and _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                chosen = (p0, p1)
                break
        if chosen is None:
            pytest.skip("No adjacent partition pair both populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        (p0_min, _), (_, p1_max) = chosen
        crossing = _crossing_feed_range(p0_min, p1_max)

        # Step 1 — drain page 1 only and save the outbound continuation.
        pager_pre = container.query_items(
            query="SELECT * FROM c",
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page()
        page_1 = list(next(pager_pre))
        ct_after_page_1 = pager_pre.continuation_token
        page_1_ids = [item["id"] for item in page_1]
        assert ct_after_page_1, (
            "expected a non-empty continuation token after page 1; the "
            "feed_range overlaps two partitions and the first page should "
            "not have drained the whole interval")

        # Step 2 — trigger a real split. This is the slow step (up to 10 min
        # for the offer-replace operation to complete).
        target_throughput = max(REPRO_THROUGHPUT * 2, 60000)
        try:
            test_config.TestConfig.trigger_split(container, target_throughput)
        except unittest.SkipTest:
            raise
        # Allow the routing map a brief settling period after the split
        # completes, then force a refresh so the SDK sees the new layout.
        time.sleep(10)
        list(container.read_feed_ranges(force_refresh=True))

        # Step 3 — resume with the saved continuation, same feed_range.
        pager_post = container.query_items(
            query="SELECT * FROM c",
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page(continuation_token=ct_after_page_1)
        post_pages, post_ids = _drain_pages(pager_post)

        combined_ids = page_1_ids + post_ids
        unique = set(combined_ids)
        assert len(combined_ids) == len(unique), (
            f"duplicates across the split boundary: {len(combined_ids)} ids "
            f"returned across page 1 + {len(post_pages)} post-split page(s), "
            f"{len(unique)} distinct, "
            f"{len(combined_ids) - len(unique)} duplicate(s). "
            "Under the buggy code path, the saved continuation is a plain "
            "backend string from the pre-split layout; sending it through "
            "the post-split routing map is the failure mode this test is "
            "designed to catch.")

        oversized = [(i, len(p)) for i, p in enumerate(post_pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size budget violated post-split; sizes="
            f"{[len(p) for p in post_pages]}; oversized={oversized}.")

        # Re-derive ground truth against the post-split routing map.
        partitions_after = _sorted_partition_ranges(container)
        post_split_overlaps = [(mn, mx) for (mn, mx) in partitions_after
                               if min(p1_max, mx) > max(p0_min, mn)]
        ground_truth = _ids_via_per_partition_scan(container, post_split_overlaps)
        assert unique == ground_truth, (
            f"item-set mismatch after post-split resume: returned="
            f"{len(unique)}, ground_truth={len(ground_truth)}, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}.")

    # ------------------------------------------------------------------ #
    # Legacy opaque token compatibility (#7 in §7.2.2)
    # ------------------------------------------------------------------ #
    def test_legacy_opaque_token_compat(self):
        """Hand the new code a continuation produced by the OLD code
        (opaque, neither base64-of-JSON nor v=1). Per §6.5 of
        ``docs/FEED_RANGE_ISSUE.md`` the new code treats it as
        ``continuation_token=None``.

        Asserts:
          (a) no exception is raised on the resume call,
          (b) all batches restart from the beginning (the union of ids
              returned equals the per-partition ground truth),
          (c) every page respects ``max_item_count``,
          (d) pagination runs to completion (final continuation is None).
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with ≥ 2 physical partitions")

        chosen = None
        for i in range(len(partitions) - 1):
            p0, p1 = partitions[i], partitions[i + 1]
            if (_count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                    and _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                chosen = (p0, p1)
                break
        if chosen is None:
            pytest.skip("No adjacent partition pair both populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        (p0_min, _), (_, p1_max) = chosen
        crossing = _crossing_feed_range(p0_min, p1_max)
        ground_truth = _ids_via_per_partition_scan(container, [chosen[0], chosen[1]])

        # An opaque pre-fix token from the buggy SDK: a backend RID:~
        # continuation string that is NOT base64-of-our-JSON. The new
        # _decode_token must return None for this and the call site must
        # restart from offset 0.
        # cspell:ignore AOXB BAAAAAAAAAA EAAAAFAAAA
        legacy_token = "+RID:~Yxs1AOXBSp4BAAAAAAAAAA==#RT:1#TRC:5#ISV:2#IEO:65567#FPC:AgEAAAAFAAAA"

        pager = container.query_items(
            query="SELECT * FROM c",
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page(continuation_token=legacy_token)

        # (a) no exception on iteration
        pages, all_ids = _drain_pages(pager)

        # (c) page-size budget respected
        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size budget violated under legacy-token resume; "
            f"sizes={[len(p) for p in pages]}; oversized={oversized}")

        # (b) full restart from offset 0 -> coverage matches ground truth,
        # no duplicates
        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"legacy-token restart produced duplicates: "
            f"{len(all_ids) - len(unique)} duplicate id(s)")
        assert unique == ground_truth, (
            f"legacy-token restart coverage mismatch: returned="
            f"{len(unique)}, ground_truth={len(ground_truth)}, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}")

        # (d) pagination ran to completion
        assert pager.continuation_token in (None, "", b""), (
            f"expected empty continuation after draining all pages on "
            f"legacy-token restart; got {pager.continuation_token!r}")

    # ------------------------------------------------------------------ #
    # Identity-fingerprint mismatch rejection (#6 in §7.2.2, live half)
    # ------------------------------------------------------------------ #
    def test_token_identity_mismatch_rejected(self):
        """Round-trip a token through ``query_items`` then replay it
        against (a) a different query text, (b) a different parameter
        value, and (c) a different ``feed_range``. Each replay must raise
        ``ValueError`` from the call-site validation in ``__QueryFeed``
        with a message that names the failing field.

        The unit tests in ``test_feed_range_continuation_token.py`` cover
        the hash-inequality contract; this test covers the live raise
        path through the SDK's actual query pipeline.
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with ≥ 2 physical partitions")

        chosen = None
        for i in range(len(partitions) - 1):
            p0, p1 = partitions[i], partitions[i + 1]
            if (_count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                    and _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                chosen = (p0, p1)
                break
        if chosen is None:
            pytest.skip("No adjacent partition pair both populated with ≥ "
                        f"{MIN_DOCS_PER_PARTITION} docs")
        (p0_min, _), (_, p1_max) = chosen
        crossing = _crossing_feed_range(p0_min, p1_max)

        # Step 1 — drain page 1 of a parameterized query and save the
        # outbound continuation. The token's qh/frh fingerprints encode
        # this query + this feed_range.
        # Use bracket notation: ``value`` is a reserved word in Cosmos SQL.
        original_query = "SELECT * FROM c WHERE c[\"value\"] >= @v"
        original_params = [{"name": "@v", "value": 0}]
        pager = container.query_items(
            query={"query": original_query, "parameters": original_params},
            feed_range=crossing,
            max_item_count=PAGE_SIZE,
        ).by_page()
        _ = list(next(pager))
        token = pager.continuation_token
        assert token, ("expected a non-empty continuation after page 1; "
                       "the test cannot exercise resume validation otherwise")

        # (a) Different query TEXT — qh mismatch.
        with pytest.raises(ValueError) as excinfo_q:
            list(container.query_items(
                query={"query": "SELECT * FROM c WHERE c[\"value\"] >= @v AND c.id != ''",
                       "parameters": original_params},
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=token))
        msg_q = str(excinfo_q.value).lower()
        assert "query" in msg_q, (
            "ValueError on query-text mismatch must name the failing "
            f"field; got: {excinfo_q.value!r}")

        # (b) Different parameter VALUE — same query text, different qh.
        with pytest.raises(ValueError) as excinfo_p:
            list(container.query_items(
                query={"query": original_query,
                       "parameters": [{"name": "@v", "value": 999999}]},
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=token))
        assert "query" in str(excinfo_p.value).lower(), (
            "ValueError on parameter-value mismatch must name the query "
            f"field; got: {excinfo_p.value!r}")

        # (c) Different feed_range — frh mismatch. Use a single-partition
        # sub-range of the original crossing range (still inside the same
        # collection so cr matches; only frh differs).
        single_p0 = _crossing_feed_range(chosen[0][0], chosen[0][1])
        with pytest.raises(ValueError) as excinfo_f:
            list(container.query_items(
                query={"query": original_query, "parameters": original_params},
                feed_range=single_p0,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=token))
        assert "feed_range" in str(excinfo_f.value).lower(), (
            "ValueError on feed_range mismatch must name the feed_range "
            f"field; got: {excinfo_f.value!r}")
