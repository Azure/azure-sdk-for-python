# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the item-read portion with the original no-response client setting."""

import uuid

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
        created_container = self.databaseForTest.get_container_client(self.container_id)

        created_item = created_container.create_item({'id': '1' + str(uuid.uuid4()), 'pk': 'pk'}, no_response=False)

        # read item with id
        read_item = created_container.read_item(item=created_item['id'], partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])

        # read item with properties
        read_item = created_container.read_item(item=created_item, partition_key=created_item['pk'])
        self.assertEqual(read_item['id'], created_item['id'])
