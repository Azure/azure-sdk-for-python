# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing legacy database-throughput check, re-run on the Rust engine.

Why this file exists: a database can own throughput that all of its containers
share. A customer reads that number with ``get_throughput`` and puts it into
cost and capacity dashboards. If Rust returned a different RU/s here, a
customer would size their database against a wrong figure.

These copies retain the throughput assertions from the original database CRUD
and manual-throughput tests. Owned fixtures and ``_backend="rust"`` isolate
execution; ``get_throughput`` replaces the removed ``read_offer`` alias.
The CRUD copy checks that get-or-create preserves existing 5000 RU/s despite
a later 6000 RU/s creation argument. The manual copy reads 1000 RU/s and
checks a replacement result of 2000 RU/s.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/sync/test_get_database_throughput_parity.py``) run
the same call on both engines and diff the numbers. This file runs on Rust
only and reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The class name and method name match the source, so the
two test IDs differ only by path.

Run with::

    pytest --noconftest tests/get_database_throughput/sync/legacy/test_crud_database.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDDatabaseOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self._created_db_ids = []

    def tearDown(self) -> None:
        try:
            for database_id in self._created_db_ids:
                try:
                    self.key_client.delete_database(database_id)
                except exceptions.CosmosResourceNotFoundError:
                    continue
        finally:
            self.key_client.close()

    def test_database_crud(self):
        """Keep the original CRUD test's shared-throughput assertions."""
        # Source: tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_crud
        database_id = "get_db_crud_" + uuid.uuid4().hex
        self._created_db_ids.append(database_id)
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)

    def test_database_level_offer_throughput(self):
        """Read provisioned throughput and check the replacement result.

        Creates a database at 1000 request units, confirms ``get_throughput``
        reports it, raises it to 2000 and confirms the new figure comes back.

        The replacement result is checked here; a separate response-contract
        copy checks a subsequent read of the persisted value.
        """
        # Source: tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_level_offer_throughput
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        self._created_db_ids.append(database_id)
        created_db = self.key_client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        self.assertEqual(created_db.id, database_id)

        # Verify offer throughput for database
        offer = created_db.get_throughput()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        self.key_client.delete_database(created_db.id)
        self._created_db_ids.remove(database_id)


if __name__ == "__main__":
    unittest.main()
