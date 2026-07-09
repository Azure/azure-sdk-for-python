# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_container_query_items_none_options_partition`` test against the
``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source at ``tests/test_none_options.py`` so test IDs differ only by
path.

Run with::

    pytest --noconftest tests/query_items/sync/legacy/test_none_options.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_query_none_options_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.container = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def test_container_query_items_none_options_partition(self):
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_query_items_none_options_partition
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(item)
        pager = self.container.query_items(
            "SELECT * FROM c",
            continuation_token_limit=None,
            enable_scan_in_query=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            max_item_count=None,
            parameters=None,
            partition_key=None,
            populate_index_metrics=None,
            populate_query_advice=None,
            populate_query_metrics=None,
            priority=None,
            response_hook=None,
            session_token=None,
            throughput_bucket=None,
            enable_cross_partition_query=True,
        )
        items = list(pager)
        assert len(items) >= 1

