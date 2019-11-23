#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import pytest

import uamqp
from uamqp import authentication, errors, c_uamqp


from azure.eventhub import (
    EventData,
    ConnectError,
    EventHubSharedKeyCredential,
    EventHubProducerClient,
    EventHubConsumerClient
)


@pytest.mark.liveTest
def test_send_with_long_interval_sync(live_eventhub, sleep):
    sender = EventHubProducerClient(live_eventhub['hostname'], live_eventhub['event_hub'],
                                    EventHubSharedKeyCredential(live_eventhub['key_name'], live_eventhub['access_key']))
    with sender:
        batch = sender.create_batch()
        batch.add(EventData(b"A single event"))
        sender.send_batch(batch)
        for _ in range(1):
            if sleep:
                time.sleep(300)
            else:
                sender._producers[-1]._handler._connection._conn.destroy()
            batch = sender.create_batch()
            batch.add(EventData(b"A single event"))
            sender.send_batch(batch)
        partition_ids = sender.get_partition_ids()

    received = []
    for p in partition_ids:
        uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
        sas_auth = authentication.SASTokenAuth.from_shared_access_key(
            uri, live_eventhub['key_name'], live_eventhub['access_key'])

        source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
            live_eventhub['hostname'],
            live_eventhub['event_hub'],
            live_eventhub['consumer_group'],
            p)
        receiver = uamqp.ReceiveClient(source, auth=sas_auth, debug=False, timeout=5000, prefetch=500)
        try:
            receiver.open()
            received.extend([EventData._from_message(x) for x in receiver.receive_message_batch(timeout=5000)])
        finally:
            receiver.close()

    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
def test_send_connection_idle_timeout_and_reconnect_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(conn_str=connection_str, idle_timeout=10)

    ed = EventData('data')
    sender = client._create_producer(partition_id='0')
    sender._unsent_events = [ed.message]

    sender._open_with_retry()

    time.sleep(11)

    with pytest.raises(uamqp.errors.ConnectionClose):
        sender._send_event_data()

    sender._send_event_data_with_retry()
    sender.close()
    client.close()

    messages = receivers[0].receive_message_batch(max_batch_size=10, timeout=10000)
    received_ed1 = EventData._from_message(messages[0])
    assert received_ed1.body_as_str() == 'data'


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

    consumer = client._create_consumer("$default", "0", "-1", on_event_received=on_event_received)
    consumer._open_with_retry()

    time.sleep(11)

    ed = EventData("Event")
    senders[0].send(ed)

    consumer._handler.do_work()
    assert consumer._handler._connection._state == c_uamqp.ConnectionState.DISCARDING

    duration = 10
    now_time = time.time()
    end_time = now_time + duration

    while now_time < end_time:
        consumer.receive()
        time.sleep(0.01)
        now_time = time.time()

    assert on_event_received.event.body_as_str() == "Event"
    consumer.close()
