#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time

from azure import eventhub
from azure.eventhub import EventData
from azure.eventhub.async import EventHubClientAsync


@pytest.mark.asyncio
async def test_send_with_partition_key_async(connection_str, receivers):
    pytest.skip("")
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    await client.run_async()

    data_val = 0
    for partition in [b"a", b"b", b"c"]:
        partition_key = b"test_partition_" + partition
        for i in range(5):
            data = EventData(str(data_val))
            data.partition_key = partition_key
            data_val += 1
            sender.send(data)
    await client.stop_async()

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive(timeout=5)
        for message in received:
            try:
                existing = found_partition_keys[message.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[message.partition_key] = index


@pytest.mark.asyncio
async def test_send_and_receive_zero_length_body_async(connection_str, receivers):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await sender.send(EventData(""))
    except:
        raise
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b""


@pytest.mark.asyncio
async def test_send_single_event_async(connection_str, receivers):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await sender.send(EventData(b"A single event"))
    except:
        raise
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.asyncio
async def test_send_batch_async(connection_str, receivers):
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await sender.send(EventData(batch=batched()))
    except:
        raise
    finally:
        await client.stop_async()

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 10
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')


@pytest.mark.asyncio
async def test_send_partition_async(connection_str, receivers):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender(partition="1")
    try:
        await client.run_async()
        await sender.send(EventData(b"Data"))
    except:
        raise
    finally:
        await client.stop_async()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1


@pytest.mark.asyncio
async def test_send_partition_batch_async(connection_str, receivers):
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender(partition="1")
    try:
        await client.run_async()
        await sender.send(EventData(batch=batched()))
    except:
        raise
    finally:
        await client.stop_async()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 10


@pytest.mark.asyncio
async def test_send_array_async(connection_str, receivers):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await sender.send(EventData([b"A", b"B", b"C"]))
    except:
        raise
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body) == [b"A", b"B", b"C"]


@pytest.mark.asyncio
async def test_send_multiple_clients_async(connection_str, receivers):
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    sender_0 = client.add_async_sender(partition="0")
    sender_1 = client.add_async_sender(partition="1")
    try:
        await client.run_async()
        await sender_0.send(EventData(b"Message 0"))
        await sender_1.send(EventData(b"Message 1"))
    except:
        raise
    finally:
        await client.stop_async()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 1
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1