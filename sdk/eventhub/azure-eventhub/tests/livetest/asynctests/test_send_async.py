# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time
import json

from azure.eventhub import EventData, TransportType, EventDataBatch
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub.exceptions import EventDataSendError, OperationTimeoutError
from azure.eventhub.amqp import (
    AmqpMessageHeader,
    AmqpMessageBodyType,
    AmqpAnnotatedMessage,
    AmqpMessageProperties,
)
try:
    import uamqp
    from uamqp.constants import TransportType as uamqp_TransportType, MessageState
    from uamqp.message import MessageProperties
except (ModuleNotFoundError, ImportError):
    uamqp = None
    uamqp_TransportType = TransportType
    MessageProperties = None
from azure.eventhub._pyamqp.message import Properties
from azure.eventhub._pyamqp.authentication import SASTokenAuth
from azure.eventhub._pyamqp.client import ReceiveClient
from azure.eventhub._pyamqp.error import AMQPConnectionError


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_amqp_annotated_message(connstr_receivers, uamqp_transport):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
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
        prop_ed = {"raw_prop": "raw_value"}
        cont_type_ed = "text/plain"
        corr_id_ed = "corr_id"
        mess_id_ed = "mess_id"
        event_data = EventData(body_ed)
        event_data.content_type = cont_type_ed
        event_data.correlation_id = corr_id_ed
        event_data.message_id = mess_id_ed

        batch = await client.create_batch()
        batch.add(data_message)
        batch.add(value_message)
        batch.add(sequence_message)
        batch.add(event_data)
        await client.send_batch(batch)
        await client.send_batch([data_message, value_message, sequence_message, event_data])
        await client.send_event(data_message)
        await client.send_event(value_message)
        await client.send_event(sequence_message)
        await client.send_event(event_data)

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

    async def on_event(partition_context, event):
        on_event.received.append(event)

    on_event.received = []
    client = EventHubConsumerClient.from_connection_string(connection_str,
                                                        consumer_group='$default', uamqp_transport=uamqp_transport)
    async with client:
        task = asyncio.ensure_future(client.receive(on_event, starting_position="-1"))
        await asyncio.sleep(15)
        for event in on_event.received:
            check_values(event)

    await task

    assert len(on_event.received) == 12
    assert received_count["data_msg"] == 3
    assert received_count["seq_msg"] == 3
    assert received_count["value_msg"] == 3
    assert received_count["normal_msg"] == 3


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_partition_key_async(connstr_receivers, live_eventhub, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(10):
                batch = await client.create_batch(partition_key=partition_key)
                batch.add(EventData(str(data_val)))
                data_val += 1
                await client.send_batch(batch)

        await client.send_batch(await client.create_batch())

        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(10):
                event_data = EventData(str(data_val))
                event_data.properties = {'is_single': True}
                data_val += 1
                await client.send_event(event_data, partition_key=partition_key)

    batch_cnt = 0
    single_cnt = 0
    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        retry_total = 0
        while retry_total < 3:
            timeout = (5 * retry_total) * timeout_factor
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
        if retry_total == 3:
            raise OperationTimeoutError(f"Exhausted retries for receiving from {live_eventhub['hostname']}.")

    assert single_cnt == 60
    assert batch_cnt == 60
    assert len(found_partition_keys) == 6


@pytest.mark.parametrize("payload", [b"", b"A single event"])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_and_receive_small_body_async(connstr_receivers, payload, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
        batch = await client.create_batch()
        batch.add(EventData(payload))
        await client.send_batch(batch)
        await client.send_event(EventData(payload))
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=5 * timeout_factor)])

    assert len(received) == 2
    assert list(received[0].body)[0] == payload
    assert list(received[1].body)[0] == payload


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_partition_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)

    async with client:
        batch = await client.create_batch()
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        await client.send_event(EventData(b"Data"))


    async with client:
        batch = await client.create_batch(partition_id="1")
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        await client.send_event(EventData(b"Data"), partition_id="1")

    partition_0 = receivers[0].receive_message_batch(timeout=10 * timeout_factor)
    partition_1 = receivers[1].receive_message_batch(timeout=10 * timeout_factor)
    assert len(partition_1) >= 2
    assert len(partition_0) + len(partition_1) == 4

    async with client:
        batch = await client.create_batch()
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        await client.send_event(EventData(b"Data"))
    async with client:
        batch = await client.create_batch(partition_id="0")
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        await client.send_event(EventData(b"Data"), partition_id="0")
    async with client:
        batch = EventDataBatch(partition_id="0")
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)

    time.sleep(5)
    partition_0 = receivers[0].receive_message_batch(timeout=10 * timeout_factor)
    partition_1 = receivers[1].receive_message_batch(timeout=10 * timeout_factor)
    assert len(partition_0) >= 3
    assert len(partition_0) + len(partition_1) == 5


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_non_ascii_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
        batch = await client.create_batch(partition_id="0")
        batch.add(EventData(u"é,è,à,ù,â,ê,î,ô,û"))
        batch.add(EventData(json.dumps({"foo": u"漢字"})))
        await client.send_batch(batch)
        await client.send_event(EventData(u"é,è,à,ù,â,ê,î,ô,û"), partition_id="0")
        await client.send_event(EventData(json.dumps({"foo": u"漢字"})), partition_id="0")
    await asyncio.sleep(1)
    # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
    # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
    # So call it twice to ensure the two events are received.
    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5 * timeout_factor)] + \
                  [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5 * timeout_factor)]

    assert len(partition_0) == 4
    assert partition_0[0].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": u"漢字"}
    assert partition_0[2].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[3].body_as_json() == {"foo": u"漢字"}


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_multiple_partition_with_app_prop_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(
        connection_str,
        uamqp_transport=uamqp_transport,
        transport_type=TransportType.Amqp
    )
    async with client:
        ed0 = EventData(b"Message 0")
        ed0.properties = app_prop
        batch = await client.create_batch(partition_id="0")
        batch.add(ed0)
        await client.send_batch(batch)
        await client.send_event(ed0, partition_id="0")

        ed1 = EventData(b"Message 1")
        ed1.properties = app_prop
        batch = await client.create_batch(partition_id="1")
        batch.add(ed1)
        await client.send_batch(batch)
        await client.send_event(ed1, partition_id="1")
    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5 * timeout_factor)]
    assert len(partition_0) == 2
    assert partition_0[0].properties[b"raw_prop"] == b"raw_value"
    assert partition_0[1].properties[b"raw_prop"] == b"raw_value"
    partition_1 = [EventData._from_message(x) for x in receivers[1].receive_message_batch(timeout=5 * timeout_factor)]
    assert len(partition_0) == 2
    assert partition_1[0].properties[b"raw_prop"] == b"raw_value"
    assert partition_0[1].properties[b"raw_prop"] == b"raw_value"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_over_websocket_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str,
                                                           transport_type=uamqp_TransportType.AmqpOverWebsocket,
                                                           uamqp_transport=uamqp_transport)

    async with client:
        batch = await client.create_batch(partition_id="0")
        batch.add(EventData("Event Data"))
        await client.send_batch(batch)
        await client.send_event(EventData("Event Data"), partition_id="0")

    time.sleep(1)
    received = []
    received.extend(receivers[0].receive_message_batch(max_batch_size=5, timeout=10 * timeout_factor))
    assert len(received) == 2


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_create_event_batch_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(connection_str,
                                                           transport_type=TransportType.AmqpOverWebsocket,
                                                           uamqp_transport=uamqp_transport)
    async with client:
        event_data_batch = await client.create_batch(max_size_in_bytes=100000)
        while True:
            try:
                ed = EventData('A single event data')
                ed.properties = app_prop
                event_data_batch.add(ed)
            except ValueError:
                break
        await client.send_batch(event_data_batch)
        received = []
        for r in receivers:
            received.extend(r.receive_message_batch(timeout=10 * timeout_factor))
        assert len(received) >= 1
        assert EventData._from_message(received[0]).properties[b"raw_prop"] == b"raw_value"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(
        connection_str,
        uamqp_transport=uamqp_transport,
        transport_type=uamqp_TransportType.Amqp
    )
    payload = "A1"
    async with client:
        await client.send_batch([EventData(payload)])
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=10 * timeout_factor)])

    assert len(received) == 1
    assert received[0].body_as_str() == payload


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_partition_async(connstr_receivers, uamqp_transport, timeout_factor):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    payload = "A1"
    async with client:
        await client.send_batch([EventData(payload)], partition_id="0")
        message = receivers[0].receive_message_batch(timeout=10 * timeout_factor)[0]
        received = EventData._from_message(message)
    assert received.body_as_str() == payload


@pytest.mark.parametrize("to_send, exception_type",
                         [([EventData("A"*1024)]*1100, ValueError),
                          ("any str", AttributeError)
                          ])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_wrong_data_async(connection_str, to_send, exception_type, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    async with client:
        with pytest.raises(exception_type):
            await client.send_batch(to_send)


@pytest.mark.parametrize("partition_id, partition_key", [("0", None), (None, "pk")])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_batch_pid_pk_async(invalid_hostname, partition_id, partition_key, uamqp_transport):
    # Use invalid_hostname because this is not a live test.
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    batch = EventDataBatch(partition_id=partition_id, partition_key=partition_key)
    async with client:
        with pytest.raises(TypeError):
            await client.send_batch(batch, partition_id=partition_id, partition_key=partition_key)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_callback_async(connstr_receivers, uamqp_transport):

    async def on_error(events, pid, err):
        on_error.err = err

    async def on_success(events, pid):
        sent_events.append((events, pid))

    sent_events = []
    on_error.err = None
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str, on_success=on_success, on_error=on_error, uamqp_transport=uamqp_transport)

    async with client:
        batch = await client.create_batch()
        batch.add(EventData(b"Data"))
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        assert len(sent_events[-1][0]) == 2
        assert not sent_events[-1][1]
        await client.send_event(EventData(b"Data"))
        assert len(sent_events[-1][0]) == 1
        assert not sent_events[-1][1]

        batch = await client.create_batch(partition_key='key')
        batch.add(EventData(b"Data"))
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        assert len(sent_events[-1][0]) == 2
        assert not sent_events[-1][1]
        await client.send_event(EventData(b"Data"), partition_key='key')
        assert len(sent_events[-1][0]) == 1
        assert not sent_events[-1][1]

        batch = await client.create_batch(partition_id="0")
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)
        batch.add(EventData(b"Data"))
        assert len(sent_events[-1][0]) == 2
        assert sent_events[-1][1] == "0"
        await client.send_event(EventData(b"Data"), partition_id="0")
        assert len(sent_events[-1][0]) == 1
        assert sent_events[-1][1] == "0"

        assert not on_error.err
