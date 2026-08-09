# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 database-throughput change, re-run on the rust engine.

Why this file exists: changing a database's shared RU/s is not a single write.
The SDK first queries for the database's offer, edits the RU/s number on the
document it got back, and sends the whole document back. If rust queried for
the wrong offer, or sent back a document missing a field the service requires,
the change would fail or land on the wrong database -- and a customer's bill
follows that number. The same call is also what the deprecated ``read_offer``
name reads back, so this test covers both halves of the read-modify-write.

What it does: the real v4 test copied from ``tests/test_crud_database.py``,
changed in one place -- the client is built with ``_backend="rust"``. It
creates a database at 1000 RU/s, reads it back, changes it to 2000, and checks
the returned object reports 2000.

This is NOT the side-by-side comparison. The comparison tests
(``replace_database_throughput/sync/test_replace_database_throughput_parity.py``)
run the same change on both engines and diff the results. This file runs on
rust only.

Self-contained: it creates and deletes its own database.

Run with::

    pytest --noconftest tests/replace_database_throughput/sync/legacy/test_crud_database.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient


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
        for database_id in self._created_db_ids:
            try:
                self.key_client.delete_database(database_id)
            except Exception:  # pylint: disable=broad-except
                pass
        self.key_client.close()

    def test_database_level_offer_throughput(self):
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
        offer = created_db.read_offer()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        self.key_client.delete_database(created_db.id)
        self._created_db_ids.remove(database_id)


if __name__ == "__main__":
    unittest.main()
