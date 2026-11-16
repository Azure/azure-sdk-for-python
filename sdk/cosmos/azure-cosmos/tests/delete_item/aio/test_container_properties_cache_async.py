# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async delete-after-container-recreation checks, on the Rust path.

The original restored a stale copy of the legacy Python container-properties
cache before deleting. Rust keeps container metadata inside the driver, so
this copy gets the same stale state from a second Rust client that loaded the
old container's metadata before the container was recreated.
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
        database_id = "delete_recreate_async_" + uuid.uuid4().hex
        self.key_databaseForTest = await cleanup.enter_async_context(
            owned_database_async(self.key_client, database_id))
        self.client = clients.create_data_client_async()
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self.databaseForTest = self.client.get_database_client(database_id)
        # A second data client whose driver keeps the pre-recreation container metadata.
        self.stale_client = clients.create_data_client_async()
        self.addAsyncCleanup(self.stale_client.close)
        await self.stale_client.__aenter__()
        self.stale_databaseForTest = self.stale_client.get_database_client(database_id)

    async def _create_container_for_test_async(self, *args, **kwargs):
        container_ref = await self.key_databaseForTest.create_container(*args, **kwargs)
        return self.databaseForTest.get_container_client(container_ref.id)

    async def _delete_container_for_test_async(self, *args, **kwargs):
        return await self.key_databaseForTest.delete_container(*args, **kwargs)

    async def test_container_recreate_delete_item_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_delete_item_async
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Create items
        try:
            item_to_delete = await created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): load the
        # old container's metadata into a separate Rust driver, which recreation leaves stale.
        stale_container = self.stale_databaseForTest.get_container_client(container_name)
        await stale_container.read_item('item1', partition_key='val')
        await self._delete_container_for_test_async(created_container)
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). This client cached the old /PK path, so these creates fail with 400/1001 before the delete step is reached.
        try:
            await created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            await created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Replaces restoring the stale legacy cache: delete through the client holding old metadata.
        created_container = stale_container
        # Should fail as the item no longer exists
        try:
            await created_container.delete_item(item_to_delete, partition_key='val')
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await self._delete_container_for_test_async(container_name)

    async def test_container_recreate_delete_item_sub_partition_async_rust(self):
        # Source: tests/test_container_properties_cache_async.py::TestContainerPropertiesCache.test_container_recreate_delete_item_sub_partition_async
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Create items
        try:
            item_to_del = await created_container.create_item(body={'id': 'item1', 'country': 'USA', 'state': 'CA'})
            await created_container.create_item(body={'id': 'item2',
                                                      'country': 'MEX',
                                                      'state': 'Michoacán'})  # cspell:disable-line
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): load the
        # old container's metadata into a separate Rust driver, which recreation leaves stale.
        stale_container = self.stale_databaseForTest.get_container_client(container_name)
        await stale_container.read_item('item1', partition_key=['USA', 'CA'])
        await self._delete_container_for_test_async(created_container)
        try:
            created_container = await self._create_container_for_test_async(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            assert False, "Container Should not Already Exist."
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). This client cached the old /country,/state paths, so these creates fail with 400/1001 before the delete step is reached.
        try:
            await created_container.create_item(body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
            await created_container.create_item(
                body={'id': 'item2', 'county': 'santa barbara', 'city': 'santa barbara'})
        except exceptions.CosmosHttpResponseError as e:
            assert False, "{}".format(e.http_error_message)
        # Replaces restoring the stale legacy cache: delete through the client holding old metadata.
        created_container = stale_container
        # Should fail as the item no longer exists
        try:
            await created_container.delete_item(item_to_del, partition_key=['USA', 'CA'])
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 404
        await self._delete_container_for_test_async(container_name)
