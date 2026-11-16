# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-backend copy of the legacy computed-properties query test.

Source: tests/test_computed_properties.py. The original method, its query
helpers, markers, queries and assertions are unchanged; only the setup differs.
Instead of the shared ``test_config`` database the class owns a fresh database
created through a key-auth client pinned to ``_backend="rust"``, so container
creation, item writes and every ``query_items`` call run on the Rust driver.
The owned database is deleted in class cleanup.
"""

import os
import time
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import DatabaseProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADLong
class TestComputedPropertiesQuery(unittest.TestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None

    @classmethod
    def setUpClass(cls):
        cls.client = cls.key_client = cosmos_client.CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls.database_id = "query_items_computed_properties_" + uuid.uuid4().hex
        cls.key_db = cls.created_db = cls.client.create_database(cls.database_id)
        cls.addClassCleanup(cls._delete_owned_database)
        cls.items = [
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
        cls.computed_properties = [{'name': "cp_lower", 'query': "SELECT VALUE LOWER(c.db_group) FROM c"},
                                   {'name': "cp_power", 'query': "SELECT VALUE POWER(c.val, 2) FROM c"},
                                   {'name': "cp_str_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]

    @classmethod
    def _delete_owned_database(cls):
        try:
            cls.client.delete_database(cls.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    def computedPropertiesTestCases(self, created_collection):
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_computed_properties.py::TestComputedPropertiesQuery.computedPropertiesTestCases
        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        # Test 0: Negative test, test if using non-existent computed property
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_upper = "GROUP2"',
                                           partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 1: Test first computed property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=5)

        # Test 1 Negative: Test if using non-existent string in group property returns nothing
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_lower = "group4"', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 2: Test second computed property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_power = 25',
            partition_key="test",
            expected_count=7)

        # Test 2 Negative: Test Non-Existent POWER
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_power = 16', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

        # Test 3: Test Third Computed Property
        self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=2)

    def _assert_query_count_eventually(self, container_client, query, partition_key, expected_count):
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_computed_properties.py::TestComputedPropertiesQuery._assert_query_count_eventually
        # Container replace can take a few seconds before computed-property queries become visible.
        last_count = -1
        for _ in range(8):
            queried_items = list(container_client.query_items(query=query, partition_key=partition_key))
            last_count = len(queried_items)
            if last_count == expected_count:
                return
            time.sleep(1)
        self.assertEqual(last_count, expected_count)

        # Test 3 Negative: Test Str length that isn't there
        queried_items = list(
            created_collection.query_items(query='Select * from c Where c.cp_str_len = 3', partition_key="test"))
        self.assertEqual(len(queried_items), 0)

    def test_computed_properties_query_rust(self):
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_computed_properties_query

        created_collection_ref = self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        self.computedPropertiesTestCases(created_collection)
        self.key_db.delete_container(created_collection.id)


    def test_replace_with_same_computed_properties_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_same_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)
        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties= self.computed_properties)
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        self.computedPropertiesTestCases(replaced_collection)
        self.key_db.delete_container(replaced_collection.id)

    def test_replace_without_computed_properties_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_without_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        # Replace Container
        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties= self.computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)
        self.computedPropertiesTestCases(replaced_collection)
        self.key_db.delete_container(replaced_collection.id)

    def test_replace_with_new_computed_properties_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties.py::TestComputedPropertiesQuery.test_replace_with_new_computed_properties
        created_collection_ref = self.key_db.create_container(
            id="computed_properties_query_test_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            created_collection.create_item(body=item)

        # Check that computed properties were properly sent
        self.assertListEqual(self.computed_properties, created_collection.read()["computedProperties"])

        new_computed_properties = [{'name': "cp_upper", 'query': "SELECT VALUE UPPER(c.db_group) FROM c"},
                                   {'name': "cp_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]
        # Replace Container
        replaced_collection_ref = self.key_db.replace_container(
            container=created_collection.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties=new_computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)
        # Check that computed properties were properly sent to replaced container
        self.assertListEqual(new_computed_properties, replaced_collection.read()["computedProperties"])

        # Test 1: Test first computed property
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_upper = "GROUP2"',
            partition_key="test",
            expected_count=3)

        # Test 1 Negative: Test if using non-existent computed property name returns nothing
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=0)

        # Test 2: Test Second Computed Property
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_len = 9',
            partition_key="test",
            expected_count=2)

        # Test 2 Negative: Test Str length using old computed properties name
        self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=0)
        self.key_db.delete_container(created_collection.id)

if __name__ == '__main__':
    unittest.main()
