# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Sync ``test_replace_item_none_options`` on the ``_backend="rust"`` path.

Copied from ``tests/test_none_options.py``; the class and method names
match the source so the parity reporter can pair the core-python and
rust runs. Builds its own database + container and reads ``ACCOUNT_HOST``
/ ``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/replace_item/sync/legacy/test_none_options.py -v``
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

    def test_replace_item_none_options(self):
        """Verify replace_item accepts None for every optional kwarg (pre_trigger_include, post_trigger_include, session_token, initial_headers, etag, match_condition, priority, no_response, retry_write, throughput_bucket) and returns the replaced item."""
        # Source: tests/test_none_options.py::TestNoneOptions.test_replace_item_none_options
        item = self._create_sample_item()
        new_body = {"id": item["id"], "pk": item["pk"], "value": 999}
        replaced = self.container.replace_item(
            item["id"], new_body, pre_trigger_include=None,
            post_trigger_include=None, session_token=None,
            initial_headers=None, etag=None, match_condition=None,
            priority=None, no_response=None, retry_write=None,
            throughput_bucket=None,
        )
        assert replaced["value"] == 999

