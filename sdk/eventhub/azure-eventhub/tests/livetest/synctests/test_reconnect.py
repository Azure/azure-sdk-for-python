#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

from azure.eventhub._pyamqp.authentication import SASTokenAuth
from azure.eventhub._pyamqp.client import ReceiveClient
from azure.eventhub._pyamqp import error, constants

import uamqp

from azure.eventhub import (
    EventData,
    EventHubSharedKeyCredential,
    EventHubProducerClient,
    EventHubConsumerClient,
    amqp
)
from azure.eventhub.exceptions import OperationTimeoutError
from azure.eventhub._utils import transform_outbound_single_message
from azure.eventhub._transport._uamqp_transport import UamqpTransport


@pytest.mark.liveTest
def test_send_with_long_interval_sync(live_eventhub, sleep):
    test_partition = "0"
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key']))
    with sender:
        batch = sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        sender.send_batch(batch)
        if sleep:
            time.sleep(250)
        else:
            sender._producers[test_partition]._handler._connection.close()
        batch = sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        sender.send_batch(batch)

    received = []

    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    sas_auth = SASTokenAuth(
        uri, uri, live_eventhub['key_name'], live_eventhub['access_key']
    )
    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['consumer_group'],
        test_partition)
    receiver = ReceiveClient(live_eventhub['hostname'], source, auth=sas_auth, debug=False, link_credit=500)
    try:
        receiver.open()
        # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
        # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
        # So call it twice to ensure the two events are received.
        received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(max_batch_size=1, timeout=5)])
        received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(max_batch_size=1, timeout=5)])
    finally:
        receiver.close()
    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"


# TODO: fix and add pyamqp transport
@pytest.mark.parametrize("amqp_transport",
                         [UamqpTransport()])
@pytest.mark.liveTest
def test_send_connection_idle_timeout_and_reconnect_sync(connstr_receivers, amqp_transport):
    connection_str, receivers = connstr_receivers
    # no retry, should just raise error
    client = EventHubProducerClient.from_connection_string(conn_str=connection_str, idle_timeout=10, retry_total=0)
    with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
    with sender:
        sender._open_with_retry()
        time.sleep(11)
        sender._unsent_events = [ed.message]
        with pytest.raises(error.AMQPConnectionError):
            sender._send_event_data()

    # with retry, should work
    client = EventHubProducerClient.from_connection_string(conn_str=connection_str, idle_timeout=10)
    with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
    with sender:
            sender._open_with_retry()
            time.sleep(11)
            ed = transform_outbound_single_message(ed, EventData, amqp_transport.to_outgoing_amqp_message)
            sender._unsent_events = [ed.message]
            ed.message.on_send_complete = sender._on_outcome
            with pytest.raises((uamqp.errors.ConnectionClose,
                                uamqp.errors.MessageHandlerError, OperationTimeoutError)):
                # Mac may raise OperationTimeoutError or MessageHandlerError
                sender._send_event_data()
            sender._send_event_data_with_retry()

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
def test_receive_connection_idle_timeout_and_reconnect_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(
        conn_str=connection_str,
        consumer_group='$default',
        idle_timeout=10
    )

    def on_event_received(event):
        on_event_received.event = event
    with client:
        consumer = client._create_consumer("$default", "0", "-1", on_event_received)
        with consumer:
            consumer._open()
            time.sleep(11)

            ed = EventData("Event")
            senders[0].send(ed)

            consumer._handler.do_work()
            assert consumer._handler._connection.state == constants.ConnectionState.END

            duration = 10
            now_time = time.time()
            end_time = now_time + duration

            while now_time < end_time:
                consumer.receive()
                time.sleep(0.01)
                now_time = time.time()

            assert on_event_received.event.body_as_str() == "Event"
