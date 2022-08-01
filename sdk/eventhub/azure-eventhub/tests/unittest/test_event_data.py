# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import platform
import pytest
from packaging import version
try:
    import uamqp
    from azure.eventhub._transport._uamqp_transport import UamqpTransport 
except ImportError:
    UamqpTransport = None
    pass
from azure.eventhub._transport._pyamqp_transport import PyamqpTransport
from azure.eventhub.amqp import AmqpAnnotatedMessage, AmqpMessageHeader, AmqpMessageProperties
from azure.eventhub import _common
from azure.eventhub._pyamqp.message import Message, Properties, Header
from azure.eventhub._utils import transform_outbound_single_message
from .._test_case import get_decorator

uamqp_transport_vals = get_decorator()

pytestmark = pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="This is ignored for PyPy")


from azure.eventhub import EventData, EventDataBatch


@pytest.mark.parametrize("test_input, expected_result",
                         [("", ""), ("AAA", "AAA"), (None, ValueError), (["a", "b", "c"], "abc"), (b"abc", "abc")])
def test_constructor(test_input, expected_result):
    if isinstance(expected_result, type):
        with pytest.raises(expected_result):
            EventData(test_input)
    else:
        event_data = EventData(test_input)
        assert event_data.body_as_str() == expected_result
        assert event_data.partition_key is None
        assert len(event_data.properties) == 0
        assert event_data.enqueued_time is None
        assert event_data.offset is None
        assert event_data.sequence_number is None
        assert len(event_data.system_properties) == 0
        assert str(event_data) == "{{ body: '{}', properties: {{}} }}".format(expected_result)
        assert repr(event_data) == "EventData(body='{}', properties={{}}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)".format(expected_result)
        with pytest.raises(TypeError):
            event_data.body_as_json()


def test_body_json():
    event_data = EventData('{"a":"b"}')
    assert str(event_data) == "{ body: '{\"a\":\"b\"}', properties: {} }"
    assert repr(event_data) == "EventData(body='{\"a\":\"b\"}', properties={}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)"
    jo = event_data.body_as_json()
    assert jo["a"] == "b"


def test_body_wrong_json():
    event_data = EventData('aaa')
    with pytest.raises(TypeError):
        event_data.body_as_json()


def test_app_properties():
    app_props = {"a": "b"}
    event_data = EventData("")
    event_data.properties = app_props
    assert str(event_data) == "{ body: '', properties: {'a': 'b'} }"
    assert repr(event_data) == "EventData(body='', properties={'a': 'b'}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)"
    assert event_data.properties["a"] == "b"


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_sys_properties(uamqp_transport):
    if uamqp_transport:
        properties = uamqp.message.MessageProperties()
        properties.message_id = "message_id"
        properties.user_id = "user_id"
        properties.to = "to"
        properties.subject = "subject"
        properties.reply_to = "reply_to"
        properties.correlation_id = "correlation_id"
        properties.content_type = "content_type"
        properties.content_encoding = "content_encoding"
        properties.absolute_expiry_time = 1
        properties.creation_time = 1
        properties.group_id = "group_id"
        properties.group_sequence = 1
        properties.reply_to_group_id = "reply_to_group_id"
        message = uamqp.message.Message(properties=properties)
        message.annotations = {_common.PROP_OFFSET: "@latest"}
    else:
        properties = Properties(
            message_id="message_id",
            user_id="user_id",
            to="to",
            subject="subject",
            reply_to="reply_to",
            correlation_id="correlation_id",
            content_type="content_type",
            content_encoding="content_encoding",
            absolute_expiry_time=1,
            creation_time=1,
            group_id="group_id",
            group_sequence=1,
            reply_to_group_id="reply_to_group_id"
        )
        message_annotations = {_common.PROP_OFFSET: "@latest"}
        message = Message(properties=properties, message_annotations=message_annotations)
    ed = EventData._from_message(message)  # type: EventData

    assert ed.system_properties[_common.PROP_OFFSET] == "@latest"
    assert ed.system_properties[_common.PROP_CORRELATION_ID] == properties.correlation_id
    assert ed.system_properties[_common.PROP_MESSAGE_ID] == properties.message_id
    assert ed.system_properties[_common.PROP_CONTENT_ENCODING] == properties.content_encoding
    assert ed.system_properties[_common.PROP_CONTENT_TYPE] == properties.content_type
    assert ed.system_properties[_common.PROP_USER_ID] == properties.user_id
    assert ed.system_properties[_common.PROP_TO] == properties.to
    assert ed.system_properties[_common.PROP_SUBJECT] == properties.subject
    assert ed.system_properties[_common.PROP_REPLY_TO] == properties.reply_to
    assert ed.system_properties[_common.PROP_ABSOLUTE_EXPIRY_TIME] == properties.absolute_expiry_time
    assert ed.system_properties[_common.PROP_CREATION_TIME] == properties.creation_time
    assert ed.system_properties[_common.PROP_GROUP_ID] == properties.group_id
    assert ed.system_properties[_common.PROP_GROUP_SEQUENCE] == properties.group_sequence
    assert ed.system_properties[_common.PROP_REPLY_TO_GROUP_ID] == properties.reply_to_group_id


# TODO: see why pyamqp went from 99 to 87
@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_event_data_batch(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport()
        if version.parse(uamqp.__version__) >= version.parse("1.2.8"):
            expected_result = 101
        else:
            expected_result = 93
    else:
        amqp_transport = PyamqpTransport()
        expected_result = 87
    batch = EventDataBatch(max_size_in_bytes=110, partition_key="par", amqp_transport=amqp_transport)
    batch.add(EventData("A"))
    assert str(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"
    assert repr(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"

    assert batch.size_in_bytes == expected_result and len(batch) == 1

    with pytest.raises(ValueError):
        batch.add(EventData("A"))


@pytest.mark.parametrize("uamqp_transport", uamqp_transport_vals)
def test_event_data_from_message(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport()
    else:
        amqp_transport = PyamqpTransport()
    annotated_message = AmqpAnnotatedMessage(data_body=b'A')
    message = amqp_transport.to_outgoing_amqp_message(annotated_message)
    event = EventData._from_message(message)
    assert event.content_type is None
    assert event.correlation_id is None
    assert event.message_id is None

    event.content_type = 'content_type'
    event.correlation_id = 'correlation_id'
    event.message_id = 'message_id'
    assert event.content_type == 'content_type'
    assert event.correlation_id == 'correlation_id'
    assert event.message_id == 'message_id'
    assert list(event.body) == [b'A']


def test_amqp_message_str_repr():
    data_body = b'A'
    message = AmqpAnnotatedMessage(data_body=data_body)
    assert str(message) == 'A'
    assert 'AmqpAnnotatedMessage(body=A, body_type=data' in repr(message)


@pytest.mark.parametrize("uamqp_transport",
                         uamqp_transport_vals)
def test_amqp_message_from_message(uamqp_transport):
    if uamqp_transport:
        header = uamqp.message.MessageHeader()
        header.delivery_count = 1
        header.time_to_live = 10000
        header.first_acquirer = True
        header.durable = True
        header.priority = 1
        properties = uamqp.message.MessageProperties()
        properties.message_id = "message_id"
        properties.user_id = "user_id"
        properties.to = "to"
        properties.subject = "subject"
        properties.reply_to = "reply_to"
        properties.correlation_id = "correlation_id"
        properties.content_type = "content_type"
        properties.content_encoding = "content_encoding"
        properties.absolute_expiry_time = 1
        properties.creation_time = 1
        properties.group_id = "group_id"
        properties.group_sequence = 1
        properties.reply_to_group_id = "reply_to_group_id"
        message = uamqp.message.Message(header=header, properties=properties)
        message.annotations = {_common.PROP_OFFSET: "@latest"}
    else:
        header = Header(
            delivery_count=1,
            ttl=10000,
            first_acquirer=True,
            durable=True,
            priority=1
        )
        properties = Properties(
            message_id="message_id",
            user_id="user_id",
            to="to",
            subject="subject",
            reply_to="reply_to",
            correlation_id="correlation_id",
            content_type="content_type",
            content_encoding="content_encoding",
            absolute_expiry_time=1,
            creation_time=1,
            group_id="group_id",
            group_sequence=1,
            reply_to_group_id="reply_to_group_id"
        )
        message_annotations = {_common.PROP_OFFSET: "@latest"}
        message = Message(properties=properties, header=header, message_annotations=message_annotations)

    amqp_message = AmqpAnnotatedMessage(message=message)
    assert amqp_message.properties.message_id == message.properties.message_id
    assert amqp_message.properties.user_id == message.properties.user_id
    assert amqp_message.properties.to == message.properties.to
    assert amqp_message.properties.subject == message.properties.subject
    assert amqp_message.properties.reply_to == message.properties.reply_to
    assert amqp_message.properties.correlation_id == message.properties.correlation_id
    assert amqp_message.properties.content_type == message.properties.content_type
    assert amqp_message.properties.absolute_expiry_time == message.properties.absolute_expiry_time
    assert amqp_message.properties.creation_time == message.properties.creation_time
    assert amqp_message.properties.group_id == message.properties.group_id
    assert amqp_message.properties.group_sequence == message.properties.group_sequence
    assert amqp_message.properties.reply_to_group_id == message.properties.reply_to_group_id
    assert amqp_message.header.time_to_live == message.header.ttl
    assert amqp_message.header.delivery_count == message.header.delivery_count
    assert amqp_message.header.first_acquirer == message.header.first_acquirer
    assert amqp_message.header.durable == message.header.durable
    assert amqp_message.header.priority == message.header.priority
    assert amqp_message.annotations == message.message_annotations
