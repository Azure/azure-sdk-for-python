# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain the original no-response client setting for database navigation."""

import pytest
from config import clients

from get_database_client._fixtures import AsyncDatabaseCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(AsyncDatabaseCase):
    async def asyncSetUp(self):
        await self.prepare_database(
            clients.create_data_client_async(_backend="rust", no_response_on_write=True)
        )

    async def test_get_resource_with_dictionary_and_object_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_get_resource_with_dictionary_and_object_async
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
