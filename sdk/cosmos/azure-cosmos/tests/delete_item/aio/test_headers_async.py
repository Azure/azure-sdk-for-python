# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_delete_item_throughput_bucket_async`` against the Rust path.

The original captured outgoing Python HTTP requests and checked their
throughput-bucket header. Rust requests bypass that transport, so this copy
checks the value the Python wrapper hands to the Rust delete binding.

Self-contained: builds its own database + container in ``asyncSetUp`` and
deletes them in ``asyncTearDown``.
"""
import importlib
import os
import unittest
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient

HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)

request_throughput_bucket_number = 3


def assert_request_throughput_bucket(prepared):
    assert prepared.settings.throughput_bucket == request_throughput_bucket_number


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "delete_headers_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.data_container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_container_delete_item_throughput_bucket_async_rust(self):
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_delete_item_throughput_bucket_async
        created_item = await self.data_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "delete_item_async", wraps=binding.delete_item_async) as operation:
            await self.data_container.delete_item(
                created_item['id'],
                partition_key='mypk',
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        requests = [operation.call_args.args[1]]
        assert requests[0].op == "delete_item"
        assert requests[0].item_id == created_item['id']
        # Known gap 33: `CosmosClient(...)`: settings from first principles, bites 1-15 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-33). The binding receives the bucket, but the pinned driver omits it on Gateway V2, so this checks the native boundary, not the wire header.
        for request in requests:
            assert_request_throughput_bucket(request)
