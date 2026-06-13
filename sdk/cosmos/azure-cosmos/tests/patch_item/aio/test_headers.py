# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_container_patch_item_throughput_bucket_async`` on the
**core-python** path (the parity reporter's core-python column).

Deterministic twin of ``aio/legacy/test_headers.py`` -- identical except
the absent ``_backend`` argument (so this runs the SDK default
core-python path) -- with a fixed partition-key value and id so the
parity reporter's body diff against the rust column is meaningful. See
the sync sibling ``tests/patch_item/sync/test_headers.py`` for the full
rationale (the main-tree async original uses a random per-run pk).

Run (core-python column):
``pytest tests/patch_item/aio/test_headers.py -v -s``
"""
import os
import unittest
import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey, http_constants


HOST = os.environ["ACCOUNT_HOST"]
KEY = os.environ["ACCOUNT_KEY"]


# Same value as the rust copy, so the wire bytes match.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # No ``_backend`` -> the SDK default (core-python) path.
        self.client = CosmosClient(HOST, KEY)
        await self.client.__aenter__()
        self._db_id = "corepy_pi_headers_" + uuid.uuid4().hex[:8]
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
        pkValue = "patch_item_pk"
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

