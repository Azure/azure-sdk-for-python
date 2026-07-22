# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected sync database response tests pinned to the Rust backend."""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.database import DatabaseProxy


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

    def test_create_database_headers(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_headers
        database_id = "responses_test" + str(uuid.uuid4())
        self.addCleanup(self.client.delete_database, database_id)
        first_response = self.client.create_database(id=database_id, return_properties=True)

        assert len(first_response[1].get_response_headers()) > 0

    def test_create_database_returns_database_proxy(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_returns_database_proxy
        database_id = "responses_test" + str(uuid.uuid4())
        self.addCleanup(self.client.delete_database, database_id)
        first_response = self.client.create_database(id=database_id)
        assert isinstance(first_response, DatabaseProxy)
