# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of tests/test_query_feed_range_multipartition.py.

``TestFeedRangeMultiPartition`` keeps the original prefix-query body with a
per-test owned database. Its 400 RU/s container does not guarantee multiple
physical partitions.

``TestFeedRangeMultiPartitionRust`` holds the remaining copies. Its
class-scoped ``repro_setup`` fixture replaces the shared ``test_config``
database with an owned one (``DATABASE_ID``), creates the original's
30,000 RU/s repro container seeded with the original 200 documents, and
always deletes the database. Queries, feed ranges and assertions are
unchanged. The post-split copy only runs when
``COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1`` authorizes a 60,000 RU/s split.
"""

import os
import time
import unittest
import uuid
from typing import Any, Iterable, List, Optional, Tuple

import pytest

from azure.cosmos import _base
from azure.cosmos import CosmosClient, PartitionKey, documents, http_constants
from azure.cosmos._routing.feed_range_continuation import _decode_token
from config.clients import create_setup_client
from config.settings import unique_database_id
from query_items import _legacy_feed_range_helpers as test_config


@pytest.mark.cosmosQuery
class TestFeedRangeMultiPartition(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self.database_id = "legacy_query_prefix_" + uuid.uuid4().hex
        self.database = self.client.create_database(self.database_id)
        self.addCleanup(self._delete_owned_database)
        print(f"\nOwned prefix query database: {self.database_id}")

    def _delete_owned_database(self):
        self.client.delete_database(self.database_id)
        print(f"Deleted owned prefix query database: {self.database_id}")

    def test_prefix_partition_key_query_pagination_resume_rust(self):
        """Prefix query resumes all matching items and preserves the COUNT result."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_prefix_partition_key_query_pagination_resume
        db = self.database
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

            # Known gap 30: aggregates beyond one complete partition key are unsupported.
            pytest.skip("driver-gap: prefix partition-key COUNT aggregate is rejected by the Rust driver "
                        "with 400/20113; "
                        "see RUST_PARITY_PUSHBACKS.md#query-full-range-sum")
            count_results = list(created_container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key=['CA'],
            ))
            assert count_results == [30]
        finally:
            db.delete_container(created_container.id)


DATABASE_ID = unique_database_id("query-feed-range-mp")

# Dedicated container for these tests. Throughput is chosen so the
# container has multiple physical partitions out of the box (no split needed
# for the two/three-overlap tests); the post-split test then forces an
# additional split on top.
REPRO_CONTAINER_ID = "FeedRangeMultiPartition-" + str(uuid.uuid4())
REPRO_PARTITION_KEY = "pk"
REPRO_THROUGHPUT = 30000  # THROUGHPUT_FOR_5_PARTITIONS -> ~5 partitions
REPRO_DOC_COUNT = 200  # spread across partitions; ensures every partition has data

# Per-page cap applied to every multi-overlap query in this module.
PAGE_SIZE = 5

# Per-overlap data threshold below which we skip a configuration as not a
# meaningful repro. Need enough docs in each partition to drive >= 3 pages
# under PAGE_SIZE = 5.
MIN_DOCS_PER_PARTITION = 15

SPLIT_TIMEOUT = 60 * 10
SLEEP_TIME = 30
REAL_SPLIT_ENV = "COSMOS_QUERY_FEED_RANGE_REAL_SPLIT"

_REPRO_STATE = {}


def _client() -> CosmosClient:
    return _REPRO_STATE["client"]


def _get_container():
    db = _client().get_database_client(DATABASE_ID)
    return db.get_container_client(REPRO_CONTAINER_ID)


def trigger_split(container, throughput):
    # Source helper: tests/test_config.py::TestConfig.trigger_split
    print("Triggering a split in session token helpers")
    container.replace_throughput(throughput)
    print(f"changed offer to {throughput}")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = container.get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > SPLIT_TIMEOUT:
                raise unittest.SkipTest("Partition split didn't complete in time")
            print("Waiting for split to complete")
            time.sleep(SLEEP_TIME)
        else:
            break
    print("Split in session token helpers has completed")


def _sorted_partition_ranges(container) -> List[Tuple[str, str]]:
    # Source helper: tests/test_query_feed_range_multipartition.py::_sorted_partition_ranges
    feed_ranges = list(container.read_feed_ranges())
    pairs: List[Tuple[str, str]] = []
    for fr in feed_ranges:
        r = fr["Range"]
        pairs.append((r["min"], r["max"]))
    pairs.sort(key=lambda p: p[0])
    return pairs


def _count_in_range(container, range_min: str, range_max: str) -> int:
    # Source helper: tests/test_query_feed_range_multipartition.py::_count_in_range
    fr = test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))
    # Known gap 30: aggregates beyond one complete partition key are unsupported.
    pytest.skip("driver-gap: feed-range COUNT aggregate is rejected by the Rust driver with 400/20113; "
                "see RUST_PARITY_PUSHBACKS.md#query-full-range-sum")
    items = list(container.query_items(
        query="SELECT VALUE COUNT(1) FROM c", feed_range=fr))
    return items[0] if items else 0


def _crossing_feed_range(range_min: str, range_max: str):
    # Source helper: tests/test_query_feed_range_multipartition.py::_crossing_feed_range
    return test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))


def _ids_via_per_partition_scan(container, partition_ranges: Iterable[Tuple[str, str]]):
    # Source helper: tests/test_query_feed_range_multipartition.py::_ids_via_per_partition_scan
    ground_truth = set()
    for (mn, mx) in partition_ranges:
        fr = _crossing_feed_range(mn, mx)
        for item in container.query_items(query="SELECT c.id FROM c", feed_range=fr):
            ground_truth.add(item["id"])
    return ground_truth


def _values_via_per_partition_scan(container, partition_ranges: Iterable[Tuple[str, str]]):
    # Source helper: tests/test_query_feed_range_multipartition.py::_values_via_per_partition_scan
    values: List[Any] = []
    for (mn, mx) in partition_ranges:
        fr = _crossing_feed_range(mn, mx)
        for value in container.query_items(query='SELECT VALUE c["value"] FROM c', feed_range=fr):
            values.append(value)
    return values


def _drain_pages(pager) -> Tuple[List[List[dict]], List[str]]:
    # Source helper: tests/test_query_feed_range_multipartition.py::_drain_pages
    pages: List[List[dict]] = []
    all_ids: List[str] = []
    for page in pager:
        items = list(page)
        pages.append(items)
        all_ids.extend(item["id"] for item in items)
    return pages, all_ids


@pytest.fixture(scope="class")
def repro_setup():
    """Owned replacement for the original class-scoped ``setup_and_teardown``."""
    client = create_setup_client(_backend="rust")
    _REPRO_STATE["client"] = client
    try:
        db = client.create_database(DATABASE_ID)
        print(f"\nOwned multi-partition feed-range database: {DATABASE_ID}")
        try:
            container = db.create_container_if_not_exists(
                id=REPRO_CONTAINER_ID,
                partition_key=PartitionKey(path="/" + REPRO_PARTITION_KEY, kind="Hash"),
                offer_throughput=REPRO_THROUGHPUT)
            for i in range(REPRO_DOC_COUNT):
                container.upsert_item({
                    REPRO_PARTITION_KEY: f"pk-{i:04d}",
                    "id": f"doc-{i:04d}",
                    "value": i,
                })
            yield
        finally:
            client.delete_database(DATABASE_ID)
            print(f"\nDeleted owned multi-partition feed-range database: {DATABASE_ID}")
    finally:
        _REPRO_STATE.pop("client", None)
        client.close()


@pytest.mark.cosmosQuery
@pytest.mark.usefixtures("repro_setup")
class TestFeedRangeMultiPartitionRust:
    """Rust-path copies of the sync multi-overlap feed_range query tests."""

    def test_single_partition_feed_range_rust(self):
        """``feed_range`` strictly inside one physical partition's EPK range."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_single_partition_feed_range
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

    def test_full_partition_key_query_pagination_resume_and_count_is_index_only_rust(self):
        """Full hierarchical partition-key query resumes and remains index-only."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_full_partition_key_query_pagination_resume_and_count_is_index_only
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

            count_iterable = created_container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key=full_key,
                enable_cross_partition_query=False,
                populate_query_metrics=True,
            )
            count_pager = count_iterable.by_page()
            count_pages = [list(page) for page in count_pager]
            assert count_pages == [[25]]
            assert count_pager.continuation_token is None

            count_headers = count_iterable.get_response_headers()
            # Known gap 36: query-metrics request options are not sent over Gateway V2.
            if http_constants.HttpHeaders.QueryMetrics not in count_headers:
                pytest.skip("driver-gap: x-ms-documentdb-query-metrics is not returned over Gateway V2; "
                            "(known gap 36, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-36).")
            count_metrics = dict(
                entry.split("=", 1)
                for entry in count_headers[http_constants.HttpHeaders.QueryMetrics].split(";")
                if entry
            )
            assert int(count_metrics["retrievedDocumentCount"]) == 0
            assert int(count_metrics["retrievedDocumentSize"]) == 0
            assert float(count_metrics["indexUtilizationRatio"]) == 1.0
            assert float(count_headers[http_constants.HttpHeaders.RequestCharge]) < 20.0

            # A single-partition feed-range query emits a legacy opaque
            # continuation token; that token must still resume on the
            # partition-key request path and return the same remaining items.
            feed_range = created_container.feed_range_from_partition_key(full_key)
            epk_pager = created_container.query_items(
                query=query,
                feed_range=feed_range,
                max_item_count=7,
            ).by_page()
            epk_first_page = list(next(epk_pager))
            assert epk_first_page
            legacy_token = epk_pager.continuation_token
            assert legacy_token
            assert _decode_token(legacy_token) is None

            expected_epk_remaining_ids = [
                item['id']
                for page in epk_pager
                for item in page
            ]
            resumed_via_partition_key_ids = [
                item['id']
                for page in created_container.query_items(
                    query=query,
                    partition_key=full_key,
                    max_item_count=7,
                ).by_page(legacy_token)
                for item in page
            ]
            assert expected_epk_remaining_ids == resumed_via_partition_key_ids
        finally:
            db.delete_container(created_container.id)

    def test_two_partition_feed_range_rust(self):
        """Feed_range overlapping two adjacent physical partitions."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_two_partition_feed_range
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

    def test_two_partition_feed_range_count_aggregate_pagination_rust(self):
        """Run a VALUE aggregate through a two-partition crossing feed_range."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_two_partition_feed_range_count_aggregate_pagination
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

    def test_two_partition_feed_range_min_aggregate_pagination_rust(self):
        """Run a VALUE MIN aggregate through a two-partition crossing feed_range."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_two_partition_feed_range_min_aggregate_pagination
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
        expected_values = _values_via_per_partition_scan(container, [chosen[0], chosen[1]])
        expected_min = min(expected_values)

        pager = container.query_items(
            query='SELECT VALUE MIN(c["value"]) FROM c',
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
        assert merged_rows[0] == expected_min, (
            "merged MIN result mismatch for two-partition crossing feed_range; "
            f"returned={merged_rows[0]}, expected={expected_min}")
        assert pager.continuation_token in (None, "", b""), (
            f"expected empty continuation after draining aggregate query; got "
            f"{pager.continuation_token!r}")

    def test_two_partition_feed_range_max_aggregate_pagination_rust(self):
        """Run a VALUE MAX aggregate through a two-partition crossing feed_range."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_two_partition_feed_range_max_aggregate_pagination
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
        expected_values = _values_via_per_partition_scan(container, [chosen[0], chosen[1]])
        expected_max = max(expected_values)

        pager = container.query_items(
            query='SELECT VALUE MAX(c["value"]) FROM c',
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
        assert merged_rows[0] == expected_max, (
            "merged MAX result mismatch for two-partition crossing feed_range; "
            f"returned={merged_rows[0]}, expected={expected_max}")
        assert pager.continuation_token in (None, "", b""), (
            f"expected empty continuation after draining aggregate query; got "
            f"{pager.continuation_token!r}")

    @pytest.mark.parametrize("merge_error_type", [TypeError, KeyError])
    def test_two_partition_feed_range_merge_fallback_preserves_rows_rust(
        self, monkeypatch, caplog, merge_error_type
    ):
        """Force merge failures and verify fallback extends docs without loss."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_two_partition_feed_range_merge_fallback_preserves_rows
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

        pytest.skip(
            "internals-only: patches Python _base._merge_query_results and asserts a "
            "_cosmos_client_connection fallback warning; the Rust driver merges query pages natively "
            "and never calls that Python helper."
        )
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

    def test_exception_during_post_preserves_resume_checkpoint_rust(self):
        """Inject a POST failure mid-query and verify the resume checkpoint."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_exception_during_post_preserves_resume_checkpoint
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

        pytest.skip(
            "internals-only: patches client_connection._CosmosClientConnection__Post and reads "
            "client_connection.last_response_headers; Rust query requests do not go through that "
            "Python transport method."
        )
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

    def test_explode_iteration_guard_raises_in_query_loop_rust(self, monkeypatch):
        """Drive the live ``__QueryFeed`` explode loop until the runtime guard raises."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_explode_iteration_guard_raises_in_query_loop
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with >= 2 physical partitions")

        p0, p1 = partitions[0], partitions[1]
        crossing = _crossing_feed_range(p0[0], p1[1])
        pytest.skip(
            "internals-only: patches client_connection._routing_map_provider and the Python "
            "_MAX_MULTI_OVERLAP_EXPLODE_ITERATIONS guard of __QueryFeed; Rust plans feed-range "
            "queries in the driver and does not use either."
        )
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

    def test_no_progress_guard_logs_warning_in_query_loop_rust(self, monkeypatch, caplog):
        """Drive repeated empty pages with unchanged continuation and assert warning emission."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_no_progress_guard_logs_warning_in_query_loop
        container = _get_container()
        partitions = _sorted_partition_ranges(container)
        if len(partitions) < 2:
            pytest.skip("Need a container with >= 2 physical partitions")

        p0, p1 = partitions[0], partitions[1]
        crossing = _crossing_feed_range(p0[0], p1[1])
        pytest.skip(
            "internals-only: patches client_connection._CosmosClientConnection__Post and the Python "
            "_MAX_CONSECUTIVE_NO_PROGRESS_PAGES guard; Rust query paging does not use either."
        )
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

    def test_three_way_overlap_rust(self):
        """Feed_range overlapping three adjacent physical partitions."""
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_three_way_overlap
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

    @pytest.mark.cosmosSplit
    @pytest.mark.cosmosAADSplit
    @pytest.mark.skipif(os.environ.get(REAL_SPLIT_ENV) != "1", reason=(
        "environment-gap: real partition split raises throughput to 60000 RU/s; "
        "opt in with COSMOS_QUERY_FEED_RANGE_REAL_SPLIT=1"
    ))
    def test_post_split_resume_rust(self):
        """Resume a saved continuation after a real partition split."""
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_post_split_resume
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
            trigger_split(container, target_throughput)
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

    def test_legacy_opaque_token_compat_rust(self, caplog):
        """Use an opaque continuation token; the query restarts from the beginning."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_legacy_opaque_token_compat
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

    def test_token_identity_mismatch_rejected_rust(self):
        """Replaying a token against a different query or feed_range must raise ValueError."""
        # pylint: disable-next=line-too-long
        # Source: tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition.test_token_identity_mismatch_rejected
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
