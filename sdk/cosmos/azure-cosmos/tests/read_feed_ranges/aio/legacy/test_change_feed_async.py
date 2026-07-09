# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_get_feed_ranges`` test against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``asyncSetUp`` and
deletes them in ``asyncTearDown``. The class name and method name match the
source at ``tests/test_change_feed_async.py`` so test IDs differ only by path.

Run with::

    pytest --noconftest tests/read_feed_ranges/aio/legacy/test_change_feed_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestChangeFeedAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_change_feed_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_get_feed_ranges(self):
        # Source: tests/test_change_feed_async.py::TestChangeFeedAsync.test_get_feed_ranges
        result = [feed_range async for feed_range in self.container.read_feed_ranges()]
        assert len(result) == 1
