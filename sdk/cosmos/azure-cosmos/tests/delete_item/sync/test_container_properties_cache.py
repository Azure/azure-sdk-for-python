# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original delete-after-container-recreation checks, on the Rust path.

The original restored a stale copy of the legacy Python container-properties
cache before deleting. Rust keeps container metadata inside the driver, so
this copy gets the same stale state from a second Rust client that loaded the
old container's metadata before the container was recreated.
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
        database_id = "delete_recreate_" + uuid.uuid4().hex
        self.key_databaseForTest = cleanup.enter_context(owned_database(self.key_client, database_id))
        self.client = clients.create_data_client()
        self.addCleanup(self.client.close)
        self.databaseForTest = self.client.get_database_client(database_id)
        # A second data client whose driver keeps the pre-recreation container metadata.
        self.stale_client = clients.create_data_client()
        self.addCleanup(self.stale_client.close)
        self.stale_databaseForTest = self.stale_client.get_database_client(database_id)

    def _create_container_for_test(self, *args, **kwargs):
        container_ref = self.key_databaseForTest.create_container(*args, **kwargs)
        return self.databaseForTest.get_container_client(container_ref.id)

    def _delete_container_for_test(self, *args, **kwargs):
        return self.key_databaseForTest.delete_container(*args, **kwargs)

    def test_container_recreate_delete_item_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_delete_item
        container_name = str(uuid.uuid4())
        container_pk = "PK"
        container2_pk = "partkey"
        # Create The Container
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path="/" + container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # create items
        try:
            item_to_delete = created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): load the
        # old container's metadata into a separate Rust driver, which recreation leaves stale.
        stale_container = self.stale_databaseForTest.get_container_client(container_name)
        stale_container.read_item('item1', partition_key='val')
        self._delete_container_for_test(created_container)
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). This client cached the old /PK path, so these creates fail with 400/1001 before the delete step is reached.
        try:
            created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Replaces restoring the stale legacy cache: delete through the client holding old metadata.
        created_container = stale_container
        # Should fail as the item no longer exists
        try:
            created_container.delete_item(item_to_delete, partition_key='val')
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, 404)
        self._delete_container_for_test(container_name)

    def test_container_recreate_delete_item_sub_partition_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_delete_item_sub_partition
        container_name = str(uuid.uuid4())
        container_pk = ["/country", "/state"]
        container2_pk = ["/county", "/city"]
        # Create The Container
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path=container_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # create items
        try:
            item_to_del = created_container.create_item(body={'id': 'item1', 'country': 'USA', 'state': 'CA'})
            created_container.create_item(body={'id': 'item2',
                                                'country': 'MEX', 'state': 'Michoacán'})  # cspell:disable-line
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): load the
        # old container's metadata into a separate Rust driver, which recreation leaves stale.
        stale_container = self.stale_databaseForTest.get_container_client(container_name)
        stale_container.read_item('item1', partition_key=['USA', 'CA'])
        self._delete_container_for_test(created_container)
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path=container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). This client cached the old /country,/state paths, so these creates fail with 400/1001 before the delete step is reached.
        try:
            created_container.create_item(body={'id': 'item1', 'county': 'ventura', 'city': 'oxnard'})
            created_container.create_item(body={'id': 'item2',
                                                'county': 'santa barbara', 'city': 'santa barbara'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        # Replaces restoring the stale legacy cache: delete through the client holding old metadata.
        created_container = stale_container
        # Should fail as the item no longer exists
        try:
            created_container.delete_item(item_to_del, partition_key=['USA', 'CA'])
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, 404)
        self._delete_container_for_test(container_name)
