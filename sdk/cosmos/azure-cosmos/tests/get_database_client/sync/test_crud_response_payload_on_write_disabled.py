# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain the original no-response client setting for database navigation."""

import pytest
from config import clients

from get_database_client._fixtures import SyncDatabaseCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(SyncDatabaseCase):
    def setUp(self):
        self.prepare_database(
            clients.create_data_client(_backend="rust", no_response_on_write=True)
        )

    def test_get_resource_with_dictionary_and_object_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_get_resource_with_dictionary_and_object
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
