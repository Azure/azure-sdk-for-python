# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import time
import unittest
import uuid
import pytest
from azure.cosmos import DatabaseProxy, PartitionKey
import test_config
import azure.cosmos.cosmos_client as cosmos_client


@pytest.mark.cosmosSplit
class TestReadItemsPartitionSplitScenariosSync(unittest.TestCase):
    """Tests the behavior of read_items in scenarios involving partition splits (sync)."""

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

    def test_read_items_with_partition_split(self):
        """Tests that read_items works correctly after a partition split."""
        container = self.database.create_container("read_items_split_test_" + str(uuid.uuid4()),
                                                   PartitionKey(path="/pk"),
                                                   offer_throughput=400)
        # 1. Create 5 items to read
        items_to_read = []
        item_ids = []
        for i in range(5):
            doc_id = f"item_split_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            # Add the partition key field 'pk' to the item body
            container.create_item({'id': doc_id, 'pk': doc_id, 'data': i})
            items_to_read.append((doc_id, doc_id))

        # 2. Initial read_items call before the split
        print("Performing initial read_items call...")
        initial_read_items = container.read_items(items=items_to_read)
        self.assertEqual(len(initial_read_items), len(items_to_read))
        print("Initial call successful.")

        # 3. Trigger a partition split
        test_config.TestConfig.trigger_split(container, 11000)

        # 4. Call read_items again after the split
        print("Performing post-split read_items call...")
        final_read_items = container.read_items(items=items_to_read)

        # 5. Verify the results
        self.assertEqual(len(final_read_items), len(items_to_read))
        final_read_ids = {item['id'] for item in final_read_items}
        self.assertSetEqual(final_read_ids, set(item_ids))
        print("Post-split call successful.")
        self.database.delete_container(container.id)

if __name__ == '__main__':
    unittest.main()