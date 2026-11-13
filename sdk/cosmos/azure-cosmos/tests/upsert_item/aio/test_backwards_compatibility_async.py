# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original async etag/match-condition compatibility test that upserts items, re-run on the Rust path.

Source: ``tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync``.
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
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceNotFoundError
from config import clients
from config.settings import TestSettings, unique_database_id


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibilityAsync(unittest.IsolatedAsyncioTestCase):
    host = TestSettings.host
    masterKey = TestSettings.masterKey

    client: CosmosClient = None
    created_database: DatabaseProxy = None

    async def asyncSetUp(self):
        self._owned_database_ids = []
        self.data_client = None
        # Key-auth client is used for control-plane operations in this test.
        self.client = CosmosClient(self.host, self.masterKey, _backend="rust")
        try:
            self.TEST_DATABASE_ID = self._unique_database_id("backcompat_db")
            self.created_database = await self.client.create_database(self.TEST_DATABASE_ID)
            # AAD (or key) client for data-plane operations
            self.data_client = clients.create_data_client_async(_backend="rust")
            self.data_database = self.data_client.get_database_client(self.TEST_DATABASE_ID)
        except BaseException:
            await self.asyncTearDown()
            raise

    async def asyncTearDown(self):
        try:
            for database_id in self._owned_database_ids:
                try:
                    await self.client.delete_database(database_id)
                except CosmosResourceNotFoundError:
                    pass
        finally:
            try:
                await self.client.close()
            finally:
                if self.data_client is not None:
                    await self.data_client.close()

    def _unique_database_id(self, label):
        database_id = unique_database_id("upsert_item_" + label)
        self._owned_database_ids.append(database_id)
        return database_id

    @pytest.mark.skip(reason="accepted-vnext-change: create_database() now rejects etag/match_condition "
                             "with TypeError on both backends (docs/api-review.md create_database proposal); the "
                             "legacy original fails the same way at its first step.")
    async def test_etag_match_condition_compatibility_async_rust(self):
        # Source: tests/test_backwards_compatibility_async.py::TestBackwardsCompatibilityAsync.test_etag_match_condition_compatibility_async
        # Verifying that behavior is unaffected across the board for using `etag`/`match_condition` on irrelevant methods
        # Database
        database = await self.client.create_database(self._unique_database_id("backcompat"), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert database is not None
        database2 = await self.client.create_database_if_not_exists(self._unique_database_id("backcompat"), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert database2 is not None
        await self.client.delete_database(database2.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            await database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = await self.created_database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                              etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert container is not None
        container2 = await self.created_database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                                             etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert container2 is not None
        container2_read = await container2.read()
        assert container2_read is not None
        replace_container = await self.created_database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30,
                                                       etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        replace_container_read = await replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        await self.created_database.delete_container(replace_container.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            await container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Item - data-plane operations use AAD client
        data_container = self.data_database.get_container_client(container.id)
        item = await data_container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert item is not None
        item2 = await data_container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()),
                                     match_condition=MatchConditions.IfNotModified)
        assert item2 is not None
        item = await data_container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item is not None
        item2 = await data_container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None,
                                            match_condition=None)
        assert item2 is not None
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 0},)),
            ("replace", (item2['id'], {"id": str(uuid.uuid4()), "pk": 0})),
            ("read", (item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 0},)),
        ]
        batch_results = await data_container.execute_item_batch(batch_operations, partition_key=0, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert len(batch_results) == 4
        for result in batch_results:
            assert result['statusCode'] in (200, 201)

        await self.client.delete_database(database.id)


if __name__ == '__main__':
    unittest.main()
