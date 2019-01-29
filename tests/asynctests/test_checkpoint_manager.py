# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio
import base64
import pytest
import time
import json
from azure.common import AzureException


def test_create_store(storage_clm):
    """
    Test the store is created correctly if not exists
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.create_checkpoint_store_if_not_exists_async())


def test_create_lease(storage_clm):
    """
    Test lease creation
    """
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.create_checkpoint_store_if_not_exists_async())
    loop.run_until_complete(storage_clm.create_lease_if_not_exists_async("1"))


def test_get_lease(storage_clm):
    """
    Test get lease
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(storage_clm.get_lease_async("1"))


def test_aquire_renew_release_lease(storage_clm):
    """
    Test aquire lease
    """
    loop = asyncio.get_event_loop()
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert lease is None
    loop.run_until_complete(storage_clm.create_lease_if_not_exists_async("1"))
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.acquire_lease_async(lease))
    loop.run_until_complete(storage_clm.renew_lease_async(lease))
    loop.run_until_complete(storage_clm.release_lease_async(lease))
    assert lease.partition_id == "1"
    assert lease.epoch == 1
    assert loop.run_until_complete(lease.state()) == "available"


def test_delete_lease(storage_clm):
    """
    Test delete lease
    """
    loop = asyncio.get_event_loop()
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert lease is None
    loop.run_until_complete(storage_clm.create_lease_if_not_exists_async("1"))
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.delete_lease_async(lease))
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert lease == None


def test_checkpointing(storage_clm):
    """
    Test checkpointing
    """
    loop = asyncio.get_event_loop()
    local_checkpoint = loop.run_until_complete(storage_clm.create_checkpoint_if_not_exists_async("1"))
    assert local_checkpoint.partition_id == "1"
    assert local_checkpoint.offset == "-1"
    lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    loop.run_until_complete(storage_clm.acquire_lease_async(lease))

    # Test EPH context encoded as bytes
    event_processor_context = {'some_string_data': 'abc', 'some_int_data': 123, 'a_list': [42]}
    cloud_event_processor_context_asbytes = json.dumps(event_processor_context).encode('utf-8')
    lease.event_processor_context = base64.b64encode(cloud_event_processor_context_asbytes).decode('ascii')
    loop.run_until_complete(storage_clm.update_checkpoint_async(lease, local_checkpoint))

    cloud_lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    cloud_event_processor_context_asbytes = cloud_lease.event_processor_context.encode('ascii')
    event_processor_context_decoded = base64.b64decode(cloud_event_processor_context_asbytes).decode('utf-8')
    cloud_event_processor_context = json.loads(event_processor_context_decoded)
    assert cloud_event_processor_context['some_string_data'] == 'abc'
    assert cloud_event_processor_context['some_int_data'] == 123
    assert cloud_event_processor_context['a_list'] == [42]

    # Test EPH context as JSON object
    lease.event_processor_context = {'some_string_data': 'abc', 'some_int_data': 123, 'a_list': [42]}
    loop.run_until_complete(storage_clm.update_checkpoint_async(lease, local_checkpoint))

    cloud_lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert cloud_lease.event_processor_context['some_string_data'] == 'abc'
    assert cloud_lease.event_processor_context['some_int_data'] == 123
    assert cloud_lease.event_processor_context['a_list'] == [42]

    cloud_checkpoint = loop.run_until_complete(storage_clm.get_checkpoint_async("1"))
    lease.offset = cloud_checkpoint.offset
    lease.sequence_number = cloud_checkpoint.sequence_number
    lease.event_processor_context = None
    assert cloud_checkpoint.partition_id == "1"
    assert cloud_checkpoint.offset == "-1"
    modify_checkpoint = cloud_checkpoint
    modify_checkpoint.offset = "512"
    modify_checkpoint.sequence_number = "32"
    time.sleep(35)
    loop.run_until_complete(storage_clm.update_checkpoint_async(lease, modify_checkpoint))
    cloud_lease = loop.run_until_complete(storage_clm.get_lease_async("1"))
    assert cloud_lease.event_processor_context is None

    cloud_checkpoint = loop.run_until_complete(storage_clm.get_checkpoint_async("1"))
    assert cloud_checkpoint.partition_id == "1"
    assert cloud_checkpoint.offset == "512"
    loop.run_until_complete(storage_clm.release_lease_async(lease))
