# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async prefix-query body with owned resources and explicit cleanup.

Both parity columns omit the unrelated shared high-throughput fixture.
The test's own 400 RU/s container and functional assertions are unchanged.
"""

import os
import unittest
import uuid
from typing import List

import pytest

from azure.cosmos import PartitionKey, documents
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosQuery
class TestFeedRangeMultiPartitionAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database_id = "legacy_query_prefix_async_" + uuid.uuid4().hex
        self.database = await self.client.create_database(self.database_id)
        self.addAsyncCleanup(self._delete_owned_database)
        print(f"\nOwned async prefix query database: {self.database_id}")

    async def _delete_owned_database(self):
        await self.client.delete_database(self.database_id)
        print(f"Deleted owned async prefix query database: {self.database_id}")

    async def test_prefix_partition_key_query_pagination_resume_async_rust(self):
        """Prefix query resumes all matching items and preserves the COUNT result."""
        # Source: tests/test_query_feed_range_multipartition_async.py::TestFeedRangeMultiPartitionAsync.test_prefix_partition_key_query_pagination_resume_async
        db = self.database
        container_id = "FeedRangeMultiPartitionAsyncPrefixPK-" + str(uuid.uuid4())
        created_container = await db.create_container_if_not_exists(
            id=container_id,
            partition_key=PartitionKey(
                path=['/state', '/city', '/zipcode'],
                kind=documents.PartitionKind.MultiHash),
            offer_throughput=400,
        )
        try:
            for i in range(30):
                await created_container.upsert_item({
                    'id': f'ca-doc-async-{i:03d}',
                    'state': 'CA',
                    'city': f'city-{i % 5}',
                    'zipcode': f'zip-{i:03d}',
                    'value': i,
                })
            for i in range(6):
                await created_container.upsert_item({
                    'id': f'wa-doc-async-{i:03d}',
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
            first_page_iter = await pager.__anext__()
            first_page = [it async for it in first_page_iter]
            assert first_page
            token = pager.continuation_token
            assert token, (
                "Expected a non-empty continuation token after page 1 "
                "to exercise the resume path")

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
                    query=query, partition_key=['CA']):
                baseline_ids.append(item['id'])
            fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
            assert baseline_ids == fetched_ids, (
                "Page 1 plus the resumed pages must equal the baseline "
                "documents for this partition key prefix in the same order")

            count_results = [
                item async for item in created_container.query_items(
                    query="SELECT VALUE COUNT(1) FROM c",
                    partition_key=['CA'],
                )
            ]
            assert count_results == [30]
        finally:
            await db.delete_container(created_container.id)
