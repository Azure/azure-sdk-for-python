# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test for read_many_items API."""

import unittest
import uuid
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

    def test_read_many_items_edge_cases(self):
        """Tests edge cases for the read_many_items API."""
        # 1. Test with an empty list
        self.assertEqual(self.container.read_many_items(items=[]), [])

        # 2. Test with a mix of existing and non-existing items
        existing_id = "existing_item" + str(uuid.uuid4())
        existing_pk = "pk_value"
        self.container.create_item({'id': existing_id, 'pk': existing_pk})

        items_to_read = [
            (existing_id, existing_pk),
            ("non_existing_item", "pk_value"),
            (existing_id, "wrong_pk")  # Non-existent due to wrong PK
        ]

        read_items = self.container.read_many_items(items=items_to_read)
        self.assertEqual(len(read_items), 1)
        self.assertEqual(read_items[0]['id'], existing_id)

        # 3. Test with only non-existing items
        items_to_read = [("non_existing_item1", "pk1"), ("non_existing_item2", "pk2")]
        read_items = self.container.read_many_items(items=items_to_read)
        self.assertEqual(len(read_items), 0)


if __name__ == '__main__':
    unittest.main()