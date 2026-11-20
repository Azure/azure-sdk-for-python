# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_patch_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the core-python and
Rust runs. The file name drops the ``_async`` suffix so it pairs with
the sync copy. A key client builds its own database + container; the
data client (AAD in AAD lanes) does the item work, as in the source.

Run: ``pytest --noconftest tests/patch_item/aio/test_headers.py -v``
"""
import importlib
import unittest
from unittest.mock import patch
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


# Same value as the source, so the wire bytes match core-python.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original. Cleanups run in
        # reverse order and still run if setup fails partway.
        self.key_client = create_setup_client_async(_backend="rust")
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self._db_id = "legacy_pi_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)
        await key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(self._db_id).get_container_client(self._container_id)

    async def test_container_patch_item_throughput_bucket_async_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_patch_item_throughput_bucket_async
        # NOTE: the partition-key value and item id are FIXED (not a random
        # uuid like the source) so the parity reporter can diff the patched
        # item field-by-field against the core-python column -- a random
        # pk would show up as a spurious body divergence. Each column builds
        # its own fresh container, so the fixed (pk, id) never collides.
        pkValue = "patch_item_pk"
        # Create item to patch
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await self.container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "patch_item_async", wraps=binding.patch_item_async) as operation:
            await self.container.patch_item(
                item="patch_item",
                partition_key=pkValue,
                patch_operations=operations,
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)
