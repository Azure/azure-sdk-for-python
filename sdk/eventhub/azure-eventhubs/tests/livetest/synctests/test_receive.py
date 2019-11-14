#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import threading
import pytest
import time
import datetime

from azure.eventhub import EventData, EventPosition, TransportType
from azure.eventhub import EventHubConsumerClient


@pytest.mark.liveTest
def test_receive_end_of_stream(connstr_senders):
    def on_event(partition_context, event):
        if partition_context.partition_id == "0":
            assert event.body_as_str() == "Receiving only a single event"
            assert list(event.body)[0] == b"Receiving only a single event"
            on_event.called = True
    on_event.called = False
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str)
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event, "$default"),
                                  kwargs={"partition_id": "0", "initial_event_position": "@latest"})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_event.called is False
        senders[0].send(EventData(b"Receiving only a single event"))
        time.sleep(5)
        assert on_event.called is True
    thread.join()


@pytest.mark.parametrize("position, inclusive, expected_result",
                         [("offset", False, "Exclusive"),
                          ("offset", True, "Inclusive"),
                          ("sequence", False, "Exclusive"),
                          ("sequence", True, "Inclusive"),
                          ("enqueued_time", False, "Exclusive")])
@pytest.mark.liveTest
def test_receive_with_event_position_sync(connstr_senders, position, inclusive, expected_result):
    def on_event(partition_context, event):
        assert event.last_enqueued_event_properties.get('sequence_number') == event.sequence_number
        assert event.last_enqueued_event_properties.get('offset') == event.offset
        assert event.last_enqueued_event_properties.get('enqueued_time') == event.enqueued_time
        assert event.last_enqueued_event_properties.get('retrieval_time') is not None

        if position == "offset":
            on_event.event_position = event.offset
        elif position == "sequence":
            on_event.event_position = event.sequence_number
        else:
            on_event.event_position = event.enqueued_time
        on_event.event = event

    on_event.event_position = None
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Inclusive"))
    client = EventHubConsumerClient.from_connection_string(connection_str)
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event, "$default"),
                                  kwargs={"initial_event_position": "-1",
                                  "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_event.event_position is not None
    thread.join()
    senders[0].send(EventData(expected_result))
    client2 = EventHubConsumerClient.from_connection_string(connection_str)
    with client2:
        thread = threading.Thread(target=client2.receive, args=(on_event, "$default"),
                                  kwargs={"initial_event_position": EventPosition(on_event.event_position, inclusive),
                                          "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_event.event.body_as_str() == expected_result
    thread.join()

'''
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
'''


@pytest.mark.liveTest
def test_receive_over_websocket_sync(connstr_senders):
    app_prop = {"raw_prop": "raw_value"}

    def on_event(partition_context, event):
        on_event.received.append(event)
        on_event.app_prop = event[0].application_properties

    on_event.received = []
    on_event.app_prop = None
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)

    event_list = []
    for i in range(20):
        ed = EventData("Event Number {}".format(i))
        ed.application_properties = app_prop
        event_list.append(ed)
    senders[0].send(event_list)

    with client:
        thread = threading.Thread(target=client.receive, args=(on_event, "$default"),
                                  kwargs={"partition_id": "0", "initial_event_position": "-1"})
        thread.start()
        time.sleep(5)
    assert len(on_event.received) == 20
    for ed in on_event.received:
        assert ed.application_properties[b"raw_prop"] == b"raw_value"
