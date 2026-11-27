# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned key-auth setup with container reads on the configured Rust data client."""

import unittest
from functools import wraps
from types import SimpleNamespace
from unittest.mock import patch

from azure.cosmos import ContainerProxy, exceptions
from azure.cosmos.aio import ContainerProxy as AsyncContainerProxy
from common._rust_checks import run_on_rust, run_on_rust_async
from config import clients
from config.settings import unique_database_id


class SyncContainerReadCase(unittest.TestCase):
    def setUp(self):
        self.key_client = clients.create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = clients.create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self.database_id = unique_database_id("ContainerRead")
        self.addCleanup(self._delete_owned_database)
        self.key_db = self.key_client.create_database(self.database_id)
        self.data_db = self.client.get_database_client(self.database_id)
        self.data_db.create_container = self.key_db.create_container
        self.data_db.delete_container = self.key_db.delete_container
        self.databaseForTest = self.test_database = self.data_db
        self.configs = SimpleNamespace(
            TEST_DATABASE_ID=self.database_id,
            TEST_MULTI_PARTITION_CONTAINER_ID="quota_target",
        )
        original_read = ContainerProxy.read

        @wraps(original_read)
        def guarded_read(container, *args, **kwargs):
            if not container.container_link.startswith(self.key_db.database_link + "/colls/"):
                return original_read(container, *args, **kwargs)
            target = (
                container if container.client_connection is self.client.client_connection
                else self.data_db.get_container_client(container.id)
            )
            return run_on_rust(self.client, lambda: original_read(target, *args, **kwargs))

        for owner, name, replacement in (
            (ContainerProxy, "read", guarded_read),
            (self.client.client_connection, "ReadContainer",
             lambda *args, **kwargs: self.fail("Rust container read entered legacy ReadContainer")),
        ):
            guard = patch.object(owner, name, replacement, create=True)
            guard.start()
            self.addCleanup(guard.stop)

    def _create_container_for_test(self, **kwargs):
        return self.key_db.create_container(**kwargs)

    def _delete_container_for_test(self, container):
        self.key_db.delete_container(container)

    def _delete_owned_database(self):
        try:
            self.key_client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass


class AsyncContainerReadCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = clients.create_setup_client_async(_backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        self.client = clients.create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.key_client.__aenter__()
        await self.client.__aenter__()
        self.database_id = unique_database_id("ContainerReadAsync")
        self.addAsyncCleanup(self._delete_owned_database)
        self.key_db = await self.key_client.create_database(self.database_id)
        self.data_db = self.client.get_database_client(self.database_id)
        self.data_db.create_container = self.key_db.create_container
        self.data_db.delete_container = self.key_db.delete_container
        self.database_for_test = self.test_database = self.data_db
        self.configs = SimpleNamespace(
            TEST_DATABASE_ID=self.database_id,
            TEST_MULTI_PARTITION_CONTAINER_ID="quota_target",
        )
        original_read = AsyncContainerProxy.read

        @wraps(original_read)
        async def guarded_read(container, *args, **kwargs):
            if not container.container_link.startswith(self.key_db.database_link + "/colls/"):
                return await original_read(container, *args, **kwargs)
            target = (
                container if container.client_connection is self.client.client_connection
                else self.data_db.get_container_client(container.id)
            )
            return await run_on_rust_async(
                self.client, lambda: original_read(target, *args, **kwargs),
            )

        for owner, name, replacement in (
            (AsyncContainerProxy, "read", guarded_read),
            (self.client.client_connection, "ReadContainer",
             lambda *args, **kwargs: self.fail("Rust container read entered legacy ReadContainer")),
        ):
            guard = patch.object(owner, name, replacement, create=True)
            guard.start()
            self.addCleanup(guard.stop)

    async def _create_container_for_test_async(self, **kwargs):
        return await self.key_db.create_container(**kwargs)

    async def _delete_container_for_test_async(self, container):
        await self.key_db.delete_container(container)

    async def _delete_owned_database(self):
        try:
            await self.key_client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
