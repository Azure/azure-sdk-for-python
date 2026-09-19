# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing legacy async create-container-if-not-exists checks, re-run on the Rust engine.

Why this file exists: the async client is a separate code path from the sync
client, so it has to be proved separately. ``create_container_if_not_exists``
has two legs. If the container is not there it creates it; if it is already
there it reads it and returns that instead. Startup code calls this on every
process start, so the second leg runs far more often than the first, and both
have to return the same shape. With ``return_properties`` set the call returns
a pair whose second half carries the response headers -- that is where a
customer reads how many request units the call cost, and the number differs
between the two legs.

What it does: two real legacy tests copied from
``tests/test_cosmos_responses_async.py``, changed in one place -- the client is
built with ``_backend="rust"``.
``test_create_container_if_not_exists_headers_async`` uses a fresh id, so it
takes the create leg.
``test_create_container_if_not_exists_headers_negative_async`` calls twice with
the same fixed id, so the second call takes the read leg, and checks that
call's headers are not empty.

This is NOT the side-by-side comparison. The comparison tests
(``create_container_if_not_exists/aio/test_create_container_if_not_exists_parity_async.py``)
run the same call on both engines and diff the results. This file runs on Rust
only and reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so the fixed id
``responses_test1`` cannot collide with a container another test left behind.
The class name and method names match the source, so the two test IDs differ
only by path. The file name drops the ``_async`` suffix because the audit
reporter pairs sync and async copies by stripping it.

Run with::

    pytest --noconftest tests/create_container_if_not_exists/aio/legacy/test_cosmos_responses.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
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
        self._database_id = "cc_if_not_exists_responses_async_" + str(uuid.uuid4())
        self.test_database = await self.client.create_database(self._database_id)

    async def asyncTearDown(self) -> None:
        try:
            await self.client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.client.close()

    async def test_create_container_if_not_exists_headers_async(self):
        """First call creates the container and returns populated headers.

        This is the create branch: nothing exists yet, so the call really does
        create. The headers carry the request unit charge.
        """
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_container_if_not_exists_headers_async
        first_response = await self.test_database.create_container_if_not_exists(
            id="responses_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    async def test_create_container_if_not_exists_headers_negative_async(self):
        """Second call finds the container already there and still returns headers.

        Despite the name, nothing fails here. "Negative" means the create was
        skipped: the same id is requested twice, so the second call takes the
        already-exists branch and reads the container instead of creating it.

        That branch is a different code path with a different response, and it
        is the one at risk of coming back with empty headers. A customer
        reading the request unit charge must get a value either way.
        """
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_container_if_not_exists_headers_negative_async
        first_response = await self.test_database.create_container_if_not_exists(
            id="responses_test1",
            partition_key=PartitionKey(path="/company"), return_properties=True)
        second_response = await self.test_database.create_container_if_not_exists(
            id="responses_test1",
            partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0


if __name__ == "__main__":
    unittest.main()
