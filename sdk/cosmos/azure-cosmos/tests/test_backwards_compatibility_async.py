# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError

@pytest.mark.cosmosEmulator
class TestBackwardsCompatibilityAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    client: CosmosClient = None
    created_database: DatabaseProxy = None

    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

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
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_session_token_compatibility_async(self):
        # Verifying that behavior is unaffected across the board for using `session_token` on irrelevant methods
        # Database
        database = await self.client.create_database(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database is not None
        database2 = await self.client.create_database_if_not_exists(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database2 is not None
        database_list = [db async for db in self.client.list_databases(session_token=str(uuid.uuid4()))]
        database_list2 = [db async for db in self.client.query_databases(query="select * from c", session_token=str(uuid.uuid4()))]
        assert len(database_list) > 0
        assert database_list == database_list2
        database_read = await database.read(session_token=str(uuid.uuid4()))
        assert database_read is not None
        await self.client.delete_database(database2.id, session_token=str(uuid.uuid4()))
        try:
            await database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = await database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container is not None
        container2 = await database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container2 is not None
        container_list = [cont async for cont in database.list_containers(session_token=str(uuid.uuid4()))]
        container_list2 = [cont async for cont in database.query_containers(query="select * from c", session_token=str(uuid.uuid4()))]
        assert len(container_list) > 0
        assert container_list == container_list2
        container2_read = await container2.read(session_token=str(uuid.uuid4()))
        assert container2_read is not None
        replace_container = await database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30, session_token=str(uuid.uuid4()))
        replace_container_read = await replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        assert replace_container_read['defaultTtl'] == 30
        await database.delete_container(replace_container.id, session_token=str(uuid.uuid4()))
        try:
            await container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        await self.client.delete_database(database.id)

    async def test_etag_match_condition_compatibility_async(self):
        # Verifying that behavior is unaffected across the board for using `etag`/`match_condition` on irrelevant methods
        # Database
        database = await self.client.create_database(str(uuid.uuid4()), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert database is not None
        database2 = await self.client.create_database_if_not_exists(str(uuid.uuid4()), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert database2 is not None
        await self.client.delete_database(database2.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            await database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = await database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                              etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert container is not None
        container2 = await database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                                             etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert container2 is not None
        container2_read = await container2.read()
        assert container2_read is not None
        replace_container = await database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30,
                                                       etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        replace_container_read = await replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        await database.delete_container(replace_container.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            await container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Item
        item = await container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert item is not None
        item2 = await container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()),
                                     match_condition=MatchConditions.IfNotModified)
        assert item2 is not None
        item = await container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item is not None
        item2 = await container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None,
                                            match_condition=None)
        assert item2 is not None
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 0},)),
            ("replace", (item2['id'], {"id": str(uuid.uuid4()), "pk": 0})),
            ("read", (item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 0},)),
        ]
        batch_results = await container.execute_item_batch(batch_operations, partition_key=0, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert len(batch_results) == 4
        for result in batch_results:
            assert result['statusCode'] in (200, 201)

        await self.client.delete_database(database.id)


if __name__ == '__main__':
    unittest.main()
