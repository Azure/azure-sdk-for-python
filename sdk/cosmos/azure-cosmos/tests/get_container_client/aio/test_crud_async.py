# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the container portion; the mixed original still owns the item checks."""

import pytest
from config import clients

from get_container_client._fixtures import AsyncContainerCase


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(AsyncContainerCase):
    async def asyncSetUp(self):
        await self.prepare_container(clients.create_data_client_async(_backend="rust"))

    async def test_get_resource_with_dictionary_and_object_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_get_resource_with_dictionary_and_object_async
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
