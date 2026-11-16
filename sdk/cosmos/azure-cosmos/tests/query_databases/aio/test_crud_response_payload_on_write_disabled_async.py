# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async SQL database queries with write responses disabled, on Rust."""

import unittest

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config import settings


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = CosmosClient(
            settings.TestSettings.host,
            settings.TestSettings.masterKey,
            no_response_on_write=True,
            _backend="rust",
        )
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()

    async def _delete_database(self, database_id):
        try:
            await self.key_client.delete_database(database_id)
        except CosmosResourceNotFoundError:
            pass

    async def test_sql_query_crud_async_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_sql_query_crud_async
        db1 = await self.key_client.create_database(settings.unique_database_id("db1"))
        self.addAsyncCleanup(self._delete_database, db1.id)
        db2 = await self.key_client.create_database(settings.unique_database_id("db2"))
        self.addAsyncCleanup(self._delete_database, db2.id)

        databases = [
            database
            async for database in self.key_client.query_databases(
                query="SELECT * FROM root r WHERE r.id=@id", parameters=[{"name": "@id", "value": db1.id}]
            )
        ]
        assert 1 == len(databases)

        databases = [
            database
            async for database in self.key_client.query_databases(
                query='SELECT * FROM root r WHERE r.id="database non-existing"'
            )
        ]
        assert 0 == len(databases)

        query_string = 'SELECT * FROM root r WHERE r.id="' + db2.id + '"'
        databases = [database async for database in self.key_client.query_databases(query=query_string)]
        assert 1 == len(databases)

        await self.key_client.delete_database(db1.id)
        await self.key_client.delete_database(db2.id)
