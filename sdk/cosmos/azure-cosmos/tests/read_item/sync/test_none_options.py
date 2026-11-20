# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_container_read_item_none_options`` test against the
``_backend="rust"`` path.

Source: ``tests/test_none_options.py``. The class name and method name
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the two runs by
``(file basename, class name, method name)``. The other methods in the
source ``TestNoneOptions`` class cover ``create_item``, ``upsert_item``,
``replace_item``, etc.; they belong to their own operations' ``legacy/``
folders.

Self-contained: builds its own database + container in ``setUp`` and
registers cleanup immediately after acquisition, including on setup failure.
Reads ``ACCOUNT_HOST`` and ``ACCOUNT_KEY``
from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/sync/test_none_options.py -v
"""
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        # Key client owns the database and container; the data client does
        # item work, as in the original.
        self.key_client = create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_ri_none_opts_" + uuid.uuid4().hex
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = self.key_client.create_database(self._db_id)
        self.addCleanup(self.key_client.delete_database, self._db_id)
        print(f"\nOwned read-test database: {self._db_id}")
        key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(self._db_id).get_container_client(self._container_id)

    def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(
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

    def test_container_read_item_none_options_rust(self):
        """read_item accepts None for every optional argument.

        None means "not supplied". Customers commonly build one call site
        that passes every option through from their own config, leaving most
        of them None, so each must behave as if it had been omitted: no
        header, no error, and the item comes back unchanged.

        The options covered are session_token,
        initial_headers, max_integrated_cache_staleness_in_ms, priority and
        throughput_bucket.
        """
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_read_item_none_options
        item = self._create_sample_item()
        read_back = self.container.read_item(
            item["id"],
            partition_key=item["pk"],
            session_token=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            priority=None,
            throughput_bucket=None,
        )
        assert read_back["id"] == item["id"]
