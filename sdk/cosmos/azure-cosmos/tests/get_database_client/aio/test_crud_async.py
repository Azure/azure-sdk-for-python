# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Copy the database portion; the mixed original still owns container/item checks."""

import pytest
from config import clients

from get_database_client._fixtures import AsyncDatabaseCase


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(AsyncDatabaseCase):
    async def asyncSetUp(self):
        await self.prepare_database(clients.create_data_client_async(_backend="rust"))

    async def test_get_resource_with_dictionary_and_object_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_get_resource_with_dictionary_and_object_async
        created_db = self.database_for_test

        # read database with id
        read_db = self.client.get_database_client(created_db.id)
        assert read_db.id == created_db.id

        # read database with instance
        read_db = self.client.get_database_client(created_db)
        assert read_db.id == created_db.id

        # read database with properties
        read_db = self.client.get_database_client(await created_db.read())
        assert read_db.id == created_db.id
