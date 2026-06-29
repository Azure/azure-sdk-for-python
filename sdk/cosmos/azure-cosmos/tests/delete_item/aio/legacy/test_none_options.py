# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async ``test_delete_item_none_options_async`` test against the
``_backend="rust"`` path.

Source: ``tests/test_none_options_async.py``. The class name and method
name match the source so the parity reporter can pair the two runs by
``(file basename, class name, method name)``. The other methods in the
source ``TestNoneOptionsAsync`` class cover ``create_item``,
``read_item``, ``upsert_item``, ``replace_item``, etc.; they belong to
their own operations' ``legacy/`` folders.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/delete_item/aio/legacy/test_none_options.py -v
"""
import os
import unittest
import uuid

from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


class TestNoneOptionsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_di_none_opts_" + uuid.uuid4().hex[:8]
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

    async def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        await self.container.create_item(
            item, pre_trigger_include=None, post_trigger_include=None,
            indexing_directive=None, enable_automatic_id_generation=False,
            session_token=None, initial_headers=None, priority=None,
            no_response=None, retry_write=None, throughput_bucket=None,
        )
        return item

    async def test_delete_item_none_options_async(self):
        """Verify the async delete_item accepts None for every optional kwarg (pre_trigger_include, post_trigger_include, session_token, initial_headers, etag, match_condition, priority, retry_write, throughput_bucket) and removes the item."""
        # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_delete_item_none_options_async
        item = await self._create_sample_item()
        await self.container.delete_item(
            item["id"], partition_key=item["pk"], pre_trigger_include=None,
            post_trigger_include=None, session_token=None, initial_headers=None,
            etag=None, match_condition=None, priority=None, retry_write=None,
            throughput_bucket=None,
        )
        with self.assertRaises(CosmosHttpResponseError):
            await self.container.read_item(
                item["id"], partition_key=item["pk"], post_trigger_include=None,
                session_token=None, initial_headers=None,
                max_integrated_cache_staleness_in_ms=None, priority=None,
                throughput_bucket=None,
            )

