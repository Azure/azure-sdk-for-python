# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned fixtures for unchanged replacement tests; item checks use core-Python."""

import os
import unittest
import uuid

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient

from common._parity_helpers import run_target_operation, run_target_operation_async


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
        self.data_client = CosmosClient(self.host, self.key, _backend="core-python", read_timeout=30)
        self.addCleanup(self.data_client.close)
        self.database_id = "replace_legacy_" + uuid.uuid4().hex
        self.addCleanup(self._delete_owned_database)
        self.key_db = self.test_db = self.test_database = self.client.create_database(self.database_id)
        self.created_db = self.data_client.get_database_client(self.database_id)
        replacement = self.key_db.replace_container

        def guarded_replace(*args, **kwargs):
            return run_target_operation(self.client, lambda: replacement(*args, **kwargs))

        self.key_db.replace_container = guarded_replace
        self._initialize_data()

    def _delete_owned_database(self):
        try:
            self.data_client.delete_database(self.database_id)
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
        self.data_client = AsyncCosmosClient(self.host, self.key, _backend="core-python", read_timeout=30)
        self.addAsyncCleanup(self.data_client.close)
        await self.client.__aenter__()
        await self.data_client.__aenter__()
        self.database_id = "replace_legacy_async_" + uuid.uuid4().hex
        self.addAsyncCleanup(self._delete_owned_database)
        self.key_db = self.test_db = self.test_database = await self.client.create_database(self.database_id)
        self.created_db = self.data_client.get_database_client(self.database_id)
        replacement = self.key_db.replace_container

        async def guarded_replace(*args, **kwargs):
            return await run_target_operation_async(self.client, lambda: replacement(*args, **kwargs))

        self.key_db.replace_container = guarded_replace
        self._initialize_data()

    async def _delete_owned_database(self):
        try:
            await self.data_client.delete_database(self.database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass
