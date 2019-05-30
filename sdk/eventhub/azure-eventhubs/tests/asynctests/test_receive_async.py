#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time

from azure.eventhub import EventData, EventPosition, EventHubError, TransportType
from azure.eventhub.aio import EventHubClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_end_of_stream_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1

        assert list(received[-1].body)[0] == b"Receiving only a single event"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=3)
        assert len(received) == 1
        offset = received[0].offset

        offset_receiver = client.create_receiver(partition_id="0", event_position=offset)
        async with offset_receiver:
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 0
            senders[0].send(EventData(b"Message after offset"))
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_inclusive_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        offset_receiver = client.create_receiver(partition_id="0", event_position=EventPosition(offset.value, inclusive=True))
        async with offset_receiver:
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_datetime_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].enqueued_time

        offset_receiver = client.create_receiver(partition_id="0", event_position=EventPosition(offset))
        async with offset_receiver:
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 0
            senders[0].send(EventData(b"Message after timestamp"))
            time.sleep(1)
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_sequence_no_async(connstr_senders):
    # TODO: sampe problem as the sync version
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.create_receiver(partition_id="0", event_position=EventPosition(offset))
        async with offset_receiver:
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 0
            senders[0].send(EventData(b"Message next in sequence"))
            time.sleep(1)
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_inclusive_sequence_no_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.create_receiver(partition_id="0", event_position=EventPosition(offset, inclusive=True))
        async with offset_receiver:
            received = await offset_receiver.receive(timeout=5)
            assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", prefetch=500, event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        for i in range(10):
            senders[0].send(EventData(b"Data"))
        received = await receiver.receive(max_batch_size=5, timeout=5)
        assert len(received) == 5


async def pump(receiver, sleep=None):
    messages = 0
    count = 0
    if sleep:
        await asyncio.sleep(sleep)
    batch = await receiver.receive(timeout=10)
    while batch:
        count += 1
        if count >= 10:
            break
        messages += len(batch)
        batch = await receiver.receive(timeout=10)
    return messages


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_exclusive_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receivers = []
    for exclusive_receiver_priority in [10, 20]:
        receivers.append(client.create_receiver(partition_id="0", exclusive_receiver_priority=exclusive_receiver_priority, prefetch=5))
    outputs = await asyncio.gather(
        pump(receivers[0]),
        pump(receivers[1]),
        return_exceptions=True)
    assert isinstance(outputs[0], EventHubError)  # TODO; it's LinkDetach error
    assert outputs[1] == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_multiple_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str, debug=True)
    partitions = await client.get_properties()
    assert partitions["partition_ids"] == ["0", "1"]
    receivers = []
    for i in range(2):
        receivers.append(client.create_receiver(partition_id="0", prefetch=10))
    try:
        more_partitions = await client.get_properties()
        assert more_partitions["partition_ids"] == ["0", "1"]
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)
        assert isinstance(outputs[0], int) and outputs[0] == 1
        assert isinstance(outputs[1], int) and outputs[1] == 1
    finally:
        for r in receivers:
            await r.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_exclusive_receiver_after_non_exclusive_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receivers = []
    receivers.append(client.create_receiver(partition_id="0", prefetch=10))
    receivers.append(client.create_receiver(partition_id="0", exclusive_receiver_priority=15, prefetch=10))
    try:
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1], sleep=5),
            return_exceptions=True)
        assert isinstance(outputs[0], EventHubError)
        assert isinstance(outputs[1], int) and outputs[1] == 1
    finally:
        for r in receivers:
            await r.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_exclusive_receiver_after_exclusive_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receivers = []
    receivers.append(client.create_receiver(partition_id="0", exclusive_receiver_priority=15, prefetch=10))
    receivers.append(client.create_receiver(partition_id="0", prefetch=10))
    try:
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)
        assert isinstance(outputs[1], EventHubError)
        assert isinstance(outputs[0], int) and outputs[0] == 1
    finally:
        for r in receivers:
            await r.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_with_app_prop_async(connstr_senders):
    connection_str, senders = connstr_senders
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}

    def batched():
        for i in range(10):
            ed = EventData("Event Data {}".format(i))
            ed.application_properties = app_prop
            yield ed
        for i in range(10, 20):
            ed = EventData("Event Data {}".format(i))
            ed.application_properties = app_prop
            yield ed

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.create_receiver(partition_id="0", prefetch=500, event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(batched())

        await asyncio.sleep(1)

        received = await receiver.receive(max_batch_size=15, timeout=5)
        assert len(received) == 15

        for index, message in enumerate(received):
            assert list(message.body)[0] == "Event Data {}".format(index).encode('utf-8')
            assert (app_prop_key.encode('utf-8') in message.application_properties) \
                and (dict(message.application_properties)[app_prop_key.encode('utf-8')] == app_prop_value.encode('utf-8'))


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_over_websocket_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket, debug=False)
    receiver = client.create_receiver(partition_id="0", prefetch=500, event_position=EventPosition('@latest'))

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0

        with senders[0]:
            senders[0].send(event_list)

        time.sleep(1)

        received = await receiver.receive(max_batch_size=50, timeout=5)
        assert len(received) == 20
