# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async ``test_container_read_item_none_options_async`` test against
the ``_backend="rust"`` path.

Source: ``tests/test_none_options_async.py``. The class name and method
name match the source (apart from the method's ``_rust`` suffix) so the parity reporter
can pair the two runs by
``(file basename, class name, method name)``.

Self-contained: builds its own database + container in ``asyncSetUp``
and registers deletion and client closure immediately, including on setup failure. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/aio/test_none_options.py -v
"""
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


@pytest.mark.cosmosEmulator
class TestNoneOptionsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Key client owns the database and container; the data client does
        # item work, as in the original.
        self.key_client = create_setup_client_async(_backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        self.client = create_data_client_async(_backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self._db_id = "legacy_ri_none_opts_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)
        print(f"\nOwned read-test database: {self._db_id}")
        await key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(self._db_id).get_container_client(self._container_id)

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

    async def test_container_read_item_none_options_async_rust(self):
        """The async read_item accepts None for every optional argument.

        None means "not supplied". Customers commonly build one call site
        that passes every option through from their own config, leaving most
        of them None, so each must behave as if it had been omitted: no
        header, no error, and the item comes back unchanged.

        The options covered are session_token,
        initial_headers, max_integrated_cache_staleness_in_ms, priority and
        throughput_bucket.
        """
        # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_container_read_item_none_options_async
        item = await self._create_sample_item()
        read_back = await self.container.read_item(
            item["id"],
            partition_key=item["pk"],
            session_token=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            priority=None,
            throughput_bucket=None,
        )
        assert read_back["id"] == item["id"]
