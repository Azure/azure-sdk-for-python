# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected async database throughput test pinned to the Rust backend."""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosLong
class TestCRUDDatabaseOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")

    async def asyncTearDown(self):
        await self.key_client.close()

    async def test_database_level_offer_throughput_async(self):
        # Source: tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = await self.key_client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        assert created_db.id == database_id

        offer = await created_db.get_throughput()
        assert offer.offer_throughput == offer_throughput

        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        assert offer.offer_throughput == new_offer_throughput

        await self.key_client.delete_database(database_id)
