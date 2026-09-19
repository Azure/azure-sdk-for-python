# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected sync database throughput test pinned to the Rust backend."""
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


@pytest.mark.cosmosLong
class TestCRUDDatabaseOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.key_client = CosmosClient(HOST, KEY, _backend="rust")

    @classmethod
    def tearDownClass(cls):
        cls.key_client.close()

    def test_database_level_offer_throughput(self):
        """Throughput set at the database level can be read back and then changed.

        Creates a database with 1000 request units, confirms ``read_offer``
        reports that figure, then raises it to 2000 through
        ``replace_throughput`` and confirms the new value comes back.

        Three separate operations have to agree about the same number. The
        replace is the interesting one: it must return the updated figure
        rather than echoing the value it was created with.
        """
        # Source: tests/test_crud_database.py::TestCRUDDatabaseOperations.test_database_level_offer_throughput
        offer_throughput = 1000
        database_id = str(uuid.uuid4())
        created_db = self.key_client.create_database(
            id=database_id,
            offer_throughput=offer_throughput
        )
        self.assertEqual(created_db.id, database_id)

        offer = created_db.read_offer()
        self.assertEqual(offer.offer_throughput, offer_throughput)

        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
        self.key_client.delete_database(created_db.id)
