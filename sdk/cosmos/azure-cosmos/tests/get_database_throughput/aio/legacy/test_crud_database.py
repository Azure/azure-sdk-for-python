# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async database-throughput check, re-run on the rust engine.

Why this file exists: the async client is a separate code path from the sync
client all the way down -- separate proxy classes, separate helper module,
separate backend object. A throughput read that works on the sync path proves
nothing about the async path. Customers running async apps read a database's
shared RU/s the same way, and rust must report the same number there.

Note the async surface has no ``read_offer``: the older alias exists only on
the sync ``DatabaseProxy``, so this test calls ``get_throughput`` directly.

What it does: the real v4 test copied from
``tests/test_crud_database_async.py``, changed in one place -- the client is
built with ``_backend="rust"``. It creates a database with 1000 RU/s, reads it
back and checks it says 1000, replaces it with 2000, and checks the replace
result says 2000.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/aio/test_get_database_throughput_parity_async.py``)
run the same call on both engines and diff the numbers. This file runs on rust
only.

Self-contained: it creates and deletes its own database. The class name and
method name match the source; the file name drops the ``_async`` suffix, which
is the naming the audit reporter expects for an aio legacy copy.

Run with::

    pytest --noconftest tests/get_database_throughput/aio/legacy/test_crud_database.py -v
"""
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


@pytest.mark.cosmosEmulator
class TestCRUDDatabaseOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self._created_db_ids = []

    async def asyncTearDown(self) -> None:
        for database_id in self._created_db_ids:
            try:
                await self.key_client.delete_database(database_id)
            except Exception:  # pylint: disable=broad-except
                pass
        await self.key_client.close()

    async def test_database_level_offer_throughput_async(self):
        # Source: tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_database_level_offer_throughput_async
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        self._created_db_ids.append(database_id)
        created_db = await self.key_client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        assert created_db.id == database_id

        # Verify offer throughput for database
        offer = await created_db.get_throughput()
        assert offer.offer_throughput == offer_throughput

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = await created_db.replace_throughput(new_offer_throughput)
        assert offer.offer_throughput == new_offer_throughput

        await self.key_client.delete_database(database_id)
        self._created_db_ids.remove(database_id)


if __name__ == "__main__":
    unittest.main()
