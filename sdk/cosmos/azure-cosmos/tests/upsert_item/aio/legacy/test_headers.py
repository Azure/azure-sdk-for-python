# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_upsert_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source so the parity reporter can pair the core-python and
Rust runs. Builds its own database + container and reads ``ACCOUNT_HOST``
/ ``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/upsert_item/aio/legacy/test_headers.py -v``
"""
import importlib
import os
import unittest
from unittest.mock import patch
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, http_constants


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_ui_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_container_upsert_item_throughput_bucket_async(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_upsert_item_throughput_bucket_async
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "upsert_item_async", wraps=binding.upsert_item_async) as operation:
            await self.container.upsert_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number,
            )
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(
                call.args[1].headers[http_constants.HttpHeaders.ThroughputBucket],
                str(request_throughput_bucket_number),
            )
