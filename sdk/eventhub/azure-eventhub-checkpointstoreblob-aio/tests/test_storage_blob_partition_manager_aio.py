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
from functools import partial
from devtools_testutils import get_credential
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.eventhub.extensions.checkpointstoreblobaio._vendor.storage.blob.aio import BlobServiceClient

STORAGE_ENV_KEYS = [
    "AZURE_STORAGE_ACCOUNT",
]


async def get_live_storage_blob_client( storage_account):
    storage_account = "https://{}.blob.core.windows.net".format(
        os.environ[storage_account])
    container_name = str(uuid.uuid4())
    blob_service_client = BlobServiceClient(storage_account, get_credential(is_async=True))
    await blob_service_client.create_container(container_name)
    return storage_account, container_name


async def _claim_and_list_ownership( storage_account, container_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    ownership_cnt = 8

    credential = get_credential(is_async=True)

    checkpoint_store = BlobCheckpointStore(storage_account, container_name, credential=credential)
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

        claimed_ownership = await checkpoint_store.claim_ownership(ownership_list)
        for i in range(ownership_cnt):
            assert ownership_list[i]['partition_id'] == str(i)
            assert claimed_ownership[i]['partition_id'] == str(i)
            assert ownership_list[i] != claimed_ownership[i]

        ownership_list = await checkpoint_store.list_ownership(
            fully_qualified_namespace=fully_qualified_namespace,
            eventhub_name=eventhub_name,
            consumer_group=consumer_group)
        assert len(ownership_list) == ownership_cnt


async def _update_checkpoint( storage_account, container_name):
    fully_qualified_namespace = 'test_namespace'
    eventhub_name = 'eventhub'
    consumer_group = '$default'
    partition_cnt = 8

    credential = get_credential(is_async=True)

    checkpoint_store = BlobCheckpointStore(storage_account, container_name, credential=credential)
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


@pytest.mark.parametrize("storage_account", STORAGE_ENV_KEYS)
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_claim_and_list_ownership_async( storage_account):
    storage_account, container_name = await get_live_storage_blob_client(storage_account)
    await _claim_and_list_ownership(storage_account, container_name)
    blob_service_client = BlobServiceClient(storage_account, credential=get_credential(is_async=True))
    blob_service_client.delete_container(container_name)


@pytest.mark.parametrize("storage_account", STORAGE_ENV_KEYS)
@pytest.mark.live_test_only
@pytest.mark.asyncio
async def test_update_checkpoint_async( storage_account):
    storage_account, container_name = await get_live_storage_blob_client(storage_account)
    await _update_checkpoint(storage_account, container_name)
    blob_service_client = BlobServiceClient(storage_account, credential=get_credential(is_async=True))
    blob_service_client.delete_container(container_name)
