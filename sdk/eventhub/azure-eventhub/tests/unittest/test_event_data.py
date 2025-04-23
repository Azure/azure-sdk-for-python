# -- coding: utf-8 --
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import platform
import pytest
import datetime
from packaging import version

try:
    import uamqp
    from azure.eventhub._transport._uamqp_transport import UamqpTransport
except (ModuleNotFoundError, ImportError):
    uamqp = None
    UamqpTransport = None
from azure.eventhub._transport._pyamqp_transport import PyamqpTransport
from azure.eventhub._pyamqp.message import Message, Properties, Header
from azure.eventhub._utils import CE_ZERO_SECONDS
from azure.eventhub._constants import PROP_TIMESTAMP
from azure.eventhub.amqp import AmqpAnnotatedMessage, AmqpMessageHeader, AmqpMessageProperties

from azure.eventhub import _common

pytestmark = pytest.mark.skipif(platform.python_implementation() == "PyPy", reason="This is ignored for PyPy")


from azure.eventhub import EventData, EventDataBatch


@pytest.mark.parametrize(
    "test_input, expected_result",
    [("", ""), ("AAA", "AAA"), (None, ValueError), (["a", "b", "c"], "abc"), (b"abc", "abc")],
)
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
        assert repr(
            event_data
        ) == "EventData(body='{}', properties={{}}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)".format(
            expected_result
        )
        with pytest.raises(TypeError):
            event_data.body_as_json()


def test_body_json():
    event_data = EventData('{"a":"b"}')
    assert str(event_data) == '{ body: \'{"a":"b"}\', properties: {} }'
    assert (
        repr(event_data)
        == 'EventData(body=\'{"a":"b"}\', properties={}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)'
    )
    jo = event_data.body_as_json()
    assert jo["a"] == "b"


def test_body_wrong_json():
    event_data = EventData("aaa")
    with pytest.raises(TypeError):
        event_data.body_as_json()


def test_app_properties():
    app_props = {"a": "b"}
    event_data = EventData("")
    event_data.properties = app_props
    assert str(event_data) == "{ body: '', properties: {'a': 'b'} }"
    assert (
        repr(event_data)
        == "EventData(body='', properties={'a': 'b'}, offset=None, sequence_number=None, partition_key=None, enqueued_time=None)"
    )
    assert event_data.properties["a"] == "b"


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
        message.annotations = {_common.PROP_OFFSET: "@latest", PROP_TIMESTAMP: CE_ZERO_SECONDS * 1000}
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
            reply_to_group_id="reply_to_group_id",
        )
        message_annotations = {_common.PROP_OFFSET: "@latest", PROP_TIMESTAMP: CE_ZERO_SECONDS * 1000}
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
    assert ed.enqueued_time == datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def test_event_data_batch(uamqp_transport):
    if uamqp_transport:
        if version.parse(uamqp.__version__) >= version.parse("1.2.8"):
            expected_result = 97
        else:
            expected_result = 93
        amqp_transport = UamqpTransport
    else:
        expected_result = 99
        amqp_transport = PyamqpTransport

    batch = EventDataBatch(max_size_in_bytes=110, partition_key="par", amqp_transport=amqp_transport)
    batch.add(EventData("A"))
    assert str(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"
    assert repr(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"

    assert batch.size_in_bytes == expected_result and len(batch) == 1

    with pytest.raises(ValueError):
        batch.add(EventData("A"))


def test_event_data_from_message(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport
    else:
        amqp_transport = PyamqpTransport
    annotated_message = AmqpAnnotatedMessage(data_body=b"A")
    message = amqp_transport.to_outgoing_amqp_message(annotated_message)
    event = EventData._from_message(message)
    assert event.content_type is None
    assert event.correlation_id is None
    assert event.message_id is None

    event.content_type = "content_type"
    event.correlation_id = "correlation_id"
    event.message_id = "message_id"
    assert event.content_type == "content_type"
    assert event.correlation_id == "correlation_id"
    assert event.message_id == "message_id"
    assert list(event.body) == [b"A"]


def test_amqp_message_str_repr():
    data_body = b"A"
    message = AmqpAnnotatedMessage(data_body=data_body)
    assert str(message) == "A"
    assert "AmqpAnnotatedMessage(body=A, body_type=data" in repr(message)


def test_outgoing_amqp_message_header_properties(uamqp_transport):
    if uamqp_transport:
        amqp_transport = UamqpTransport
    else:
        amqp_transport = PyamqpTransport
    ann_message = AmqpAnnotatedMessage(data_body=b"A")
    ann_message.header = AmqpMessageHeader()
    ann_message.properties = AmqpMessageProperties()
    amqp_message = amqp_transport.to_outgoing_amqp_message(ann_message)

    assert not amqp_message.header
    assert not amqp_message.properties

    ann_message = AmqpAnnotatedMessage(data_body=b"A")
    ann_message.header = AmqpMessageHeader()
    ann_message.properties = AmqpMessageProperties()
    ann_message.header.first_acquirer = False
    ann_message.properties.creation_time = 0
    amqp_message = amqp_transport.to_outgoing_amqp_message(ann_message)

    assert amqp_message.header
    assert amqp_message.properties

    ann_message = AmqpAnnotatedMessage(data_body=b"A")
    ann_message.header = AmqpMessageHeader()
    ann_message.properties = AmqpMessageProperties()
    ann_message.properties.message_id = ""
    ann_message.application_properties = {b"key": b"val"}
    amqp_message = amqp_transport.to_outgoing_amqp_message(ann_message)

    assert not amqp_message.header
    assert amqp_message.properties
    assert isinstance(amqp_message.application_properties, dict)


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
        header = Header(delivery_count=1, ttl=10000, first_acquirer=True, durable=True, priority=1)
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
            reply_to_group_id="reply_to_group_id",
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


def test_legacy_message(uamqp_transport):
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
        message = uamqp.message.Message(body=b"abc", header=header, properties=properties)
        message.annotations = {_common.PROP_OFFSET: "@latest"}
        amqp_transport = UamqpTransport
    else:
        header = Header(delivery_count=1, ttl=10000, first_acquirer=True, durable=True, priority=1)
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
            reply_to_group_id="reply_to_group_id",
        )
        message_annotations = {_common.PROP_OFFSET: "@latest"}
        message = Message(data=b"abc", properties=properties, header=header, message_annotations=message_annotations)
        amqp_transport = PyamqpTransport
    event_data = EventData._from_message(message=message)
    assert event_data.message.properties.user_id == b"user_id"
    assert event_data.message.properties.message_id == b"message_id"
    assert event_data.message.properties.to == b"to"
    assert event_data.message.properties.subject == b"subject"
    assert event_data.message.properties.reply_to == b"reply_to"
    assert event_data.message.properties.correlation_id == b"correlation_id"
    assert event_data.message.properties.content_type == b"content_type"
    assert event_data.message.properties.content_encoding == b"content_encoding"
    assert event_data.message.properties.absolute_expiry_time == 1
    assert event_data.message.properties.creation_time == 1
    assert event_data.message.properties.group_id == b"group_id"
    assert event_data.message.properties.group_sequence == 1
    assert event_data.message.properties.reply_to_group_id == b"reply_to_group_id"
    assert event_data.message.state.value == 2
    assert event_data.message.delivery_annotations == {}
    assert event_data.message.delivery_no is None
    assert event_data.message.delivery_tag is None
    assert event_data.message.on_send_complete is None
    assert event_data.message.footer == {}
    assert event_data.message.retries == 0
    assert event_data.message.idle_time == 0

    event_data_batch = EventDataBatch(partition_key=b"par", partition_id="1", amqp_transport=amqp_transport)
    event_data_batch.add(event_data)
    assert event_data_batch.message.max_message_length == 1024 * 1024
    assert event_data_batch.message.size_offset == 0
    assert event_data_batch.message.batch_format == 0x80013700
    assert len(event_data_batch.message.annotations) == 1
    assert event_data_batch.message.application_properties is None
    assert event_data_batch.message.header.delivery_count == 0
    assert event_data_batch.message.header.time_to_live is None
    assert event_data_batch.message.header.first_acquirer is None
    assert event_data_batch.message.header.durable is True
    assert event_data_batch.message.header.priority is None
    assert event_data_batch.message.on_send_complete is None
    assert event_data_batch.message.properties is None

def test_from_bytes(uamqp_transport):
    if uamqp_transport:
        pytest.skip("This test is only for pyamqp transport")
    data = b'\x00Sr\xc1\x87\x08\xa3\x1bx-opt-sequence-number-epochT\xff\xa3\x15x-opt-sequence-numberU\x00\xa3\x0cx-opt-offsetU\x00\xa3\x13x-opt-enqueued-time\x00\xa3\x1dcom.microsoft:datetime-offset\x83\x00\x00\x01\x95\xf3XB\x86\x00St\xc1I\x02\xa1\rDiagnostic-Id\xa1700-1aa201483d464ac3c3d2ab796fbccb36-72e947bb22f404fc-00\x00Su\xa0\x08message1'

    event_data = EventData.from_bytes(data)
    assert event_data.body_as_str() == 'message1'
    assert event_data.sequence_number == 0
    assert event_data.offset is None
    assert event_data.properties == {b'Diagnostic-Id': b'00-1aa201483d464ac3c3d2ab796fbccb36-72e947bb22f404fc-00'}
    assert event_data.partition_key is None
    assert isinstance(event_data.enqueued_time, datetime.datetime)