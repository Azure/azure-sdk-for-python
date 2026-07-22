# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected async autoscale database test pinned to the Rust backend."""
import os
import unittest
import uuid

import pytest

from azure.cosmos import ThroughputProperties
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosLong
class TestAutoScaleAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")

    async def asyncTearDown(self):
        await self.key_client.close()

    async def test_autoscale_create_database_async(self):
        # Source: tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_database_async
        database_id = None
        try:
            database_id = "db1_" + str(uuid.uuid4())
            created_database = await self.key_client.create_database(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=5000,
                    auto_scale_increment_percent=0,
                ),
            )
            created_db_properties = await created_database.get_throughput()
            assert created_db_properties.auto_scale_max_throughput == 5000
            assert created_db_properties.auto_scale_increment_percent == 0

            await self.key_client.delete_database(created_database.id)

            database_id = "db2_" + str(uuid.uuid4())
            created_database = await self.key_client.create_database_if_not_exists(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=9000,
                    auto_scale_increment_percent=11,
                ),
            )
            created_db_properties = await created_database.get_throughput()
            assert created_db_properties.auto_scale_max_throughput == 9000
            assert created_db_properties.auto_scale_increment_percent == 11
        finally:
            await self.key_client.delete_database(database_id)
