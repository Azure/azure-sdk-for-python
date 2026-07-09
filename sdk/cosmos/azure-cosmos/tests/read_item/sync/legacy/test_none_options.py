# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_container_read_item_none_options`` test against the
``_backend="rust"`` path.

Source: ``tests/test_none_options.py``. The class name and method name
match the source so the parity reporter can pair the two runs by
``(file basename, class name, method name)``. The other methods in the
source ``TestNoneOptions`` class cover ``create_item``, ``upsert_item``,
``replace_item``, etc.; they belong to their own operations' ``legacy/``
folders.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. Reads ``ACCOUNT_HOST`` and ``ACCOUNT_KEY``
from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/sync/legacy/test_none_options.py -v
"""
import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


class TestNoneOptions(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_ri_none_opts_" + uuid.uuid4().hex[:8]
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
            # Best-effort cleanup: the test has already produced its
            # verdict by the time tearDown runs, and a stuck account
            # state should not mask the test result.
            pass

    def _create_sample_item(self):
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(
            item, pre_trigger_include=None, post_trigger_include=None,
            indexing_directive=None, enable_automatic_id_generation=False,
            session_token=None, initial_headers=None, priority=None,
            no_response=None, retry_write=None, throughput_bucket=None,
        )
        return item

    def test_container_read_item_none_options(self):
        """Verify read_item accepts None for every optional kwarg (post_trigger_include, session_token, initial_headers, max_integrated_cache_staleness_in_ms, priority, throughput_bucket) and returns the item unchanged."""
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_read_item_none_options
        item = self._create_sample_item()
        read_back = self.container.read_item(
            item["id"], partition_key=item["pk"], post_trigger_include=None,
            session_token=None, initial_headers=None,
            max_integrated_cache_staleness_in_ms=None, priority=None,
            throughput_bucket=None,
        )
        assert read_back["id"] == item["id"]

