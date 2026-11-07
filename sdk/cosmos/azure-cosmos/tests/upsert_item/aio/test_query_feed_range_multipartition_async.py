# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the async full-partition-key feed-range pagination test, which seeds
items with upsert_item.

The autouse class fixture owns a unique database (``DATABASE_ID``) and always deletes it;
the test creates its own MultiHash container in it as the original does. The original
module's 5-partition repro container is not used by this test, so it is not created.
The test body is unchanged.
"""

import unittest
import uuid
from typing import List

import pytest
import pytest_asyncio

from azure.cosmos import documents
from azure.cosmos import http_constants
from azure.cosmos.aio import CosmosClient
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id

DATABASE_ID = unique_database_id("upsert-feed-range-mp-async")


def _client() -> CosmosClient:
    """Return a data-plane client. Uses AAD when COSMOS_TEST_DATA_AUTH_MODE=aad,
    key auth otherwise, so the AAD lane actually exercises AAD."""
    return create_data_client_async(_backend="rust")


@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    client = CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust")
    try:
        await client.create_database(DATABASE_ID)
        try:
            yield
        finally:
            await client.delete_database(DATABASE_ID)
    finally:
        await client.close()


@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestFeedRangeMultiPartitionAsync:
    """Rust-path copy of tests/test_query_feed_range_multipartition_async.py::TestFeedRangeMultiPartitionAsync."""

    async def test_full_partition_key_query_pagination_resume_and_count_is_index_only_async_rust(self):
        """Query with a full partition key on a hierarchical container, drain
        page 1, resume from the returned continuation token, and confirm the
        resumed pages match the remaining pages of a fresh iterator and
        cover the same documents as a baseline scan in the same order. Also
        confirm a partition-scoped aggregate remains index-only.
        """
        # Source: tests/test_query_feed_range_multipartition_async.py::TestFeedRangeMultiPartitionAsync.test_full_partition_key_query_pagination_resume_and_count_is_index_only_async
        client = _client()
        try:
            db = client.get_database_client(DATABASE_ID)
            container_id = "FeedRangeMultiPartitionAsyncFullPK-" + str(uuid.uuid4())
            created_container = await db.create_container_if_not_exists(
                id=container_id,
                partition_key=PartitionKey(
                    path=['/state', '/city', '/zipcode'],
                    kind=documents.PartitionKind.MultiHash),
                offer_throughput=400,
            )
            try:
                full_key = ['CA', 'Oxnard', '93033']
                for i in range(25):
                    await created_container.upsert_item({
                        'id': f'full-pk-doc-async-{i:03d}',
                        'state': full_key[0],
                        'city': full_key[1],
                        'zipcode': full_key[2],
                        'value': i,
                    })
                for i in range(5):
                    await created_container.upsert_item({
                        'id': f'other-doc-async-{i:03d}',
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
                first_page_iter = await pager.__anext__()
                first_page = [it async for it in first_page_iter]
                assert first_page, (
                    "first page must contain at least one item to exercise resume")
                token = pager.continuation_token
                assert token, (
                    "expected a non-empty continuation token after page 1 to "
                    "exercise the resume path")

                expected_remaining_ids: List[str] = []
                async for page in pager:
                    expected_remaining_ids.extend(
                        [it['id'] async for it in page])

                resumed_remaining_ids: List[str] = []
                async for page in query_iterable.by_page(token):
                    resumed_remaining_ids.extend(
                        [it['id'] async for it in page])

                assert expected_remaining_ids == resumed_remaining_ids, (
                    "Pages returned after resuming from the continuation token "
                    "must match the pages returned by draining a fresh iterator")

                baseline_ids: List[str] = []
                async for item in created_container.query_items(
                        query=query, partition_key=full_key):
                    baseline_ids.append(item['id'])
                fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
                assert baseline_ids == fetched_ids, (
                    "Page 1 plus the resumed pages must equal the baseline "
                    "documents for this partition key in the same order")

                count_iterable = created_container.query_items(
                    query="SELECT VALUE COUNT(1) FROM c",
                    partition_key=full_key,
                    populate_query_metrics=True,
                )
                count_pager = count_iterable.by_page()
                count_pages = []
                async for page in count_pager:
                    count_pages.append([item async for item in page])
                assert count_pages == [[25]]
                assert count_pager.continuation_token is None

                count_headers = count_iterable.get_response_headers()
                # Divergence not yet in docs/V5/api-review/RUST_PARITY_PUSHBACKS.md: Rust query_items with populate_query_metrics=True returns no x-ms-documentdb-query-metrics response header (legacy does), so this lookup raises KeyError.
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
                feed_range = await created_container.feed_range_from_partition_key(full_key)
                # Known gap 30: `query_items()`: remaining query, paging, and continuation-token gaps (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30). The point feed range from feed_range_from_partition_key is rejected with ValueError ("nonempty min-inclusive, max-exclusive Range").
                epk_pager = created_container.query_items(
                    query=query,
                    feed_range=feed_range,
                    max_item_count=7,
                ).by_page()
                epk_first_page_iter = await epk_pager.__anext__()
                epk_first_page = [item async for item in epk_first_page_iter]
                assert epk_first_page
                legacy_token = epk_pager.continuation_token
                assert legacy_token
                assert _decode_token(legacy_token) is None

                expected_epk_remaining_ids: List[str] = []
                async for page in epk_pager:
                    expected_epk_remaining_ids.extend(
                        [item['id'] async for item in page])

                resumed_via_partition_key_ids: List[str] = []
                partition_key_pager = created_container.query_items(
                    query=query,
                    partition_key=full_key,
                    max_item_count=7,
                ).by_page(legacy_token)
                async for page in partition_key_pager:
                    resumed_via_partition_key_ids.extend(
                        [item['id'] async for item in page])

                assert expected_epk_remaining_ids == resumed_via_partition_key_ids
            finally:
                try:
                    await db.delete_container(created_container.id)
                except Exception:  # pylint: disable=broad-except
                    pass
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()
