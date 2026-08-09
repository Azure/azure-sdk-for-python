# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async autoscale-database check, re-run on the rust engine.

Why this file exists: it covers the one combination the other three legacy
files leave out -- reading an autoscale setting (a ceiling plus a growth step,
rather than a fixed RU/s number) on the async client. Autoscale values come
back in different fields from a fixed number, and the async client is a
separate code path from the sync one, so neither the sync autoscale test nor
the async fixed-number test covers this case.

What it does: the real v4 test copied from ``tests/test_auto_scale_async.py``,
changed in one place -- the client is built with ``_backend="rust"``. It
creates a database with a 5000 RU/s ceiling and a 0% step, reads the setting
back and checks both values, then does the same through
``create_database_if_not_exists`` with a 9000 ceiling and an 11% step.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/aio/test_get_database_throughput_parity_async.py``)
run the same call on both engines and diff the numbers. This file runs on rust
only.

Self-contained: it creates and deletes its own databases.

Run with::

    pytest --noconftest tests/get_database_throughput/aio/legacy/test_auto_scale.py -v
"""
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


@pytest.mark.cosmosEmulator
class TestAutoScaleAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")

    async def asyncTearDown(self) -> None:
        await self.key_client.close()

    async def test_autoscale_create_database_async(self):
        # Source: tests/test_auto_scale_async.py::TestAutoScaleAsync.test_autoscale_create_database_async
        database_id = None
        try:
            # Testing auto_scale_settings for the create_database method
            database_id = "db1_" + str(uuid.uuid4())
            created_database = await self.key_client.create_database(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=5000,
                    auto_scale_increment_percent=0))
            created_db_properties = await created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 5000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 0

            await self.key_client.delete_database(created_database.id)

            # Testing auto_scale_settings for the create_database_if_not_exists method
            database_id = "db2_" + str(uuid.uuid4())
            created_database = await self.key_client.create_database_if_not_exists(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=9000,
                    auto_scale_increment_percent=11))
            created_db_properties = await created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 9000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 11
        finally:
            await self.key_client.delete_database(database_id)


if __name__ == "__main__":
    unittest.main()
