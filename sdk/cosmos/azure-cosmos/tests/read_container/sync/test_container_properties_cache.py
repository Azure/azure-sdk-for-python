# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's cache-versus-fresh-read assertions on Rust."""

import uuid

import pytest
from azure.core import MatchConditions
from azure.cosmos import PartitionKey, exceptions
from read_container._container_setup import SyncContainerReadCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(SyncContainerReadCase):
    def setUp(self):
        super().setUp()
        self.databaseForTest = self.data_db

    def test_container_properties_cache_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_properties_cache
        client = self.client
        database_name = self.configs.TEST_DATABASE_ID
        created_db = self.databaseForTest
        container_name = "Container Properties Cache Test " + str(uuid.uuid4())
        container_pk = "PK"
        try:
            self._create_container_for_test(id=container_name, partition_key=PartitionKey(path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        client.client_connection._CosmosClientConnection__container_properties_cache = {}
        self.assertTrue(client.client_connection._container_properties_cache == {})
        client.get_database_client(database_name).get_container_client(container_name).create_item(
            body={'id': 'item1', container_pk: 'value'})
        # Rust adaptation: item creation no longer warms Python's metadata cache.
        created_db.get_container_client(container_name)._get_properties()
        self.assertTrue(client.client_connection._container_properties_cache != {})
        cached_properties = created_db.get_container_client(container_name)._get_properties()
        fresh_container_read = created_db.get_container_client(container_name).read()
        self.assertEqual(cached_properties.get("_rid"), fresh_container_read.get("_rid"))
        self.assertEqual(cached_properties.get("partitionKey"), fresh_container_read.get("partitionKey"))
        self._delete_container_for_test(container_name)

    def test_not_modified_read_preserves_properties_cache_rust(self):
        # Source: (new) Conditional reads preserve warm or absent container properties.
        container_name = "conditional-read-" + str(uuid.uuid4())
        self._create_container_for_test(id=container_name, partition_key=PartitionKey(path="/pk"))
        container = self.data_db.get_container_client(container_name)
        properties = container.read()
        cache = self.client.client_connection._container_properties_cache
        cached = cache[container.container_link]

        for warm_cache in (True, False):
            if not warm_cache:
                del cache[container.container_link]
            result = container.read(etag=properties["_etag"], match_condition=MatchConditions.IfModified)
            assert result == {}
            assert result.get_response_headers()["etag"] == properties["_etag"]
            if warm_cache:
                assert cache[container.container_link] is cached
            else:
                assert container.container_link not in cache
            refreshed = container._get_properties()
            assert refreshed["_rid"] == properties["_rid"]
            assert refreshed["partitionKey"] == properties["partitionKey"]
