# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync etag/match-condition compatibility test that upserts items, re-run on the Rust path.

Source: ``tests/test_backwards_compatibility.py::TestBackwardsCompatibility``.
The method keeps the original steps and assertions; only setup changed. Both
clients use ``_backend="rust"``: a key-authenticated client owns a uniquely
named database (deleted afterwards) in place of the shared test database, and
a data client runs the item operations, like the original key/data client
pair. Databases the test creates itself are also deleted if it fails early.
"""

import unittest
import uuid

import pytest

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError
from config import clients
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):
    databaseForTest: DatabaseProxy = None
    client: CosmosClient = None
    containerForTest: ContainerProxy = None
    host = TestSettings.host
    masterKey = TestSettings.masterKey

    populate_true = True

    def setUp(self):
        self._owned_database_ids = []
        self.client = CosmosClient(self.host, self.masterKey, _backend="rust")
        self.addCleanup(self.client.close)
        self.addCleanup(self._delete_owned_databases)
        self.TEST_DATABASE_ID = self._unique_database_id("backcompat_db")
        self.databaseForTest = self.client.create_database(self.TEST_DATABASE_ID)
        self.data_client = clients.create_data_client(_backend="rust")
        self.addCleanup(self.data_client.close)
        self.data_database = self.data_client.get_database_client(self.TEST_DATABASE_ID)

    def _unique_database_id(self, label):
        database_id = unique_database_id("upsert_item_" + label)
        self._owned_database_ids.append(database_id)
        return database_id

    def _delete_owned_databases(self):
        for database_id in self._owned_database_ids:
            try:
                self.client.delete_database(database_id)
            except CosmosResourceNotFoundError:
                pass

    @pytest.mark.skip(reason="accepted-vnext-change: create_database() now rejects etag/match_condition "
                             "with TypeError on both backends (docs/api-review.md create_database proposal); the "
                             "legacy original fails the same way at its first step.")
    def test_etag_match_condition_compatibility_rust(self):
        # Source: tests/test_backwards_compatibility.py::TestBackwardsCompatibility.test_etag_match_condition_compatibility
        # Verifying that behavior is unaffected across the board for using `etag`/`match_condition` on irrelevant methods
        # Database
        database = self.client.create_database(self._unique_database_id("backcompat"), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert database is not None
        database2 = self.client.create_database_if_not_exists(self._unique_database_id("backcompat"), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert database2 is not None
        self.client.delete_database(database2.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = self.databaseForTest.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                              etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert container is not None
        container2 = self.databaseForTest.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                                             etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert container2 is not None
        container2_read = container2.read()
        assert container2_read is not None
        replace_container = self.databaseForTest.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30,
                                                       etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        replace_container_read = replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        self.databaseForTest.delete_container(replace_container.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Item - data-plane operations use AAD client
        data_container = self.data_database.get_container_client(container.id)
        item = data_container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert item is not None
        item2 = data_container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()),
                                     match_condition=MatchConditions.IfNotModified)
        assert item2 is not None
        item = data_container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item is not None
        item2 = data_container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item2 is not None
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 0},)),
            ("replace", (item2['id'], {"id": str(uuid.uuid4()), "pk": 0})),
            ("read", (item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 0},)),
        ]
        batch_results = data_container.execute_item_batch(batch_operations, partition_key=0, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert len(batch_results) == 4
        for result in batch_results:
            assert result['statusCode'] in (200, 201)

        self.client.delete_database(database.id)

if __name__ == "__main__":
    unittest.main()
