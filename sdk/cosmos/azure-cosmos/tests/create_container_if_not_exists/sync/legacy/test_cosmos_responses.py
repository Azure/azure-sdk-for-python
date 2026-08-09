# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 create-container-if-not-exists checks, re-run on the rust engine.

Why this file exists: ``create_container_if_not_exists`` has two legs. If the
container is not there it creates it; if it is already there it reads it and
returns that instead. Startup code calls this on every process start, so the
second leg runs far more often than the first, and both have to return the same
shape. With ``return_properties`` set the call returns a pair whose second half
carries the response headers -- that is where a customer reads how many request
units the call cost, and the number differs between the two legs.

What it does: two real v4 tests copied from
``tests/test_cosmos_responses.py``, changed in one place -- the client is built
with ``_backend="rust"``. ``test_create_container_if_not_exists_headers`` uses
a fresh id, so it takes the create leg.
``test_create_container_if_not_exists_headers_negative`` calls twice with the
same fixed id, so the second call takes the read leg, and checks that call's
headers are not empty.

This is NOT the side-by-side comparison. The comparison tests
(``create_container_if_not_exists/sync/test_create_container_if_not_exists_parity.py``)
run the same call on both engines and diff the results. This file runs on rust
only and reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so the fixed id
``responses_test`` cannot collide with a container another test left behind.
The class name and method names match the source, so the two test IDs differ
only by path.

Run with::

    pytest --noconftest tests/create_container_if_not_exists/sync/legacy/test_cosmos_responses.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCosmosResponses(unittest.TestCase):

    def setUp(self) -> None:
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._database_id = "cc_if_not_exists_responses_" + str(uuid.uuid4())
        self.test_database = self.client.create_database(self._database_id)

    def tearDown(self) -> None:
        try:
            self.client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        self.client.close()

    def test_create_container_if_not_exists_headers(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_container_if_not_exists_headers
        first_response = self.test_database.create_container_if_not_exists(
            id="responses_test" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    def test_create_container_if_not_exists_headers_negative(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_create_container_if_not_exists_headers_negative
        first_response = self.test_database.create_container_if_not_exists(
            id="responses_test",
            partition_key=PartitionKey(path="/company"), return_properties=True)
        second_response = self.test_database.create_container_if_not_exists(
            id="responses_test",
            partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0


if __name__ == "__main__":
    unittest.main()
