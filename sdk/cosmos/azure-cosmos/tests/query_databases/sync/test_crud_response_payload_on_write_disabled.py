# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original SQL database queries with write responses disabled, on Rust."""

import unittest

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config import settings


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(unittest.TestCase):
    def setUp(self):
        self.key_client = CosmosClient(
            settings.TestSettings.host,
            settings.TestSettings.masterKey,
            no_response_on_write=True,
            _backend="rust",
        )
        self.addCleanup(self.key_client.close)

    def _delete_database(self, database_id):
        try:
            self.key_client.delete_database(database_id)
        except CosmosResourceNotFoundError:
            pass

    def test_sql_query_crud_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_sql_query_crud
        db1 = self.key_client.create_database(settings.unique_database_id("db1"))
        self.addCleanup(self._delete_database, db1.id)
        db2 = self.key_client.create_database(settings.unique_database_id("db2"))
        self.addCleanup(self._delete_database, db2.id)

        databases = list(
            self.key_client.query_databases(
                {"query": "SELECT * FROM root r WHERE r.id=@id", "parameters": [{"name": "@id", "value": db1.id}]}
            )
        )
        self.assertEqual(1, len(databases), "Unexpected number of query results.")

        databases = list(
            self.key_client.query_databases({"query": 'SELECT * FROM root r WHERE r.id="database non-existing"'})
        )
        self.assertEqual(0, len(databases), "Unexpected number of query results.")

        databases = list(self.key_client.query_databases('SELECT * FROM root r WHERE r.id="' + db2.id + '"'))  # nosec
        self.assertEqual(1, len(databases), "Unexpected number of query results.")
        self.key_client.delete_database(db1.id)
        self.key_client.delete_database(db2.id)
