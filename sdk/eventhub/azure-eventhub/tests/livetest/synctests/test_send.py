# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import threading
import time
import json
import sys

import uamqp
from uamqp.message import MessageProperties
from azure.eventhub import EventData, TransportType, EventDataBatch
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub.exceptions import EventDataSendError, OperationTimeoutError
from azure.eventhub.amqp import (
    AmqpMessageHeader,
    AmqpMessageBodyType,
    AmqpAnnotatedMessage,
    AmqpMessageProperties,
)
from azure.eventhub._pyamqp.message import Properties
try:
    from azure.eventhub._transport._uamqp_transport import UamqpTransport
except (ImportError, ModuleNotFoundError):
    UamqpTransport = None
from azure.eventhub._transport._pyamqp_transport import PyamqpTransport
from ..._test_case import get_decorator

uamqp_transport_vals = get_decorator()

@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_with_partition_key(connstr_receivers, live_eventhub, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(10):
                batch = client.create_batch(partition_key=partition_key)
                batch.add(EventData(str(data_val)))
                data_val += 1
                client.send_batch(batch)

        client.send_batch(client.create_batch())

        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(10):
                event_data = EventData(str(data_val))
                event_data.properties = {'is_single': True}
                data_val += 1
                client.send_event(event_data, partition_key=partition_key)

    batch_cnt = 0
    single_cnt = 0
    found_partition_keys = {}
    reconnect_receivers = []
    for index, partition in enumerate(receivers):
        retry_total = 0
        while retry_total < 3:
            timeout = (5 + retry_total) * timeout_factor
            try:
                received = partition.receive_message_batch(timeout=timeout)
                for message in received:
                    try:
                        event_data = EventData._from_message(message)
                        if event_data.properties and event_data.properties[b'is_single']:
                            single_cnt += 1
                        else:
                            batch_cnt += 1
                        existing = found_partition_keys[event_data.partition_key]
                        assert existing == index
                    except KeyError:
                        found_partition_keys[event_data.partition_key] = index
                if received:
                    break
                retry_total += 1
            except uamqp.errors.ConnectionClose:
                for r in reconnect_receivers:
                    r.close()
                uri = "sb://{}/{}".format(live_eventhub['hostname'], live_eventhub['event_hub'])
                sas_auth = uamqp.authentication.SASTokenAuth.from_shared_access_key(
                    uri, live_eventhub['key_name'], live_eventhub['access_key'])

                source = "amqps://{}/{}/ConsumerGroups/{}/Partitions/{}".format(
                    live_eventhub['hostname'],
                    live_eventhub['event_hub'],
                    live_eventhub['consumer_group'],
                    index)
                partition = uamqp.ReceiveClient(source, auth=sas_auth, debug=True, timeout=0, prefetch=500)
                reconnect_receivers.append(partition)
                retry_total += 1
        if retry_total == 3:
            raise OperationTimeoutError(f"Exhausted retries for receiving from {live_eventhub['hostname']}.")

    for r in reconnect_receivers:
        r.close()

    assert single_cnt == 60
    assert batch_cnt == 60
    assert len(found_partition_keys) == 6


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_and_receive_large_body_size(connstr_receivers, uamqp_transport, timeout_factor):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        payload = 250 * 1024
        batch = client.create_batch()
        batch.add(EventData("A" * payload))
        client.send_batch(batch)
        client.send_event(EventData("A" * payload))

    received = []
    timeout = 10 * timeout_factor
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 2
    assert len(list(received[0].body)[0]) == payload
    assert len(list(received[1].body)[0]) == payload

    client = EventHubProducerClient.from_connection_string(connection_str)
    with client:
        payload = 250 * 1024
        batch = client.create_batch()
        batch.add(EventData("A" * payload))
        client.send_batch(batch)
        client.send_event(EventData("A" * payload))

    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 2
    assert len(list(received[0].body)[0]) == payload
    assert len(list(received[1].body)[0]) == payload


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_amqp_annotated_message(connstr_receivers, uamqp_transport):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        sequence_body = [b'message', 123.456, True]
        footer = {'footer_key': 'footer_value'}
        prop = {"subject": "sequence"}
        seq_app_prop = {"body_type": "sequence"}

        sequence_message = AmqpAnnotatedMessage(
            sequence_body=sequence_body,
            footer=footer,
            properties=prop,
            application_properties=seq_app_prop
        )

        value_body = {b"key": [-123, b'data', False]}
        header = {"priority": 10}
        anno = {"ann_key": "ann_value"}
        value_app_prop = {"body_type": "value"}
        value_message = AmqpAnnotatedMessage(
            value_body=value_body,
            header=header,
            annotations=anno,
            application_properties=value_app_prop
        )

        data_body = [b'aa', b'bb', b'cc']
        data_app_prop = {"body_type": "data"}
        del_anno = {"delann_key": "delann_value"}
        data_message = AmqpAnnotatedMessage(
            data_body=data_body,
            header=header,
            delivery_annotations=del_anno,
            application_properties=data_app_prop
        )

        body_ed = """{"json_key": "json_val"}"""
        prop_ed = {b"raw_prop": b"raw_value"}
        cont_type_ed = "text/plain"
        corr_id_ed = "corr_id"
        mess_id_ed = "mess_id"
        event_data = EventData(body_ed)
        event_data.content_type = cont_type_ed
        event_data.correlation_id = corr_id_ed
        event_data.message_id = mess_id_ed
        event_data.properties = prop_ed

        batch = client.create_batch()
        batch.add(data_message)
        batch.add(value_message)
        batch.add(sequence_message)
        batch.add(event_data)
        client.send_batch(batch)
        client.send_batch([data_message, value_message, sequence_message, event_data])
        client.send_event(data_message)
        client.send_event(value_message)
        client.send_event(sequence_message)
        client.send_event(event_data)

    received_count = {}
    received_count["data_msg"] = 0
    received_count["seq_msg"] = 0
    received_count["value_msg"] = 0
    received_count["normal_msg"] = 0

    def check_values(event):
        raw_amqp_message = event.raw_amqp_message
        if raw_amqp_message.body_type == AmqpMessageBodyType.DATA:
            if raw_amqp_message.application_properties and raw_amqp_message.application_properties.get(b'body_type') == b'data':
                body = [data for data in raw_amqp_message.body]
                assert data_body == body
                assert event.body_as_str() == "aabbcc"
                assert raw_amqp_message.delivery_annotations[b'delann_key'] == b'delann_value'
                assert raw_amqp_message.application_properties[b'body_type'] == b'data'
                received_count["data_msg"] += 1
            else:
                assert event.body_as_json() == {'json_key': 'json_val'}
                assert event.correlation_id == corr_id_ed
                assert event.message_id == mess_id_ed
                assert event.content_type == cont_type_ed
                assert event.properties == prop_ed
                assert event.body_type == AmqpMessageBodyType.DATA
                received_count["normal_msg"] += 1
        elif raw_amqp_message.body_type == AmqpMessageBodyType.SEQUENCE:
            body = [sequence for sequence in raw_amqp_message.body]
            assert [sequence_body] == body
            assert event.body_as_str() == "['message', 123.456, True]"
            assert raw_amqp_message.footer[b'footer_key'] == b'footer_value'
            assert raw_amqp_message.properties.subject == b'sequence'
            assert raw_amqp_message.application_properties[b'body_type'] == b'sequence'
            received_count["seq_msg"] += 1
        elif raw_amqp_message.body_type == AmqpMessageBodyType.VALUE:
            assert raw_amqp_message.body == value_body
            assert event.body_as_str() == "{'key': [-123, 'data', False]}"
            assert raw_amqp_message.annotations[b'ann_key'] == b'ann_value'
            assert raw_amqp_message.application_properties[b'body_type'] == b'value'
            received_count["value_msg"] += 1

    def on_event(partition_context, event):
        on_event.received.append(event)

    on_event.received = []
    client = EventHubConsumerClient.from_connection_string(connection_str,
                                                           consumer_group='$default',
                                                           uamqp_transport=uamqp_transport)
    with client:
        thread = threading.Thread(target=client.receive, args=(on_event,),
                                  kwargs={"starting_position": "-1"})
        thread.start()
        time.sleep(15)
        for event in on_event.received:
            check_values(event)

    assert len(on_event.received) == 12
    assert received_count["data_msg"] == 3
    assert received_count["seq_msg"] == 3
    assert received_count["value_msg"] == 3
    assert received_count["normal_msg"] == 3


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
@pytest.mark.parametrize("payload",
                         [(b""), (b"A single event")])
@pytest.mark.liveTest
def test_send_and_receive_small_body(connstr_receivers, payload, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        batch = client.create_batch()
        batch.add(EventData(payload))
        client.send_batch(batch)
        client.send_event(EventData(payload))
    received = []
    timeout = 5 * timeout_factor
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 2
    assert list(received[0].body)[0] == payload
    assert list(received[1].body)[0] == payload


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_partition(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 5 * timeout_factor
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)

    with client:
        batch = client.create_batch()
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        client.send_event(EventData(b"Data"))

    with client:
        batch = client.create_batch(partition_id="1")
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        client.send_event(EventData(b"Data"), partition_id="1")

    partition_0 = receivers[0].receive_message_batch(timeout=timeout)
    partition_1 = receivers[1].receive_message_batch(timeout=timeout)
    assert len(partition_1) >= 2
    assert len(partition_0) + len(partition_1) == 4

    with client:
        batch = client.create_batch()
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        client.send_event(EventData(b"Data"))

    with client:
        batch = client.create_batch(partition_id="0")
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        client.send_event(EventData(b"Data"), partition_id="0")

    time.sleep(5)
    partition_0 = receivers[0].receive_message_batch(timeout=timeout)
    partition_1 = receivers[1].receive_message_batch(timeout=timeout)
    assert len(partition_0) >= 2
    assert len(partition_0) + len(partition_1) == 4


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_non_ascii(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 5 * timeout_factor
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        batch = client.create_batch(partition_id="0")
        batch.add(EventData(u"é,è,à,ù,â,ê,î,ô,û"))
        batch.add(EventData(json.dumps({"foo": u"漢字"})))
        client.send_batch(batch)
        client.send_event(EventData(u"é,è,à,ù,â,ê,î,ô,û"), partition_id="0")
        client.send_event(EventData(json.dumps({"foo": u"漢字"})), partition_id="0")
    time.sleep(1)
    # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
    # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
    # So call it twice to ensure the two events are received.
    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=timeout)] + \
                  [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=timeout)]
    assert len(partition_0) == 4
    assert partition_0[0].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": u"漢字"}
    assert partition_0[2].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[3].body_as_json() == {"foo": u"漢字"}


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_multiple_partitions_with_app_prop(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 5 * timeout_factor
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        ed0 = EventData(b"Message 0")
        ed0.properties = app_prop
        batch = client.create_batch(partition_id="0")
        batch.add(ed0)
        client.send_batch(batch)
        client.send_event(ed0, partition_id="0")

        ed1 = EventData(b"Message 1")
        ed1.properties = app_prop
        batch = client.create_batch(partition_id="1")
        batch.add(ed1)
        client.send_batch(batch)
        client.send_event(ed1, partition_id="1")

    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=timeout)]
    assert len(partition_0) == 2
    assert partition_0[0].properties[b"raw_prop"] == b"raw_value"
    assert partition_0[1].properties[b"raw_prop"] == b"raw_value"
    partition_1 = [EventData._from_message(x) for x in receivers[1].receive_message_batch(timeout=timeout)]
    assert len(partition_1) == 2
    assert partition_1[0].properties[b"raw_prop"] == b"raw_value"
    assert partition_1[1].properties[b"raw_prop"] == b"raw_value"


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_over_websocket_sync(connstr_receivers, uamqp_transport, timeout_factor):
    timeout = 10 * timeout_factor
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(
        connection_str, transport_type=TransportType.AmqpOverWebsocket, uamqp_transport=uamqp_transport
    )

    with client:
        batch = client.create_batch(partition_id="0")
        batch.add(EventData("Event Data"))
        client.send_batch(batch)
        client.send_event(EventData("Event Data"), partition_id="0")

    time.sleep(1)
    received = []
    received.extend(receivers[0].receive_message_batch(max_batch_size=5, timeout=timeout))
    assert len(received) == 2


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_with_create_event_batch_with_app_prop_sync(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 5 * timeout_factor
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(
        connection_str, transport_type=TransportType.AmqpOverWebsocket, uamqp_transport=uamqp_transport
    )
    with client:
        event_data_batch = client.create_batch(max_size_in_bytes=100000)
        while True:
            try:
                ed = EventData('A single event data')
                ed.properties = app_prop
                event_data_batch.add(ed)
            except ValueError:
                break
        client.send_batch(event_data_batch)
        received = []
        for r in receivers:
            received.extend(r.receive_message_batch(timeout=timeout))
        assert len(received) >= 1
        assert EventData._from_message(received[0]).properties[b"raw_prop"] == b"raw_value"


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_list(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 10 * timeout_factor
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    payload = "A1"
    with client:
        client.send_batch([EventData(payload)])
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 1
    assert received[0].body_as_str() == payload


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_list_partition(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    timeout = 10 * timeout_factor
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    payload = "A1"
    with client:
        client.send_batch([EventData(payload)], partition_id="0")
        message = receivers[0].receive_message_batch(timeout=timeout)[0]
        received = EventData._from_message(message)
    assert received.body_as_str() == payload


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
@pytest.mark.parametrize("to_send, exception_type",
                         [([EventData("A"*1024)]*1100, ValueError),
                          ("any str", AttributeError)])
@pytest.mark.liveTest
def test_send_list_wrong_data(connection_str, to_send, exception_type, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(exception_type):
            client.send_batch(to_send)


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
@pytest.mark.parametrize("partition_id, partition_key", [("0", None), (None, "pk")])
def test_send_batch_pid_pk(invalid_hostname, partition_id, partition_key, uamqp_transport):
    # Use invalid_hostname because this is not a live test.
    amqp_transport = UamqpTransport if uamqp_transport else PyamqpTransport
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    batch = EventDataBatch(partition_id=partition_id, partition_key=partition_key, amqp_transport=amqp_transport)
    with client:
        with pytest.raises(TypeError):
            client.send_batch(batch, partition_id=partition_id, partition_key=partition_key)


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
def test_send_with_callback(connstr_receivers, uamqp_transport):

    def on_error(events, pid, err):
        on_error.err = err

    def on_success(events, pid):
        sent_events.append((events, pid))

    sent_events = []
    on_error.err = None
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, on_success=on_success, on_error=on_error, uamqp_transport=uamqp_transport)

    with client:
        batch = client.create_batch()
        batch.add(EventData(b"Data"))
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        assert len(sent_events[-1][0]) == 2
        assert not sent_events[-1][1]
        client.send_event(EventData(b"Data"))
        assert len(sent_events[-1][0]) == 1
        assert not sent_events[-1][1]

        batch = client.create_batch(partition_key='key')
        batch.add(EventData(b"Data"))
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        assert len(sent_events[-1][0]) == 2
        assert not sent_events[-1][1]
        client.send_event(EventData(b"Data"), partition_key='key')
        assert len(sent_events[-1][0]) == 1
        assert not sent_events[-1][1]

        batch = client.create_batch(partition_id="0")
        batch.add(EventData(b"Data"))
        client.send_batch(batch)
        batch.add(EventData(b"Data"))
        assert len(sent_events[-1][0]) == 2
        assert sent_events[-1][1] == "0"
        client.send_event(EventData(b"Data"), partition_id="0")
        assert len(sent_events[-1][0]) == 1
        assert sent_events[-1][1] == "0"

        assert not on_error.err

# TODO: add more checks after LegacyMessage has been added
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
@pytest.mark.liveTest
def test_send_message_modify_backcompat(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    if uamqp_transport:
        properties = MessageProperties

    timeout = 10 * timeout_factor
    outgoing_event_data = EventData(body="hello")
    message = outgoing_event_data.message
    message.properties = properties(user_id='fake_user')
    assert outgoing_event_data.message.properties.user_id == b'fake_user'
    assert outgoing_event_data.message.state == uamqp.constants.MessageState.WaitingToBeSent
    assert outgoing_event_data.message.delivery_annotations is None
    assert outgoing_event_data.message.delivery_no is None
    assert outgoing_event_data.message.delivery_tag is None
    assert outgoing_event_data.message.on_send_complete is None
    assert outgoing_event_data.message.footer is None
    assert outgoing_event_data.message.retries == 0
    assert outgoing_event_data.message.idle_time == 0
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        client.send_batch([outgoing_event_data])
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 1
    received_ed = received[0]
    # check that setting properties directly on uamqp message doesn't update the outgoing message from the event data
    assert received_ed.message.properties.user_id is None
    assert received_ed.message.state == uamqp.constants.MessageState.ReceivedSettled
    assert received_ed.message.delivery_annotations is None
    assert received_ed.message.delivery_no >= 1
    assert received_ed.message.delivery_tag is None
    assert received_ed.message.on_send_complete is None
    assert received_ed.message.footer is None
    assert received_ed.message.retries >= 0
    assert received_ed.message.idle_time >= 0

    # setting message properties by calling event data properties SHOULD update the outgoing uamqp message
    received_ed.properties = {'prop': 'test'}
    received_ed.message_id = "id_message"
    received_ed.content_type = "content type"
    received_ed.correlation_id = "correlation"

    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        client.send_batch([received_ed])
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=timeout)])

    assert len(received) == 1
    received_ed = received[0]
    assert received_ed.message.application_properties == {b"prop": b"test"}
    assert received_ed.message_id == "id_message"
    assert received_ed.content_type == "content type"
    assert received_ed.correlation_id == "correlation"
