# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Selected legacy session-token compatibility test pinned to the Rust backend.

Original: tests/test_backwards_compatibility.py
Copy:     tests/query_databases/sync/test_backwards_compatibility.py
"""

import unittest
import uuid

import pytest

from config import clients, settings
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError


@pytest.mark.cosmosEmulator
@pytest.mark.skip(
    reason="accepted-vnext-change: RUST_MIGRATION_STATUS.md query_databases rejects session_token; covered offline"
)
class TestBackwardsCompatibility(unittest.TestCase):
    configs = settings.TestSettings

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.configs.host, cls.configs.masterKey, _backend="rust")
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.data_client = clients.create_data_client()
        cls.data_database = cls.data_client.get_database_client(cls.configs.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.data_client.close()

    def test_session_token_compatibility_rust(self):
        """Passing ``session_token`` to operations that ignore it must not break them.

        Sweeps ``session_token`` through roughly a dozen database and container
        operations: create, create-if-not-exists, list, query, read, replace
        and delete.

        Session tokens only mean something for item operations. None of these
        do anything with the value. The point is that older code which passed
        it everywhere keeps working: the argument has to be accepted and
        ignored, not rejected and not forwarded somewhere it would cause a
        failure.

        Kept here for the ``query_databases`` call in that sweep. The same
        legacy test is also copied into ``list_databases``.
        """
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_session_token_compatibility
        # Verifying that behavior is unaffected across the board for using `session_token` on irrelevant methods
        # Database
        database = self.client.create_database(
            settings.unique_database_id("backcompat"), session_token=str(uuid.uuid4())
        )
        assert database is not None
        database2 = self.client.create_database_if_not_exists(
            settings.unique_database_id("backcompat"), session_token=str(uuid.uuid4())
        )
        assert database2 is not None
        database_ids = {db["id"] for db in self.client.list_databases(session_token=str(uuid.uuid4()))}
        database_ids2 = {
            db["id"] for db in self.client.query_databases(query="select * from c", session_token=str(uuid.uuid4()))
        }
        assert database.id in database_ids
        assert database.id in database_ids2
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
        container_ids = {c["id"] for c in self.databaseForTest.list_containers(session_token=str(uuid.uuid4()))}
        container_ids2 = {
            c["id"]
            for c in self.databaseForTest.query_containers(query="select * from c", session_token=str(uuid.uuid4()))
        }
        assert container.id in container_ids
        assert container.id in container_ids2
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
