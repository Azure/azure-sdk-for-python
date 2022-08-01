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
import uamqp

from azure.eventhub import EventData, TransportType, EventHubConsumerClient
from azure.eventhub.exceptions import EventHubError
from ..._test_case import get_decorator

uamqp_transport_vals = get_decorator()


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_receive_end_of_stream(connstr_senders, uamqp_transport):
    def on_event(partition_context, event):
        if partition_context.partition_id == "0":
            assert event.body_as_str() == "Receiving only a single event"
            assert list(event.body)[0] == b"Receiving only a single event"
            on_event.called = True
            assert event.partition_key == b'0'
            event_str = str(event)
            assert ", offset: " in event_str
            assert ", sequence_number: " in event_str
            assert ", enqueued_time: " in event_str
            assert ", partition_key: 0" in event_str
    on_event.called = False
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"partition_id": "0", "starting_position": "@latest"})
        thread.daemon = True
        thread.start()
        time.sleep(10)
        assert on_event.called is False
        senders[0].send(EventData(b"Receiving only a single event"), partition_key='0')
        time.sleep(10)
        assert on_event.called is True
    thread.join()


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
@pytest.mark.parametrize("position, inclusive, expected_result",
                         [("offset", False, "Exclusive"),
                          ("offset", True, "Inclusive"),
                          ("sequence", False, "Exclusive"),
                          ("sequence", True, "Inclusive"),
                          ("enqueued_time", False, "Exclusive")])
@pytest.mark.liveTest
def test_receive_with_event_position_sync(uamqp_transport, connstr_senders, position, inclusive, expected_result):
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
    client = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )
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
    client2 = EventHubConsumerClient.from_connection_string(
        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
    )
    with client2:
        thread = threading.Thread(target=client2.receive, args=(on_event,),
                                  kwargs={"starting_position": on_event.event_position,
                                          "starting_position_inclusive": inclusive,
                                          "track_last_enqueued_event_properties": True})
        thread.daemon = True
        thread.start()
        time.sleep(15)
        assert on_event.event.body_as_str() == expected_result

    thread.join()

# TODO: after fixing message property mutability, test
#@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
#@pytest.mark.liveTest
#def test_receive_modify_message_resend_sync(uamqp_transport, connstr_senders):
#    received_modified = [False]
#    def on_event(partition_context, event):
#        message = event.message
#        if message.properties.message_id == b'a1':
#            message.properties.message_id = 'a2'
#            senders[0].send(event)
#        elif message.properties.message_id == b'a2':
#            received_modified = [True]
#
#    connection_str, senders = connstr_senders
#    event = EventData("A", message_id='a1')
#    senders[0].send(event)
#    client = EventHubConsumerClient.from_connection_string(
#        connection_str, consumer_group='$default', uamqp_transport=uamqp_transport
#    )
#    with client:
#        thread = threading.Thread(target=client.receive, args=(on_event,),
#                                  kwargs={"partition_id": "0", "starting_position": "-1"})
#        thread.daemon = True
#        thread.start()
#        time.sleep(10)
#        assert received_modified[0]
#    thread.join()


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_receive_owner_level(connstr_senders, uamqp_transport):
    def on_event(partition_context, event):
        pass
    def on_error(partition_context, error):
        on_error.error = error

    on_error.error = None
    connection_str, senders = connstr_senders
    client1 = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)
    client2 = EventHubConsumerClient.from_connection_string(connection_str, consumer_group='$default', uamqp_transport=uamqp_transport)
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


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_receive_over_websocket_sync(connstr_senders, uamqp_transport):
    app_prop = {"raw_prop": "raw_value"}
    content_type = "text/plain"
    message_id_base = "mess_id_sample_"

    def on_event(partition_context, event):
        on_event.received.append(event)
        on_event.app_prop = event.properties

    on_event.received = []
    on_event.app_prop = None
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str,
                                                           consumer_group='$default',
                                                           transport_type=TransportType.AmqpOverWebsocket,
                                                           uamqp_transport=uamqp_transport)

    event_list = []
    for i in range(5):
        ed = EventData("Event Number {}".format(i))
        ed.properties = app_prop
        ed.content_type = content_type
        ed.correlation_id = message_id_base
        ed.message_id = message_id_base + str(i)
        event_list.append(ed)
    senders[0].send(event_list)
    single_ed = EventData("Event Number {}".format(6))
    single_ed.properties = app_prop
    single_ed.content_type = content_type
    single_ed.correlation_id = message_id_base
    single_ed.message_id = message_id_base + str(6)
    senders[0].send(single_ed)

    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"partition_id": "0", "starting_position": "-1"})
        thread.start()
        time.sleep(10)
    assert len(on_event.received) == 6
    for ed in on_event.received:
        assert ed.correlation_id == message_id_base
        assert message_id_base in ed.message_id
        assert ed.content_type == "text/plain"
        assert ed.properties[b"raw_prop"] == b"raw_value"
