#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time
import datetime

from azure.eventhub import EventData, EventPosition, TransportType
from azure.eventhub.client import EventHubClient


@pytest.mark.liveTest
def test_receive_end_of_stream(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1

        assert received[0].body_as_str() == "Receiving only a single event"
        assert list(received[-1].body)[0] == b"Receiving only a single event"
    client.close()


@pytest.mark.liveTest
def test_receive_with_offset_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    partitions = client.get_properties()
    assert partitions["partition_ids"] == ["0", "1"]
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    with receiver:
        more_partitions = client.get_properties()
        assert more_partitions["partition_ids"] == ["0", "1"]

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=False))
    with offset_receiver:
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after offset"))
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    client.close()


@pytest.mark.liveTest
def test_receive_with_inclusive_offset(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))

    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=True))
    with offset_receiver:
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    client.close()


@pytest.mark.liveTest
def test_receive_with_datetime_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    partitions = client.get_properties()
    assert partitions["partition_ids"] == ["0", "1"]
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    with receiver:
        more_partitions = client.get_properties()
        assert more_partitions["partition_ids"] == ["0", "1"]
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].enqueued_time

        assert list(received[0].body) == [b'Data']
        assert received[0].body_as_str() == "Data"

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset))
    with offset_receiver:
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after timestamp"))
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    client.close()


@pytest.mark.liveTest
def test_receive_with_custom_datetime_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    for i in range(5):
        senders[0].send(EventData(b"Message before timestamp"))
    time.sleep(65)

    now = datetime.datetime.utcnow()
    offset = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
    for i in range(5):
        senders[0].send(EventData(b"Message after timestamp"))

    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset))
    with receiver:
        all_received = []
        received = receiver.receive(timeout=5)
        while received:
            all_received.extend(received)
            received = receiver.receive(timeout=5)

        assert len(all_received) == 5
        for received_event in all_received:
            assert received_event.body_as_str() == "Message after timestamp"
            assert received_event.enqueued_time > offset
    client.close()


@pytest.mark.liveTest
def test_receive_with_sequence_no(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))

    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, False))
    with offset_receiver:
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message next in sequence"))
        time.sleep(1)
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    client.close()


@pytest.mark.liveTest
def test_receive_with_inclusive_sequence_no(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number
    offset_receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition(offset, inclusive=True))
    with offset_receiver:
        received = offset_receiver.receive(timeout=5)
        assert len(received) == 1
    client.close()


@pytest.mark.liveTest
def test_receive_batch(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)
    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0
        for i in range(10):
            senders[0].send(EventData(b"Data"))
        received = receiver.receive(max_batch_size=5, timeout=5)
        assert len(received) == 5

        for event in received:
            assert event.system_properties
            assert event.sequence_number is not None
            assert event.offset
            assert event.enqueued_time
    client.close()


@pytest.mark.liveTest
def test_receive_batch_with_app_prop_sync(connstr_senders):
    #pytest.skip("Waiting on uAMQP release")
    connection_str, senders = connstr_senders
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    batch_app_prop = {app_prop_key: app_prop_value}

    def batched():
        for i in range(10):
            ed = EventData("Event Data {}".format(i))
            ed.application_properties = batch_app_prop
            yield ed
        for i in range(10, 20):
            ed = EventData("Event Data {}".format(i))
            ed.application_properties = batch_app_prop
            yield ed

    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)
    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(batched())

        time.sleep(1)

        received = receiver.receive(max_batch_size=15, timeout=5)
        assert len(received) == 15

        for index, message in enumerate(received):
            assert list(message.body)[0] == "Event Data {}".format(index).encode('utf-8')
            assert (app_prop_key.encode('utf-8') in message.application_properties) \
                and (dict(message.application_properties)[app_prop_key.encode('utf-8')] == app_prop_value.encode('utf-8'))
    client.close()


@pytest.mark.liveTest
def test_receive_over_websocket_sync(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), prefetch=500)

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(event_list)

        time.sleep(1)

        received = receiver.receive(max_batch_size=50, timeout=5)
        assert len(received) == 20
    client.close()


@pytest.mark.liveTest
def test_receive_run_time_metric(connstr_senders):
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

    with receiver:
        received = receiver.receive(timeout=5)
        assert len(received) == 0

        senders[0].send(event_list)

        time.sleep(1)

        received = receiver.receive(max_batch_size=50, timeout=5)
        assert len(received) == 20
        assert receiver.last_enqueued_event_properties
        assert receiver.last_enqueued_event_properties.get('sequence_number', None)
        assert receiver.last_enqueued_event_properties.get('offset', None)
        assert receiver.last_enqueued_event_properties.get('enqueued_time', None)
        assert receiver.last_enqueued_event_properties.get('retrieval_time', None)
    client.close()
