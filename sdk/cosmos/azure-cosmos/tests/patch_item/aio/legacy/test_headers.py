# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_patch_item_throughput_bucket_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers_async.py``; the class and method names
match the source so the parity reporter can pair the core-python and
rust runs. The file name drops the ``_async`` suffix so it pairs with
the sync copy. Builds its own database + container and reads
``ACCOUNT_HOST`` / ``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/patch_item/aio/legacy/test_headers.py -v``
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
        self._db_id = "legacy_pi_headers_" + uuid.uuid4().hex[:8]
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

    async def test_container_patch_item_throughput_bucket_async(self):
        """Verify the async patch_item forwards the throughput_bucket kwarg as the x-ms-cosmos-throughput-bucket header and that all six patch operations produce the expected document."""
        # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_patch_item_throughput_bucket_async
        # NOTE: the partition-key value and item id are FIXED (not a random
        # uuid like the source) so the parity reporter can diff the patched
        # document field-by-field against the core-python column -- a random
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
        await self.container.patch_item(
            item="patch_item",
            partition_key=pkValue,
            patch_operations=operations,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

