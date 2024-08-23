# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


class TestComputedPropertiesQuery(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    config = test_config.TestConfig
    host = config.host
    masterKey = config.masterKey
    connectionPolicy = config.connectionPolicy
    TEST_DATABASE_ID = config.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def test_computed_properties_query(self):
        computed_properties = [{'name': "cp_lower", 'query': "SELECT VALUE LOWER(c.db_group) FROM c"},
                               {'name': "cp_power",
                                'query': "SELECT VALUE POWER(c.val, 2) FROM c"},
                               {'name': "cp_str_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]
        items = [
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'prefixOne', 'db_group': 'GroUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'prefixTwo', 'db_group': 'GrOUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord1', 'db_group': 'GroUp2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord2', 'db_group': 'groUp1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord3', 'db_group': 'GroUp3'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord4', 'db_group': 'GrOUP1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 5, 'stringProperty': 'randomWord5', 'db_group': 'GroUp2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 0, 'stringProperty': 'randomWord6', 'db_group': 'group1'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 3, 'stringProperty': 'randomWord7', 'db_group': 'group2'},
            {'id': str(uuid.uuid4()), 'pk': 'test', 'val': 2, 'stringProperty': 'randomWord8', 'db_group': 'GroUp3'}
        ]
        created_collection = self.created_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()), PartitionKey(path="/pk")
            , computed_properties=computed_properties)

        # Create Items
        for item in items:
            created_collection.create_item(body=item)
        # Check that computed properties were properly sent
        self.assertListEqual(computed_properties, created_collection.read()["computedProperties"])

        # Test 0: Negative test, test if using non-existent computed property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_upper = "GROUP2"',
                                           partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 1: Test first computed property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_lower = "group1"', partition_key="test"))
        self.assertEqual(len(queried_items), 5)

        # Test 1 Negative: Test if using non-existent string in group property returns nothing
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_lower = "group4"', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 2: Test second computed property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_power = 25', partition_key="test"))
        self.assertEqual(len(queried_items), 7)

        # Test 2 Negative: Test Non-Existent POWER
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_power = 16', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 3: Test Third Computed Property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_str_len = 9', partition_key="test"))
        self.assertEqual(len(queried_items), 2)

        # Test 3 Negative: Test Str length that isn't there
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_str_len = 3', partition_key="test"))
        self.assertEqual(len(queried_items), 0)
        self.created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
