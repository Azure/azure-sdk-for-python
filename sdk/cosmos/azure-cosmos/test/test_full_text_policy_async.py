# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy


class TestFullTextPolicyAsync(unittest.IsolatedAsyncioTestCase):
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
        self.test_db = await self.client.create_database(str(uuid.uuid4()))

    async def tearDown(self):
        await self.client.delete_database(self.test_db.id)
        await self.client.close()

    async def test_create_full_text_container_async(self):
        return

    async def test_fail_create_vector_embedding_policy_async(self):
        return

    async def test_fail_create_full_text_indexing_policy_async(self):
        return

    async def test_replace_full_text_policy_async(self):
        return

    async def test_replace_full_text_indexing_policy_async(self):
        return


if __name__ == '__main__':
    unittest.main()
