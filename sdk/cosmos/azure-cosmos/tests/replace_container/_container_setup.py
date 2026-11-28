# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned fixtures for unchanged replacement tests.

The key client creates, replaces and deletes resources, as in the originals.
Item checks use a Rust data client with the configured data auth (AAD in
AAD lanes), matching the originals' ``create_data_client`` role.
"""

import os
import unittest
import uuid

from azure.cosmos import exceptions

from common._rust_checks import run_on_rust, run_on_rust_async
from config.clients import create_data_client_async_for_endpoint, create_data_client_for_endpoint


class SyncReplacementCase(unittest.TestCase):
    def _create_key_client(self):
        raise NotImplementedError

    def _initialize_data(self):
        pass

    def setUp(self):
        self.host = os.environ["ACCOUNT_HOST"]
        self.key = os.environ["ACCOUNT_KEY"]
        self.client = self.key_client = self._create_key_client()
        self.addCleanup(self.client.close)
        self.data_client = create_data_client_for_endpoint(self.host, _backend="rust")
        self.addCleanup(self.data_client.close)
        self.database_id = "replace_legacy_" + uuid.uuid4().hex
        self.addCleanup(self._delete_owned_database)
        self.key_db = self.test_db = self.test_database = self.client.create_database(self.database_id)
        self.created_db = self.data_client.get_database_client(self.database_id)
        replacement = self.key_db.replace_container

        def guarded_replace(*args, **kwargs):
            return run_on_rust(self.client, lambda: replacement(*args, **kwargs))

        self.key_db.replace_container = guarded_replace
        self._initialize_data()

    def _delete_owned_database(self):
        try:
            self.key_client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass


class AsyncReplacementCase(unittest.IsolatedAsyncioTestCase):
    def _create_key_client(self):
        raise NotImplementedError

    def _initialize_data(self):
        pass

    async def asyncSetUp(self):
        self.host = os.environ["ACCOUNT_HOST"]
        self.key = os.environ["ACCOUNT_KEY"]
        self.client = self.key_client = self._create_key_client()
        self.addAsyncCleanup(self.client.close)
        self.data_client = create_data_client_async_for_endpoint(self.host, _backend="rust")
        self.addAsyncCleanup(self.data_client.close)
        await self.client.__aenter__()
        await self.data_client.__aenter__()
        self.database_id = "replace_legacy_async_" + uuid.uuid4().hex
        self.addAsyncCleanup(self._delete_owned_database)
        self.key_db = self.test_db = self.test_database = await self.client.create_database(self.database_id)
        self.created_db = self.data_client.get_database_client(self.database_id)
        replacement = self.key_db.replace_container

        async def guarded_replace(*args, **kwargs):
            return await run_on_rust_async(self.client, lambda: replacement(*args, **kwargs))

        self.key_db.replace_container = guarded_replace
        self._initialize_data()

    async def _delete_owned_database(self):
        try:
            await self.key_client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
