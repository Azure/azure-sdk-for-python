# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_delete_item_throughput_bucket_async`` against the Rust path.

The original captured outgoing Python HTTP requests and checked their
throughput-bucket header. Rust requests bypass that transport, so this copy
checks the value the Python wrapper hands to the Rust delete binding.

Self-contained: builds its own database + container through a key client in
``asyncSetUp`` and deletes them on cleanup; the tested operations run on the
data client (AAD in the cosmosAAD* lanes).
"""
import importlib
import unittest
import uuid
from unittest.mock import patch

import pytest

from config.clients import create_data_client_async, create_setup_client_async

from azure.cosmos import PartitionKey

request_throughput_bucket_number = 3


def assert_request_throughput_bucket(prepared):
    assert prepared.settings.throughput_bucket == request_throughput_bucket_number


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
        self._db_id = "delete_headers_async_" + uuid.uuid4().hex[:8]
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
        # Known gap 36: Request options are not sent over Gateway V2. The binding receives the bucket, but the pinned driver omits it on Gateway V2, so this checks the native boundary, not the wire header.
        for request in requests:
            assert_request_throughput_bucket(request)
