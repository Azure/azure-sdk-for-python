# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original prefix-query body with an owned database, without unrelated shared setup.

Both parity columns use this fixture. The original three-level key,
400 RU/s container, seeded items, queries and assertions are preserved.
Multiple physical partitions are not guaranteed by this test.
"""

import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, documents


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

            count_results = list(created_container.query_items(
                query="SELECT VALUE COUNT(1) FROM c",
                partition_key=['CA'],
            ))
            assert count_results == [30]
        finally:
            db.delete_container(created_container.id)
