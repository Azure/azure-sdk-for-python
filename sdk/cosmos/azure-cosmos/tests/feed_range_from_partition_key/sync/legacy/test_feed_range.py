# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_partition_key_to_feed_range`` test against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and deletes them in
``tearDown``. The class name and method name match the source at ``tests/test_feed_range.py``
so test IDs differ only by path.

This is layer 3 of a three-layer defense (unit -> emulator parity -> legacy snapshot).
The parity suite only proves the two backends agree with each other; if both drifted the
same way they would still pass while the value is wrong. This test pins the feed range for
a known key to a hard-coded expected value, so an absolute regression is caught even when
the backends match.

Run with::

    pytest --noconftest tests/feed_range_from_partition_key/sync/legacy/test_feed_range.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestFeedRange(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_feed_range_pk_sync_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.container = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/id"),
        )

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def test_partition_key_to_feed_range(self):
        # Source: tests/test_feed_range.py::TestFeedRange.test_partition_key_to_feed_range
        feed_range = self.container.feed_range_from_partition_key("1")
        feed_range_epk = FeedRangeInternalEpk.from_json(feed_range)
        expected_range = Range(
            "3C80B1B7310BB39F29CC4EA05BDD461E",
            "3c80b1b7310bb39f29cc4ea05bdd461f",
            True,
            False,
        )
        self.assertEqual(feed_range_epk.get_normalized_range(), expected_range)

    def test_feed_range_is_subset_from_pk(self):
        # Source: tests/test_feed_range.py::TestFeedRange.test_feed_range_is_subset_from_pk
        parent_feed_range = FeedRangeInternalEpk(Range("", "FF", True, False)).to_dict()
        child_feed_range = self.container.feed_range_from_partition_key("1")
        self.assertTrue(self.container.is_feed_range_subset(parent_feed_range, child_feed_range))
