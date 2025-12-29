# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
import pytest_asyncio
from azure.core.exceptions import AzureError
from azure.cosmos import PartitionKey

from azure.cosmos.exceptions import CosmosResourceNotFoundError

import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos.aio import CosmosClient, DatabaseProxy, ContainerProxy
from typing import Any, Optional

from test_partition_key import ItemDict, PkField, _assert_pk, VERSIONS, _new_null_pk_doc

COLLECTION = "created_collection"
DATABASE = "created_db"
CLIENT = "client"

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

@pytest_asyncio.fixture()
async def setup_async():
    if (TestPartitionKeyAsync.masterKey == '[YOUR_KEY_HERE]' or
            TestPartitionKeyAsync.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = CosmosClient(TestPartitionKeyAsync.host, TestPartitionKeyAsync.masterKey)
    created_db = test_client.get_database_client(TestPartitionKeyAsync.TEST_DATABASE_ID)
    yield {
        DATABASE: created_db,
        COLLECTION: created_db.get_container_client(TestPartitionKeyAsync.TEST_CONTAINER_ID)
    }
    await test_client.close()

async def _assert_no_conflicts(container: ContainerProxy, pk_value: PkField) -> None:
    conflict_definition: ItemDict = {'id': 'new conflict', 'resourceId': 'doc1', 'operationType': 'create', 'resourceType': 'document'}
    if pk_value:
        conflicts_iter = container.query_conflicts(query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'', partition_key=pk_value)
        conflicts = [c async for c in conflicts_iter]
        assert len(conflicts) == 0
    for api_call in (container.get_conflict, container.delete_conflict):
        try:
            await api_call(conflict_definition['id'], partition_key=pk_value)
            pytest.fail("Should have thrown since there are no conflicts")
        except AzureError as ex:
            assert isinstance(ex, CosmosResourceNotFoundError)

async def _perform_operations_on_pk(created_container, pk_field, pk_value):
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
    await _assert_no_conflicts(created_container, pk_value)
    # Get Feed Range
    feed_range = await created_container.feed_range_from_partition_key(partition_key=pk_value)
    assert feed_range is not None
    items_iter = created_container.query_items(query='SELECT * FROM c',
                                               feed_range=feed_range)
    items_list = [i async for i in items_iter]
    assert len(items_list) > 0
    for item in items_list:
        _assert_pk(item, pk_field)
    # Delete
    await created_container.delete_item(item=document_definition['id'], partition_key=pk_value)
    # recreate the item to test delete item api
    await created_container.create_item(body=document_definition)
    await created_container.delete_all_items_by_partition_key(partition_key=pk_value)

@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_async")
@pytest.mark.cosmosEmulator
class TestPartitionKeyAsync:
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

    @pytest.mark.parametrize("version", VERSIONS)
    async def test_multi_partition_collection_read_document_with_no_pk_async(self, setup_async, version) -> None:
        pk_val = partition_key.NonePartitionKeyValue
        created_container = await setup_async[DATABASE].create_container_if_not_exists(id="container_with_no_pk" + str(uuid.uuid4()), partition_key=PartitionKey(path="/pk", kind='Hash'))
        try:
           await _perform_operations_on_pk(created_container, pk_field=None, pk_value=pk_val)
        finally:
            await setup_async[DATABASE].delete_container(created_container)


    @pytest.mark.parametrize("version", VERSIONS)
    async def test_with_null_pk_async(self, setup_async, version) -> None:
        pk_field = 'pk'
        pk_values = [None, partition_key.NullPartitionKeyValue]
        created_container = await setup_async[DATABASE].create_container_if_not_exists(id="container_with_nul_pk" + str(uuid.uuid4()), partition_key=PartitionKey(path="/pk", kind='Hash'))
        try:
            for pk_value in pk_values:
                await _perform_operations_on_pk(created_container, pk_field, pk_value)
        finally:
            await setup_async[DATABASE].delete_container(created_container)

    async def test_hash_v2_partition_key_definition_async(self, setup_async) -> None:
        created_container_properties = await setup_async[COLLECTION].read()
        assert created_container_properties['partitionKey']['version'] == 2

    async def test_hash_v1_partition_key_definition_async(self, setup_async) -> None:
        created_container = await setup_async[DATABASE].create_container(id='container_with_pkd_v2' + str(uuid.uuid4()), partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1))
        created_container_properties = await created_container.read()
        assert created_container_properties['partitionKey']['version'] == 1
        await setup_async[DATABASE].delete_container(created_container)


if __name__ == '__main__':
    unittest.main()
