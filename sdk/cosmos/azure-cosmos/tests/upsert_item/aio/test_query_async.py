# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copies of the async query tests that seed items with upsert_item.

Setup owns a unique database with a multi-partition ``/pk`` container standing in for the
shared ``TEST_MULTI_PARTITION_CONTAINER_ID`` container, and always deletes it. As in the
original, a sync key-auth client (Rust-backed here) does control-plane work and an async
data client does data-plane work. Test bodies are unchanged.
"""
import unittest
import uuid
from asyncio import gather

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos._retry_options import RetryOptions
from azure.cosmos._routing.feed_range_continuation import _decode_token
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client_async, create_setup_client
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copies of tests/test_query_async.py::TestQueryAsync."""

    created_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    client: CosmosClient = None
    key_client = None
    key_db = None
    config = TestSettings
    TEST_CONTAINER_ID = config.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("upsert-query-async")
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). Rust-backed clients reject the
        # original's multiple_write_locations argument (even False), so it is omitted.
        cls.key_client = create_setup_client(_backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls.key_db = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.addClassCleanup(cls.key_client.delete_database, cls.TEST_DATABASE_ID)
        cls.key_db.create_container(
            id=cls.config.TEST_MULTI_PARTITION_CONTAINER_ID,
            partition_key=PartitionKey(path="/" + cls.config.TEST_CONTAINER_PARTITION_KEY),
            offer_throughput=cls.config.THROUGHPUT_FOR_5_PARTITIONS)

    async def asyncSetUp(self):
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    def _create_container_if_not_exists_for_test(self, container_id, partition_key, **kwargs):
        """Create container if not exists via sync key-auth setup client, return async data-plane proxy."""
        self.key_db.create_container_if_not_exists(id=container_id, partition_key=partition_key, **kwargs)
        return self.created_db.get_container_client(container_id)

    def _delete_container_for_test(self, container_id):
        """Delete container via sync key-auth setup client (control-plane)."""
        self.key_db.delete_container(container_id)

    async def test_full_pk_continuation_emits_legacy_by_default_async_rust(self):
        """Full partition-key queries return legacy continuation tokens by default."""
        # Source: tests/test_query_async.py::TestQueryAsync.test_full_pk_continuation_emits_legacy_by_default_async
        # The token is the legacy (opaque) form, not the new feed-range token: _decode_token
        # returns None only for the legacy form. Without this, changing the default token format
        # could break customers who stored an old token and replay it later.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        assert token is not None
        assert _decode_token(token) is None

    async def test_full_pk_legacy_replay_resumes_same_page_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_full_pk_legacy_replay_resumes_same_page_async
        # Replaying that legacy continuation token must resume on the same next page. Without
        # this, a regression in legacy-token replay would drop or repeat results for customers
        # who page through query results.
        created_collection = self.created_db.get_container_client(self.config.TEST_MULTI_PARTITION_CONTAINER_ID)
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})
        await created_collection.upsert_item(body={'pk': 'pk', 'id': str(uuid.uuid4())})

        query_iterable = created_collection.query_items(
            query='SELECT * from c',
            partition_key='pk',
            max_item_count=1,
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token
        second_page = [item async for item in await pager.__anext__()][0]

        assert token is not None
        assert _decode_token(token) is None

        replay_pager = query_iterable.by_page(token)
        replay_second_page = [item async for item in await replay_pager.__anext__()][0]
        assert second_page['id'] == replay_second_page['id']

    async def test_cosmos_query_retryable_error_async_rust(self):
        # Source: tests/test_query_async.py::TestQueryAsync.test_cosmos_query_retryable_error_async
        async def query_items(database):
            # Tests to make sure 429 exception is surfaced when retries run out in the first page of a query.
            try:
                # create_container here is control-plane. Using key_db (sync, key-auth).
                # Container access for data is through the async AAD client.
                self.key_db.create_container(
                    id="query_retryable_error_test", partition_key=PartitionKey(path="/pk"), offer_throughput=400
                )
                container = database.get_container_client("query_retryable_error_test")
            except exceptions.CosmosResourceExistsError:
                container = database.get_container_client("query_retryable_error_test")
            query = "SELECT * FROM c"
            try:
                query_iterable = [d async for d in container.query_items(query, max_item_count=10)]
                if len(query_iterable) == 0:
                    # Query should not return empty if it has items to query on a retryable exception is raised
                    pytest.fail("Expected 429 Exception.")
            except exceptions.CosmosHttpResponseError as ex:
                # A retryable exception should be surfaced when retries run out
                assert ex.status_code == 429

        self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client("query_retryable_error_test")
        # Created items to query
        for _ in range(150):
            partition_key = 'pk' + str(uuid.uuid4())
            item = {
                'id': 'item' + str(uuid.uuid4()),
                'partitionKey': partition_key,
                'content': 'This is some random content',
            }

            try:
                await created_collection.upsert_item(item)
            except exceptions.CosmosHttpResponseError as e:
                pytest.fail(e)
        # Set retry options to fail much more easily to avoid too much concurrency
        # Known gap 11: Closed: driver-owned throttle retry waiting (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-11). The Rust driver owns 429 retry waiting, so mutating the connection policy's RetryOptions after construction does not shorten its retries; the queries below still pass because each either returns items or surfaces a 429.
        retry_options = RetryOptions(max_retry_attempt_count=1,
                                     fixed_retry_interval_in_milliseconds=1, max_wait_time_in_seconds=1)
        old_retry = self.client.client_connection.connection_policy.RetryOptions
        self.client.client_connection.connection_policy.RetryOptions = retry_options
        self._create_container_if_not_exists_for_test("query_retryable_error_test", PartitionKey(path="/pk"))
        # Force a 429 exception by having multiple concurrent queries.
        num_queries = 4
        await gather(*[query_items(self.created_db) for _ in range(num_queries)])

        self.client.client_connection.connection_policy.RetryOptions = old_retry
        self._delete_container_for_test("query_retryable_error_test")


if __name__ == '__main__':
    unittest.main()
