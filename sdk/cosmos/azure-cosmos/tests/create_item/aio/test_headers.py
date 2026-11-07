# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeadersAsync`` class cover other
operations; they belong to their own operations' ``legacy/`` folders.

Self-contained: key-owned setup registers cleanup in ``asyncSetUp``;
data operations follow the configured key/AAD lane. The class name matches
``tests/test_headers_async.py``; copied method names add ``_rust``.

Run with::

    pytest --noconftest tests/create_item/aio/test_headers.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
import importlib
from unittest.mock import patch
from config import clients


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Preserve the original value at the typed native boundary.
# Wire-header conversion is checked by the binding settings tests.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self._db_id = "legacy_headers_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)
        await key_database.create_container(
            id=self._container_id, partition_key=PartitionKey(path="/pk"),
        )
        self.client = clients.create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.database = self.client.get_database_client(self._db_id)
        self.container = self.database.get_container_client(self._container_id)

    async def test_container_create_item_throughput_bucket_async_rust(self):
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_create_item_throughput_bucket_async
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "create_item_async", wraps=binding.create_item_async) as operation:
            created = await self.container.create_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        prepared = operation.call_args.args[1]
        self.assertEqual(prepared.settings.throughput_bucket, request_throughput_bucket_number)
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(created["id"], prepared.item_id)
