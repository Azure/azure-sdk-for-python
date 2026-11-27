# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's async cache-versus-fresh-read assertions on Rust."""

import uuid

import pytest
from azure.core import MatchConditions
from azure.cosmos import PartitionKey, exceptions
from read_container._container_setup import AsyncContainerReadCase


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(AsyncContainerReadCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.databaseForTest = self.data_db

    async def test_container_properties_cache_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_properties_cache_async
        client = self.client
        database_name = self.configs.TEST_DATABASE_ID
        created_db = self.databaseForTest
        container_name = "Container Properties Cache Test " + str(uuid.uuid4())
        container_pk = "PK"
        try:
            await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        client.client_connection._CosmosClientConnection__container_properties_cache = {}
        assert client.client_connection._container_properties_cache == {}
        await client.get_database_client(database_name).get_container_client(container_name).create_item(
            body={'id': 'item1', container_pk: 'value'})
        # Rust adaptation: item creation no longer warms Python's metadata cache.
        await created_db.get_container_client(container_name)._get_properties()
        assert client.client_connection._container_properties_cache != {}
        cached_properties = await created_db.get_container_client(container_name)._get_properties()
        fresh_container_read = await created_db.get_container_client(container_name).read()
        assert cached_properties.get("_rid") == fresh_container_read.get("_rid")
        assert cached_properties.get("partitionKey") == fresh_container_read.get("partitionKey")
        await self._delete_container_for_test_async(container_name)

    async def test_not_modified_read_preserves_properties_cache_async_rust(self):
        # Source: (new) Conditional reads preserve warm or absent container properties.
        container_name = "conditional-read-" + str(uuid.uuid4())
        await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(path="/pk"))
        container = self.data_db.get_container_client(container_name)
        properties = await container.read()
        cache = self.client.client_connection._container_properties_cache
        cached = cache[container.container_link]

        for warm_cache in (True, False):
            if not warm_cache:
                del cache[container.container_link]
            result = await container.read(etag=properties["_etag"], match_condition=MatchConditions.IfModified)
            assert result == {}
            assert result.get_response_headers()["etag"] == properties["_etag"]
            if warm_cache:
                assert cache[container.container_link] is cached
            else:
                assert container.container_link not in cache
            refreshed = await container._get_properties()
            assert refreshed["_rid"] == properties["_rid"]
            assert refreshed["partitionKey"] == properties["partitionKey"]
