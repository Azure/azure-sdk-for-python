# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_container_create_item_none_options`` test against the
``_backend="rust"`` path.

Self-contained: a key client builds its own database + container in
``setUp`` and registers cleanup after acquisition, including on setup
failure. The data client (AAD in AAD lanes) does the item work, as in the
source. The class name and method name match the
source (apart from the method's ``_rust`` suffix) at ``tests/test_none_options.py`` so
test IDs differ by path and method suffix.

Run with::

    pytest --noconftest tests/create_item/sync/test_none_options.py -v
"""
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = create_setup_client(_backend="rust")
        self.addCleanup(self.key_client.close)
        self.client = create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "legacy_none_options_" + uuid.uuid4().hex
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = self.key_client.create_database(self._db_id)
        self.addCleanup(self.key_client.delete_database, self._db_id)
        key_database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        self.database = self.client.get_database_client(self._db_id)
        self.container = self.database.get_container_client(self._container_id)

    def test_container_create_item_none_options_rust(self):
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_create_item_none_options
        # The source also passes pre_trigger_include=None and
        # post_trigger_include=None. The Rust path rejects trigger arguments
        # even when they are None (triggers are out of scope),
        # so they are left out here.
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = self.container.create_item(
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
        assert created["id"] == item["id"]
