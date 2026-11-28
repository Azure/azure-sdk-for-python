# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_read_item_throughput_bucket_async`` test
against the ``_backend="rust"`` path.

Source: ``tests/test_headers_async.py``. The other methods in the
source ``TestHeadersAsync`` class cover create-item throughput-bucket,
query-item throughput-bucket, etc.; they belong to their own
operations' ``legacy/`` folders. Async source has no
``test_negative_max_integrated_cache_staleness_async`` counterpart, so
the negative-validation test is sync-only.

Self-contained: builds its own database + container in ``asyncSetUp``
and registers deletion and client closure immediately, including on setup failure. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/aio/test_headers.py -v
"""
import importlib
import unittest
from unittest.mock import patch
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


# Constants kept identical to the source so the wire value is the same
# as what the legacy path sent.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original.
        self.key_client = create_setup_client_async(_backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.client = create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)
        print(f"\nOwned read-test database: {self._db_id}")
        await key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(self._db_id).get_container_client(self._container_id)

    async def test_container_read_item_throughput_bucket_async_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_read_item_throughput_bucket_async
        created_document = await self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'}
        )
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "read_item_async", wraps=binding.read_item_async) as operation:
            await self.container.read_item(
                item=created_document['id'],
                partition_key="mypk",
                throughput_bucket=request_throughput_bucket_number,
            )
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)
