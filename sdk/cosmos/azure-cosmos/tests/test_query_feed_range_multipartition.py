# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""End-to-end tests for ``query_items(feed_range=...)`` against a feed_range
that overlaps more than one physical partition.

These tests pin two invariants of the multi-overlap pagination contract:

* every page returns at most ``max_item_count`` items, and
* no item id is returned on more than one page (no duplicates across the
  fan-out / resume boundary).

Three scenarios are covered:

* ``test_two_partition_feed_range`` — feed_range overlaps two adjacent
  physical partitions.
* ``test_three_way_overlap`` — feed_range overlaps three adjacent physical
  partitions; wider fan-out.
* ``test_post_split_resume`` — emit a continuation under one physical
  layout, force a real partition split, then resume with the same
  continuation against the new layout. Slow (``cosmosSplit``).


Async parity lives in ``test_query_feed_range_multipartition_async.py``.
"""

import time
import unittest
import uuid
from typing import Iterable, List, Optional, Tuple

import pytest

import test_config
from azure.cosmos import _base
from azure.cosmos import CosmosClient, documents, http_constants
from azure.cosmos._routing.feed_range_continuation import _decode_token
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

# Per-page cap applied to every multi-overlap query in this module.
# Small enough to drive several pages per partition under the seeded data
# count, so any per-page over-fetch or duplicate-on-resume shows up across
# the page sequence rather than only on the last page.
PAGE_SIZE = 5

# Per-overlap data threshold below which we skip a configuration as not a
# meaningful repro. Need enough docs in each partition to drive ≥ 3 pages
# under PAGE_SIZE = 5.
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
    of one or more current physical partitions — the shape a feed_range
    takes after the underlying partition has been split."""
    return test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))


def _ids_via_per_partition_scan(container, partition_ranges: Iterable[Tuple[str, str]]):
    """Ground-truth set of document ids inside the union of the given physical
    partition ranges. Each partition is queried independently (each call is a
    single-overlap query that does NOT exercise the multi-overlap fan-out
    branch), so this is the correct baseline to compare a crossing-feed_range
    query against."""
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

        This is the path the vast majority of feedRanges follow. It does
        NOT exercise the multi-overlap fan-out branch; a regression here
        means the single-overlap path itself is broken.
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
    # Partition-key caller shapes (full key and prefix key)
    # ------------------------------------------------------------------ #
    def test_full_partition_key_query_pagination_resume(self):
        """Full hierarchical partition-key query resumes correctly by continuation.

        This uses a dedicated MultiHash container and a full key value so the
        query stays scoped to one logical partition while still exercising
        pagination + resume on the partition_key path.
        """
        db = _client().get_database_client(DATABASE_ID)
        container_id = "FeedRangeMultiPartitionFullPK-" + str(uuid.uuid4())
        created_container = db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash),
            offer_throughput=400,
        )
        try:
            full_key = ['CA', 'Oxnard', '93033']
            for i in range(25):
                created_container.upsert_item({
                    'id': f'full-pk-doc-{i:03d}',
                    'state': full_key[0],
                    'city': full_key[1],
                    'zipcode': full_key[2],
                    'value': i,
                })
            for i in range(5):
                created_container.upsert_item({
                    'id': f'other-doc-{i:03d}',
                    'state': 'WA',
                    'city': 'Seattle',
                    'zipcode': f'98{i:03d}',
                    'value': i,
                })

            query = 'SELECT c.id FROM c ORDER BY c.id'
            query_iterable = created_container.query_items(
                query=query,
                partition_key=full_key,
                max_item_count=7,
            )

            pager = query_iterable.by_page()
            first_page = list(next(pager))
            assert first_page
            token = pager.continuation_token
            assert token

            expected_remaining_ids = []
            for page in pager:
                expected_remaining_ids.extend(item['id'] for item in page)

            resumed_remaining_ids = []
            for page in query_iterable.by_page(token):
                resumed_remaining_ids.extend(item['id'] for item in page)

            assert expected_remaining_ids == resumed_remaining_ids

            baseline_ids = [
                item['id'] for item in created_container.query_items(query=query, partition_key=full_key)
            ]
            fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
            assert baseline_ids == fetched_ids
        finally:
            db.delete_container(created_container.id)

    def test_prefix_partition_key_query_pagination_resume(self):
        """Prefix hierarchical partition-key query resumes correctly by continuation.

        The caller provides only the first level (``['CA']``). The query spans
        multiple descendants under that prefix and must preserve continuation
        correctness on resume.
        """
        db = _client().get_database_client(DATABASE_ID)
        container_id = "FeedRangeMultiPartitionPrefixPK-" + str(uuid.uuid4())
        created_container = db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash),
            offer_throughput=400,
        )
        try:
            for i in range(30):
                created_container.upsert_item({
                    'id': f'ca-doc-{i:03d}',
                    'state': 'CA',
                    'city': f'city-{i % 5}',
                    'zipcode': f'zip-{i:03d}',
                    'value': i,
                })
            for i in range(6):
                created_container.upsert_item({
                    'id': f'wa-doc-{i:03d}',
                    'state': 'WA',
                    'city': f'city-{i % 2}',
                    'zipcode': f'zip-{i:03d}',
                    'value': i,
                })

            query = 'SELECT c.id FROM c ORDER BY c.id'
            query_iterable = created_container.query_items(
                query=query,
                partition_key=['CA'],
                max_item_count=7,
            )

            pager = query_iterable.by_page()
            first_page = list(next(pager))
            assert first_page
            token = pager.continuation_token
            assert token

            expected_remaining_ids = []
            for page in pager:
                expected_remaining_ids.extend(item['id'] for item in page)

            resumed_remaining_ids = []
            for page in query_iterable.by_page(token):
                resumed_remaining_ids.extend(item['id'] for item in page)

            assert expected_remaining_ids == resumed_remaining_ids

            baseline_ids = [
                item['id'] for item in created_container.query_items(query=query, partition_key=['CA'])
            ]
            fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
            assert baseline_ids == fetched_ids
        finally:
            db.delete_container(created_container.id)


    # ------------------------------------------------------------------ #
    # Two-partition feed_range
    # ------------------------------------------------------------------ #
    def test_two_partition_feed_range(self):
        """Construct a feed_range that overlaps two adjacent physical
        partitions and pin three invariants:

          (a) per-page item count ≤ ``max_item_count`` (the fan-out must
              not concatenate per-overlap responses into one oversized
              logical page),
          (b) no duplicate ids across pages (each overlap's outbound
              continuation must be preserved so the next page resumes
              instead of restarting from offset 0),
          (c) the union of ids returned matches the union of ids from
              independent per-partition scans (no missing items).
        """
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with ≥ 2 physical partitions")

        # Find the first adjacent pair where both partitions hold enough docs
        # to drive ≥ 3 pages under PAGE_SIZE = 5.
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
            f"page-size limit violated (max_item_count={PAGE_SIZE}); "
            f"got pages with sizes {[len(p) for p in pages]}; "
            f"oversized pages (index, size): {oversized}.")

        # (b) no duplicates across pages
        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"duplicates across pages: {len(all_ids)} items returned, "
            f"{len(unique)} distinct, "
            f"{len(all_ids) - len(unique)} duplicate(s).")

        # (c) no missing items vs ground truth
        assert unique == ground_truth, (
            f"item-set mismatch: returned={len(unique)} ids, "
            f"ground_truth={len(ground_truth)} ids, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}.")

    def test_two_partition_feed_range_count_aggregate_pagination(self):
        """Run a VALUE aggregate through a two-partition crossing feed_range.

        Guards aggregate-specific invariants on the multi-overlap path:
          (a) each logical page still respects ``max_item_count``,
          (b) partial aggregate fragments are merged client-side (one scalar
              result after draining),
          (c) merged count matches an independent per-partition scan baseline.
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

        # Ground truth from independent per-partition scans, not aggregate path.
        expected_count = len(_ids_via_per_partition_scan(container, [chosen[0], chosen[1]]))

        pager = container.query_items(
            query="SELECT VALUE COUNT(1) FROM c",
            feed_range=crossing,
            max_item_count=1,
        ).by_page()

        pages: List[List[object]] = []
        merged_rows: List[object] = []
        for page in pager:
            items = list(page)
            pages.append(items)
            merged_rows.extend(items)

        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > 1]
        assert not oversized, (
            "aggregate page-size limit violated (max_item_count=1); "
            f"page sizes={[len(p) for p in pages]}, oversized={oversized}.")

        assert len(merged_rows) == 1, (
            "aggregate merge leaked partial fragments or dropped final value; "
            f"expected one merged row, got {len(merged_rows)} rows: {merged_rows}")
        assert merged_rows[0] == expected_count, (
            "merged COUNT result mismatch for two-partition crossing feed_range; "
            f"returned={merged_rows[0]}, expected={expected_count}")
        assert pager.continuation_token in (None, "", b""), (
            f"expected empty continuation after draining aggregate query; got "
            f"{pager.continuation_token!r}")

    @pytest.mark.parametrize("merge_error_type", [TypeError, KeyError])
    def test_two_partition_feed_range_merge_fallback_preserves_rows(
        self, monkeypatch, caplog, merge_error_type
    ):
        """Force merge failures and verify fallback extends docs without loss."""
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

        merge_call_count = 0

        def _raising_merge(*_args, **_kwargs):
            nonlocal merge_call_count
            merge_call_count += 1
            raise merge_error_type("injected-merge-failure")

        monkeypatch.setattr(_base, "_merge_query_results", _raising_merge)

        with caplog.at_level("WARNING", logger="azure.cosmos._cosmos_client_connection"):
            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page()
            pages, all_ids = _drain_pages(pager)

        assert merge_call_count > 0
        assert any(
            "Falling back to non-aggregate merge after aggregate merge failure" in record.getMessage()
            for record in caplog.records
        ), "Expected warning log for merge fallback path"

        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size limit violated (max_item_count={PAGE_SIZE}); "
            f"got pages with sizes {[len(p) for p in pages]}; "
            f"oversized pages (index, size): {oversized}.")

        unique = set(all_ids)
        assert len(all_ids) == len(unique), (
            f"fallback path produced duplicates: {len(all_ids)} items returned, "
            f"{len(unique)} distinct, "
            f"{len(all_ids) - len(unique)} duplicate(s).")
        assert unique == ground_truth, (
            f"fallback path dropped/added items: returned={len(unique)} ids, "
            f"ground_truth={len(ground_truth)} ids, "
            f"missing={len(ground_truth - unique)}, "
            f"unexpected={len(unique - ground_truth)}.")

    def test_exception_during_post_preserves_resume_checkpoint(self):
        """Inject a POST failure mid-query and verify the call site stamps
        an outbound continuation that resumes from the last successful slice.
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

        client_conn = container.client_connection
        original_post = client_conn._CosmosClientConnection__Post
        call_count = 0

        def _failing_post(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise RuntimeError("injected-post-failure")
            return original_post(*args, **kwargs)

        client_conn._CosmosClientConnection__Post = _failing_post
        try:
            pager = container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                feed_range=crossing,
                max_item_count=1,
            ).by_page()
            with pytest.raises(RuntimeError, match="injected-post-failure"):
                _ = list(next(pager))
        finally:
            client_conn._CosmosClientConnection__Post = original_post

        token = client_conn.last_response_headers.get(http_constants.HttpHeaders.Continuation)
        assert token, "Expected continuation checkpoint to be stamped on POST failure"
        decoded = _decode_token(token)
        assert decoded is not None
        assert decoded["c"][0]["min"] == chosen[1][0], (
            "Checkpoint should resume from the second sub-range after the first "
            "sub-range completed successfully before failure."
        )

    def test_explode_iteration_guard_raises_in_query_loop(self, monkeypatch):
        """Drive the live ``__QueryFeed`` explode loop until the runtime guard raises."""
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with >= 2 physical partitions")

        p0, p1 = partitions[0], partitions[1]
        crossing = _crossing_feed_range(p0[0], p1[1])
        client_conn = container.client_connection

        # Force every routing lookup to look like an unresolved post-split overlap.
        def _always_multi_overlap(_rid, feed_ranges, _opts):
            head = feed_ranges[0]
            return [
                {"id": "left", "minInclusive": head.min, "maxExclusive": head.max},
                {"id": "right", "minInclusive": head.min, "maxExclusive": head.max},
            ]

        monkeypatch.setattr(
            client_conn._routing_map_provider, "get_overlapping_ranges", _always_multi_overlap
        )
        monkeypatch.setattr(
            "azure.cosmos._routing.feed_range_continuation._MAX_MULTI_OVERLAP_EXPLODE_ITERATIONS", 2
        )

        with pytest.raises(RuntimeError) as excinfo:
            list(
                container.query_items(
                    query="SELECT * FROM c", feed_range=crossing, max_item_count=PAGE_SIZE
                ).by_page()
            )
        assert "split re-resolution" in str(excinfo.value)

    def test_no_progress_guard_logs_warning_in_query_loop(self, monkeypatch, caplog):
        """Drive repeated empty pages with unchanged continuation and assert warning emission."""
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with >= 2 physical partitions")

        p0, p1 = partitions[0], partitions[1]
        crossing = _crossing_feed_range(p0[0], p1[1])
        client_conn = container.client_connection

        post_call_count = 0

        def _stalled_post(*_args, **_kwargs):
            nonlocal post_call_count
            post_call_count += 1
            continuation = "stalled-token" if post_call_count <= 3 else None
            return {"Documents": []}, {http_constants.HttpHeaders.Continuation: continuation}

        monkeypatch.setattr(client_conn, "_CosmosClientConnection__Post", _stalled_post)
        monkeypatch.setattr(
            "azure.cosmos._cosmos_client_connection._MAX_CONSECUTIVE_NO_PROGRESS_PAGES", 2
        )

        with caplog.at_level("WARNING", logger="azure.cosmos._cosmos_client_connection"):
            list(
                container.query_items(
                    query="SELECT * FROM c", feed_range=crossing, max_item_count=PAGE_SIZE
                ).by_page()
            )

        assert post_call_count >= 3
        assert any(
            "same continuation token" in record.getMessage() for record in caplog.records
        ), "Expected warning log from no-progress guard"

    # ------------------------------------------------------------------ #
    # Three-way overlap (synthetic, wider fan-out)
    # ------------------------------------------------------------------ #
    def test_three_way_overlap(self):
        """Same shape as ``test_two_partition_feed_range`` but with a
        ``feed_range`` that overlaps **three** adjacent physical partitions.
        Wider fan-out exercises the same three guarantees as the
        two-partition test on a larger overlap set.
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
            f"page-size limit violated; sizes={[len(p) for p in pages]}; "
            f"oversized={oversized}.")

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

        On the post-split resume path, the saved continuation must remain
        valid (or be safely restarted) under the new physical layout - the
        combined ids across the split boundary must still be unique and
        cover the same EPK interval.
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
        duplicate_count = len(combined_ids) - len(unique)
        # When the parent's backend continuation is dropped during the
        # post-split explode (children won't accept the parent's bc),
        # the children restart at offset 0 of their slice. The lower
        # child can therefore re-emit up to PAGE_SIZE rows that page 1
        # already returned. The strict no-dup invariant only holds when
        # page 1 happened to fully drain the parent slice; the
        # bounded-replay invariant always holds and is what we assert
        # here. The strict no-loss / no-out-of-range guarantee is still
        # enforced by the ``unique == ground_truth`` check below.
        assert duplicate_count <= PAGE_SIZE, (
            f"unexpected duplicate count across the split boundary: "
            f"{len(combined_ids)} ids returned across page 1 + "
            f"{len(post_pages)} post-split page(s), {len(unique)} distinct, "
            f"{duplicate_count} duplicate(s) (max allowed: {PAGE_SIZE}).")

        oversized = [(i, len(p)) for i, p in enumerate(post_pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size limit violated post-split; sizes="
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
    # Legacy opaque token compatibility
    # ------------------------------------------------------------------ #
    def test_legacy_opaque_token_compat(self, caplog):
        """Use an opaque continuation token (not base64 JSON, not v=1).
        The query restarts from the beginning.

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

        # Opaque continuation string that does not match the structured
        # token format.
        # cspell:ignore AOXB BAAAAAAAAAA EAAAAFAAAA
        legacy_token = "+RID:~Yxs1AOXBSp4BAAAAAAAAAA==#RT:1#TRC:5#ISV:2#IEO:65567#FPC:AgEAAAAFAAAA"

        with caplog.at_level("WARNING", logger="azure.cosmos._cosmos_client_connection"):
            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=legacy_token)

            # (a) no exception on iteration
            pages, all_ids = _drain_pages(pager)

        assert any(
            "not in the supported structured format" in record.getMessage()
            for record in caplog.records
        ), "Expected warning log when a non-structured continuation token is supplied"
        assert all(
            legacy_token not in record.getMessage() for record in caplog.records
        ), "Warning log must not include raw continuation token text"

        # (c) page-size limit respected
        oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
        assert not oversized, (
            f"page-size limit violated under legacy-token resume; "
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
    # Identity-fingerprint mismatch rejection (live half)
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
