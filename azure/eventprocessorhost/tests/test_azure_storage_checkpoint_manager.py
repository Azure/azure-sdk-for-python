# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import pytest
import asyncio
import time
from azure.common import AzureException


def test_init(empty_eph, storage_clm):
    """
    Test that the AzureStorageCheckpointLeaseManager initializes correctly
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)


def test_create_store(empty_eph, storage_clm):
    """
    Test the store is created correctly if not exists
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        loop.run_until_complete(storage.create_checkpoint_store_if_not_exists_async())
    else:
        with pytest.raises(AzureException):
            loop.run_until_complete(storage.create_checkpoint_store_if_not_exists_async())


def test_create_lease(empty_eph, storage_clm):
    """
    Test lease creation
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        loop.run_until_complete(storage.create_checkpoint_store_if_not_exists_async())
        loop.run_until_complete(storage.create_lease_if_not_exists_async("1"))


def test_get_lease(empty_eph, storage_clm):
    """
    Test get lease
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        loop.run_until_complete(storage.get_lease_async("1"))


def test_aquire_renew_release_lease(empty_eph, storage_clm):
    """
    Test aquire lease
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        lease = loop.run_until_complete(storage.get_lease_async("1"))
        loop.run_until_complete(storage.acquire_lease_async(lease))
        loop.run_until_complete(storage.renew_lease_async(lease))
        loop.run_until_complete(storage.release_lease_async(lease))
        assert lease.partition_id == "1"
        assert lease.epoch == 1
        assert loop.run_until_complete(lease.state()) == "available"


def test_delete_lease(empty_eph, storage_clm):
    """
    Test delete lease
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        lease = loop.run_until_complete(storage.get_lease_async("1"))
        loop.run_until_complete(storage.delete_lease_async(lease))
        lease = loop.run_until_complete(storage.get_lease_async("1"))
        assert lease == None


def test_checkpointing(empty_eph, storage_clm):
    """
    Test checkpointing
    """
    is_live, storage = storage_clm
    storage.initialize(empty_eph)
    loop = asyncio.get_event_loop()
    if is_live:
        local_checkpoint = loop.run_until_complete(storage.create_checkpoint_if_not_exists_async("1"))
        assert local_checkpoint.partition_id == "1"
        assert local_checkpoint.offset == "-1"
        lease = loop.run_until_complete(storage.get_lease_async("1"))
        loop.run_until_complete(storage.acquire_lease_async(lease))
        loop.run_until_complete(storage.update_checkpoint_async(lease, local_checkpoint))
        cloud_checkpoint = loop.run_until_complete(storage.get_checkpoint_async("1"))
        lease.offset = cloud_checkpoint.offset
        lease.sequence_number = cloud_checkpoint.sequence_number
        assert cloud_checkpoint.partition_id == "1"
        assert cloud_checkpoint.offset == "-1"
        modify_checkpoint = cloud_checkpoint
        modify_checkpoint.offset = "512"
        modify_checkpoint.sequence_number = "32"
        time.sleep(35)
        loop.run_until_complete(storage.update_checkpoint_async(lease, modify_checkpoint))
        cloud_checkpoint = loop.run_until_complete(storage.get_checkpoint_async("1"))
        assert cloud_checkpoint.partition_id == "1"
        assert cloud_checkpoint.offset == "512"
        loop.run_until_complete(storage.release_lease_async(lease))
