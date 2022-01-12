import platform
import pytest
from packaging import version
from azure.eventhub.amqp import AmqpAnnotatedMessage
from azure.eventhub import _common
from azure.eventhub._pyamqp.message import Message, Properties

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


def test_sys_properties():
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


def test_event_data_batch():
    batch = EventDataBatch(max_size_in_bytes=110, partition_key="par")
    batch.add(EventData("A"))
    assert str(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"
    assert repr(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"

    # TODO: uamqp uses 93 bytes for encode, while python amqp uses 99 bytes
    #  we should understand why extra bytes are needed to encode the content and how it could be improved
    assert batch.size_in_bytes == 99 and len(batch) == 1

    with pytest.raises(ValueError):
        batch.add(EventData("A"))


def test_event_data_from_message():
    message = Message(data=b'A')
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
    assert event.body == b'A'


def test_amqp_message_str_repr():
    data_body = b'A'
    message = AmqpAnnotatedMessage(data_body=data_body)
    assert str(message) == 'A'
    assert 'AmqpAnnotatedMessage(body=A, body_type=data' in repr(message)
