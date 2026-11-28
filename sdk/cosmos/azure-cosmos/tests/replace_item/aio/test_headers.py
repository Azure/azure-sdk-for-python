# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_replace_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the core-python and
Rust runs. The file name drops the ``_async`` suffix so it pairs with
the sync copy. Builds its own database + container through a key client;
the tested operations run on the data client (AAD in the cosmosAAD* lanes).

Run: ``pytest --noconftest tests/replace_item/aio/test_headers.py -v``
"""
import importlib
import unittest
from unittest.mock import patch
import uuid

import pytest

from config.clients import create_data_client_async, create_setup_client_async

from azure.cosmos import PartitionKey


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        self.key_client = create_setup_client_async()
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self._delete_owned_database)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.data_database = self.client.get_database_client(self._db_id)
        self.data_container = self.data_database.get_container_client(self._container_id)

    async def _delete_owned_database(self):
        try:
            await self.key_client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    async def test_container_replace_item_throughput_bucket_async_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_replace_item_throughput_bucket_async
        created_document = await self.data_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "replace_item_async", wraps=binding.replace_item_async) as operation:
            await self.data_container.replace_item(
                item=created_document['id'],
                body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)
