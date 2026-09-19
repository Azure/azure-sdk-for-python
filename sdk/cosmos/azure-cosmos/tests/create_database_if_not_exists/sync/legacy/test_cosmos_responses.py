# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Legacy response assertions using Rust transport."""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient


@pytest.mark.cosmosEmulator
class TestCosmosResponses(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust"
        )
        self.addCleanup(self.client.close)

    def test_create_database_if_not_exists_headers(self):
        """First call creates the database and returns its id with populated headers.

        This is the create branch: nothing exists yet. The returned properties
        must carry the id that was asked for, and the headers must hold the
        request unit charge.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_if_not_exists_headers
        database_id = "responses_test" + str(uuid.uuid4())
        first_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
        try:
            assert first_response[1]["id"] == database_id
            assert len(first_response[1].get_response_headers()) > 0
        finally:
            self.client.delete_database(database_id)

    def test_create_database_if_not_exists_headers_negative(self):
        """Calls against an existing database return that same database, with headers.

        Despite the name, nothing fails here. "Negative" means the create was
        skipped: the database is made up front, then asked for twice more.

        The strongest check is on ``_rid``, the resource id the service assigns
        at creation time. Both responses must carry the same ``_rid`` as the
        database created up front, which proves the existing database was
        handed back rather than a fresh one quietly created in its place. The
        id alone could not tell those two apart.

        Headers must still be populated on this branch, since it reads rather
        than creates and is the one more likely to return them empty.
        """
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_database_if_not_exists_headers_negative
        database_id = "responses_test" + str(uuid.uuid4())
        _, existing = self.client.create_database(id=database_id, return_properties=True)
        try:
            first_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
            second_response = self.client.create_database_if_not_exists(id=database_id, return_properties=True)
            assert first_response[1]["id"] == second_response[1]["id"] == database_id
            assert first_response[1]["_rid"] == second_response[1]["_rid"] == existing["_rid"]
            assert len(second_response[1].get_response_headers()) > 0
        finally:
            self.client.delete_database(database_id)
