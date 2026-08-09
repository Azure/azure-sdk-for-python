# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async create-container return-shape checks, re-run on the rust engine.

Why this file exists: the async client is a separate code path from the sync
client, so it has to be proved separately. ``create_container`` returns two
different things depending on one argument. By default it returns a
``ContainerProxy`` -- the object you go on to read and write items through.
With ``return_properties`` set, it returns a pair, and the second half of that
pair carries the response headers, which is where a customer reads how many
request units the create cost. Code written against either shape breaks if the
other one comes back.

What it does: two real v4 tests copied from
``tests/test_cosmos_responses_async.py``, changed in one place -- the client is
built with ``_backend="rust"``. ``test_create_container_headers_async`` asks
for properties and checks the headers are not empty.
``test_create_container_returns_container_proxy_async`` does not ask, and
checks a ``ContainerProxy`` came back.

This is NOT the side-by-side comparison. The comparison tests
(``create_container/aio/test_create_container_parity_async.py``) run the same
call on both engines and diff the results. This file runs on rust only and
reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The class name and method names match the source, so the
two test IDs differ only by path. The file name drops the ``_async`` suffix
because the audit reporter pairs sync and async copies by stripping it.

Run with::

    pytest --noconftest tests/create_container/aio/legacy/test_cosmos_responses.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient, ContainerProxy
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCosmosResponsesAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._database_id = "create_container_responses_async_" + str(uuid.uuid4())
        self.test_database = await self.client.create_database(self._database_id)

    async def asyncTearDown(self) -> None:
        try:
            await self.client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_create_container_headers_async(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_container_headers_async
        first_response = await self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                                   partition_key=PartitionKey(path="/company"),
                                                                   return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    async def test_create_container_returns_container_proxy_async(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_container_returns_container_proxy_async
        first_response = await self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                                   partition_key=PartitionKey(path="/company"))
        assert isinstance(first_response, ContainerProxy)


if __name__ == "__main__":
    unittest.main()
