# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``is_feed_range_subset`` test against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``asyncSetUp`` and deletes
them in ``asyncTearDown``. The class name and method name match the source at
``tests/test_feed_range_async.py`` so test IDs differ only by path.

The parity suite only proves the two backends agree with each other; if both
drifted the same way they would still pass while the answer is wrong. This test
pins the async subset answer for a known feed-range pair, so an absolute
regression is caught even when the backends match.

Run with::

    pytest --noconftest tests/is_feed_range_subset/aio/legacy/test_feed_range_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestFeedRangeAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_is_feed_range_subset_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/id"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_feed_range_is_subset_from_pk_async(self):
        # Source: tests/test_feed_range_async.py::TestFeedRangeAsync.test_feed_range_is_subset_from_pk_async
        parent_feed_range = FeedRangeInternalEpk(Range("", "FF", True, False)).to_dict()
        child_feed_range = await self.container.feed_range_from_partition_key("1")
        self.assertTrue(await self.container.is_feed_range_subset(parent_feed_range, child_feed_range))
