# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async autoscale-change check, re-run on the rust engine.

Why this file exists: it covers the one combination the other three files in
this operation leave out -- changing an autoscale setting on the async client.
An autoscale change rewrites a ceiling and a growth step that sit in a nested
part of the offer document, and the async client builds and sends that document
through its own code path. Neither the sync autoscale test nor the async
fixed-number test would catch rust dropping the new ceiling here.

What it does: the real v4 test copied from
``tests/test_auto_scale_async.py``, changed in one place -- the client is built
with ``_backend="rust"``. It creates a database with a 5000 ceiling and 0%
step, changes it to a 7000 ceiling and 20% step, reads it back and checks both
new values. It then does the same change on a container, which is the
neighbouring operation that shares the offer document format.

This is NOT the side-by-side comparison. The comparison tests
(``replace_database_throughput/aio/test_replace_database_throughput_parity_async.py``)
run the same change on both engines and diff the results. This file runs on
rust only.

Self-contained: it creates and deletes its own database and container.

Run with::

    pytest --noconftest tests/replace_database_throughput/aio/legacy/test_auto_scale.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, ThroughputProperties
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
        self._host_db_id = "legacy_replace_db_tp_a_" + uuid.uuid4().hex[:8]
        self.created_database = await self.key_client.create_database(self._host_db_id)

    async def asyncTearDown(self) -> None:
        try:
            await self.key_client.delete_database(self._host_db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.key_client.close()

    async def test_replace_throughput_async(self):
        # Source: tests/test_auto_scale_async.py::TestAutoScaleAsync.test_replace_throughput_async
        database_id = "replace_db" + str(uuid.uuid4())
        container_id = None
        try:
            created_database = await self.key_client.create_database(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=5000,
                    auto_scale_increment_percent=0))
            await created_database.replace_throughput(
                throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20))
            created_db_properties = await created_database.get_throughput()
            # Testing the replaced value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 7000
            # Testing the replaced value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 20
            await self.key_client.delete_database(database_id)

            container_id = "container_with_auto_scale_settings" + str(uuid.uuid4())
            created_container = await self.created_database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0))
            await created_container.replace_throughput(
                throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20))
            created_container_properties = await created_container.get_throughput()
            # Testing the input value of the replaced auto_scale settings
            assert created_container_properties.auto_scale_max_throughput == 7000
            assert created_container_properties.auto_scale_increment_percent == 20
        finally:
            await self.created_database.delete_container(container_id)


if __name__ == "__main__":
    unittest.main()
