# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned Rust-only fixtures for creation assertions copied from main."""

import unittest
import uuid

from azure.cosmos import exceptions
from common._rust_checks import run_on_rust, run_on_rust_async
from config.clients import create_setup_client, create_setup_client_async
from config.settings import TestSettings


class SyncCreationCase(unittest.TestCase):
    def _create_client(self):
        return create_setup_client()

    def setUp(self):
        self.host = TestSettings.host
        self.client = self.key_client = self._create_client()
        self.addCleanup(self.client.close)
        self._database_id = "create_container_" + uuid.uuid4().hex
        self.addCleanup(self._delete_owned_database)
        self.test_db = self.test_database = self.databaseForTest = (
            self.client.create_database(self._database_id)
        )
        create = self.test_db.create_container

        def guarded_create(*args, **kwargs):
            return run_on_rust(self.client, lambda: create(*args, **kwargs))

        self.test_db.create_container = guarded_create

    def _delete_owned_database(self):
        try:
            self.client.delete_database(self._database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass


class AsyncCreationCase(unittest.IsolatedAsyncioTestCase):
    def _create_client(self):
        return create_setup_client_async()

    async def asyncSetUp(self):
        self.host = TestSettings.host
        self.client = self.key_client = self._create_client()
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self._database_id = "create_container_async_" + uuid.uuid4().hex
        self.addAsyncCleanup(self._delete_owned_database)
        self.test_db = self.test_database = self.database_for_test = (
            await self.client.create_database(self._database_id)
        )
        create = self.test_db.create_container

        async def guarded_create(*args, **kwargs):
            return await run_on_rust_async(self.client, lambda: create(*args, **kwargs))

        self.test_db.create_container = guarded_create

    async def _delete_owned_database(self):
        try:
            await self.client.delete_database(self._database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
