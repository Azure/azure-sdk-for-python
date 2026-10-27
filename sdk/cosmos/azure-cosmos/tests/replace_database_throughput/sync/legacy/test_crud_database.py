# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing legacy database-throughput change, re-run on the Rust engine.

Why this file exists: changing a database's shared RU/s is not a single write.
The SDK first queries for the database's offer, edits the RU/s number on the
document it got back, and sends the whole document back. If Rust queried for
the wrong offer, or sent back a document missing a field the service requires,
the change would fail or land on the wrong database -- and a customer's bill
follows that number. This test reads the original configuration with
``get_throughput`` before replacing it.

What it does: the real legacy test copied from ``tests/test_crud_database.py``,
adapted to build the client with ``_backend="rust"`` and call
``get_throughput`` instead of the removed ``read_offer`` alias. It
creates a database at 1000 RU/s, reads it back, changes it to 2000, and checks
the returned object reports 2000.

This is NOT the side-by-side comparison. The comparison tests
(``replace_database_throughput/sync/test_replace_database_throughput_parity.py``)
run the same change on both engines and diff the results. This file runs on
Rust only.

Self-contained: it creates and deletes its own database.

Run with::

    pytest --noconftest tests/replace_database_throughput/sync/legacy/test_crud_database.py -v
"""
import os
import unittest
import uuid
from contextlib import ExitStack

import pytest

from azure.cosmos import CosmosClient
from replace_database_throughput._fixtures import owned_database


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDDatabaseOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self.addCleanup(self.key_client.close)
        self._databases = ExitStack()
        self.addCleanup(self._databases.close)

    def test_database_level_offer_throughput_rust(self):
        """Throughput on a database can be raised after creation and reports the new value.

        Created at 1000 request units, then moved to 2000 through
        ``replace_throughput``.

        Kept here for the change itself. The replacement must return the
        updated figure rather than echoing the value the database was created
        with, which is the easiest way for a change that never took effect to
        look successful.
        """
        # Source: tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_level_offer_throughput
        # Create a database with throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = self._databases.enter_context(owned_database(
            self.key_client, database_id, offer_throughput=offer_throughput,
        ))
        self.assertEqual(created_db.id, database_id)

        # Verify offer throughput for database
        offer = created_db.get_throughput()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        # Update database offer throughput
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        self.key_client.delete_database(created_db.id)


if __name__ == "__main__":
    unittest.main()
