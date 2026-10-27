# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original replacement-header and persisted-throughput assertions."""

import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosEmulator
class TestCosmosResponses(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.database_id = "get_db_response_" + uuid.uuid4().hex
        self.addCleanup(self.client.close)

    def test_database_replace_throughput_rust(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_database_replace_throughput
        db = self.client.create_database(id=self.database_id, offer_throughput=400)
        self.addCleanup(self.client.delete_database, db.id)
        replace_throughput_value = 500
        first_response = db.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        assert replace_throughput_value == db.get_throughput().offer_throughput

    def test_container_replace_throughput_rust(self):
        # Source: tests/test_cosmos_responses.py::TestCosmosResponses.test_container_replace_throughput
        db = self.client.create_database(self.database_id)
        self.addCleanup(self.client.delete_database, db.id)
        container = db.create_container(
            id="responses_test", partition_key=PartitionKey(path="/company"), offer_throughput=400,
        )
        replace_throughput_value = 500
        first_response = container.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        assert replace_throughput_value == container.get_throughput().offer_throughput
