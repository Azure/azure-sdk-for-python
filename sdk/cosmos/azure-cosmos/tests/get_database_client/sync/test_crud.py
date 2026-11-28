# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the database portion; the mixed original still owns container/item checks."""

import pytest
from config import clients

from get_database_client._fixtures import SyncDatabaseCase


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperations(SyncDatabaseCase):
    def setUp(self):
        self.prepare_database(clients.create_data_client(_backend="rust"))

    def test_get_resource_with_dictionary_and_object_rust(self):
        # Source: tests/test_crud.py::TestCRUDOperations.test_get_resource_with_dictionary_and_object
        created_db = self.databaseForTest

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        self.assertEqual(read_db.id, created_db.id)

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        self.assertEqual(read_db.id, created_db.id)

        # read database with properties
        read_db = self.client.get_database_client(created_db.read())
        self.assertEqual(read_db.id, created_db.id)
