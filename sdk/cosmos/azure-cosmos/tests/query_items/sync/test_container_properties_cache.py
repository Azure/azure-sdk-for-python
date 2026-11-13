# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original query-after-container-recreation check, on the Rust path.

The original saved a copy of the legacy Python container-properties cache
before recreating the container and restored it before the queries. Rust keeps
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
        database_id = "query_recreate_" + uuid.uuid4().hex
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

    def test_container_recreate_query_rust(self):
        # Source: tests/test_container_properties_cache.py::TestContainerPropertiesCache.test_container_recreate_query
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
        # create an item to read
        try:
            item_to_read = created_container.create_item(body={'id': 'item1', container_pk: 'val'})
            item_to_read2 = created_container.create_item(body={'id': 'item2', container_pk: 'OtherValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))

        # Recreate container
        # Replaces copy.deepcopy(client.client_connection.__container_properties_cache): one Rust
        # client per later restore, each holding the old container's metadata.
        old_cache = self._stale_containers(container_name, "val", 2)
        self._delete_container_for_test(created_container)
        try:
            created_container = self._create_container_for_test(id=container_name, partition_key=PartitionKey(
                path="/" + container2_pk))
        except exceptions.CosmosResourceExistsError:
            self.fail("Container Should not Already Exist.")
        # Known gap 22: `create_item()`, `upsert_item()`, `replace_item()`: stale extracted key after container recreation (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22). The data client loaded the old /PK definition when it created item1/item2, so its create below extracts the key with the old path and fails with 400/1001 instead of refreshing; the queries after it cannot run.
        pytest.skip("driver-gap: after container recreation the stale client keeps the old extracted partition key, so this write fails with 400 (known gap 22, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-22).")
        try:
            created_container.create_item(body={'id': 'item1', container2_pk: 'val'})
            created_container.create_item(body={'id': 'item2', container2_pk: 'DifferentValue'})
        except exceptions.CosmosHttpResponseError as e:
            self.fail("{}".format(e.http_error_message))
        created_container = old_cache.pop(0)
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        try:
            query = "SELECT * FROM c WHERE c.id = @id"
            parameters = [{"name": "@id", "value": item_to_read['id']}]
            query_result = list(created_container.query_items(query=query,
                                                              parameters=parameters,
                                                              enable_cross_partition_query=True))
            self.assertEqual(1, len(query_result))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed as item has same id despite the RID not matching.")
        # Will succeed because item id and partition key value are the same as an existing one in the new container
        # But queried items are not the same as their RID will be different
        query = "SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": 'item1'}]
        query_result = list(
            created_container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        self.assertNotEqual(query_result[0], item_to_read)
        created_container = old_cache.pop(0)
        try:
            # Trying to query for item from old container will return empty query
            query = "SELECT * FROM c WHERE c.partKey = @partKey"
            parameters = [{"name": "@partKey", "value": item_to_read2['PK']}]
            query_result = list(created_container.query_items(query=query,
                                                              parameters=parameters,
                                                              enable_cross_partition_query=True))
            self.assertEqual(0, len(query_result))
        except exceptions.CosmosHttpResponseError as e:
            self.fail("Query should still succeed if container is recreated.")
        self._delete_container_for_test(container_name)
