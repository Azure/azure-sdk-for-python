#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest

from azure import eventhub
from azure.eventhub import EventData, Offset, EventHubError, EventHubClient
from azure.eventhub.async import EventHubClientAsync


def test_send_partition_key_with_partition(connection_str):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="1")
    client.run()
    data = EventData(b"Data")
    data.partition_key = b"PKey"
    with pytest.raises(ValueError):
        sender.send(data)
    client.stop()


@pytest.mark.asyncio
async def test_send_partition_key_with_partition_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender(partition="1")
    await client.run_async()
    data = EventData(b"Data")
    data.partition_key = b"PKey"
    with pytest.raises(ValueError):
        await sender.send(data)
    await client.stop_async()


def test_non_existing_entity_sender(connection_str):
    client = EventHubClient.from_connection_string(connection_str, eventhub="nemo", debug=False)
    sender = client.add_sender(partition="1")
    client.run()
    data = EventData(b"Data")
    with pytest.raises(EventHubError):
        sender.send(data)
    client.stop()


@pytest.mark.asyncio
async def test_non_existing_entity_sender_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, eventhub="nemo", debug=False)
    sender = client.add_async_sender(partition="1")
    await client.run_async()
    data = EventData(b"Data")
    with pytest.raises(EventHubError):
        await sender.send(data)
    await client.stop_async()


def test_non_existing_entity_receiver(connection_str):
    client = EventHubClient.from_connection_string(connection_str, eventhub="nemo", debug=False)
    receiver = client.add_receiver("$default", "0")
    client.run()
    with pytest.raises(EventHubError):
        receiver.receive(timeout=2)
    client.stop()


@pytest.mark.asyncio
async def test_non_existing_entity_receiver_async(connection_str):
    client = EventHubClientAsync.from_connection_string(connection_str, eventhub="nemo", debug=False)
    receiver = client.add_async_receiver("$default", "0")
    await client.run_async()
    with pytest.raises(EventHubError):
        await receiver.receive(timeout=2)
    await client.stop_async()


def test_receive_from_invalid_partitions(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str, debug=False)
        receiver = client.add_receiver("$default", p)
        client.run()
        with pytest.raises(EventHubError):
            receiver.receive(timeout=2)
        client.stop()


@pytest.mark.asyncio
async def test_receive_from_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
        receiver = client.add_async_receiver("$default", p)
        await client.run_async()
        with pytest.raises(EventHubError):
            await receiver.receive(timeout=2)
        await client.stop_async()


def test_send_to_invalid_partitions(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str, debug=False)
        sender = client.add_sender(partition=p)
        client.run()
        data = EventData(b"Data")
        with pytest.raises(EventHubError):
            sender.send(data)
        client.stop()


@pytest.mark.asyncio
async def test_send_to_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
        sender = client.add_async_sender(partition=p)
        await client.run_async()
        data = EventData(b"Data")
        with pytest.raises(EventHubError):
            await sender.send(data)
        await client.stop_async()


def test_send_too_large_message(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    data = EventData(b"A" * 300000)
    with pytest.raises(EventHubError):
        sender.send(data)
    client.stop()


@pytest.mark.asyncio
async def test_send_too_large_message_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    await client.run_async()
    data = EventData(b"A" * 300000)
    with pytest.raises(EventHubError):
        await sender.send(data)
    await client.stop_async()


def test_send_null_body(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    with pytest.raises(ValueError):
        data = EventData(None)
        sender.send(data)
    client.stop()


@pytest.mark.asyncio
async def test_send_null_body_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    await client.run_async()
    with pytest.raises(ValueError):
        data = EventData(None)
        await sender.send(data)
    await client.stop_async()


async def pump(receiver):
    messages = 0
    batch = await receiver.receive(timeout=10)
    while batch:
        messages += len(batch)
        batch = await receiver.receive(timeout=10)
    return messages


@pytest.mark.asyncio
async def test_max_receivers_async(connection_str, senders):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receivers = []
    for i in range(6):
        receivers.append(client.add_async_receiver("$default", "0", prefetch=1000, offset=Offset('@latest')))
    await client.run_async()
    try:
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            pump(receivers[2]),
            pump(receivers[3]),
            pump(receivers[4]),
            pump(receivers[5]),
            return_exceptions=True)
        assert len([o for o in outputs if isinstance(o, EventHubError)]) == 1

    except:
        raise
    finally:
        await client.stop_async()