# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original database CRUD and throughput checks with write responses disabled."""

import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos import exceptions
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.http_constants import StatusCodes
from config import settings


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

    @pytest.mark.cosmosLong
    @pytest.mark.cosmosAADLong
    def test_database_crud_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_database_crud
        database_id = settings.unique_database_id()
        self.database_id = database_id
        created_db = self.key_client.create_database(database_id)
        self.assertEqual(created_db.id, database_id)
        databases = list(
            self.key_client.query_databases(
                {"query": "SELECT * FROM root r WHERE r.id=@id", "parameters": [{"name": "@id", "value": database_id}]}
            )
        )
        self.assertTrue(databases, "number of results for the query should be > 0")
        self.key_client.get_database_client(created_db.id).read()
        self.key_client.delete_database(created_db.id)
        read_db = self.key_client.get_database_client(created_db.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, read_db.read)
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=5000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)
        database_proxy = self.key_client.create_database_if_not_exists(id=database_id, offer_throughput=6000)
        self.assertEqual(database_id, database_proxy.id)
        self.assertEqual(5000, database_proxy.get_throughput().offer_throughput)

        self.key_client.delete_database(database_id)

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFalse(True, "function should fail.")
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @pytest.mark.cosmosEmulator
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
