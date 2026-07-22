# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Selected sync autoscale database test pinned to the Rust backend."""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, ThroughputProperties


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosLong
class TestAutoScale(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.key_client = CosmosClient(HOST, KEY, _backend="rust")

    @classmethod
    def tearDownClass(cls):
        cls.key_client.close()

    def test_autoscale_create_database(self):
        # Source: tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_database
        database_id = "db_auto_scale_" + str(uuid.uuid4())
        try:
            created_database = self.key_client.create_database(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=5000,
                    auto_scale_increment_percent=2,
                ),
            )
            created_db_properties = created_database.get_throughput()
            assert created_db_properties.auto_scale_max_throughput == 5000
            assert created_db_properties.auto_scale_increment_percent == 2

            self.key_client.delete_database(created_database.id)

            database_id = "db_auto_scale_2_" + str(uuid.uuid4())
            created_database = self.key_client.create_database_if_not_exists(
                database_id,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=9000,
                    auto_scale_increment_percent=11,
                ),
            )
            created_db_properties = created_database.get_throughput()
            assert created_db_properties.auto_scale_max_throughput == 9000
            assert created_db_properties.auto_scale_increment_percent == 11
        finally:
            self.key_client.delete_database(database_id)
