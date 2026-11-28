# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Own a database and container per case instead of using the shared test container."""

import unittest
from uuid import uuid4

from config import settings
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

CONTAINER_ID = "orders"


class SyncContainerCase(unittest.TestCase):
    def prepare_container(self, client):
        self.client = client
        self.addCleanup(client.close)
        setup = CosmosClient(
            settings.TestSettings.host, settings.TestSettings.masterKey, _backend="rust"
        )
        self.addCleanup(setup.close)
        database_id = "get-container-client-" + uuid4().hex
        database = setup.create_database(database_id)
        self.addCleanup(setup.delete_database, database_id)
        database.create_container(CONTAINER_ID, partition_key=PartitionKey(path="/pk"))
        self.container_id = CONTAINER_ID
        self.databaseForTest = client.get_database_client(database_id)


class AsyncContainerCase(unittest.IsolatedAsyncioTestCase):
    async def prepare_container(self, client):
        self.client = client
        self.addAsyncCleanup(client.close)
        await client.__aenter__()
        setup = AsyncCosmosClient(
            settings.TestSettings.host, settings.TestSettings.masterKey, _backend="rust"
        )
        self.addAsyncCleanup(setup.close)
        await setup.__aenter__()
        database_id = "get-container-client-" + uuid4().hex
        database = await setup.create_database(database_id)
        self.addAsyncCleanup(setup.delete_database, database_id)
        await database.create_container(CONTAINER_ID, partition_key=PartitionKey(path="/pk"))
        self.container_id = CONTAINER_ID
        self.database_for_test = client.get_database_client(database_id)
