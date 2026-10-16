# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected async database response tests pinned to the Rust backend."""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from azure.cosmos.aio._database import DatabaseProxy


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCosmosResponsesAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self.addAsyncCleanup(self.client.close)

    async def test_create_database_headers_async(self):
        """With ``return_properties=True``, the response headers come back populated.

        The second half of the returned pair is what a customer reads the
        request unit charge from, so it must not be empty.
        """
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_database_headers_async
        database_id = "responses_test" + str(uuid.uuid4())
        self.addAsyncCleanup(self.client.delete_database, database_id)
        first_response = await self.client.create_database(id=database_id, return_properties=True)

        assert len(first_response[1].get_response_headers()) > 0

    async def test_create_database_returns_database_proxy_async(self):
        """Without ``return_properties``, the plain ``DatabaseProxy`` comes back.

        This is the default and by far the common case: callers chain straight
        into creating containers. Returning the pair here instead would break
        every existing caller.
        """
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_create_database_returns_database_proxy_async
        database_id = "responses_test" + str(uuid.uuid4())
        self.addAsyncCleanup(self.client.delete_database, database_id)
        first_response = await self.client.create_database(id=database_id)
        assert isinstance(first_response, DatabaseProxy)
