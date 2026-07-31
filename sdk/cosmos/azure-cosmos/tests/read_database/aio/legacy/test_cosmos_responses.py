# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected async database response test pinned to the Rust backend.

Async twin of ``tests/read_database/sync/legacy/test_cosmos_responses.py``. Same
purpose: an existing test from the main suite, re-run with the client forced onto
the rust engine so it keeps covering rust regardless of which engine is the
default, and checking that a customer can still read response headers -- request
charge and activity id -- off the result of ``await db.read()``.
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos.aio import CosmosClient


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

    async def test_database_read_headers_async(self):
        # Source: tests/test_cosmos_responses_async.py::TestCosmosResponsesAsync.test_database_read_headers_async
        database_id = "responses_test" + str(uuid.uuid4())
        self.addAsyncCleanup(self.client.delete_database, database_id)
        db = await self.client.create_database(id=database_id)
        first_response = await db.read()
        assert len(first_response.get_response_headers()) > 0
