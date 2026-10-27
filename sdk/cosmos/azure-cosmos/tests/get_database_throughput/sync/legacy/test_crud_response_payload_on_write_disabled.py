# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original database-throughput assertions with write responses disabled."""

import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError


@pytest.mark.cosmosEmulator
class TestCRUDOperationsResponsePayloadOnWriteDisabled(unittest.TestCase):
    def setUp(self):
        self.key_client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", no_response_on_write=True,
        )
        self.database_id = "get_db_noresponse_" + uuid.uuid4().hex
        self.addCleanup(self.key_client.close)
        self.addCleanup(self._delete_database)

    def _delete_database(self):
        try:
            self.key_client.delete_database(self.database_id)
        except CosmosResourceNotFoundError:
            pass

    def test_database_crud_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_database_crud
        database_id = self.database_id
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)

    def test_database_level_offer_throughput_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_database_level_offer_throughput
        offer_throughput = 1000
        database_id = self.database_id
        created_db = self.key_client.create_database(id=database_id, offer_throughput=offer_throughput)
        self.assertEqual(created_db.id, database_id)
        offer = created_db.get_throughput()
        self.assertEqual(offer.offer_throughput, offer_throughput)
        new_offer_throughput = 2000
        offer = created_db.replace_throughput(new_offer_throughput)
        self.assertEqual(offer.offer_throughput, new_offer_throughput)
