import pytest
from azure.eventhub.extensions.checkpointstoretable import TableCheckpointStore
from azure.data.tables import TableServiceClient
import uuid
import warnings
import random
import os

STORAGE_CONN_STR = os.environ['Azure-storage-conn']

def get_live_storage_table_client(storage_connection_str):
    try:
        table_name = chr(random.randint(ord('a'), ord('z'))) +(uuid.uuid4().hex)
        table_service_client = TableServiceClient.from_connection_string(storage_connection_str)
        table_service_client.create_table_if_not_exists(table_name)
        return storage_connection_str, table_name
    except:
        pytest.skip("Storage table client can't be created")

def remove_live_storage_table_client(storage_connection_str, table_name):
    try:
        table_service_client = TableServiceClient.from_connection_string(storage_connection_str)
        table_service_client.delete_table(table_name)
    except:
        warnings.warn(UserWarning("storage table teardown failed"))

def _claim_and_list_ownership(storage_connection_str, table_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    ownership_cnt = 8

    checkpoint_store = TableCheckpointStore.from_connection_string(
        storage_connection_str, table_name)
    ownership_list = checkpoint_store.list_ownership(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            consumer_group=consumer_group)
    assert len(ownership_list) == 0

    ownership_list = []

    for i in range(ownership_cnt):
            ownership = {}
            ownership['fully_qualified_namespace'] = fully_qualified_namespace
            ownership['eventhub_name'] = eventhub_name
            ownership['consumer_group'] = consumer_group
            ownership['owner_id'] = 'ownerid'
            ownership['partition_id'] = str(i)
            ownership['etag'] = None
            ownership_list.append(ownership)
    checkpoint_store.claim_ownership(ownership_list)

    ownership_list = checkpoint_store.list_ownership(fully_qualified_namespace=fully_qualified_namespace,eventhub_name=eventhub_name,consumer_group=consumer_group)
    assert len(ownership_list) == ownership_cnt

def _update_and_list_checkpoint(storage_connection_str, table_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    partition_cnt = 8

    checkpoint_store = TableCheckpointStore.from_connection_string(
        storage_connection_str, table_name)
    for i in range(partition_cnt):
            checkpoint = {
                'fully_qualified_namespace': fully_qualified_namespace,
                'eventhub_name': eventhub_name,
                'consumer_group': consumer_group,
                'partition_id': str(i),
                'offset': '2',
                'sequence_number': "20"
            }
            checkpoint_store.update_checkpoint(checkpoint)

    checkpoint_list = checkpoint_store.list_checkpoints(
            fully_qualified_namespace,
            eventhub_name,
            consumer_group)
    assert len(checkpoint_list) == partition_cnt
    for checkpoint in checkpoint_list:
            assert checkpoint['offset'] == '2'
            assert checkpoint['sequence_number'] == "20"

    for i in range(partition_cnt):
            checkpoint = {
                'fully_qualified_namespace': fully_qualified_namespace,
                'eventhub_name': eventhub_name,
                'consumer_group': consumer_group,
                'partition_id': str(i),
                'offset': '29',
                'sequence_number': "42"
            }
            checkpoint_store.update_checkpoint(checkpoint)

    checkpoint_list = checkpoint_store.list_checkpoints(
            fully_qualified_namespace,
            eventhub_name,
            consumer_group)
    assert len(checkpoint_list) == partition_cnt
    for checkpoint in checkpoint_list:
            assert checkpoint['offset'] == '29'
            assert checkpoint['sequence_number'] == "42"

@pytest.mark.parametrize("storage_connection_str", STORAGE_CONN_STR)
def test_claim_and_list_ownership(storage_connection_str):
    storage_connection_str, table_name = get_live_storage_table_client(storage_connection_str)
    try:
        _claim_and_list_ownership(storage_connection_str, table_name)
    finally:
        remove_live_storage_table_client(storage_connection_str, table_name)

@pytest.mark.parametrize("storage_connection_str",STORAGE_CONN_STR)
def test_update_checkpoint(storage_connection_str):
    storage_connection_str, table_name = get_live_storage_table_client(storage_connection_str)
    try:
        _update_and_list_checkpoint(storage_connection_str, table_name)
    finally:
        remove_live_storage_table_client(storage_connection_str, table_name)
