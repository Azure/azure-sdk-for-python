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
and deletes them in ``asyncTearDown``. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/aio/legacy/test_headers.py -v
"""
import os
import unittest
import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, http_constants


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Constants kept identical to the source so the wire value is the same
# as what core-python sent.
request_throughput_bucket_number = 3


async def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
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

    async def test_container_read_item_throughput_bucket_async(self):
        """Verify the async read_item forwards the per-request throughput_bucket kwarg as the x-ms-cosmos-throughput-bucket header."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_read_item_throughput_bucket_async
        created_document = await self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'}
        )
        await self.container.read_item(
            item=created_document['id'],
            partition_key="mypk",
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook,
        )

