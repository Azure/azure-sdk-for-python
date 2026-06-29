# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_replace_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source so the parity reporter can pair the core-python and
rust runs. The file name drops the ``_async`` suffix so it pairs with
the sync copy. Builds its own database + container and reads
``ACCOUNT_HOST`` / ``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/replace_item/aio/legacy/test_headers.py -v``
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


# Same value as the source, so the wire bytes match core-python.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
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

    async def test_container_replace_item_throughput_bucket_async(self):
        """Verify the async replace_item forwards the per-request throughput_bucket kwarg as the x-ms-cosmos-throughput-bucket header (item id differs from the body id, exercising the URL-id-from-item path)."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_replace_item_throughput_bucket_async
        created_document = await self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        await self.container.replace_item(
            item=created_document['id'],
            body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

