# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_container_read_all_items_none_options`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source (apart from the method's ``_rust`` suffix) at ``tests/test_none_options.py`` so
test IDs differ by path and method suffix.

Run with::

    pytest --noconftest tests/read_all_items/sync/test_none_options.py -v
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
        self.key_client = create_setup_client(_backend="rust", timeout=30)
        self.client = create_data_client(_backend="rust", timeout=30)
        self._db_id = "rust_read_all_none_opts_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = self.key_client.create_database(self._db_id)
        key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.container = self.client.get_database_client(
            self._db_id
        ).get_container_client(self._container_id)

    def tearDown(self) -> None:
        try:
            self.key_client.delete_database(self._db_id)
        finally:
            self.client.close()
            self.key_client.close()

    def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(item)
        return item

    def test_container_read_all_items_none_options_rust(self):
        """read_all_items accepts None for every optional argument.

        None means "not supplied". Customers commonly build one call site that
        passes every option through from their own config, leaving most of
        them None, so each must behave as if it had been omitted: no header,
        no error, and the container enumerates normally.

        The options covered are max_item_count, session_token,
        initial_headers, max_integrated_cache_staleness_in_ms, priority and
        throughput_bucket.

        This runs against a real account on the Rust driver, so it also proves
        the whole-container read still works on the fast path.
        """
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_read_all_items_none_options
        self._create_sample_item()
        pager = self.container.read_all_items(
            max_item_count=None,
            session_token=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            priority=None,
            throughput_bucket=None,
        )
        items = list(pager)
        assert len(items) >= 1
