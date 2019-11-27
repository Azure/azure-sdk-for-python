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

from azure.eventhub import EventData, TransportType, EventHubConsumerClient
from azure.eventhub.exceptions import EventHubError


@pytest.mark.liveTest
def test_receive_end_of_stream(connstr_senders):
    def on_event(partition_context, event):
        if partition_context.partition_id == "0":
            assert event.body_as_str() == "Receiving only a single event"
            assert list(event.body)[0] == b"Receiving only a single event"
            on_event.called = True
    on_event.called = False
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"partition_id": "0", "starting_position": "@latest"})
        thread.daemon = True
        thread.start()
        time.sleep(10)
        assert on_event.called is False
        senders[0].send(EventData(b"Receiving only a single event"))
        time.sleep(10)
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
        assert partition_context.last_enqueued_event_properties.get('sequence_number') == event.sequence_number
        assert partition_context.last_enqueued_event_properties.get('offset') == event.offset
        assert partition_context.last_enqueued_event_properties.get('enqueued_time') == event.enqueued_time
        assert partition_context.last_enqueued_event_properties.get('retrieval_time') is not None

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
    senders[1].send(EventData(b"Inclusive"))
    client = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1",
                                          "starting_position_inclusive": inclusive,
                                          "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(10)
        assert on_event.event_position is not None
    thread.join()
    senders[0].send(EventData(expected_result))
    senders[1].send(EventData(expected_result))
    client2 = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    with client2:
        thread = threading.Thread(target=client2.receive, args=(on_event,),
                                  kwargs={"starting_position": on_event.event_position,
                                          "starting_position_inclusive": inclusive,
                                          "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(10)
        assert on_event.event.body_as_str() == expected_result
    thread.join()


@pytest.mark.liveTest
def test_receive_owner_level(connstr_senders):
    def on_event(partition_context, event):
        pass
    def on_error(partition_context, error):
        on_error.error = error

    on_error.error = None
    connection_str, senders = connstr_senders
    client1 = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    client2 = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default')
    with client1, client2:
        thread1 = threading.Thread(target=client1.receive, args=(on_event,),
                                   kwargs={"partition_id": "0", "starting_position": "-1",
                                           "on_error": on_error})
        thread1.start()
        for i in range(5):
            ed = EventData("Event Number {}".format(i))
            senders[0].send(ed)
        time.sleep(10)
        thread2 = threading.Thread(target=client2.receive, args=(on_event,),
                                   kwargs = {"partition_id": "0", "starting_position": "-1", "owner_level": 1})
        thread2.start()
        for i in range(5):
            ed = EventData("Event Number {}".format(i))
            senders[0].send(ed)
        time.sleep(20)
    thread1.join()
    thread2.join()
    assert isinstance(on_error.error, EventHubError)


@pytest.mark.liveTest
def test_receive_over_websocket_sync(connstr_senders):
    app_prop = {"raw_prop": "raw_value"}

    def on_event(partition_context, event):
        on_event.received.append(event)
        on_event.app_prop = event.properties

    on_event.received = []
    on_event.app_prop = None
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str,
                                                           consumer_group='$default',
                                                           transport_type=TransportType.AmqpOverWebsocket)

    event_list = []
    for i in range(5):
        ed = EventData("Event Number {}".format(i))
        ed.properties = app_prop
        event_list.append(ed)
    senders[0].send(event_list)

    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"partition_id": "0", "starting_position": "-1"})
        thread.start()
        time.sleep(10)
    assert len(on_event.received) == 5
    for ed in on_event.received:
        assert ed.properties[b"raw_prop"] == b"raw_value"
