# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
from azure.core.exceptions import AzureError

from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos import DatabaseProxy, PartitionKey, ContainerProxy
from typing import Any, Dict, Union

ItemDict = Dict[str, Any]
PkField = Union[str, None, type[partition_key.NonePartitionKeyValue], type[partition_key.NullPartitionKeyValue]]
COLLECTION = "created_collection"
DATABASE = "created_db"
VERSIONS = [1, 2]


def _new_null_pk_doc(pk_field: PkField) -> ItemDict:
    if pk_field is None:
        return {'id': str(uuid.uuid4())}
    return {'id': str(uuid.uuid4()), pk_field: None}


def _assert_pk(item: ItemDict, pk_field: PkField = 'pk') -> None:
    if pk_field:
        assert item[pk_field] is None
    else:
        assert pk_field not in item


def _read_and_assert(container: ContainerProxy, doc_id: str, pk_field: PkField = 'pk', pk_value: Any = None) -> None:
    item = container.read_item(item=doc_id, partition_key=pk_value)
    _assert_pk(item, pk_field)


def _query_and_assert_single(container: ContainerProxy, pk_field: PkField = 'pk', pk_value: Any = None) -> None:
    query_iterable = container.query_items(query='SELECT * from c', partition_key=pk_value)
    results = list(query_iterable)
    assert len(results) > 0
    for result in results:
        _assert_pk(result, pk_field)


def _change_feed_and_assert(container: ContainerProxy, pk_field: PkField = 'pk', pk_value: Any = None) -> None:
    changes_iterable = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk_value)
    changes = list(changes_iterable)
    assert len(changes) > 0
    for change in changes:
        _assert_pk(change, pk_field)


def _replace_update_cycle(container: ContainerProxy, doc: ItemDict, pk_field: PkField = 'pk') -> None:
    doc['newField'] = 'newValue'
    item = container.replace_item(item=doc['id'], body=doc)
    assert item['newField'] == 'newValue'
    _assert_pk(item, pk_field)
    item = container.upsert_item(body=doc)
    _assert_pk(item, pk_field)


def _patch_and_assert(container: ContainerProxy, doc_id: str, pk_field: PkField = 'pk', pk_value: Any = None) -> None:
    operations = [{"op": "add", "path": "/favorite_color", "value": "red"}]
    item = container.patch_item(item=doc_id, partition_key=pk_value, patch_operations=operations)
    assert item['favorite_color'] == 'red'
    _assert_pk(item, pk_field)


def _batch_and_assert(container: ContainerProxy, pk_field: PkField = 'pk', pk_value: Any = None) -> None:
    if pk_value == partition_key.NullPartitionKeyValue:
        batch_operations = [
            ("upsert", (({"id": str(uuid.uuid4()), pk_field: None}),)),
        ]
    elif pk_field:
        batch_operations = [
            ("upsert", (({"id": str(uuid.uuid4()), pk_field: pk_value}),)),
        ]
    else:
        batch_operations = [
            ("upsert", (({"id": str(uuid.uuid4())}),)),
        ]
    items = container.execute_item_batch(batch_operations=batch_operations, partition_key=pk_value)
    assert len(items) == 1
    _assert_pk(items[0]['resourceBody'], pk_field)

@pytest.fixture(scope="class")
def setup():
    if (TestPartitionKey.masterKey == '[YOUR_KEY_HERE]' or
            TestPartitionKey.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(TestPartitionKey.host, TestPartitionKey.masterKey),
    created_db = test_client[0].get_database_client(TestPartitionKey.TEST_DATABASE_ID)
    return {
        DATABASE: created_db,
        COLLECTION: created_db.get_container_client(TestPartitionKey.TEST_CONTAINER_ID)
    }


def _assert_no_conflicts(container: ContainerProxy, pk_value: PkField) -> None:
    conflict_definition: ItemDict = {'id': 'new conflict', 'resourceId': 'doc1', 'operationType': 'create', 'resourceType': 'document'}
    if pk_value:
        assert len(list(container.query_conflicts(query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'', partition_key=pk_value))) == 0
    else:
        try:
            list(container.query_conflicts(query='SELECT * FROM root r WHERE r.resourceType=\'' + conflict_definition.get('resourceType') + '\'', partition_key=pk_value))
            pytest.fail("Should have thrown since cross partition query not allowed")
        except CosmosHttpResponseError as ex:
            assert ex.status_code, 400
    for api_call in (container.get_conflict, container.delete_conflict):
        try:
            api_call(conflict_definition['id'], partition_key=pk_value)
            pytest.fail("Should have thrown since there are no conflicts")
        except AzureError as ex:
            assert isinstance(ex, CosmosResourceNotFoundError)


def _perform_operations_on_pk(created_container, pk_field, pk_value):
    # Create initial null PK doc
    document_definition = _new_null_pk_doc(pk_field)
    item = created_container.create_item(body=document_definition)
    _assert_pk(item, pk_field)
    # Read & point reads
    _read_and_assert(created_container, document_definition['id'], pk_field, pk_value)
    items_iter = created_container.read_items(items=[(document_definition['id'], pk_value)])
    items_list = list(items_iter)
    assert len(items_list) == 1
    _assert_pk(items_list[0], pk_field)
    # Change feed
    # If partition key is missing, change feed does not work
    if pk_field:
        _change_feed_and_assert(created_container, pk_field, pk_value)
    # Query
    if pk_value:
        _query_and_assert_single(created_container, pk_field, pk_value)
    else:
        try:
            # passing None directly should throw as requires cross partition param
            _query_and_assert_single(created_container, pk_field, pk_value)
            pytest.fail("Should have thrown")
        except CosmosHttpResponseError as ex:
            assert ex.status_code, 400
    # Replace / Upsert cycle
    _replace_update_cycle(created_container, document_definition, pk_field)
    # Patch
    _patch_and_assert(created_container, document_definition['id'], pk_field, pk_value)
    # Batch
    _batch_and_assert(created_container, pk_field, pk_value)
    # Conflicts
    _assert_no_conflicts(created_container, pk_value)
    # Get Feed Range
    feed_range = created_container.feed_range_from_partition_key(partition_key=pk_value)
    assert feed_range is not None
    items_iter = created_container.query_items(query='SELECT * FROM c',
                                               feed_range=feed_range,
                                               enable_cross_partition_query=True)
    items_list = list(items_iter)
    assert len(items_list) > 0
    for item in items_list:
        _assert_pk(item, pk_field)
    # Delete
    created_container.delete_item(item=document_definition['id'], partition_key=pk_value)
    # recreate the item to test delete item api
    created_container.create_item(body=document_definition)
    created_container.delete_all_items_by_partition_key(partition_key=pk_value)


@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestPartitionKey:
    """Tests to verify if non-partitioned collections are properly accessed on migration with version 2018-12-31.
    """

    client: cosmos_client.CosmosClient = None
    created_db: DatabaseProxy = None
    created_collection: ContainerProxy = None
    host: str = test_config.TestConfig.host
    masterKey: str = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy  # policy object (SDK internal type)
    TEST_DATABASE_ID: str = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID: str = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @pytest.mark.parametrize("version", VERSIONS)
    def test_multi_partition_collection_read_document_with_no_pk(self, setup, version) -> None:
        pk_val: PkField = partition_key.NonePartitionKeyValue  # type: ignore[assignment]
        created_container = setup[DATABASE].create_container_if_not_exists(
            id="container_with_no_pk" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk", kind='Hash', version=version)
        )
        try:
           _perform_operations_on_pk(created_container, None, pk_val)
        finally:
            setup[DATABASE].delete_container(created_container)

    @pytest.mark.parametrize("version", VERSIONS)
    def test_with_null_pk(self, setup, version) -> None:
        pk_field = 'pk'
        pk_vals = [None, partition_key.NullPartitionKeyValue]
        created_container = setup[DATABASE].create_container_if_not_exists(
            id="container_with_nul_pk" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk", kind='Hash', version=version)
        )
        try:
            for pk_value in pk_vals:
                _perform_operations_on_pk(created_container, pk_field, pk_value)
        finally:
            setup[DATABASE].delete_container(created_container)

    def test_hash_v2_partition_key_definition(self, setup) -> None:
        created_container_properties = setup[COLLECTION].read()
        assert created_container_properties['partitionKey']['version'] == 2

    def test_hash_v1_partition_key_definition(self, setup) -> None:
        created_container = setup[DATABASE].create_container(
            id='container_with_pkd_v2' + str(uuid.uuid4()),
            partition_key=partition_key.PartitionKey(path="/id", kind="Hash", version=1)
        )
        created_container_properties = created_container.read()
        assert created_container_properties['partitionKey']['version'] == 1
        setup[DATABASE].delete_container(created_container)


if __name__ == '__main__':
    unittest.main()
