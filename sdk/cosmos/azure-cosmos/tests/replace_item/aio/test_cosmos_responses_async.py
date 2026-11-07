# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async point-operation header test that replaces an item, re-run on the Rust path.

Source: ``tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync``. The
method keeps the original steps and assertions; only setup changed. Both
clients use ``_backend="rust"``: a key-authenticated setup client owns a
uniquely named database (deleted afterwards) and a data client runs the item
operations, like the original key/data client pair.
"""

import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from config import clients
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestCosmosResponsesAsync(unittest.IsolatedAsyncioTestCase):
    """Python Cosmos Responses Tests.
    """

    async def asyncSetUp(self):
        self.TEST_DATABASE_ID = unique_database_id("replace_item_responses_async")
        self.client = CosmosClient(TestSettings.host, TestSettings.masterKey, _backend="rust")
        await self.client.__aenter__()
        self.data_client = None
        self.test_database = None
        try:
            self.test_database = await self.client.create_database(self.TEST_DATABASE_ID)
            self.data_client = clients.create_data_client_async(_backend="rust")
            await self.data_client.__aenter__()
            self.data_test_database = self.data_client.get_database_client(self.TEST_DATABASE_ID)
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            if self.test_database is not None:
                await self.client.delete_database(self.TEST_DATABASE_ID)
        finally:
            try:
                if self.data_client is not None:
                    await self.data_client.close()
            finally:
                await self.client.close()

    async def test_point_operation_headers_async_rust(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_point_operation_headers_async
        # Container create stays on key-auth (control-plane); data ops route through AAD.
        container_id = "responses_test" + str(uuid.uuid4())
        await self.test_database.create_container(id=container_id,
                                                  partition_key=PartitionKey(path="/company"))
        container = self.data_test_database.get_container_client(container_id)
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
