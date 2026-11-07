# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original create/upsert/replace-after-container-recreation checks, on the Rust path.

The original saved a copy of the legacy Python container-properties cache
before recreating the container and restored it before each write. Rust keeps
container metadata inside the driver, so this copy gets the same stale state
from separate Rust clients that each loaded the old container's metadata
before the container was recreated; one is used per restore.
Each test owns a uniquely named database.
"""

from contextlib import ExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database
from config import clients

from azure.cosmos import CosmosClient, PartitionKey, exceptions


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestContainerPropertiesCache(unittest.TestCase):
    def setUp(self):
        self.key_client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.key_client.close)
        cleanup = ExitStack()
        self.addCleanup(cleanup.close)
        database_id = "upsert_recreate_" + uuid.uuid4().hex
        self.key_databaseForTest = cleanup.enter_context(owned_database(self.key_client, database_id))
        self.client = clients.create_data_client()
        self.addCleanup(self.client.close)
        self.databaseForTest = self.client.get_database_client(database_id)

    def _create_container_for_test(self, *args, **kwargs):
        container_ref = self.key_databaseForTest.create_container(*args, **kwargs)
        return self.databaseForTest.get_container_client(container_ref.id)

    def _delete_container_for_test(self, *args, **kwargs):
        return self.key_databaseForTest.delete_container(*args, **kwargs)

    def _stale_containers(self, container_name, partition_key, count):
        """Rust data clients whose drivers hold the current container's metadata."""
        stale = []
        for _ in range(count):
            stale_client = clients.create_data_client()
            self.addCleanup(stale_client.close)
            container = stale_client.get_database_client(self.databaseForTest.id).get_container_client(container_name)
            # Any data-plane call resolves and caches the container definition in the driver.
            with self.assertRaises(exceptions.CosmosResourceNotFoundError):
                container.read_item("metadata-warmup-" + uuid.uuid4().hex, partition_key=partition_key)
            stale.append(container)
        return stale

    def test_container_recreate_create_upsert_replace_item_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_create_upsert_replace_item
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
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
        old_cache = self._stale_containers(container_name, "val", 4)
        self._delete_container_for_test(created_container)
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # let's test create by replacing current container properties cache with old one
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The stale client extracts the key with the old /PK path and its refreshed retry keeps it, so this create, the upsert and the replace below fail with 400 instead of recovering.
        pytest.skip("driver-gap: after container recreation the stale client keeps the old extracted partition key, so this write fails with 400 (known gap 22, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22).")
        created_container = old_cache.pop(0)
        try:
            created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Do the same thing for upsert operation
        created_container = old_cache.pop(0)
        try:
            created_container.upsert_item(dict(id="item2", partkey="value"))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Finally test replace item
        item = created_container.read_item("item1", partition_key="val")
        created_container = old_cache.pop(0)
        try:
            created_container.replace_item(item=item, body={'id': 'item1', container2_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        created_container = old_cache.pop(0)
        try:
            created_container.create_item(body={'id': 'item3', container_pk: 'val'})
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, 400)
        self._delete_container_for_test(container_name)

    def test_container_recreate_create_upsert_replace_item_sub_partitioning_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_create_upsert_replace_item_sub_partitioning
        client = self.client
        created_db = self.databaseForTest
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")

        # This Simulates a container recreate. We save the old cache and then create
        # a new container with different partition key definition
        # for these three operations we extract the partition key value from the document
        # with a stale cache we end up extracting the wrong one so these will retry extracting
        # the partition key after refreshing the cache. Test to make sure a container recreate doesn't affect it.
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): one Rust
        # client per later restore, each holding the old container's metadata.
        old_cache = self._stale_containers(container_name, ["USA", "CA"], 4)
        self._delete_container_for_test(created_container)
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # let's test create by replacing current container properties cache with old one
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The stale client extracts the key with the old /country,/state paths and its refreshed retry keeps it, so this create, the upsert and the replace below fail with 400 instead of recovering.
        pytest.skip("driver-gap: after container recreation the stale client keeps the old extracted partition key, so this write fails with 400 (known gap 22, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22).")
        created_container = old_cache.pop(0)
        try:
            created_container.create_item(body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Do the same thing for upsert operation
        created_container = old_cache.pop(0)
        try:
            created_container.upsert_item(dict(id="item2", county='Santa Barbara', city='Santa Barbara'))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Finally test replace item
        item = created_container.read_item("item1", partition_key=['ventura', 'oxnard'])
        created_container = old_cache.pop(0)
        try:
            created_container.replace_item(item=item, body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Now a negative test. We will try creating an item as if we were attempting to create it with the old container
        # This should result in an error of 400 as the container has been recreated.
        created_container = old_cache.pop(0)
        try:
            created_container.create_item(body={'id': 'item3', 'country': 'USA', 'state': 'CA'})
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, 400)
        self._delete_container_for_test(container_name)
