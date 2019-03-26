#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time
import sys

from azure import eventhub
from azure.eventhub import (
    EventHubClientAsync,
    EventData,
    Offset,
    EventHubError)


@pytest.mark.asyncio
async def test_send_with_invalid_hostname_async(invalid_hostname, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClientAsync.from_connection_string(invalid_hostname, debug=True)
    sender = client.add_async_sender()
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_receive_with_invalid_hostname_async(invalid_hostname):
    client = EventHubClientAsync.from_connection_string(invalid_hostname, debug=True)
    sender = client.add_async_receiver("$default", "0")
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_send_with_invalid_key_async(invalid_key, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClientAsync.from_connection_string(invalid_key, debug=False)
    sender = client.add_async_sender()
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_receive_with_invalid_key_async(invalid_key):
    client = EventHubClientAsync.from_connection_string(invalid_key, debug=True)
    sender = client.add_async_receiver("$default", "0")
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_send_with_invalid_policy_async(invalid_policy, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClientAsync.from_connection_string(invalid_policy, debug=False)
    sender = client.add_async_sender()
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_receive_with_invalid_policy_async(invalid_policy):
    client = EventHubClientAsync.from_connection_string(invalid_policy, debug=True)
    sender = client.add_async_receiver("$default", "0")
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_send_partition_key_with_partition_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender(partition="1")
    try:
        await client.run_async()
        data = EventData(b"Data")
        data.partition_key = b"PKey"
        with pytest.raises(ValueError):
            await sender.send(data)
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_non_existing_entity_sender_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, eventhub="nemo", debug=False)
    sender = client.add_async_sender(partition="1")
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_non_existing_entity_receiver_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, eventhub="nemo", debug=False)
    receiver = client.add_async_receiver("$default", "0")
    with pytest.raises(EventHubError):
        await client.run_async()


@pytest.mark.asyncio
async def test_receive_from_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
        receiver = client.add_async_receiver("$default", p)
        try:
            with pytest.raises(EventHubError):
                await client.run_async()
                await receiver.receive(timeout=10)
        finally:
            await client.stop_async()


@pytest.mark.asyncio
async def test_send_to_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
        sender = client.add_async_sender(partition=p)
        try:
            with pytest.raises(EventHubError):
                await client.run_async()
        finally:
            await client.stop_async()


@pytest.mark.asyncio
async def test_send_too_large_message_async(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        data = EventData(b"A" * 300000)
        with pytest.raises(EventHubError):
            await sender.send(data)
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_send_null_body_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        with pytest.raises(ValueError):
            data = EventData(None)
            await sender.send(data)
    finally:
        await client.stop_async()


async def pump(receiver):
    messages = 0
    count = 0
    batch = await receiver.receive(timeout=10)
    while batch and count <= 5:
        count += 1
        messages += len(batch)
        batch = await receiver.receive(timeout=10)
    return messages


@pytest.mark.asyncio
async def test_max_receivers_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    receivers = []
    for i in range(6):
        receivers.append(client.add_async_receiver("$default", "0", prefetch=1000, offset=Offset('@latest')))
    try:
        await client.run_async()
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            pump(receivers[2]),
            pump(receivers[3]),
            pump(receivers[4]),
            pump(receivers[5]),
            return_exceptions=True)
        print(outputs)
        failed = [o for o in outputs if isinstance(o, EventHubError)]
        assert len(failed) == 1
        print(failed[0].message)
    finally:
        await client.stop_async()
