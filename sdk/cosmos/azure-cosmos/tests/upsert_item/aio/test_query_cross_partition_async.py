# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the async cross-partition paging test, which seeds items with upsert_item.

Each test owns a unique database (key-auth Rust client for control plane, Rust data client
for data plane) with the original 5-partition ``/pk`` container, and always deletes it.
The test body is unchanged.
"""
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client_async
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryCrossPartitionAsync(unittest.IsolatedAsyncioTestCase):
    """Rust-path copy of tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync."""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    key_container: ContainerProxy = None
    client: CosmosClient = None
    key_client: CosmosClient = None
    config = TestSettings
    host = config.host
    masterKey = config.masterKey
    TEST_CONTAINER_ID = str(uuid.uuid4())

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = unique_database_id("upsert-query-xp-async")
        # Closed decision: Rust owns endpoint discovery and multi-write routing
        # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). Rust-backed clients reject the
        # original's multiple_write_locations argument (even False), so it is omitted.
        # Key-auth client for control-plane operations (create/delete database and containers)
        self.key_client = CosmosClient(self.host, self.masterKey, _backend="rust")
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.key_db = await self.key_client.create_database(self.TEST_DATABASE_ID)
        self.addAsyncCleanup(self.key_client.delete_database, self.TEST_DATABASE_ID)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        # Create container via key-auth (control-plane), get data container via data client
        created_container_ref = await self.key_db.create_container(
            self.TEST_CONTAINER_ID,
            PartitionKey(path="/pk"),
            offer_throughput=self.config.THROUGHPUT_FOR_5_PARTITIONS)
        self.created_container = self.created_db.get_container_client(created_container_ref.id)
        self.key_container = self.key_db.get_container_client(created_container_ref.id)

    async def test_paging_with_continuation_token_async_rust(self):
        # Source: tests/test_query_cross_partition_async.py::TestQueryCrossPartitionAsync.test_paging_with_continuation_token_async
        document_definition = {'pk': 'pk', 'id': '1'}
        await self.created_container.upsert_item(body=document_definition)
        document_definition = {'pk': 'pk', 'id': '2'}
        await self.created_container.upsert_item(body=document_definition)

        query = 'SELECT * from c'
        query_iterable = self.created_container.query_items(
            query=query,
            partition_key='pk',
            max_item_count=1
        )
        pager = query_iterable.by_page()
        await pager.__anext__()
        token = pager.continuation_token

        second_page = [item async for item in await pager.__anext__()][0]

        pager = query_iterable.by_page(token)
        second_page_fetched_with_continuation_token = [item async for item in await pager.__anext__()][0]

        assert second_page['id'] == second_page_fetched_with_continuation_token['id']


if __name__ == '__main__':
    unittest.main()
