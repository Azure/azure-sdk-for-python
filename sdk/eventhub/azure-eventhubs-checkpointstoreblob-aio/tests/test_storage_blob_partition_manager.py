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

from azure.eventhub.extensions.checkpointstoreblobaio import BlobPartitionManager


def get_live_storage_blob_client():
    try:
        storage_connection_str = os.environ['AZURE_STORAGE_CONN_STR']
    except KeyError:
        return None, None
    try:
        from azure.storage.blob import BlobServiceClient
        from azure.storage.blob.aio import ContainerClient
    except ImportError or ModuleNotFoundError:
        return None, None

    container_str = str(uuid.uuid4())
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_str)
    blob_service_client.create_container(container_str)
    container_client = ContainerClient.from_connection_string(storage_connection_str, container=container_str)
    return container_str, container_client


def remove_live_storage_blob_client(container_str):
    try:
        storage_connection_str = os.environ['AZURE_STORAGE_CONN_STR']
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_str)
        blob_service_client.delete_container(container_str)
    except:
        warnings.warn(UserWarning("storage container teardown failed"))


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_claim_and_list_ownership():
    container_str, live_storage_blob_client = get_live_storage_blob_client()
    if not live_storage_blob_client:
        pytest.skip("Storage blob client can't be created")

    eventhub_name = 'eventhub'
    consumer_group_name = '$default'
    ownership_cnt = 8

    try:
        async with live_storage_blob_client:

            partition_manager = BlobPartitionManager(container_client=live_storage_blob_client)

            ownership_list = await partition_manager.list_ownership(eventhub_name=eventhub_name, consumer_group_name=consumer_group_name)
            assert len(ownership_list) == 0

            ownership_list = []

            for i in range(ownership_cnt):
                ownership = {}
                ownership['eventhub_name'] = eventhub_name
                ownership['consumer_group_name'] = consumer_group_name
                ownership['owner_id'] = 'ownerid'
                ownership['partition_id'] = str(i)
                ownership['last_modified_time'] = time.time()
                ownership["offset"] = "1"
                ownership["sequence_number"] = "1"
                ownership_list.append(ownership)

            await partition_manager.claim_ownership(ownership_list)

            ownership_list = await partition_manager.list_ownership(eventhub_name=eventhub_name, consumer_group_name=consumer_group_name)
            assert len(ownership_list) == ownership_cnt
    finally:
        remove_live_storage_blob_client(container_str)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_update_checkpoint():
    container_str, live_storage_blob_client = get_live_storage_blob_client()
    if not live_storage_blob_client:
        pytest.skip("Storage blob client can't be created")

    eventhub_name = 'eventhub'
    consumer_group_name = '$default'
    owner_id = 'owner'
    partition_cnt = 8

    try:
        async with live_storage_blob_client:
            partition_manager = BlobPartitionManager(container_client=live_storage_blob_client)

            ownership_list = await partition_manager.list_ownership(eventhub_name=eventhub_name, consumer_group_name=consumer_group_name)
            assert len(ownership_list) == 0

            ownership_list = []

            for i in range(partition_cnt):
                ownership = {}
                ownership['eventhub_name'] = eventhub_name
                ownership['consumer_group_name'] = consumer_group_name
                ownership['owner_id'] = owner_id
                ownership['partition_id'] = str(i)
                ownership['last_modified_time'] = time.time()
                ownership['offset'] = '1'
                ownership['sequence_number'] = '10'
                ownership_list.append(ownership)

            await partition_manager.claim_ownership(ownership_list)

            ownership_list = await partition_manager.list_ownership(eventhub_name=eventhub_name, consumer_group_name=consumer_group_name)
            assert len(ownership_list) == partition_cnt

            for i in range(partition_cnt):
                await partition_manager.update_checkpoint(eventhub_name, consumer_group_name, str(i),
                                                          owner_id, '2', '20')

            ownership_list = await partition_manager.list_ownership(eventhub_name=eventhub_name, consumer_group_name=consumer_group_name)
            for ownership in ownership_list:
                assert ownership['offset'] == '2'
                assert ownership['sequence_number'] == '20'
    finally:
        remove_live_storage_blob_client(container_str)
