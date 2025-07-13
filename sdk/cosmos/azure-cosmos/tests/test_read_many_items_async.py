# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test for read_many_items API."""

import unittest
import uuid
from unittest.mock import patch, AsyncMock

import pytest
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestReadManyItems(unittest.IsolatedAsyncioTestCase):
    """Test cases for the read_many_items API."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    client: CosmosClient = None
    database = None
    container = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' in the test_config class to run the "
                "tests.")
        # Use async client
        cls.client = CosmosClient(cls.host, cls.masterKey)

    async def asyncSetUp(self):
        """Set up async resources before each test."""
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)

        # Create container asynchronously
        self.container = await self.database.create_container(
            id='read_many_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )

    async def asyncTearDown(self):
        """Clean up async resources after each test."""
        if self.container:
            await self.database.delete_container(self.container)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # Close async client
            import asyncio
            asyncio.run(cls.client.close())

    async def test_read_many_items_with_missing_items(self):
        """Tests read_many_items with a mix of existing and non-existent items."""
        # Create 5 items in the container
        existing_items = []
        for i in range(5):
            doc_id = "existing_item" + str(i) + str(uuid.uuid4())
            await self.container.create_item({'id': doc_id, 'data': i})
            # Since partition key is /id, use doc_id as partition key value
            existing_items.append((doc_id, doc_id))

        # Prepare items to read: 3 existing + 2 non-existent
        items_to_read = []

        # Add 3 existing items
        items_to_read.extend(existing_items[:3])

        # Add 2 non-existent items with non-existent partition keys
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))

        # Read the items back
        read_items = await self.container.read_many_items(items=items_to_read)

        # Verify results - should only return the 3 existing items
        self.assertEqual(len(read_items), 3)

        # Verify that only existing items are returned
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in existing_items[:3]}
        self.assertSetEqual(returned_ids, expected_ids)

        # Verify no non-existent items are in the results
        for item in read_items:
            self.assertFalse(item['id'].startswith('non_existent_item'))

    async def test_read_many_items_different_partition_key(self):
        """Tests read_many_items with partition key different from id."""
        # Create a new container with /pk as partition key
        container_pk = await self.database.create_container(
            id='read_many_pk_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        try:
            # Create some items with different id and pk values
            item_ids = []
            items_to_read = []
            for i in range(5):
                doc_id = "item" + str(i) + str(uuid.uuid4())
                pk_value = "pk_" + str(i)
                item_ids.append(doc_id)
                await container_pk.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
                items_to_read.append((doc_id, pk_value))

            # Read the items back
            read_items = await container_pk.read_many_items(items=items_to_read)

            # Verify the results
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))

            # Verify partition key values are correct
            for item in read_items:
                self.assertTrue(item['pk'].startswith('pk_'))

        finally:
            await self.database.delete_container(container_pk)

    async def test_read_many_items_hierarchical_partition_key(self):
        """Tests read_many_items with hierarchical partition key."""
        # Create a new container with hierarchical partition key
        container_hpk = await self.database.create_container(
            id='read_many_hpk_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash")
        )

        try:
            # Create some items with hierarchical partition key
            item_ids = []
            items_to_read = []
            for i in range(3):
                doc_id = "item" + str(i) + str(uuid.uuid4())
                tenant_id = f"tenant{i % 2}"  # Use 2 different tenants
                user_id = f"user{i}"
                item_ids.append(doc_id)

                await container_hpk.create_item({
                    'id': doc_id,
                    'tenantId': tenant_id,
                    'userId': user_id,
                    'data': i
                })

                # HPK should be passed as a list
                items_to_read.append((doc_id, [tenant_id, user_id]))

            # Read the items back
            read_items = await container_hpk.read_many_items(items=items_to_read)

            # Verify the results
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))

            # Verify hierarchical partition key values are correct
            for item in read_items:
                self.assertTrue(item['tenantId'].startswith('tenant'))
                self.assertTrue(item['userId'].startswith('user'))

        finally:
            await self.database.delete_container(container_hpk)

    async def test_read_many_items(self):
        """Tests the basic functionality of read_many_items."""
        # Create some items to read
        item_ids = []
        items_to_read = []
        for i in range(5):
            doc_id = "item" + str(i) + str(uuid.uuid4())
            item_ids.append(doc_id)
            await self.container.create_item({'id': doc_id, 'pk': doc_id, 'data': i})
            items_to_read.append((doc_id, doc_id))

        # Read the items back
        read_items = await self.container.read_many_items(items=items_to_read)


        # Verify the results
        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    async def test_read_many_items_concurrency_internals(self):
        """Tests that read_many_items properly chunks large requests with 1000 item chunks and 10 concurrent semaphore limit."""

        # Create 2500 items to force chunking (will create 3 chunks of 1000, 1000, 500)
        items_to_read = []
        for i in range(2500):
            doc_id = f"chunk_item_{i}_{uuid.uuid4()}"
            items_to_read.append((doc_id, doc_id))

        # Mock the internal QueryItems method to capture actual chunking behavior
        with patch.object(self.container.client_connection, 'QueryItems') as mock_query:
            # Create a proper async iterator mock
            class MockAsyncIterator:
                def __init__(self):
                    pass

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    raise StopAsyncIteration

            # Return the async iterator directly, not a coroutine
            mock_query.return_value = MockAsyncIterator()

            # Execute read_many_items - let the REAL chunking logic run
            result = await self.container.read_many_items(items=items_to_read)

            # Now verify that the chunking logic actually worked correctly
            self.assertEqual(mock_query.call_count, 3)

            # Verify the actual SQL queries and parameters generated by the REAL chunking logic
            for i, call in enumerate(mock_query.call_args_list):
                query_spec = call[0][1]  # The actual SQL query specification
                param_count = len(query_spec['parameters'])

                # Check that the real chunking logic created the correct parameter counts
                if i < 2:
                    self.assertEqual(param_count, 1000)  # 1000 items * 1 param each
                else:
                    self.assertEqual(param_count, 500)  # 500 items * 1 param each


if __name__ == '__main__':
    unittest.main()