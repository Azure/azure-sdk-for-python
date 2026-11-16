# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-backend copy of the legacy async computed-properties query test.

Source: tests/test_computed_properties_async.py. The original method, its query
helpers, markers, queries and assertions are unchanged; only the setup differs.
Instead of the shared ``test_config`` database each test owns a fresh database
created through an async key-auth client pinned to ``_backend="rust"``, so
container creation, item writes and every ``query_items`` call run on the Rust
driver. The owned database is deleted in async cleanup.
"""

import asyncio
import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADLong
class TestComputedPropertiesQueryAsync(unittest.IsolatedAsyncioTestCase):
    """Test to ensure escaping of non-ascii characters from partition key"""

    created_db: DatabaseProxy = None
    key_db: DatabaseProxy = None
    created_container: ContainerProxy = None
    client: CosmosClient = None
    key_client: CosmosClient = None

    async def asyncSetUp(self):
        self.client = self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self.database_id = "query_items_computed_properties_async_" + uuid.uuid4().hex
        self.key_db = self.created_db = await self.client.create_database(self.database_id)
        self.addAsyncCleanup(self._delete_owned_database)
        self.items = [
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
        self.computed_properties = [{'name': "cp_lower", 'query': "SELECT VALUE LOWER(c.db_group) FROM c"},
                                   {'name': "cp_power", 'query': "SELECT VALUE POWER(c.val, 2) FROM c"},
                                   {'name': "cp_str_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]

    async def _delete_owned_database(self):
        try:
            await self.client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    async def computedPropertiesTestCases(self, created_collection):
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync.computedPropertiesTestCases
        # Check if computed properties were set
        container = await created_collection.read()
        assert self.computed_properties == container["computedProperties"]

        # Test 0: Negative test, test if using non-existent computed property
        queried_items = [q async for q in
                         created_collection.query_items(query='Select * from c Where c.cp_upper = "GROUP2"',
                                                        partition_key="test")]
        assert len(queried_items) == 0

        # Test 1: Test first computed property
        await self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=5)

        # Test 1 Negative: Test if using non-existent string in group property returns nothing
        queried_items = [q async for q in
                         created_collection.query_items(query='Select * from c Where c.cp_lower = "group4"',
                                                        partition_key="test")]
        assert len(queried_items) == 0

        # Test 2: Test second computed property
        await self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_power = 25',
            partition_key="test",
            expected_count=7)

        # Test 2 Negative: Test Non-Existent POWER
        queried_items = [q async for q in created_collection.query_items(query='Select * from c Where c.cp_power = 16',
                                                                         partition_key="test")]
        assert len(queried_items) == 0

        # Test 3: Test Third Computed Property
        await self._assert_query_count_eventually(
            created_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=2)

    async def _assert_query_count_eventually(self, container_client, query, partition_key, expected_count):
        # pylint: disable-next=line-too-long
        # Source helper: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync._assert_query_count_eventually
        # Container replace can take a few seconds before computed-property queries become visible.
        last_count = -1
        for _ in range(8):
            queried_items = [q async for q in container_client.query_items(query=query, partition_key=partition_key)]
            last_count = len(queried_items)
            if last_count == expected_count:
                return
            await asyncio.sleep(1)
        self.assertEqual(last_count, expected_count)

        # Test 3 Negative: Test Str length that isn't there
        queried_items = [q async for q in created_collection.query_items(query='Select * from c Where c.cp_str_len = 3',
                                                                         partition_key="test")]
        assert len(queried_items) == 0

    async def test_computed_properties_query_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync.test_computed_properties_query_async
        # create_container is control-plane and uses key_db (key-auth).
        created_collection_ref = await self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            await created_collection.create_item(body=item)

        await self.computedPropertiesTestCases(created_collection)
        await self.key_db.delete_container(created_collection_ref.id)


    async def test_replace_with_same_computed_properties_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync.test_replace_with_same_computed_properties_async
        # create_container/replace_container are control-plane and use key_db (key-auth).
        created_collection_ref = await self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            await created_collection.create_item(body=item)

        # Replace Container
        replaced_collection_ref = await self.key_db.replace_container(
            container=created_collection_ref.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        await self.computedPropertiesTestCases(replaced_collection)
        await self.key_db.delete_container(created_collection_ref.id)

    async def test_replace_without_computed_properties_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync.test_replace_without_computed_properties_async
        # create_container/replace_container are control-plane and use key_db (key-auth).
        created_collection_ref = await self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            await created_collection.create_item(body=item)

        # Replace Container
        replaced_collection_ref = await self.key_db.replace_container(
            container=created_collection_ref.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties=self.computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        await self.computedPropertiesTestCases(replaced_collection)
        await self.key_db.delete_container(created_collection_ref.id)

    async def test_replace_with_new_computed_properties_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_computed_properties_async.py::TestComputedPropertiesQueryAsync.test_replace_with_new_computed_properties_async
        # create_container/replace_container are control-plane and use key_db (key-auth).
        created_collection_ref = await self.key_db.create_container(
            "computed_properties_query_test_" + str(uuid.uuid4()),
            PartitionKey(path="/pk"),
            computed_properties=self.computed_properties)
        created_collection = self.created_db.get_container_client(created_collection_ref.id)

        # Create Items
        for item in self.items:
            await created_collection.create_item(body=item)

        # Check if computed properties were set
        container = await created_collection.read()
        assert self.computed_properties == container["computedProperties"]

        new_computed_properties = [{'name': "cp_upper", 'query': "SELECT VALUE UPPER(c.db_group) FROM c"},
                                   {'name': "cp_len", 'query': "SELECT VALUE LENGTH(c.stringProperty) FROM c"}]

        # Replace Container
        replaced_collection_ref = await self.key_db.replace_container(
            container=created_collection_ref.id,
            partition_key=PartitionKey(path="/pk"),
            computed_properties=new_computed_properties
        )
        replaced_collection = self.created_db.get_container_client(replaced_collection_ref.id)

        # Check if computed properties were set
        container = await replaced_collection.read()
        assert new_computed_properties == container["computedProperties"]

        # Diagnostic: query all items and their computed property values to understand indexing state
        all_items = [q async for q in
                     replaced_collection.query_items(
                         query='SELECT c.id, c.db_group, c.cp_upper FROM c',
                         partition_key="test")]
        print(f"\n[DIAG] Total items after replace: {len(all_items)}")
        for diag_item in all_items[:3]:
            print(f"[DIAG] Item id={diag_item.get('id', '?')}, "
                  f"db_group={diag_item.get('db_group', '?')}, "
                  f"cp_upper={diag_item.get('cp_upper', 'MISSING')}")

        # Polling: retry the cp_upper query with delays to detect emulator reindexing lag
        queried_items = []
        for attempt in range(10):
            queried_items = [q async for q in
                             replaced_collection.query_items(
                                 query='Select * from c Where c.cp_upper = "GROUP2"',
                                 partition_key="test")]
            if len(queried_items) == 3:
                print(f"[DIAG] cp_upper query succeeded on attempt {attempt + 1}")
                break
            print(f"[DIAG] cp_upper query attempt {attempt + 1}: got {len(queried_items)}, expected 3")
            await asyncio.sleep(1)

        # Test 1: Test first computed property
        await self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_upper = "GROUP2"',
            partition_key="test",
            expected_count=3)

        # Test 1 Negative: Test if using non-existent computed property name returns nothing
        await self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_lower = "group1"',
            partition_key="test",
            expected_count=0)

        # Test 2: Test Second Computed Property
        await self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_len = 9',
            partition_key="test",
            expected_count=2)

        # Test 2 Negative: Test Str length using old computed properties name
        await self._assert_query_count_eventually(
            replaced_collection,
            query='Select * from c Where c.cp_str_len = 9',
            partition_key="test",
            expected_count=0)
        await self.key_db.delete_container(created_collection_ref.id)

if __name__ == '__main__':
    unittest.main()
