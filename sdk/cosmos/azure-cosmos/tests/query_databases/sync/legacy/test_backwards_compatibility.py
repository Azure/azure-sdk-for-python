# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Selected v4 session-token compatibility test pinned to the Rust backend.

Original: tests/test_backwards_compatibility.py
Copy:     tests/query_databases/sync/legacy/test_backwards_compatibility.py
"""

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):
    configs = test_config.TestConfig

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.configs.host, cls.configs.masterKey, _backend="rust")
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.data_client = cls.configs.create_data_client()
        cls.data_database = cls.data_client.get_database_client(cls.configs.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.data_client.close()

    def test_session_token_compatibility(self):
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_session_token_compatibility
        # Verifying that behavior is unaffected across the board for using `session_token` on irrelevant methods
        # Database
        database = self.client.create_database(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database is not None
        database2 = self.client.create_database_if_not_exists(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database2 is not None
        database_list = list(self.client.list_databases(session_token=str(uuid.uuid4())))
        database_list2 = list(self.client.query_databases(query="select * from c", session_token=str(uuid.uuid4())))
        assert len(database_list) > 0
        assert len(database_list2) > 0
        database_read = database.read(session_token=str(uuid.uuid4()))
        assert database_read is not None
        self.client.delete_database(database2.id, session_token=str(uuid.uuid4()))
        try:
            database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = self.databaseForTest.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container is not None
        container2 = self.databaseForTest.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container2 is not None
        container_list = list(self.databaseForTest.list_containers(session_token=str(uuid.uuid4())))
        container_list2 = list(self.databaseForTest.query_containers(query="select * from c", session_token=str(uuid.uuid4())))
        assert len(container_list) > 0
        assert len(container_list2) > 0
        container2_read = container2.read(session_token=str(uuid.uuid4()))
        assert container2_read is not None
        replace_container = self.databaseForTest.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30, session_token=str(uuid.uuid4()))
        replace_container_read = replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        self.databaseForTest.delete_container(replace_container.id, session_token=str(uuid.uuid4()))
        try:
            container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        self.client.delete_database(database.id)
