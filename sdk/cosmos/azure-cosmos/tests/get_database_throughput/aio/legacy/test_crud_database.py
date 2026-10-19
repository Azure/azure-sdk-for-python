# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing legacy async database-throughput check, re-run on the Rust engine.

Why this file exists: the async client is a separate code path from the sync
client all the way down -- separate proxy classes, separate helper module,
separate backend object. A throughput read that works on the sync path proves
nothing about the async path. Customers running async apps read a database's
shared RU/s the same way, and Rust must report the same number there.

These copies retain the throughput assertions from the original async database
CRUD and manual-throughput tests, with owned fixtures and ``_backend="rust"``.
The CRUD copy checks that get-or-create preserves existing 5000 RU/s despite
a later 6000 RU/s creation argument. The manual copy reads 1000 RU/s and
checks a replacement result of 2000 RU/s.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/aio/test_get_database_throughput_parity_async.py``)
run the same call on both engines and diff the numbers. This file runs on Rust
only.

Self-contained: it creates and deletes its own database. The class name and
method name match the source (apart from the method's ``_rust`` suffix); the file name
drops the ``_async`` suffix, which
is the naming the audit reporter expects for an aio legacy copy.

Run with::

    pytest --noconftest tests/get_database_throughput/aio/legacy/test_crud_database.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions


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
        try:
            for database_id in self._created_db_ids:
                try:
                    await self.key_client.delete_database(database_id)
                except exceptions.CosmosResourceNotFoundError:
                    continue
        finally:
            await self.key_client.close()

    async def test_database_crud_async_rust(self):
        """Keep the original CRUD test's shared-throughput assertions."""
        # Source: tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_database_crud_async
        database_id = "get_db_crud_a_" + uuid.uuid4().hex
        self._created_db_ids.append(database_id)
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput
        database_proxy = await self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        assert database_id == database_proxy.id
        db_throughput = await database_proxy.get_throughput()
        assert 5000 == db_throughput.offer_throughput

    async def test_database_level_offer_throughput_async_rust(self):
        """Read provisioned throughput and check the replacement result.

        Creates a database at 1000 request units, confirms ``get_throughput``
        reports it, raises it to 2000 and confirms the new figure comes back.

        The replacement result is checked here; a separate response-contract
        copy checks a subsequent read of the persisted value.
        """
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
