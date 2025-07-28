# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import time
import unittest
import uuid
import pytest
from azure.cosmos.aio import CosmosClient, DatabaseProxy
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError

@pytest.mark.cosmosSplit
class TestReadManyItemsPartitionSplitScenarios(unittest.IsolatedAsyncioTestCase):
    """Tests the behavior of read_many_items in scenarios involving partition splits."""

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
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = await self.database.create_container(
            id='read_many_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )

    async def asyncTearDown(self):
        """Clean up async resources after each test."""
        if self.container:
            try:
                await self.database.delete_container(self.container)
            except CosmosHttpResponseError as e:
                # Container may have been deleted by the test itself
                if e.status_code != 404:
                    raise
        if self.client:
            await self.client.close()

    async def test_read_many_items_with_partition_split_async(self):
        """Tests that read_many_items works correctly after a partition split."""
        # 1. Create 100 items to read
        items_to_read = []
        item_ids = []
        for i in range(5):
            doc_id = f"item_split_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            await self.container.create_item({'id': doc_id, 'data': i})
            items_to_read.append((doc_id, doc_id))

        # 2. Initial read_many_items call before the split
        print("Performing initial read_many_items call...")
        initial_read_items = await self.container.read_many_items(items=items_to_read)
        self.assertEqual(len(initial_read_items), len(items_to_read))
        print("Initial call successful.")

        # 3. Trigger a partition split
        await test_config.TestConfig.trigger_split_async(self.container, 11000)

        # 4. Call read_many_items again after the split
        print("Performing post-split read_many_items call...")
        final_read_items = await self.container.read_many_items(items=items_to_read)

        # 5. Verify the results
        self.assertEqual(len(final_read_items), len(items_to_read))
        final_read_ids = {item['id'] for item in final_read_items}
        self.assertSetEqual(final_read_ids, set(item_ids))
        print("Post-split call successful.")


if __name__ == '__main__':
    unittest.main()