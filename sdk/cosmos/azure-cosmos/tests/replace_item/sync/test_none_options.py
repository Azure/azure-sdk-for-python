# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_replace_item_none_options`` on the ``_backend="rust"`` path.

Copied from ``tests/test_none_options.py``; the class and method names
match the source (apart from the method's ``_rust`` suffix) so the parity reporter can
pair the core-python and
Rust runs. Builds its own database + container through a key client; the
tested operations run on the data client (AAD in the cosmosAAD* lanes).
Registers cleanup after acquisition so partial setup still releases resources.

Run: ``pytest --noconftest tests/replace_item/sync/test_none_options.py -v``
"""
import unittest
import uuid

import pytest

from config.clients import create_data_client, create_setup_client

from azure.cosmos import PartitionKey


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        self.key_client = create_setup_client()
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_replace_none_opts_" + uuid.uuid4().hex
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

    def test_replace_item_none_options_rust(self):
        """Verify replace_item accepts None for every optional kwarg (session_token, initial_headers, etag, match_condition, priority, no_response, retry_write, throughput_bucket) and returns the replaced item."""
        # Source: tests/test_none_options.py::TestNoneOptions.test_replace_item_none_options
        item = self._create_sample_item()
        new_body = {"id": item["id"], "pk": item["pk"], "value": 999}
        replaced = self.container.replace_item(
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
