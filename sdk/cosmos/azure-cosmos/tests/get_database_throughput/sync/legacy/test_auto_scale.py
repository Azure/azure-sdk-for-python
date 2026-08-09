# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 autoscale-database check, re-run on the rust engine.

Why this file exists: a database's throughput can be a fixed number of RU/s, or
it can be an autoscale setting -- a ceiling the service is allowed to scale up
to, plus the percentage step it grows by. Those two settings do not travel in
the same field as a fixed RU/s number: reading them back returns
``auto_scale_max_throughput`` and ``auto_scale_increment_percent`` while
``offer_throughput`` stays empty. The test in ``test_crud_database.py`` only
covers the fixed-number shape, so without this file the autoscale shape of the
read would be untested on rust, and rust could report a fixed number where the
customer configured a ceiling.

What it does: the real v4 test copied from ``tests/test_auto_scale.py``,
changed in one place -- the client is built with ``_backend="rust"``. It
creates a database with a 5000 RU/s ceiling growing in 2% steps, reads the
setting back and checks both values, then does the same through
``create_database_if_not_exists`` with a 9000 ceiling and 11% steps.

This is NOT the side-by-side comparison. The comparison tests
(``get_database_throughput/sync/test_get_database_throughput_parity.py``) run
the same call on both engines and diff the numbers. This file runs on rust only.

Self-contained: it creates and deletes its own databases.

Run with::

    pytest --noconftest tests/get_database_throughput/sync/legacy/test_auto_scale.py -v
"""
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


@pytest.mark.cosmosEmulator
class TestAutoScale(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")

    def tearDown(self) -> None:
        self.key_client.close()

    def test_autoscale_create_database(self):
        # Source: tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_database
        database_id = "db_auto_scale_" + str(uuid.uuid4())
        try:
            # Testing auto_scale_settings for the create_database method
            created_database = self.key_client.create_database(database_id, offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=2))
            created_db_properties = created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 5000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 2

            self.key_client.delete_database(created_database.id)

            # Testing auto_scale_settings for the create_database_if_not_exists method
            database_id = "db_auto_scale_2_" + str(uuid.uuid4())
            created_database = self.key_client.create_database_if_not_exists(database_id,
                                                                             offer_throughput=ThroughputProperties(
                                                                                 auto_scale_max_throughput=9000,
                                                                                 auto_scale_increment_percent=11))
            created_db_properties = created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 9000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 11
        finally:
            self.key_client.delete_database(database_id)


if __name__ == "__main__":
    unittest.main()
