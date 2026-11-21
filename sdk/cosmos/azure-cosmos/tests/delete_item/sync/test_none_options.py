# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_delete_item_none_options`` test against the
``_backend="rust"`` path.

Source: ``tests/test_none_options.py``. The class name and method name
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the two runs by
``(file basename, class name, method name)``. The other methods in the
source ``TestNoneOptions`` class cover ``create_item``, ``read_item``,
``upsert_item``, ``replace_item``, etc.; they belong to their own
operations' ``legacy/`` folders.

Self-contained: builds its own database + container through a key client in
``setUp`` and registers cleanup after acquisition, including on setup
failure. The tested operations run on the data client (AAD in the
cosmosAAD* lanes).

Run with::

    pytest --noconftest tests/delete_item/sync/test_none_options.py -v
"""
import unittest
import uuid

import pytest

from config.clients import create_data_client, create_setup_client

from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        self.key_client = create_setup_client()
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_delete_none_opts_" + uuid.uuid4().hex
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.key_database = self.key_client.create_database(self._db_id)
        self.addCleanup(self.key_client.delete_database, self._db_id)
        self.key_container = self.key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.database = self.client.get_database_client(self._db_id)
        self.container = self.database.get_container_client(self._container_id)

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

    def test_delete_item_none_options_rust(self):
        """Verify delete_item accepts None for every optional kwarg (session_token, initial_headers, etag, match_condition, priority, retry_write, throughput_bucket) and removes the item."""
        # Source: tests/test_none_options.py::TestNoneOptions.test_delete_item_none_options
        item = self._create_sample_item()
        before_delete = self.container.read_item(item["id"], partition_key=item["pk"])
        self.assertEqual({key: before_delete[key] for key in item}, item)
        self.container.delete_item(
            item["id"],
            partition_key=item["pk"],
            session_token=None,
            initial_headers=None,
            etag=None,
            match_condition=None,
            priority=None,
            retry_write=None,
            throughput_bucket=None,
        )
        with self.assertRaises(CosmosHttpResponseError) as caught:
            self.container.read_item(
                item["id"],
                partition_key=item["pk"],
                session_token=None,
                initial_headers=None,
                max_integrated_cache_staleness_in_ms=None,
                priority=None,
                throughput_bucket=None,
            )
        self.assertEqual(caught.exception.status_code, 404)
