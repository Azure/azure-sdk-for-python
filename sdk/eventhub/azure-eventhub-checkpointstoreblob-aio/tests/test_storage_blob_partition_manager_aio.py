#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import time
import os
import uuid
import warnings
import asyncio

from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.eventhub.extensions.checkpointstoreblobaio._vendor.storage.blob import BlobServiceClient

STORAGE_ENV_KEYS = [
    "AZURE_STORAGE_CONN_STR",
    "AZURE_STORAGE_DATA_LAKE_ENABLED_CONN_STR"
]


def get_live_storage_blob_client(conn_str_env_key):
    try:
        storage_connection_str = os.environ[conn_str_env_key]
        container_name = str(uuid.uuid4())
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_str)
        blob_service_client.create_container(container_name)
        return storage_connection_str, container_name
    except:
        pytest.skip("Storage blob client can't be created")


def remove_live_storage_blob_client(storage_connection_str, container_str):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_str)
        blob_service_client.delete_container(container_str)
    except:
        warnings.warn(UserWarning("storage container teardown failed"))


async def _claim_and_list_ownership(connection_str, container_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    ownership_cnt = 8

    checkpoint_store = BlobCheckpointStore.from_connection_string(connection_str, container_name)
    async with checkpoint_store:
        ownership_list = await checkpoint_store.list_ownership(
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
            ownership['last_modified_time'] = time.time()
            ownership_list.append(ownership)

        await checkpoint_store.claim_ownership(ownership_list)

        ownership_list = await checkpoint_store.list_ownership(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            consumer_group=consumer_group)
        assert len(ownership_list) == ownership_cnt


async def _update_checkpoint(connection_str, container_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    partition_cnt = 8

    checkpoint_store = BlobCheckpointStore.from_connection_string(connection_str, container_name)
    async with checkpoint_store:
        for i in range(partition_cnt):
            checkpoint = {
                'fully_qualified_namespace': fully_qualified_namespace,
                'eventhub_name': eventhub_name,
                'consumer_group': consumer_group,
                'partition_id': str(i),
                'offset': '2',
                'sequence_number': 20
            }
            await checkpoint_store.update_checkpoint(checkpoint)

        checkpoint_list = await checkpoint_store.list_checkpoints(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            consumer_group=consumer_group)
        assert len(checkpoint_list) == partition_cnt
        for checkpoint in checkpoint_list:
            assert checkpoint['offset'] == '2'
            assert checkpoint['sequence_number'] == 20


@pytest.mark.parametrize("conn_str_env_key", STORAGE_ENV_KEYS)
@pytest.mark.liveTest
def test_claim_and_list_ownership(conn_str_env_key):
    storage_connection_str, container_name = get_live_storage_blob_client(conn_str_env_key)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_claim_and_list_ownership(storage_connection_str, container_name))
    finally:
        remove_live_storage_blob_client(storage_connection_str, container_name)


@pytest.mark.parametrize("conn_str_env_key", STORAGE_ENV_KEYS)
@pytest.mark.liveTest
def test_update_checkpoint(conn_str_env_key):
    storage_connection_str, container_name = get_live_storage_blob_client(conn_str_env_key)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_update_checkpoint(storage_connection_str, container_name))
    finally:
        remove_live_storage_blob_client(storage_connection_str, container_name)
