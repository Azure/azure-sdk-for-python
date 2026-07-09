# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_get_feed_ranges`` test against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and
deletes them in ``tearDown``. The class name and method name match the
source at ``tests/test_change_feed.py`` so test IDs differ only by path.

Run with::

    pytest --noconftest tests/read_feed_ranges/sync/legacy/test_change_feed.py -v
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
class TestChangeFeed(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_change_feed_" + uuid.uuid4().hex[:8]
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

    def test_get_feed_ranges(self):
        # Source: tests/test_change_feed.py::TestChangeFeed.test_get_feed_ranges
        result = list(self.container.read_feed_ranges())
        assert len(result) == 1
