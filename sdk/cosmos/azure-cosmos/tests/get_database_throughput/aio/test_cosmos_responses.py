# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async replacement-header and persisted-throughput assertions."""

import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey


@pytest.mark.cosmosEmulator
class TestCosmosResponsesAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.database_id = "get_db_response_a_" + uuid.uuid4().hex
        self.addAsyncCleanup(self.client.close)

    async def test_database_replace_throughput_async_rust(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_database_replace_throughput_async
        db = await self.client.create_database(id=self.database_id, offer_throughput=400)
        self.addAsyncCleanup(self.client.delete_database, db.id)
        replace_throughput_value = 500
        first_response = await db.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        new_throughput = await db.get_throughput()
        assert replace_throughput_value == new_throughput.offer_throughput

    async def test_container_replace_throughput_async_rust(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_container_replace_throughput_async
        db = await self.client.create_database(self.database_id)
        self.addAsyncCleanup(self.client.delete_database, db.id)
        container = await db.create_container(
            id="responses_test", partition_key=PartitionKey(path="/company"), offer_throughput=400,
        )
        replace_throughput_value = 500
        first_response = await container.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        new_throughput = await container.get_throughput()
        assert replace_throughput_value == new_throughput.offer_throughput
