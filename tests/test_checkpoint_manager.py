# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import pytest
import asyncio
import time
from azure.common import AzureException


def test_init(eph, storage_clm):
    """
    Test that the AzureStorageCheckpointLeaseManager initializes correctly
    """
    storage_clm.initialize(eph)


def test_create_store(eph, storage_clm):
    """
    Test the store is created correctly if not exists
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.create_checkpoint_store_if_not_exists_async())


def test_create_lease(eph, storage_clm):
    """
    Test lease creation
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.create_checkpoint_store_if_not_exists_async())
    loop.run_until_complete(storage_clm.create_lease_if_not_exists_async("1"))


def test_get_lease(eph, storage_clm):
    """
    Test get lease
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.get_lease_async("1"))


def test_aquire_renew_release_lease(eph, storage_clm):
    """
    Test aquire lease
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.acquire_lease_async(lease))
    loop.run_until_complete(storage_clm.renew_lease_async(lease))
    loop.run_until_complete(storage_clm.release_lease_async(lease))
    assert lease.partition_id == "1"
    assert lease.epoch == 1
    assert loop.run_until_complete(lease.state()) == "available"


def test_delete_lease(eph, storage_clm):
    """
    Test delete lease
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.delete_lease_async(lease))
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert lease == None


def test_checkpointing(eph, storage_clm):
    """
    Test checkpointing
    """
    storage_clm.initialize(eph)
    loop = asyncio.get_event_loop()
    local_checkpoint = loop.run_until_complete(storage_clm.create_checkpoint_if_not_exists_async("1"))
    assert local_checkpoint.partition_id == "1"
    assert local_checkpoint.offset == "-1"
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.acquire_lease_async(lease))
    loop.run_until_complete(storage_clm.update_checkpoint_async(lease, local_checkpoint))
    cloud_checkpoint = loop.run_until_complete(storage_clm.get_checkpoint_async("1"))
    lease.offset = cloud_checkpoint.offset
    lease.sequence_number = cloud_checkpoint.sequence_number
    assert cloud_checkpoint.partition_id == "1"
    assert cloud_checkpoint.offset == "-1"
    modify_checkpoint = cloud_checkpoint
    modify_checkpoint.offset = "512"
    modify_checkpoint.sequence_number = "32"
    time.sleep(35)
    loop.run_until_complete(storage_clm.update_checkpoint_async(lease, modify_checkpoint))
    cloud_checkpoint = loop.run_until_complete(storage_clm.get_checkpoint_async("1"))
    assert cloud_checkpoint.partition_id == "1"
    assert cloud_checkpoint.offset == "512"
    loop.run_until_complete(storage_clm.release_lease_async(lease))
