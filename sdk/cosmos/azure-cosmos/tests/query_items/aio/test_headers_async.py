# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_query_items_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names match
the source (apart from the method's ``_rust`` suffix). Builds its own database
+ container with a key client and runs the tested operations through the data
client from ``config.clients``.

The legacy test captured outgoing HTTP requests, which the Rust transport does
not expose (known gap 6). This copy instead checks the request the SDK hands to
the Rust binding, as the ``upsert_item`` copies do. Gateway V2 may still drop
the header on the wire (known gap 36).

Run: ``pytest --noconftest tests/query_items/aio/test_headers_async.py -v``
"""
import importlib
import unittest
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) backs data_container.
        self.key_client = create_setup_client_async()
        await self.key_client.__aenter__()
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_query_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.key_client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.data_database = self.client.get_database_client(self._db_id)
        self.data_container = self.data_database.get_container_client(self._container_id)

    async def asyncTearDown(self):
        try:
            await self.key_client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.key_client.close()
        await self.client.close()

    async def test_container_query_items_throughput_bucket_async_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_query_items_throughput_bucket_async
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await self.data_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "fetch_page_with_cursor_async",
                          wraps=binding.fetch_page_with_cursor_async) as operation:
            query_results = [item async for item in self.data_container.query_items(
                query=query,
                partition_key='pk',
                throughput_bucket=request_throughput_bucket_number)]
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)


if __name__ == "__main__":
    unittest.main()
