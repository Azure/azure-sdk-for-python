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
    def on_events(partition_context, events):
        if partition_context.partition_id == "0":
            on_events.called = True
            assert events[0].body_as_str() == "Receiving only a single event"
            assert list(events[-1].body)[0] == b"Receiving only a single event"
    on_events.called = False
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str)
    with client:
        thread = threading.Thread(target=client.receive, args=(on_events, "$default"),
                                  kwargs={"partition_id": "0", "initial_event_position": "@latest"})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_events.called is False
        senders[0].send(EventData(b"Receiving only a single event"))
        time.sleep(5)
        assert on_events.called is True
    thread.join()


@pytest.mark.parametrize("position, inclusive, expected_result",
                         [("offset", False, "Exclusive"),
                          ("offset", True, "Inclusive"),
                          ("sequence", False, "Exclusive"),
                          ("sequence", True, "Inclusive"),
                          ("enqueued_time", False, "Exclusive")])
@pytest.mark.liveTest
def test_receive_with_event_position_sync(connstr_senders, position, inclusive, expected_result):
    def on_events(partition_context, events):
        if position == "offset":
            on_events.event_position = events[-1].offset
        elif position == "sequence":
            on_events.event_position = events[-1].sequence_number
        else:
            on_events.event_position = events[-1].enqueued_time
        on_events.event = events[0]

        assert events[0].last_enqueued_event_properties.get('sequence_number') == events[0].sequence_number
        assert events[0].last_enqueued_event_properties.get('offset') == events[0].offset
        assert events[0].last_enqueued_event_properties.get('enqueued_time') == events[0].enqueued_time
        assert events[0].last_enqueued_event_properties.get('retrieval_time') is not None

    on_events.event_position = None
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Inclusive"))
    client = EventHubConsumerClient.from_connection_string(connection_str)
    with client:
        thread = threading.Thread(target=client.receive, args=(on_events, "$default"),
                                  kwargs={"initial_event_position": "-1"})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_events.event_position is not None
    thread.join()
    senders[0].send(EventData(expected_result))
    client2 = EventHubConsumerClient.from_connection_string(connection_str)
    with client2:
        thread = threading.Thread(target=client2.receive, args=(on_events, "$default"),
                                  kwargs={"initial_event_position": EventPosition(on_events.event_position, inclusive),
                                          "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(5)
        assert on_events.event.body_as_str() == expected_result
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

    def on_events(partition_context, events):
        on_events.received.extend(events)
        on_events.app_prop = events[0].application_properties

    on_events.received = []
    on_events.app_prop = None
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)

    event_list = []
    for i in range(20):
        ed = EventData("Event Number {}".format(i))
        ed.application_properties = on_events.app_prop
        event_list.append(ed)
    senders[0].send(event_list)

    with client:
        thread = threading.Thread(target=client.receive, args=(on_events, "$default"),
                                  kwargs={"partition_id": "0", "event_position": "-1"})
        thread.start()
        time.sleep(5)
    assert len(on_events.received) == 20
