# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 database-throughput check, re-run on the rust engine.

Why this file exists: a database can own throughput that all of its containers
share. A customer reads that number with ``read_offer`` (the older name) or
``get_throughput`` (the current name), and puts it into cost and capacity
dashboards. ``read_offer`` is not a separate request path -- it forwards to
``get_throughput`` -- so this file also proves the older name still returns the
same number after the move to rust. If rust returned a different RU/s here, a
customer would size their database against a wrong figure.

What it does: the real v4 test copied from ``tests/test_crud_database.py``,
changed in one place -- the client is built with ``_backend="rust"``. It
creates a database with 1000 RU/s, reads the offer back and checks it says
1000, replaces it with 2000, and checks the replace result says 2000.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/sync/test_get_database_throughput_parity.py``) run
the same call on both engines and diff the numbers. This file runs on rust
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
