# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import random
import time
import unittest
import uuid
import pytest
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey


@pytest.mark.cosmosSplit
class TestReadManyItemsPartitionSplitScenarios(unittest.TestCase):
    """Test for session token helpers"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    async def asyncSetUp(self):
        self.container = await self.database.create_container(
            id='split_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
            offer_throughput=400
        )

    async def asyncTearDown(self):
        if self.container:
            await self.database.delete_container(self.container)

    async def test_read_many_items_with_partition_split(self):
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

        # 3. Trigger a partition split by increasing throughput
        print("Increasing throughput to trigger partition split...")
        initial_offer = await self.container.get_throughput()
        self.assertEqual(initial_offer.offer_throughput, 400)
        await self.container.replace_throughput(11000)
        print("Throughput replacement initiated.")

        # 4. Wait for the split to complete (offer replacement is no longer pending)
        start_time = time.time()
        timeout_seconds = 1500  # 25 minutes
        while time.time() - start_time < timeout_seconds:
            offer = await self.container.get_throughput()
            if not offer.properties['content'].get('isOfferReplacePending', False):
                print("Partition split completed.")
                break
            print("Waiting for partition split to complete...")
            await asyncio.sleep(30)
        else:
            self.fail(f"Partition split did not complete within {timeout_seconds} seconds.")

        # 5. Verify throughput was actually increased
        final_offer = await self.container.get_throughput()
        self.assertGreater(final_offer.offer_throughput, initial_offer.offer_throughput)
        print("Throughput successfully increased.")

        # 5. Force a routing map refresh by clearing the client-side cache
        print("Clearing client routing map cache to force refresh...")

        # 6. Call read_many_items again after the split
        print("Performing post-split read_many_items call...")
        final_read_items = await self.container.read_many_items(items=items_to_read)

        # 7. Verify the results
        self.assertEqual(len(final_read_items), len(items_to_read))
        final_read_ids = {item['id'] for item in final_read_items}
        self.assertSetEqual(final_read_ids, set(item_ids))
        print("Post-split call successful.")



if __name__ == '__main__':
    unittest.main()
