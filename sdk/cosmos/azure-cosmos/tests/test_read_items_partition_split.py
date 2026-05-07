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
@pytest.mark.cosmosAAD
class TestReadItemsPartitionSplitScenariosSync(unittest.TestCase):
    """Tests the behavior of read_items in scenarios involving partition splits (sync)."""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None  # AAD  -  data-plane (create_item / read_items)
    key_client: cosmos_client.CosmosClient = None  # key-auth  -  control-plane (create/delete container, trigger_split)
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        # Control-plane: key-auth (container lifecycle + replace_throughput inside trigger_split)
        cls.key_client, cls.key_database, cls.client, cls.database = (
            test_config.TestConfig.create_test_clients(cls.TEST_DATABASE_ID))

    def test_read_items_with_partition_split(self):
        """Tests that read_items works correctly after a partition split."""
        container_id = "read_items_split_test_" + str(uuid.uuid4())
        # Control-plane: create via key-auth setup database
        key_container = self.key_database.create_container(
            container_id,
            PartitionKey(path="/pk"),
            offer_throughput=400)
        # Data-plane: re-bind the container to the AAD client for create_item / read_items
        container = self.database.get_container_client(container_id)
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

        # 3. Trigger a partition split (control-plane: replace_throughput / get_throughput)
        test_config.TestConfig.trigger_split(key_container, 11000)

        # 4. Call read_items again after the split
        print("Performing post-split read_items call...")
        final_read_items = container.read_items(items=items_to_read)

        # 5. Verify the results
        self.assertEqual(len(final_read_items), len(items_to_read))
        final_read_ids = {item['id'] for item in final_read_items}
        self.assertSetEqual(final_read_ids, set(item_ids))
        print("Post-split call successful.")
        # Control-plane: delete via key-auth setup database
        self.key_database.delete_container(container_id)

if __name__ == '__main__':
    unittest.main()