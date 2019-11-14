#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import pytest
import time

from azure.eventhub import EventData, EventPosition, TransportType, ConnectionLostError
from azure.eventhub.aio import EventHubConsumerClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_end_of_stream_async(connstr_senders):
    async def on_event(partition_context, event):
        if partition_context.partition_id == "0":
            assert event.body_as_str() == "Receiving only a single event"
            assert list(event.body)[0] == b"Receiving only a single event"
            on_event.called = True
    on_event.called = False
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str)
    async with client:
        task = asyncio.ensure_future(client.receive(on_event, "$default", partition_id="0", initial_event_position="-1"))
        await asyncio.sleep(10)
        assert on_event.called is False
        senders[0].send(EventData(b"Receiving only a single event"))
        time.sleep(10)
        assert on_event.called is True
    task.cancel()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=3)
        assert len(received) == 1
        offset = received[0].offset

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=False))
    async with offset_receiver:
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after offset"))
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_inclusive_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=True))
    async with offset_receiver:
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_datetime_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].enqueued_time

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset))
    async with offset_receiver:
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after timestamp"))
        time.sleep(1)
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_sequence_no_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset))
    async with offset_receiver:
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message next in sequence"))
        time.sleep(1)
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_inclusive_sequence_no_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=True))
    async with offset_receiver:
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_batch_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)
    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        for i in range(10):
            senders[0].send(EventData(b"Data"))
        received = await receiver.receive(max_batch_size=5, timeout=5)
        assert len(received) == 5

        for event in received:
            assert event.system_properties
            assert event.sequence_number is not None
            assert event.offset
            assert event.enqueued_time
    await client.close()


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

    client = EventHubClient.from_connection_string(connection_str)
    receiver1 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), owner_level=10, prefetch=5)
    receiver2 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), owner_level=20, prefetch=10)
    try:
        await pump(receiver1)
        output2 = await pump(receiver2)
        with pytest.raises(ConnectionLostError):
            await receiver1.receive(timeout=3)
        assert output2 == 1
    finally:
        await receiver1.close()
        await receiver2.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_multiple_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str)
    partitions = await client.get_properties()
    assert partitions["partition_ids"] == ["0", "1"]
    receivers = []
    for i in range(2):
        receivers.append(client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), prefetch=10))
    try:
        more_partitions = await client.get_properties()
        assert more_partitions["partition_ids"] == ["0", "1"]
        outputs = [0, 0]
        outputs[0] = await pump(receivers[0])
        outputs[1] = await pump(receivers[1])
        assert isinstance(outputs[0], int) and outputs[0] == 1
        assert isinstance(outputs[1], int) and outputs[1] == 1
    finally:
        for r in receivers:
            await r.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_exclusive_receiver_after_non_exclusive_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str)
    receiver1 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), prefetch=10)
    receiver2 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), owner_level=15, prefetch=10)
    try:
        await pump(receiver1)
        output2 = await pump(receiver2)
        with pytest.raises(ConnectionLostError):
            await receiver1.receive(timeout=3)
        assert output2 == 1
    finally:
        await receiver1.close()
        await receiver2.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_exclusive_receiver_after_exclusive_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClient.from_connection_string(connection_str)
    receiver1 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), owner_level=15, prefetch=10)
    receiver2 = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), prefetch=10)
    try:
        output1 = await pump(receiver1)
        with pytest.raises(ConnectionLostError):
            await pump(receiver2)
        assert output1 == 1
    finally:
        await receiver1.close()
        await receiver2.close()
    await client.close()


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

    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)
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
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_over_websocket_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(event_list)

        time.sleep(1)

        received = await receiver.receive(max_batch_size=50, timeout=5)
        assert len(received) == 20
    await client.close()


@pytest.mark.asyncio
@pytest.mark.liveTest
async def test_receive_run_time_metric_async(connstr_senders):
    from uamqp import __version__ as uamqp_version
    from distutils.version import StrictVersion
    if StrictVersion(uamqp_version) < StrictVersion('1.2.3'):
        pytest.skip("Disabled for uamqp 1.2.2. Will enable after uamqp 1.2.3 is released.")
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0",
                                       event_position=EventPosition('@latest'), prefetch=500,
                                       track_last_enqueued_event_properties=True)

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    async with receiver:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(event_list)

        await asyncio.sleep(1)

        received = await receiver.receive(max_batch_size=50, timeout=5)
        assert len(received) == 20
        assert receiver.last_enqueued_event_properties
        assert receiver.last_enqueued_event_properties.get('sequence_number', None)
        assert receiver.last_enqueued_event_properties.get('offset', None)
        assert receiver.last_enqueued_event_properties.get('enqueued_time', None)
        assert receiver.last_enqueued_event_properties.get('retrieval_time', None)
    await client.close()
