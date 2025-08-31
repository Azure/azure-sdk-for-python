# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
from azure.core.exceptions import AzureError
from azure.cosmos import PartitionKey

from azure.cosmos.exceptions import CosmosResourceNotFoundError

import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from typing import Any, Optional

from tests.test_partition_key import _new_null_pk_doc, ItemDict, PkField, _assert_pk


async def _read_and_assert(container: ContainerProxy, doc_id: str, pk_field: Optional[str] = 'pk', pk_value: Any = None) -> None:
    item = await container.read_item(item=doc_id, partition_key=pk_value)
    _assert_pk(item, pk_field)


async def _query_and_assert_single(container: ContainerProxy, pk_field: Optional[str] = 'pk', pk_value: Any = None) -> None:
    query_iterable = container.query_items(query='SELECT * from c', partition_key=pk_value)
    counter = 0
    async for item in query_iterable:
        _assert_pk(item, pk_field)
        counter += 1
    assert counter > 0


async def _change_feed_and_assert(container: ContainerProxy, pk_field: Optional[str] = 'pk', pk_value: Any = None) -> None:
    changes_iterable = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk_value)
    counter = 0
    async for change in changes_iterable:
        _assert_pk(change, pk_field)
        counter += 1
    assert counter > 0


async def _replace_update_cycle(container: ContainerProxy, doc: ItemDict, pk_field: Optional[str] = 'pk') -> None:
    doc['newField'] = 'newValue'
    item = await container.replace_item(item=doc['id'], body=doc)
    assert item['newField'] == 'newValue'
    _assert_pk(item, pk_field)
    item = await container.upsert_item(body=doc)
    _assert_pk(item, pk_field)


async def _patch_and_assert(container: ContainerProxy, doc_id: str, pk_field: Optional[str] = 'pk', pk_value: Any = None) -> None:
    operations = [{"op": "add", "path": "/favorite_color", "value": "red"}]
    item = await container.patch_item(item=doc_id, partition_key=pk_value, patch_operations=operations)
    assert item['favorite_color'] == 'red'
    _assert_pk(item, pk_field)


async def _batch_and_assert(container: ContainerProxy, pk_field: Optional[str] = 'pk', pk_value: Any = None) -> None:
    if pk_value == partition_key.NullPartitionKeyValue:
        batch_operations = [("upsert", (({"id": str(uuid.uuid4()), pk_field: None}),)),]
    elif pk_field:
        batch_operations = [("upsert", (({"id": str(uuid.uuid4()), pk_field: pk_value}),)),]
    else:
        batch_operations = [("upsert", (({"id": str(uuid.uuid4())}),)),]
    items = await container.execute_item_batch(batch_operations=batch_operations, partition_key=pk_value)
    assert len(items) == 1
    _assert_pk(items[0]['resourceBody'], pk_field)


@pytest.mark.asyncio
@pytest.mark.cosmosEmulator
class TestPartitionKeyAsync(unittest.IsolatedAsyncioTestCase):
    """Tests to verify if non-partitioned collections are properly accessed on migration with version 2018-12-31.
    """

    client: CosmosClient = None
    created_db: DatabaseProxy = None
    created_collection: ContainerProxy = None
    host: str = test_config.TestConfig.host
    masterKey: str = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID: str = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID: str = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    async def asyncSetUp(cls) -> None:
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_collection = cls.created_db.get_container_client(cls.TEST_CONTAINER_ID)

    async def asyncTearDown(self) -> None:
        await self.client.close()

    async def _assert_no_conflicts(self, container: ContainerProxy, pk_value: PkField) -> None:
        conflict_definition: ItemDict = {'id': 'new conflict', 'resourceId': 'doc1', 'operationType': 'create', 'resourceType': 'document'}
        if pk_value:
            conflicts_iter = container.query_conflicts(query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'', partition_key=pk_value)
            conflicts = [c async for c in conflicts_iter]
            assert len(conflicts) == 0
        for api_call in (container.get_conflict, container.delete_conflict):
            try:
                await api_call(conflict_definition['id'], partition_key=pk_value)
                self.fail("Should have thrown since there are no conflicts")
            except AzureError as ex:  # type: ignore[unused-ignore]
                assert isinstance(ex, CosmosResourceNotFoundError)

    async def test_multi_partition_collection_read_document_with_no_pk_async(self) -> None:
        pk_val = partition_key.NonePartitionKeyValue
        created_container = await self.created_db.create_container_if_not_exists(id="container_with_no_pk" + str(uuid.uuid4()), partition_key=PartitionKey(path="/pk", kind='Hash'))
        try:
           await self._perform_operations_on_pk(created_container, pk_field=None, pk_value=pk_val)
        finally:
            await self.created_db.delete_container(created_container)

    async def test_with_null_pk_async(self) -> None:
        pk_field = 'pk'
        pk_values = [None, partition_key.NullPartitionKeyValue]
        created_container = await self.created_db.create_container_if_not_exists(id="container_with_nul_pk" + str(uuid.uuid4()), partition_key=PartitionKey(path="/pk", kind='Hash'))
        try:
            for pk_value in pk_values:
                await self._perform_operations_on_pk(created_container, pk_field, pk_value)
        finally:
            await self.created_db.delete_container(created_container)

    async def _perform_operations_on_pk(self, created_container, pk_field, pk_value):
        # Create initial null PK doc
        document_definition = _new_null_pk_doc(pk_field)
        item = await created_container.create_item(body=document_definition)
        _assert_pk(item, pk_field)
        # Read & point reads
        await _read_and_assert(created_container, document_definition['id'], pk_field, pk_value)
        items_iter = await created_container.read_items(items=[(document_definition['id'], pk_value)])
        items_list = [i for i in items_iter]
        assert len(items_list) == 1
        _assert_pk(items_list[0], pk_field)
        # Change feed
        if pk_field:
            await _change_feed_and_assert(created_container, pk_field, pk_value)
        # Query
        if pk_value:
            await _query_and_assert_single(created_container, pk_field, pk_value)
        # Replace / Upsert cycle
        await _replace_update_cycle(created_container, document_definition, pk_field)
        # Patch
        await _patch_and_assert(created_container, document_definition['id'], pk_field, pk_value)
        # Batch
        await _batch_and_assert(created_container, pk_field, pk_value)
        # Conflicts
        await self._assert_no_conflicts(created_container, pk_value)
        # Delete
        await created_container.delete_item(item=document_definition['id'], partition_key=pk_value)
        # Get Feed Range
        feed_range = await created_container.feed_range_from_partition_key(partition_key=None)
        assert feed_range is not None
        items_iter = created_container.query_items(query='SELECT * FROM c',
                                                   feed_range=feed_range)
        items_list = [i async for i in items_iter]
        assert len(items_list) > 0
        for item in items_list:
            _assert_pk(item, pk_field)
        # recreate the item to test delete item api
        await created_container.create_item(body=document_definition)
        await created_container.delete_all_items_by_partition_key(partition_key=pk_value)

    async def test_hash_v2_partition_key_definition_async(self) -> None:
        created_container_properties = await self.created_collection.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 2)

    async def test_hash_v1_partition_key_definition_async(self) -> None:
        created_container = await self.created_db.create_container(id='container_with_pkd_v2' + str(uuid.uuid4()), partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1))
        created_container_properties = await created_container.read()
        self.assertEqual(created_container_properties['partitionKey']['version'], 1)
        await self.created_db.delete_container(created_container)


if __name__ == '__main__':
    unittest.main()
