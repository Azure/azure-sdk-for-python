# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 replace-throughput checks (async), re-run on the rust engine.

Why this file exists: see the sync sibling
(``replace_throughput/sync/legacy/test_crud_container.py``). This is the async
surface of the same contract: a customer who changes throughput through the async
client must get the same applied RU/s back, and the same client-side guard when a
``ThroughputProperties`` mixes fixed and autoscale settings.

What it does: the real v4 async tests copied verbatim from
``tests/test_crud_container_async.py``, changed in exactly one place -- the client is
built with ``_backend="rust"`` -- so the same assertions run against the rust path.

This is NOT the side-by-side parity comparison; that lives in
``replace_throughput/aio/test_replace_throughput_parity_async.py``. This file runs on
rust only and reuses checks the team already trusts.

Self-contained: builds its own database + container in ``asyncSetUp`` and deletes
them in ``asyncTearDown``. The class name and method names match the source so the
two test IDs differ only by path. The container is created with dedicated throughput
because ``replace_throughput`` only has an offer to change when the container owns
one.

Run with::

    pytest --noconftest tests/replace_throughput/aio/legacy/test_crud_container_async.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import PartitionKey, ThroughputProperties
from azure.cosmos.aio import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Async surface of the v4 throughput-change checks on the rust engine (rust-only).

    Same intent as the sync ``TestCRUDContainerOperations``: build a fresh container
    at 400 RU/s, change its throughput through the async client, and confirm the
    change took -- the v4 assertions run with a ``_backend="rust"`` client. The
    core-python side is guaranteed by the originals in
    ``tests/test_crud_container_async.py``.
    """

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        await self.client.__aenter__()
        self._db_id = "legacy_replace_tp_async_" + uuid.uuid4().hex[:8]
        self._container_id = "c_" + uuid.uuid4().hex[:8]
        self.database = await self.client.create_database(self._db_id)
        self.container = await self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=400,
        )

    async def asyncTearDown(self):
        try:
            await self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_replace_throughput_offer_with_int(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_int
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500)
        await collection.replace_throughput(new_throughput.offer_throughput)

        retrieve_throughput = await collection.get_throughput()
        assert getattr(retrieve_throughput, "offer_throughput") == getattr(new_throughput, "offer_throughput")

    async def test_replace_throughput_offer_with_object(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_replace_throughput_offer_with_object
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500)
        await collection.replace_throughput(new_throughput)

        retrieve_throughput = await collection.get_throughput()
        assert getattr(retrieve_throughput, "offer_throughput") == getattr(new_throughput, "offer_throughput")

    async def test_negative_replace_throughput_with_all_configs_set(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_negative_replace_throughput_with_all_configs_set
        collection = self.container

        new_throughput = ThroughputProperties(offer_throughput=2500, auto_scale_max_throughput=4000, auto_scale_increment_percent=5)

        with pytest.raises(KeyError):
            await collection.replace_throughput(new_throughput)


if __name__ == "__main__":
    unittest.main()
