# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own a database per case without requiring a pre-existing container."""

import unittest
from uuid import uuid4

from config import settings
from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient


class SyncDatabaseCase(unittest.TestCase):
    def prepare_database(self, client):
        self.client = client
        self.addCleanup(client.close)
        setup = CosmosClient(
            settings.TestSettings.host, settings.TestSettings.masterKey, _backend="rust"
        )
        self.addCleanup(setup.close)
        database_id = "get-database-client-" + uuid4().hex
        setup.create_database(database_id)
        self.addCleanup(setup.delete_database, database_id)
        self.databaseForTest = client.get_database_client(database_id)


class AsyncDatabaseCase(unittest.IsolatedAsyncioTestCase):
    async def prepare_database(self, client):
        self.client = client
        self.addAsyncCleanup(client.close)
        await client.__aenter__()
        setup = AsyncCosmosClient(
            settings.TestSettings.host, settings.TestSettings.masterKey, _backend="rust"
        )
        self.addAsyncCleanup(setup.close)
        await setup.__aenter__()
        database_id = "get-database-client-" + uuid4().hex
        await setup.create_database(database_id)
        self.addAsyncCleanup(setup.delete_database, database_id)
        self.database_for_test = client.get_database_client(database_id)
