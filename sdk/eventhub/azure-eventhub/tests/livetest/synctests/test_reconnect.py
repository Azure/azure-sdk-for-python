#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

from azure.eventhub import (
    EventData,
    EventHubSharedKeyCredential,
    EventHubProducerClient,
    EventHubConsumerClient,
)
from azure.eventhub.exceptions import OperationTimeoutError
from azure.eventhub._utils import transform_outbound_single_message
from azure.eventhub._pyamqp.authentication import SASTokenAuth
from azure.eventhub._pyamqp import ReceiveClient, error, constants
from azure.eventhub._transport._pyamqp_transport import PyamqpTransport
try:
    import uamqp
    from uamqp import compat
    from azure.eventhub._transport._uamqp_transport import UamqpTransport
except (ModuleNotFoundError, ImportError):
    UamqpTransport = None


@pytest.mark.liveTest
def test_send_with_long_interval_sync(live_eventhub, sleep, uamqp_transport, timeout_factor):
    test_partition = "0"
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'],
                                    live_eventhub['access_key']), uamqp_transport=uamqp_transport
                                    )
    with sender:
        batch = sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        sender.send_batch(batch)
        if sleep:
            time.sleep(250)
        else:
            if uamqp_transport:
                sender._producers[test_partition]._handler._connection._conn.destroy()
            else:
                sender._producers[test_partition]._handler._connection.close()
        batch = sender.create_batch(partition_id=test_partition)
        batch.add(EventData(b"A single event"))
        sender.send_batch(batch)

    received = []

    uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
    source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
        live_eventhub['hostname'],
        live_eventhub['event_hub'],
        live_eventhub['consumer_group'],
        test_partition)
    if uamqp_transport:
        sas_auth = uamqp.authentication.SASTokenAuth.from_shared_access_key(
            uri, live_eventhub['key_name'], live_eventhub['access_key'])
        receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=5000, prefetch=500)
    else:
        sas_auth = SASTokenAuth(
            uri, uri, live_eventhub['key_name'], live_eventhub['access_key']
        )
        receiver = ReceiveClient(live_eventhub['hostname'], source, auth=sas_auth, debug=False, link_credit=500)

    try:
        receiver.open()
        # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
        # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
        # So call it twice to ensure the two events are received.
        received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(max_batch_size=1, timeout=5 * timeout_factor)])
        received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(max_batch_size=1, timeout=5 * timeout_factor)])
    finally:
        receiver.close()
    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
def test_send_connection_idle_timeout_and_reconnect_sync(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    if uamqp_transport:
        amqp_transport = UamqpTransport
        retry_total = 3
        timeout_exc = compat.TimeoutException
    else:
        amqp_transport = PyamqpTransport
        retry_total = 0
        timeout_exc = TimeoutError
    client = EventHubProducerClient.from_connection_string(
        conn_str=connection_str, idle_timeout=10, retry_total=retry_total, uamqp_transport=uamqp_transport
    )
    with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
    with sender:
        sender._open_with_retry()
        time.sleep(11)
        ed = transform_outbound_single_message(ed, EventData, amqp_transport.to_outgoing_amqp_message)
        sender._unsent_events = [ed._message]
        if uamqp_transport:
            sender._unsent_events[0].on_send_complete = sender._on_outcome
            with pytest.raises((uamqp.errors.ConnectionClose,
                                    uamqp.errors.MessageHandlerError, OperationTimeoutError)):
                sender._send_event_data()
        else:
            with pytest.raises(error.AMQPConnectionError):
                sender._send_event_data()
        if uamqp_transport:
            sender._send_event_data_with_retry()

    if not uamqp_transport:
        client = EventHubProducerClient.from_connection_string(
            conn_str=connection_str, idle_timeout=10, uamqp_transport=uamqp_transport
        )
        with client:
            ed = EventData('data')
            sender = client._create_producer(partition_id='0')
        with sender:
                sender._open_with_retry()
                time.sleep(11)
                ed = transform_outbound_single_message(ed, EventData, amqp_transport.to_outgoing_amqp_message)
                sender._unsent_events = [ed._message]
                sender._send_event_data()

    retry = 0
    while retry < 3:
        try:
            messages = receivers[0].receive_message_batch(max_batch_size=10, timeout=10 * timeout_factor)
            if messages:
                received_ed1 = EventData._from_message(messages[0])
                assert received_ed1.body_as_str() == 'data'
                break
        except timeout_exc:
            retry += 1


@pytest.mark.liveTest
def test_receive_connection_idle_timeout_and_reconnect_sync(connstr_senders, uamqp_transport):
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(
        conn_str=connection_str,
        consumer_group='$default',
        idle_timeout=10,
        uamqp_transport=uamqp_transport
    )

    def on_event_received(event):
        on_event_received.event = event
    with client:
        consumer = client._create_consumer("$default", "0", "-1", on_event_received)
        with consumer:
            while not consumer.handler_ready:
                consumer._open()
            time.sleep(11)

            ed = EventData("Event")
            senders[0].send(ed)

            if uamqp_transport:
                consumer._handler.do_work()
                assert consumer._handler._connection._state == uamqp.c_uamqp.ConnectionState.DISCARDING
            else:
                with pytest.raises(error.AMQPConnectionError):
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
