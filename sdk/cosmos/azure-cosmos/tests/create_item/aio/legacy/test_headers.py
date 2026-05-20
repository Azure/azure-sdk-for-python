# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeadersAsync`` class cover other
operations; they belong to their own operations' ``legacy/`` folders.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. The class name and method name
match the source at ``tests/test_headers_async.py`` so test IDs differ
only by path.

Run with::

    pytest --noconftest tests/create_item/aio/legacy/test_headers.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, http_constants
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# The throughput-bucket number the test asserts is stamped on the
# outgoing request. Kept identical to the source constant so the wire
# value is the same as what core-python sent.
request_throughput_bucket_number = 3


async def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


@pytest.mark.cosmosEmulator
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_headers_async_" + uuid.uuid4().hex[:8]
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

    async def test_container_create_item_throughput_bucket_async(self):
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_create_item_throughput_bucket_async
        await self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

