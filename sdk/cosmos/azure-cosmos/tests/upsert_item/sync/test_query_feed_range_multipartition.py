# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the sync full-partition-key feed-range pagination test, which seeds
items with upsert_item.

The autouse class fixture owns a unique database (``DATABASE_ID``) and always deletes it;
the test creates its own MultiHash container in it as the original does. The original
module's 5-partition repro container is not used by this test, so it is not created.
The test body is unchanged.
"""

import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, documents, http_constants
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_setup_client
from config.settings import unique_database_id

DATABASE_ID = unique_database_id("upsert-feed-range-mp")


def _client() -> CosmosClient:
    return create_setup_client(_backend="rust")


@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    client = _client()
    try:
        client.create_database(DATABASE_ID)
        try:
            yield
        finally:
            client.delete_database(DATABASE_ID)
    finally:
        client.close()


@pytest.mark.cosmosQuery
class TestFeedRangeMultiPartition:
    """Rust-path copy of tests/test_query_feed_range_multipartition.py::TestFeedRangeMultiPartition."""

    def test_full_partition_key_query_pagination_resume_and_count_is_index_only_rust(self):
        """Full hierarchical partition-key query resumes and remains index-only.

        This uses a dedicated MultiHash container and a full key value so the
        query stays scoped to one logical partition while still exercising
        pagination, resume, and aggregate query metrics on the partition_key path.
        """
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
            feed_range = created_container.feed_range_from_partition_key(full_key)
            # Known gap 30: `query_items()`: remaining query, paging, and continuation-token gaps (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-30). The point feed range from feed_range_from_partition_key is rejected with ValueError ("nonempty min-inclusive, max-exclusive Range").
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


if __name__ == "__main__":
    unittest.main()
