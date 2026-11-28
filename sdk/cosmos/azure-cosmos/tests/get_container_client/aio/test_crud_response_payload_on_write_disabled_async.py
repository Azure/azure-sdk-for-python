# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain the original no-response client setting for container navigation."""

import pytest
from config import clients

from get_container_client._fixtures import AsyncContainerCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(AsyncContainerCase):
    async def asyncSetUp(self):
        await self.prepare_container(
            clients.create_data_client_async(_backend="rust", no_response_on_write=True)
        )

    async def test_get_resource_with_dictionary_and_object_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_get_resource_with_dictionary_and_object_async
        created_db = self.database_for_test

        created_container = self.database_for_test.get_container_client(self.container_id)

        # read container with id
        read_container = created_db.get_container_client(created_container.id)
        assert read_container.id == created_container.id

        # read container with instance
        read_container = created_db.get_container_client(created_container)
        assert read_container.id == created_container.id

        # read container with properties
        created_properties = await created_container.read()
        read_container = created_db.get_container_client(created_properties)
        assert read_container.id == created_container.id
