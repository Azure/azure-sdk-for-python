# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async parity for the multi-partition feed_range tests.

Async mirror of ``test_query_feed_range_multipartition.py``; assertions
are identical, only the I/O is ``async``/``await``.
"""

import asyncio
import unittest
import uuid
from typing import Iterable, List, Optional, Tuple

import pytest
import pytest_asyncio

import test_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey

CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID

REPRO_CONTAINER_ID = "FeedRangeMultiPartitionAsync-" + str(uuid.uuid4())
REPRO_PARTITION_KEY = "pk"
REPRO_THROUGHPUT = CONFIG.THROUGHPUT_FOR_5_PARTITIONS
REPRO_DOC_COUNT = 200
PAGE_SIZE = 5
MIN_DOCS_PER_PARTITION = 15


def _client() -> CosmosClient:
    return CosmosClient(HOST, KEY)


def _get_container(client: CosmosClient):
    return client.get_database_client(DATABASE_ID).get_container_client(REPRO_CONTAINER_ID)


async def _sorted_partition_ranges(container) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    async for fr in container.read_feed_ranges():
        r = fr["Range"]
        pairs.append((r["min"], r["max"]))
    pairs.sort(key=lambda p: p[0])
    return pairs


async def _count_in_range(container, range_min: str, range_max: str) -> int:
    fr = test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))
    items = [it async for it in container.query_items(
        query="SELECT VALUE COUNT(1) FROM c", feed_range=fr)]
    return items[0] if items else 0


def _crossing_feed_range(range_min: str, range_max: str):
    return test_config.create_feed_range_in_dict(
        test_config.create_range(range_min=range_min, range_max=range_max,
                                 is_min_inclusive=True, is_max_inclusive=False))


async def _ids_via_per_partition_scan(container, partition_ranges: Iterable[Tuple[str, str]]):
    ground_truth = set()
    for (mn, mx) in partition_ranges:
        fr = _crossing_feed_range(mn, mx)
        async for item in container.query_items(query="SELECT c.id FROM c", feed_range=fr):
            ground_truth.add(item["id"])
    return ground_truth


async def _drain_pages(pager) -> Tuple[List[List[dict]], List[str]]:
    pages: List[List[dict]] = []
    all_ids: List[str] = []
    async for page in pager:
        items = [it async for it in page]
        pages.append(items)
        all_ids.extend(it["id"] for it in items)
    return pages, all_ids


@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    client = _client()
    db = client.get_database_client(DATABASE_ID)
    container = await db.create_container_if_not_exists(
        id=REPRO_CONTAINER_ID,
        partition_key=PartitionKey(path="/" + REPRO_PARTITION_KEY, kind="Hash"),
        offer_throughput=REPRO_THROUGHPUT)
    for i in range(REPRO_DOC_COUNT):
        await container.upsert_item({
            REPRO_PARTITION_KEY: f"pk-{i:04d}",
            "id": f"doc-{i:04d}",
            "value": i,
        })
    yield
    try:
        await db.delete_container(REPRO_CONTAINER_ID)
    except Exception:  # pylint: disable=broad-except
        pass
    await client.close()


@pytest.mark.cosmosQuery
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestFeedRangeMultiPartitionAsync:
    """Async end-to-end tests for feed_range queries that overlap multiple
    physical partitions."""

    # ------------------------------------------------------------------ #
    # Single-partition control
    # ------------------------------------------------------------------ #
    async def test_single_partition_feed_range_async(self):
        """Async parity for the no-fan-out regression guard. See the sync
        ``test_single_partition_feed_range`` for the assertion contract."""
        client = _client()
        try:
            container = _get_container(client)
            partitions = await _sorted_partition_ranges(container)
            if not partitions:
                pytest.skip("Container has no physical partitions")

            chosen_pp = None
            for (mn, mx) in partitions:
                if await _count_in_range(container, mn, mx) >= MIN_DOCS_PER_PARTITION:
                    chosen_pp = (mn, mx)
                    break
            if chosen_pp is None:
                pytest.skip("No single partition populated with ≥ "
                            f"{MIN_DOCS_PER_PARTITION} docs")
            single = _crossing_feed_range(chosen_pp[0], chosen_pp[1])
            ground_truth = await _ids_via_per_partition_scan(container, [chosen_pp])

            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=single,
                max_item_count=PAGE_SIZE,
            ).by_page()
            pages, all_ids = await _drain_pages(pager)

            for idx, page in enumerate(pages):
                if idx < len(pages) - 1:
                    assert len(page) == PAGE_SIZE, (
                        f"page {idx} returned {len(page)} items, expected "
                        f"exactly {PAGE_SIZE}")
                else:
                    assert len(page) <= PAGE_SIZE

            unique = set(all_ids)
            assert len(all_ids) == len(unique), (
                f"single-partition path returned duplicates: "
                f"{len(all_ids) - len(unique)} duplicate id(s)")
            assert unique == ground_truth, (
                f"single-partition coverage mismatch: returned={len(unique)}, "
                f"ground_truth={len(ground_truth)}, "
                f"missing={len(ground_truth - unique)}, "
                f"unexpected={len(unique - ground_truth)}")

            assert pager.continuation_token in (None, "", b""), (
                f"expected empty continuation after draining all pages; got "
                f"{pager.continuation_token!r}")
        finally:
            await client.close()

    # ------------------------------------------------------------------ #
    # Two-partition feed_range
    # ------------------------------------------------------------------ #
    async def test_two_partition_feed_range_async(self):
        client = _client()
        try:
            container = _get_container(client)
            partitions = await _sorted_partition_ranges(container)
            if len(partitions) < 2:
                pytest.skip("Need a container with ≥ 2 physical partitions")

            chosen = None
            for i in range(len(partitions) - 1):
                p0, p1 = partitions[i], partitions[i + 1]
                if (await _count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                        and await _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                    chosen = (p0, p1)
                    break
            if chosen is None:
                pytest.skip("No adjacent partition pair both populated with ≥ "
                            f"{MIN_DOCS_PER_PARTITION} docs")
            (p0_min, _), (_, p1_max) = chosen
            crossing = _crossing_feed_range(p0_min, p1_max)
            ground_truth = await _ids_via_per_partition_scan(
                container, [chosen[0], chosen[1]])

            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page()
            pages, all_ids = await _drain_pages(pager)

            oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
            assert not oversized, (
                f"page-size budget violated (max_item_count={PAGE_SIZE}); "
                f"got pages with sizes {[len(p) for p in pages]}; "
                f"oversized pages: {oversized}.")

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
        finally:
            await client.close()

    # ------------------------------------------------------------------ #
    # Three-way overlap
    # ------------------------------------------------------------------ #
    async def test_three_way_overlap_async(self):
        client = _client()
        try:
            container = _get_container(client)
            partitions = await _sorted_partition_ranges(container)
            if len(partitions) < 3:
                pytest.skip("Need a container with ≥ 3 physical partitions")

            chosen: Optional[List[Tuple[str, str]]] = None
            for i in range(len(partitions) - 2):
                triple = partitions[i:i + 3]
                ok = True
                for mn, mx in triple:
                    if await _count_in_range(container, mn, mx) < MIN_DOCS_PER_PARTITION:
                        ok = False
                        break
                if ok:
                    chosen = triple
                    break
            if chosen is None:
                pytest.skip("No three adjacent partitions all populated with ≥ "
                            f"{MIN_DOCS_PER_PARTITION} docs")
            assert chosen is not None  # narrows for type checkers; pytest.skip raises
            crossing = _crossing_feed_range(chosen[0][0], chosen[2][1])
            ground_truth = await _ids_via_per_partition_scan(container, chosen)

            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page()
            pages, all_ids = await _drain_pages(pager)

            oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
            assert not oversized, (
                f"page-size budget violated; sizes={[len(p) for p in pages]}; "
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
        finally:
            await client.close()

    # ------------------------------------------------------------------ #
    # Post-split resume (slow)
    # ------------------------------------------------------------------ #
    @pytest.mark.cosmosSplit
    async def test_post_split_resume_async(self):
        client = _client()
        try:
            container = _get_container(client)
            partitions_before = await _sorted_partition_ranges(container)
            if len(partitions_before) < 2:
                pytest.skip("Need a container with ≥ 2 physical partitions")

            chosen = None
            for i in range(len(partitions_before) - 1):
                p0, p1 = partitions_before[i], partitions_before[i + 1]
                if (await _count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                        and await _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
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
            page_1_iter = await pager_pre.__anext__()
            page_1 = [it async for it in page_1_iter]
            ct_after_page_1 = pager_pre.continuation_token
            page_1_ids = [item["id"] for item in page_1]
            assert ct_after_page_1, (
                "expected a non-empty continuation token after page 1")

            # Step 2 — trigger a real split.
            target_throughput = max(REPRO_THROUGHPUT * 2, 60000)
            try:
                await test_config.TestConfig.trigger_split_async(container, target_throughput)
            except unittest.SkipTest:
                raise
            await asyncio.sleep(10)
            _ = [fr async for fr in container.read_feed_ranges(force_refresh=True)]

            # Step 3 — resume with the saved continuation, same feed_range.
            pager_post = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=ct_after_page_1)
            post_pages, post_ids = await _drain_pages(pager_post)

            combined_ids = page_1_ids + post_ids
            unique = set(combined_ids)
            assert len(combined_ids) == len(unique), (
                f"duplicates across the split boundary: {len(combined_ids)} ids "
                f"returned across page 1 + {len(post_pages)} post-split page(s), "
                f"{len(unique)} distinct, "
                f"{len(combined_ids) - len(unique)} duplicate(s).")

            oversized = [(i, len(p)) for i, p in enumerate(post_pages) if len(p) > PAGE_SIZE]
            assert not oversized, (
                f"page-size budget violated post-split; sizes="
                f"{[len(p) for p in post_pages]}; oversized={oversized}.")

            partitions_after = await _sorted_partition_ranges(container)
            post_split_overlaps = [(mn, mx) for (mn, mx) in partitions_after
                                   if min(p1_max, mx) > max(p0_min, mn)]
            ground_truth = await _ids_via_per_partition_scan(container, post_split_overlaps)
            assert unique == ground_truth, (
                f"item-set mismatch after post-split resume: returned="
                f"{len(unique)}, ground_truth={len(ground_truth)}, "
                f"missing={len(ground_truth - unique)}, "
                f"unexpected={len(unique - ground_truth)}.")
        finally:
            await client.close()

    # ------------------------------------------------------------------ #
    # Legacy opaque token compatibility
    # ------------------------------------------------------------------ #
    async def test_legacy_opaque_token_compat_async(self):
        """Async parity for the legacy-opaque-token compatibility test.
        See the sync ``test_legacy_opaque_token_compat`` for the assertion
        contract."""
        client = _client()
        try:
            container = _get_container(client)
            partitions = await _sorted_partition_ranges(container)
            if len(partitions) < 2:
                pytest.skip("Need a container with ≥ 2 physical partitions")

            chosen = None
            for i in range(len(partitions) - 1):
                p0, p1 = partitions[i], partitions[i + 1]
                if (await _count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                        and await _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
                    chosen = (p0, p1)
                    break
            if chosen is None:
                pytest.skip("No adjacent partition pair both populated with ≥ "
                            f"{MIN_DOCS_PER_PARTITION} docs")
            (p0_min, _), (_, p1_max) = chosen
            crossing = _crossing_feed_range(p0_min, p1_max)
            ground_truth = await _ids_via_per_partition_scan(
                container, [chosen[0], chosen[1]])

            # cspell:ignore AOXB BAAAAAAAAAA EAAAAFAAAA
            legacy_token = "+RID:~Yxs1AOXBSp4BAAAAAAAAAA==#RT:1#TRC:5#ISV:2#IEO:65567#FPC:AgEAAAAFAAAA"

            pager = container.query_items(
                query="SELECT * FROM c",
                feed_range=crossing,
                max_item_count=PAGE_SIZE,
            ).by_page(continuation_token=legacy_token)
            pages, all_ids = await _drain_pages(pager)

            oversized = [(i, len(p)) for i, p in enumerate(pages) if len(p) > PAGE_SIZE]
            assert not oversized, (
                f"page-size budget violated under legacy-token resume; "
                f"sizes={[len(p) for p in pages]}; oversized={oversized}")

            unique = set(all_ids)
            assert len(all_ids) == len(unique), (
                f"legacy-token restart produced duplicates: "
                f"{len(all_ids) - len(unique)} duplicate id(s)")
            assert unique == ground_truth, (
                f"legacy-token restart coverage mismatch: returned="
                f"{len(unique)}, ground_truth={len(ground_truth)}, "
                f"missing={len(ground_truth - unique)}, "
                f"unexpected={len(unique - ground_truth)}")

            assert pager.continuation_token in (None, "", b""), (
                f"expected empty continuation after draining all pages on "
                f"legacy-token restart; got {pager.continuation_token!r}")
        finally:
            await client.close()

    # ------------------------------------------------------------------ #
    # Identity-fingerprint mismatch rejection (live half)
    # ------------------------------------------------------------------ #
    async def test_token_identity_mismatch_rejected_async(self):
        """Async parity for the live identity-mismatch test. See the
        sync ``test_token_identity_mismatch_rejected`` for the assertion
        contract."""
        client = _client()
        try:
            container = _get_container(client)
            partitions = await _sorted_partition_ranges(container)
            if len(partitions) < 2:
                pytest.skip("Need a container with ≥ 2 physical partitions")

            chosen = None
            for i in range(len(partitions) - 1):
                p0, p1 = partitions[i], partitions[i + 1]
                if (await _count_in_range(container, p0[0], p0[1]) >= MIN_DOCS_PER_PARTITION
                        and await _count_in_range(container, p1[0], p1[1]) >= MIN_DOCS_PER_PARTITION):
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
            page_1_iter = await pager.__anext__()
            _ = [it async for it in page_1_iter]
            token = pager.continuation_token
            assert token, ("expected a non-empty continuation after page 1; "
                           "test cannot exercise resume validation otherwise")

            async def _drain(p):
                async for page in p:
                    _ = [it async for it in page]

            # (a) Different query TEXT.
            with pytest.raises(ValueError) as excinfo_q:
                await _drain(container.query_items(
                    query={"query": "SELECT * FROM c WHERE c[\"value\"] >= @v AND c.id != ''",
                           "parameters": original_params},
                    feed_range=crossing,
                    max_item_count=PAGE_SIZE,
                ).by_page(continuation_token=token))
            assert "query" in str(excinfo_q.value).lower(), (
                f"ValueError on query-text mismatch must name the failing "
                f"field; got: {excinfo_q.value!r}")

            # (b) Different parameter VALUE.
            with pytest.raises(ValueError) as excinfo_p:
                await _drain(container.query_items(
                    query={"query": original_query,
                           "parameters": [{"name": "@v", "value": 999999}]},
                    feed_range=crossing,
                    max_item_count=PAGE_SIZE,
                ).by_page(continuation_token=token))
            assert "query" in str(excinfo_p.value).lower(), (
                f"ValueError on parameter-value mismatch must name the "
                f"query field; got: {excinfo_p.value!r}")

            # (c) Different feed_range.
            single_p0 = _crossing_feed_range(chosen[0][0], chosen[0][1])
            with pytest.raises(ValueError) as excinfo_f:
                await _drain(container.query_items(
                    query={"query": original_query, "parameters": original_params},
                    feed_range=single_p0,
                    max_item_count=PAGE_SIZE,
                ).by_page(continuation_token=token))
            assert "feed_range" in str(excinfo_f.value).lower(), (
                f"ValueError on feed_range mismatch must name the "
                f"feed_range field; got: {excinfo_f.value!r}")
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()

