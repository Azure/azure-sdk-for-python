# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import platform
import pytest
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
        expected_result = 101
    else:
        amqp_transport = PyamqpTransport()
        expected_result = 87
    batch = EventDataBatch(max_size_in_bytes=110, partition_key="par", amqp_transport=amqp_transport)
    batch.add(EventData("A"))
    assert str(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"
    assert repr(batch) == "EventDataBatch(max_size_in_bytes=110, partition_id=None, partition_key='par', event_count=1)"

    # TODO: uamqp uses 93 bytes for encode, while python amqp uses 99 bytes
    #  we should understand why extra bytes are needed to encode the content and how it could be improved
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

# TODO: ADD MESSAGE BACKCOMPAT TESTS
#class EventDataMessageBackcompatTests:
#
#    def test_message_backcompat_receive_and_delete_databody():
#        outgoing_event_data = EventData(body="hello")
#        outgoing_event_data.application_properties = {'prop': 'test'}
#        outgoing_event_data.session_id = "id_session"
#        outgoing_event_data.message_id = "id_message"
#        outgoing_event_data.time_to_live = timedelta(seconds=30)
#        outgoing_event_data.content_type = "content type"
#        outgoing_event_data.correlation_id = "correlation"
#        outgoing_event_data.subject = "github"
#        outgoing_event_data.partition_key = "id_session"
#        outgoing_event_data.to = "forward to"
#        outgoing_event_data.reply_to = "reply to"
#        outgoing_event_data.reply_to_session_id = "reply to session"
#
#        # TODO: Attribute shouldn't exist until after message has been sent.
#        # with pytest.raises(AttributeError):
#        #     outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=True)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        assert outgoing_message.message
#        with pytest.raises(TypeError):
#            outgoing_message.message.accept()
#        with pytest.raises(TypeError):
#            outgoing_message.message.release()
#        with pytest.raises(TypeError):
#            outgoing_message.message.reject()
#        with pytest.raises(TypeError):
#            outgoing_message.message.modify(True, True)
#        assert outgoing_message.message.state == uamqp.constants.MessageState.SendComplete
#        assert outgoing_message.message.settled
#        assert outgoing_message.message.delivery_annotations is None
#        assert outgoing_message.message.delivery_no is None
#        assert outgoing_message.message.delivery_tag is None
#        assert outgoing_message.message.on_send_complete is None
#        assert outgoing_message.message.footer is None
#        assert outgoing_message.message.retries >= 0
#        assert outgoing_message.message.idle_time >= 0
#        with pytest.raises(Exception):
#            outgoing_message.message.gather()
#        assert isinstance(outgoing_message.message.encode_message(), bytes)
#        assert outgoing_message.message.get_message_encoded_size() == 208
#        assert list(outgoing_message.message.get_data()) == [b'hello']
#        assert outgoing_message.message.application_properties == {'prop': 'test'}
#        assert outgoing_message.message.get_message()  # C instance.
#        assert len(outgoing_message.message.annotations) == 1
#        assert list(outgoing_message.message.annotations.values())[0] == 'id_session'
#        assert str(outgoing_message.message.header) == str({'delivery_count': None, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
#        assert outgoing_message.message.header.get_header_obj().delivery_count is None
#        assert outgoing_message.message.properties.message_id == b'id_message'
#        assert outgoing_message.message.properties.user_id is None
#        assert outgoing_message.message.properties.to == b'forward to'
#        assert outgoing_message.message.properties.subject == b'github'
#        assert outgoing_message.message.properties.reply_to == b'reply to'
#        assert outgoing_message.message.properties.correlation_id == b'correlation'
#        assert outgoing_message.message.properties.content_type == b'content type'
#        assert outgoing_message.message.properties.content_encoding is None
#        assert outgoing_message.message.properties.absolute_expiry_time
#        assert outgoing_message.message.properties.creation_time
#        assert outgoing_message.message.properties.group_id == b'id_session'
#        assert outgoing_message.message.properties.group_sequence is None
#        assert outgoing_message.message.properties.reply_to_group_id == b'reply to session'
#        assert outgoing_message.message.properties.get_properties_obj().message_id
#
#        # TODO: Test updating message and resending
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            assert incoming_message.message.delivery_annotations == {}
#            assert incoming_message.message.delivery_no >= 1
#            assert incoming_message.message.delivery_tag is None
#            assert incoming_message.message.on_send_complete is None
#            assert incoming_message.message.footer is None
#            assert incoming_message.message.retries >= 0
#            assert incoming_message.message.idle_time == 0
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert isinstance(incoming_message.message.encode_message(), bytes)
#            # TODO: Pyamqp has size at 266
#            # assert incoming_message.message.get_message_encoded_size() == 267
#            assert list(incoming_message.message.get_data()) == [b'hello']
#            assert incoming_message.message.application_properties == {b'prop': b'test'}
#            assert incoming_message.message.get_message()  # C instance.
#            assert len(incoming_message.message.annotations) == 3
#            assert incoming_message.message.annotations[b'x-opt-enqueued-time'] > 0
#            assert incoming_message.message.annotations[b'x-opt-sequence-number'] > 0
#            assert incoming_message.message.annotations[b'x-opt-partition-key'] == b'id_session'
#            # TODO: Pyamqp has header {'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None}
#            # assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': True, 'durable': True, 'priority': 4})
#            assert incoming_message.message.header.get_header_obj().delivery_count == 0
#            assert incoming_message.message.properties.message_id == b'id_message'
#            assert incoming_message.message.properties.user_id is None
#            assert incoming_message.message.properties.to == b'forward to'
#            assert incoming_message.message.properties.subject == b'github'
#            assert incoming_message.message.properties.reply_to == b'reply to'
#            assert incoming_message.message.properties.correlation_id == b'correlation'
#            assert incoming_message.message.properties.content_type == b'content type'
#            assert incoming_message.message.properties.content_encoding is None
#            assert incoming_message.message.properties.absolute_expiry_time
#            assert incoming_message.message.properties.creation_time
#            assert incoming_message.message.properties.group_id == b'id_session'
#            assert incoming_message.message.properties.group_sequence is None
#            assert incoming_message.message.properties.reply_to_group_id == b'reply to session'
#            assert incoming_message.message.properties.get_properties_obj().message_id
#            assert not incoming_message.message.accept()
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#            # TODO: Test updating message and resending
#
#    @pytest.mark.liveTest
#    @pytest.mark.live_test_only
#    @CachedResourceGroupPreparer(name_prefix='servicebustest')
#    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
#    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
#    def test_message_backcompat_peek_lock_databody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
#        queue_name = servicebus_queue.name
#        outgoing_message = ServiceBusMessage(
#            body="hello",
#            application_properties={'prop': 'test'},
#            session_id="id_session",
#            message_id="id_message",
#            time_to_live=timedelta(seconds=30),
#            content_type="content type",
#            correlation_id="correlation",
#            subject="github",
#            partition_key="id_session",
#            to="forward to",
#            reply_to="reply to",
#            reply_to_session_id="reply to session"
#        )
#
#        # TODO: Attribute shouldn't exist until after message has been sent.
#        # with pytest.raises(AttributeError):
#        #     outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=True)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        assert outgoing_message.message
#        with pytest.raises(TypeError):
#            outgoing_message.message.accept()
#        with pytest.raises(TypeError):
#            outgoing_message.message.release()
#        with pytest.raises(TypeError):
#            outgoing_message.message.reject()
#        with pytest.raises(TypeError):
#            outgoing_message.message.modify(True, True)
#        assert outgoing_message.message.state == uamqp.constants.MessageState.SendComplete
#        assert outgoing_message.message.settled
#        assert outgoing_message.message.delivery_annotations is None
#        assert outgoing_message.message.delivery_no is None
#        assert outgoing_message.message.delivery_tag is None
#        assert outgoing_message.message.on_send_complete is None
#        assert outgoing_message.message.footer is None
#        assert outgoing_message.message.retries >= 0
#        assert outgoing_message.message.idle_time >= 0
#        with pytest.raises(Exception):
#            outgoing_message.message.gather()
#        assert isinstance(outgoing_message.message.encode_message(), bytes)
#        assert outgoing_message.message.get_message_encoded_size() == 208
#        assert list(outgoing_message.message.get_data()) == [b'hello']
#        assert outgoing_message.message.application_properties == {'prop': 'test'}
#        assert outgoing_message.message.get_message()  # C instance.
#        assert len(outgoing_message.message.annotations) == 1
#        assert list(outgoing_message.message.annotations.values())[0] == 'id_session'
#        assert str(outgoing_message.message.header) == str({'delivery_count': None, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
#        assert outgoing_message.message.header.get_header_obj().delivery_count is None
#        assert outgoing_message.message.properties.message_id == b'id_message'
#        assert outgoing_message.message.properties.user_id is None
#        assert outgoing_message.message.properties.to == b'forward to'
#        assert outgoing_message.message.properties.subject == b'github'
#        assert outgoing_message.message.properties.reply_to == b'reply to'
#        assert outgoing_message.message.properties.correlation_id == b'correlation'
#        assert outgoing_message.message.properties.content_type == b'content type'
#        assert outgoing_message.message.properties.content_encoding is None
#        assert outgoing_message.message.properties.absolute_expiry_time
#        assert outgoing_message.message.properties.creation_time
#        assert outgoing_message.message.properties.group_id == b'id_session'
#        assert outgoing_message.message.properties.group_sequence is None
#        assert outgoing_message.message.properties.reply_to_group_id == b'reply to session'
#        assert outgoing_message.message.properties.get_properties_obj().message_id
#
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
#            assert not incoming_message.message.settled
#            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
#            assert incoming_message.message.delivery_no >= 1
#            assert incoming_message.message.delivery_tag
#            assert incoming_message.message.on_send_complete is None
#            assert incoming_message.message.footer is None
#            assert incoming_message.message.retries >= 0
#            assert incoming_message.message.idle_time == 0
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert isinstance(incoming_message.message.encode_message(), bytes)
#            # TODO: Pyamqp has size at 336
#            # assert incoming_message.message.get_message_encoded_size() == 334
#            assert list(incoming_message.message.get_data()) == [b'hello']
#            assert incoming_message.message.application_properties == {b'prop': b'test'}
#            assert incoming_message.message.get_message()  # C instance.
#            assert len(incoming_message.message.annotations) == 4
#            assert incoming_message.message.annotations[b'x-opt-enqueued-time'] > 0
#            assert incoming_message.message.annotations[b'x-opt-sequence-number'] > 0
#            assert incoming_message.message.annotations[b'x-opt-partition-key'] == b'id_session'
#            assert incoming_message.message.annotations[b'x-opt-locked-until']
#            # TODO: Pyamqp has header {'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None}
#            # assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': True, 'durable': True, 'priority': 4})
#            assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
#            assert incoming_message.message.header.get_header_obj().delivery_count == 0
#            assert incoming_message.message.properties.message_id == b'id_message'
#            assert incoming_message.message.properties.user_id is None
#            assert incoming_message.message.properties.to == b'forward to'
#            assert incoming_message.message.properties.subject == b'github'
#            assert incoming_message.message.properties.reply_to == b'reply to'
#            assert incoming_message.message.properties.correlation_id == b'correlation'
#            assert incoming_message.message.properties.content_type == b'content type'
#            assert incoming_message.message.properties.content_encoding is None
#            assert incoming_message.message.properties.absolute_expiry_time
#            assert incoming_message.message.properties.creation_time
#            assert incoming_message.message.properties.group_id == b'id_session'
#            assert incoming_message.message.properties.group_sequence is None
#            assert incoming_message.message.properties.reply_to_group_id == b'reply to session'
#            assert incoming_message.message.properties.get_properties_obj().message_id
#            assert incoming_message.message.accept()
#            # TODO: State isn't updated if settled correctly via the receiver.
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#    @pytest.mark.liveTest
#    @pytest.mark.live_test_only
#    @CachedResourceGroupPreparer(name_prefix='servicebustest')
#    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
#    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
#    def test_message_backcompat_receive_and_delete_valuebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
#        queue_name = servicebus_queue.name
#        outgoing_message = AmqpAnnotatedMessage(value_body={b"key": b"value"})
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=False)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert incoming_message.message.get_data() == {b"key": b"value"}
#            assert not incoming_message.message.accept()
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#    @pytest.mark.liveTest
#    @pytest.mark.live_test_only
#    @CachedResourceGroupPreparer(name_prefix='servicebustest')
#    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
#    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
#    def test_message_backcompat_peek_lock_valuebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
#        queue_name = servicebus_queue.name
#        outgoing_message = AmqpAnnotatedMessage(value_body={b"key": b"value"})
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=False)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
#            assert not incoming_message.message.settled
#            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
#            assert incoming_message.message.delivery_no >= 1
#            assert incoming_message.message.delivery_tag
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert incoming_message.message.get_data() == {b"key": b"value"}
#            assert incoming_message.message.accept()
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#    @pytest.mark.liveTest
#    @pytest.mark.live_test_only
#    @CachedResourceGroupPreparer(name_prefix='servicebustest')
#    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
#    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
#    def test_message_backcompat_receive_and_delete_sequencebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
#        queue_name = servicebus_queue.name
#        outgoing_message = AmqpAnnotatedMessage(sequence_body=[1, 2, 3])
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=False)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert list(incoming_message.message.get_data()) == [[1, 2, 3]]
#            assert not incoming_message.message.accept()
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#    @pytest.mark.liveTest
#    @pytest.mark.live_test_only
#    @CachedResourceGroupPreparer(name_prefix='servicebustest')
#    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
#    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
#    def test_message_backcompat_peek_lock_sequencebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
#        queue_name = servicebus_queue.name
#        outgoing_message = AmqpAnnotatedMessage(sequence_body=[1, 2, 3])
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        sb_client = ServiceBusClient.from_connection_string(
#        servicebus_namespace_connection_string, logging_enable=False)
#        with sb_client.get_queue_sender(queue_name) as sender:
#            sender.send_messages(outgoing_message)
#
#        with pytest.raises(AttributeError):
#            outgoing_message.message
#
#        with sb_client.get_queue_receiver(queue_name,
#                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
#                                            max_wait_time=10) as receiver:
#            batch = receiver.receive_messages()
#            incoming_message = batch[0]
#            assert incoming_message.message
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
#            assert not incoming_message.message.settled
#            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
#            assert incoming_message.message.delivery_no >= 1
#            assert incoming_message.message.delivery_tag
#            with pytest.raises(Exception):
#                incoming_message.message.gather()
#            assert list(incoming_message.message.get_data()) == [[1, 2, 3]]
#            assert incoming_message.message.accept()
#            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
#            assert incoming_message.message.settled
#            assert not incoming_message.message.release()
#            assert not incoming_message.message.reject()
#            assert not incoming_message.message.modify(True, True)
#
#    # TODO: Add batch message backcompat tests
