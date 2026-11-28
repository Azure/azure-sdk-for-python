# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async ``test_replace_item_none_options_async`` on the
``_backend="rust"`` path.

Copied from ``tests/test_none_options_async.py``; the class and method
names match the source (apart from the method's ``_rust`` suffix) so the parity reporter
can pair the core-python
and Rust runs. The file name drops the ``_async`` suffix so it pairs
with the sync copy. Builds its own database + container through a key
client; the tested operations run on the data client (AAD in the
cosmosAAD* lanes).

Run: ``pytest --noconftest tests/replace_item/aio/test_none_options.py -v``
"""
import unittest
import uuid

import pytest

from config.clients import create_data_client_async, create_setup_client_async

from azure.cosmos import PartitionKey


@pytest.mark.cosmosEmulator
class TestNoneOptionsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        self.key_client = create_setup_client_async()
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self._db_id = "legacy_ri_none_opts_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self._delete_owned_database)
        self.key_container = await key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.database = self.client.get_database_client(self._db_id)
        self.container = self.database.get_container_client(self._container_id)

    async def _delete_owned_database(self):
        try:
            await self.key_client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    async def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        await self.container.create_item(
            item,
            indexing_directive=None,
            enable_automatic_id_generation=False,
            session_token=None,
            initial_headers=None,
            priority=None,
            no_response=None,
            retry_write=None,
            throughput_bucket=None,
        )
        return item

    async def test_replace_item_none_options_async_rust(self):
        """Verify the async replace_item accepts None for every optional kwarg (session_token, initial_headers, etag, match_condition, priority, no_response, retry_write, throughput_bucket) and returns the replaced item."""
        # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_replace_item_none_options_async
        item = await self._create_sample_item()
        new_body = {"id": item["id"], "pk": item["pk"], "value": 999}
        replaced = await self.container.replace_item(
            item["id"],
            new_body,
            session_token=None,
            initial_headers=None,
            etag=None,
            match_condition=None,
            priority=None,
            no_response=None,
            retry_write=None,
            throughput_bucket=None,
        )
        assert replaced["value"] == 999
