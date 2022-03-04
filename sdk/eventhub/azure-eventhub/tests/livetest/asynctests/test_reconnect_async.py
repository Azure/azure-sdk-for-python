#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import asyncio
import pytest
import time

from azure.eventhub._pyamqp.aio._authentication_async import SASTokenAuthAsync
from azure.eventhub._pyamqp.aio import ReceiveClientAsync
from azure.eventhub._pyamqp import error, constants

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient, EventHubSharedKeyCredential
from azure.eventhub.exceptions import OperationTimeoutError


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_long_interval_async(live_eventhub, sleep):
    test_partition = "0"
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key']))
    async with sender:
        batch = await sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        await sender.send_batch(batch)

        if sleep:
            await asyncio.sleep(250)  # EH server side idle timeout is 240 second
        else:
            await sender._producers[test_partition]._handler._connection.close()
        batch = await sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        await sender.send_batch(batch)

    received = []
    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = SASTokenAuthAsync(
        uri, uri, live_eventhub['key_name'], live_eventhub['access_key']
    )

    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['consumer_group'],
        test_partition)
    receiver = ReceiveClientAsync(live_eventhub['hostname'], source, auth=sas_auth, debug=False, link_credit=500)
    try:
        await receiver.open_async()

        # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
        # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
        # So call it twice to ensure the two events are received.
        received.extend([EventData._from_message(x) for x in (await receiver.receive_message_batch_async(max_batch_size=1, timeout=5))])
        received.extend([EventData._from_message(x) for x in (await receiver.receive_message_batch_async(max_batch_size=1, timeout=5))])
    finally:
        await receiver.close_async()
    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_connection_idle_timeout_and_reconnect_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    # no retry, should just raise error
    client = EventHubProducerClient.from_connection_string(conn_str=connection_str, idle_timeout=10, retry_total=0)
    async with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
        async with sender:
            await sender._open_with_retry()
            await asyncio.sleep(11)
            sender._unsent_events = [ed.message]
            with pytest.raises(error.AMQPConnectionError):
                await sender._send_event_data()

    # with retry, should work
    client = EventHubProducerClient.from_connection_string(conn_str=connection_str, idle_timeout=10)
    async with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
    async with sender:
        await sender._open_with_retry()
        await asyncio.sleep(11)
        sender._unsent_events = [ed.message]
        await sender._send_event_data()

    retry = 0
    while retry < 3:
        try:
            messages = receivers[0].receive_message_batch(max_batch_size=10, timeout=10)
            if messages:
                received_ed1 = EventData._from_message(messages[0])
                assert received_ed1.body_as_str() == 'data'
                break
        except TimeoutError:
            retry += 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_connection_idle_timeout_and_reconnect_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(
        conn_str=connection_str,
        consumer_group='$default',
        idle_timeout=10
    )

    async def on_event_received(event):
        on_event_received.event = event

    async with client:
        consumer = client._create_consumer("$default", "0", "-1", on_event_received)
        async with consumer:
            await consumer._open()
            await asyncio.sleep(11)

            ed = EventData("Event")
            senders[0].send(ed)

            await consumer._handler.do_work_async()
            assert consumer._handler._connection.state == constants.ConnectionState.END

            try:
                await asyncio.wait_for(consumer.receive(), timeout=10)
            except asyncio.TimeoutError:
                pass

            assert on_event_received.event.body_as_str() == "Event"
