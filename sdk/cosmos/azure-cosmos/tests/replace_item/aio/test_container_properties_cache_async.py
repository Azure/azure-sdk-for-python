# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async create/upsert/replace-after-container-recreation checks, on the Rust path.

The original saved a copy of the legacy Python container-properties cache
before recreating the container and restored it before each write. Rust keeps
container metadata inside the driver, so this copy gets the same stale state
from separate Rust clients that each loaded the old container's metadata
before the container was recreated; one is used per restore.
Each test owns a uniquely named database.
"""

from contextlib import AsyncExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database_async
from config import clients

from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.key_client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        await self.key_client.__aenter__()
        cleanup = AsyncExitStack()
        self.addAsyncCleanup(cleanup.aclose)
        database_id = "replace_recreate_async_" + uuid.uuid4().hex
        self.key_databaseForTest = await cleanup.enter_async_context(
            owned_database_async(self.key_client, database_id))
        self.client = clients.create_data_client_async()
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.databaseForTest = self.client.get_database_client(database_id)

    async def _create_container_for_test_async(self, *args, **kwargs):
        container_ref = await self.key_databaseForTest.create_container(*args, **kwargs)
        return self.databaseForTest.get_container_client(container_ref.id)

    async def _delete_container_for_test_async(self, *args, **kwargs):
        return await self.key_databaseForTest.delete_container(*args, **kwargs)

    async def _stale_databases(self, container_name, partition_key, count):
        """Rust data clients whose drivers hold the current container's metadata."""
        stale = []
        for _ in range(count):
            stale_client = clients.create_data_client_async()
            self.addAsyncCleanup(stale_client.close)
            await stale_client.__aenter__()
            database = stale_client.get_database_client(self.databaseForTest.id)
            # Any data-plane call resolves and caches the container definition in the driver.
            with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                await database.get_container_client(container_name).read_item(
                    "metadata-warmup-" + uuid.uuid4().hex, partition_key=partition_key)
            stale.append(database)
        return stale

    async def test_container_recreate_create_upsert_replace_item_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_create_upsert_replace_item_async
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        # This Simulates a container recreate. We save the old cache and then create
        # a new container with different partition key definition
        # for these three operations we extract the partition key value from the document
        # with a stale cache we end up extracting the wrong one so these will retry extracting
        # the partition key after refreshing the cache. Test to make sure a container recreate doesn't affect it.
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): one Rust
        # client per later restore, each holding the old container's metadata.
        old_cache = await self._stale_databases(container_name, "val", 4)
        await self._delete_container_for_test_async(container_name)
        try:
            await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # let's test create by replacing current container properties cache with old one
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The stale client extracts the key with the old /PK path and its refreshed retry keeps it, so this create, the upsert and the replace below fail with 400 instead of recovering.
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item1', container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Do the same thing for upsert operation
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).upsert_item(dict(id="item2", partkey="value"))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Finally test replace item
        item = await created_db.get_container_client(container_name).read_item("item1", partition_key="val")
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).replace_item(item=item, body={'id': 'item1',
                                                                                                container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).create_item(body={'id': 'item3', container_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
        await self._delete_container_for_test_async(container_name)

    async def test_container_recreate_create_upsert_replace_item_sub_partitioning_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_create_upsert_replace_item_sub_partitioning_async
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."

        # This Simulates a container recreate. We save the old cache and then create
        # a new container with different partition key definition
        # for these three operations we extract the partition key value from the document
        # with a stale cache we end up extracting the wrong one so these will retry extracting
        # the partition key after refreshing the cache. Test to make sure a container recreate doesn't affect it.
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): one Rust
        # client per later restore, each holding the old container's metadata.
        old_cache = await self._stale_databases(container_name, ["USA", "CA"], 4)
        await self._delete_container_for_test_async(container_name)
        try:
            await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # let's test create by replacing current container properties cache with old one
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The stale client extracts the key with the old /country,/state paths and its refreshed retry keeps it, so this create, the upsert and the replace below fail with 400 instead of recovering.
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Do the same thing for upsert operation
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).upsert_item(
                dict(id="item2", county='Santa Barbara', city='Santa Barbara'))
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Finally test replace item
        item = await created_db.get_container_client(container_name).read_item("item1",
                                                                               partition_key=['ventura', 'oxnard'])
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).replace_item(item=item,
                                                                               body={'id': 'item1', 'county': 'ventura',
                                                                                     'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        created_db = old_cache.pop(0)
        try:
            await created_db.get_container_client(container_name).create_item(
                body={'id': 'item3', 'country': 'USA', 'state': 'CA'})
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400, "Expected status code 400"
        await self._delete_container_for_test_async(container_name)
