# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected sync database response test pinned to the Rust backend.

An existing test from the main suite, re-run with the client forced onto the
rust engine. The main suite runs it on whichever engine is the default, so on
its own it would stop covering rust the moment that default changes.

What it protects: a customer calling ``db.read()`` gets a result they can pull
response headers off (``get_response_headers()``). Those headers carry the
request charge and the activity id -- what customers use to track cost and to
identify one request when opening a support case. An empty header map means the
call worked but is untraceable and its cost is invisible.
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCosmosResponses(unittest.TestCase):

    def setUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self.addCleanup(self.client.close)

    def test_database_read_headers(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_database_read_headers
        database_id = "responses_test" + str(uuid.uuid4())
        self.addCleanup(self.client.delete_database, database_id)
        db = self.client.create_database(id=database_id)
        first_response = db.read()
        assert len(first_response.get_response_headers()) > 0
