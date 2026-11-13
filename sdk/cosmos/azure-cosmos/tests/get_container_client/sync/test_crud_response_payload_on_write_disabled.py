# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain the original no-response client setting for container navigation."""

import pytest
from config import clients

from get_container_client._fixtures import SyncContainerCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(SyncContainerCase):
    def setUp(self):
        self.prepare_container(clients.create_data_client(_backend="rust", no_response_on_write=True))

    def test_get_resource_with_dictionary_and_object_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_get_resource_with_dictionary_and_object
        created_db = self.databaseForTest

        created_container = self.databaseForTest.get_container_client(self.container_id)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        self.assertEqual(read_container.id, created_container.id)

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        self.assertEqual(read_container.id, created_container.id)

        # read container with properties
        created_properties = created_container.read()
        read_container = created_db.get_container_client(created_properties)
        self.assertEqual(read_container.id, created_container.id)
