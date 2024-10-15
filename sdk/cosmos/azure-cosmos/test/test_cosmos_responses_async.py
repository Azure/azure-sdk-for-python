# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import HttpHeaders


# TODO: add more tests in this file once we have response headers in control plane operations
# TODO: add query tests once those changes are available

@pytest.mark.cosmosEmulator
class TestCosmosResponsesAsync(unittest.IsolatedAsyncioTestCase):
    """Python Cosmos Responses Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

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
        self.test_database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_point_operation_headers_async(self):
        container = await self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                              partition_key=PartitionKey(path="/company"))
        first_response = await container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        lsn = first_response.get_response_headers()['lsn']

        create_response = await container.create_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(create_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(create_response.get_response_headers()['lsn'])
        lsn = create_response.get_response_headers()['lsn']

        read_response = await container.read_item(create_response['id'], create_response['company'])
        assert len(read_response.get_response_headers()) > 0

        upsert_response = await container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(upsert_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(upsert_response.get_response_headers()['lsn'])
        lsn = upsert_response.get_response_headers()['lsn']

        upsert_response['replace'] = True
        replace_response = await container.replace_item(upsert_response['id'], upsert_response)
        assert replace_response['replace'] is not None
        assert len(replace_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(replace_response.get_response_headers()['lsn'])

        batch = []
        for i in range(50):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))
        batch_response = await container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response.get_response_headers()) > 0
        assert int(lsn) + 1 < int(batch_response.get_response_headers()['lsn'])


if __name__ == '__main__':
    unittest.main()
