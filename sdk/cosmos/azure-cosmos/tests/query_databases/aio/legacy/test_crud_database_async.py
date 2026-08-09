# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Selected async v4 database-query tests pinned to the Rust backend.

Original: tests/test_crud_database_async.py
Copy:     tests/query_databases/aio/legacy/test_crud_database_async.py
"""

import unittest
import uuid

import pytest

import test_config
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosEmulator
class TestCRUDDatabaseOperationsAsync(unittest.IsolatedAsyncioTestCase):
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey

    async def asyncSetUp(self):
        self.key_client = CosmosClient(self.host, self.masterKey, _backend="rust")
        await self.key_client.__aenter__()

    async def asyncTearDown(self):
        await self.key_client.close()

    async def test_sql_query_crud_async(self):
        """Query databases by id with a parameterized query, a no-match filter and a plain query string."""
        # Source: tests/test_crud_database_async.py::TestCRUDDatabaseOperationsAsync.test_sql_query_crud_async
        # create two databases.
        db1 = await self.key_client.create_database('database 1' + str(uuid.uuid4()))
        db2 = await self.key_client.create_database('database 2' + str(uuid.uuid4()))

        # query with parameters.
        databases = [database async for database in self.key_client.query_databases(
            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': db1.id}
            ]
        )]
        assert 1 == len(databases)

        # query without parameters.
        databases = [database async for database in self.key_client.query_databases(
            query='SELECT * FROM root r WHERE r.id="database non-existing"'
        )]
        assert 0 == len(databases)

        # query with a string.
        query_string = 'SELECT * FROM root r WHERE r.id="' + db2.id + '"'
        databases = [database async for database in
                     self.key_client.query_databases(query=query_string)]
        assert 1 == len(databases)

        await self.key_client.delete_database(db1.id)
        await self.key_client.delete_database(db2.id)


if __name__ == "__main__":
    unittest.main()
