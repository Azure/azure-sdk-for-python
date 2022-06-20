from __future__ import annotations
import uamqp
import os
import pytest
from datetime import datetime, timedelta
from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage,
    ServiceBusReceivedMessage,
    ServiceBusMessageState,
    ServiceBusReceiveMode
)
from azure.servicebus._common.constants import (
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_SCHEDULED_ENQUEUE_TIME
)
from azure.servicebus.amqp import (
    AmqpAnnotatedMessage,
    AmqpMessageBodyType,
    AmqpMessageProperties,
    AmqpMessageHeader
)

from devtools_testutils import AzureMgmtTestCase, CachedResourceGroupPreparer
from servicebus_preparer import CachedServiceBusNamespacePreparer, ServiceBusQueuePreparer


def test_servicebus_message_repr():
    message = ServiceBusMessage("hello")
    assert "application_properties=None, session_id=None," in message.__repr__()
    assert "content_type=None, correlation_id=None, to=None, reply_to=None, reply_to_session_id=None, subject=None, time_to_live=None, partition_key=None, scheduled_enqueue_time_utc" in message.__repr__()


def test_servicebus_message_repr_with_props():
    message = ServiceBusMessage(
        body="hello",
        application_properties={'prop': 'test'},
        session_id="id_session",
        message_id="id_message",
        scheduled_enqueue_time_utc=datetime.now(),
        time_to_live=timedelta(seconds=30),
        content_type="content type",
        correlation_id="correlation",
        subject="github",
        partition_key="id_session",
        to="forward to",
        reply_to="reply to",
        reply_to_session_id="reply to session"
        )
    assert "application_properties={'prop': 'test'}, session_id=id_session," in message.__repr__()
    assert "content_type=content type, correlation_id=correlation, to=forward to, reply_to=reply to, reply_to_session_id=reply to session, subject=github, time_to_live=0:00:30, partition_key=id_session, scheduled_enqueue_time_utc" in message.__repr__()


def test_servicebus_received_message_repr():
    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
            _X_OPT_PARTITION_KEY: b'r_key',
            _X_OPT_VIA_PARTITION_KEY: b'r_via_key',
            _X_OPT_SCHEDULED_ENQUEUE_TIME: 123424566,
        },
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    repr_str = received_message.__repr__()
    assert "application_properties=None, session_id=None" in repr_str
    assert "content_type=None, correlation_id=None, to=None, reply_to=None, reply_to_session_id=None, subject=None,"
    assert "partition_key=r_key, scheduled_enqueue_time_utc" in repr_str

def test_servicebus_received_state():
    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
            b"x-opt-message-state": 3
        },
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    assert received_message.state == 3

    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
            b"x-opt-message-state": 1
        },
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    assert received_message.state == ServiceBusMessageState.DEFERRED

    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
        },
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    assert received_message.state == ServiceBusMessageState.ACTIVE

    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    assert received_message.state == ServiceBusMessageState.ACTIVE

    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
            b"x-opt-message-state": 0
        },
        properties=uamqp.message.MessageProperties()
    )
    received_message = ServiceBusReceivedMessage(uamqp_received_message, receiver=None)
    assert received_message.state == ServiceBusMessageState.ACTIVE

def test_servicebus_received_message_repr_with_props():
    uamqp_received_message = uamqp.message.Message(
        body=b'data',
        annotations={
            _X_OPT_PARTITION_KEY: b'r_key',
            _X_OPT_VIA_PARTITION_KEY: b'r_via_key',
            _X_OPT_SCHEDULED_ENQUEUE_TIME: 123424566,
        },
        properties=uamqp.message.MessageProperties(
            message_id="id_message",
            absolute_expiry_time=100,
            content_type="content type",
            correlation_id="correlation",
            subject="github",
            group_id="id_session",
            reply_to="reply to",
            reply_to_group_id="reply to group"
        )
    )
    received_message = ServiceBusReceivedMessage(
        message=uamqp_received_message,
        receiver=None,
        )
    assert "application_properties=None, session_id=id_session" in received_message.__repr__()
    assert "content_type=content type, correlation_id=correlation, to=None, reply_to=reply to, reply_to_session_id=reply to group, subject=github" in received_message.__repr__()
    assert "partition_key=r_key, scheduled_enqueue_time_utc" in received_message.__repr__()


def test_amqp_message():
    sb_message = ServiceBusMessage(body=None)
    assert sb_message.body_type == AmqpMessageBodyType.VALUE
    assert not sb_message.body

    amqp_annotated_message = AmqpAnnotatedMessage(data_body=b"data")
    assert amqp_annotated_message.body_type == AmqpMessageBodyType.DATA
    body = [data for data in amqp_annotated_message.body]
    assert len(body) == 1
    assert body[0] == b"data"

    amqp_annotated_message = AmqpAnnotatedMessage(value_body={b"key": b"value"})
    assert amqp_annotated_message.body_type == AmqpMessageBodyType.VALUE
    assert amqp_annotated_message.body == {b"key": b"value"}

    amqp_annotated_message = AmqpAnnotatedMessage(sequence_body=[1, 2, 3])
    body = [sequence for sequence in amqp_annotated_message.body]
    assert amqp_annotated_message.body_type == AmqpMessageBodyType.SEQUENCE
    assert len(body) == 1
    assert body[0] == [1, 2, 3]

    amqp_annotated_message = AmqpAnnotatedMessage(
        value_body=None,
        header=AmqpMessageHeader(priority=1, delivery_count=1, time_to_live=1, first_acquirer=True, durable=True),
        properties=AmqpMessageProperties(message_id='id', user_id='id', to='to', subject='sub', correlation_id='cid', content_type='ctype', content_encoding='cencoding', creation_time=1, absolute_expiry_time=1, group_id='id', group_sequence=1, reply_to_group_id='id'),
        footer={"key": "value"},
        delivery_annotations={"key": "value"},
        annotations={"key": "value"},
        application_properties={"key": "value"}
    )

    assert amqp_annotated_message.body_type == AmqpMessageBodyType.VALUE
    assert amqp_annotated_message.header.priority == 1
    assert amqp_annotated_message.header.delivery_count == 1
    assert amqp_annotated_message.header.time_to_live == 1
    assert amqp_annotated_message.header.first_acquirer
    assert amqp_annotated_message.header.durable

    assert amqp_annotated_message.footer == {"key": "value"}
    assert amqp_annotated_message.delivery_annotations == {"key": "value"}
    assert amqp_annotated_message.annotations == {"key": "value"}
    assert amqp_annotated_message.application_properties == {"key": "value"}

    assert amqp_annotated_message.properties.message_id == 'id'
    assert amqp_annotated_message.properties.user_id == 'id'
    assert amqp_annotated_message.properties.to == 'to'
    assert amqp_annotated_message.properties.subject == 'sub'
    assert amqp_annotated_message.properties.correlation_id == 'cid'
    assert amqp_annotated_message.properties.content_type == 'ctype'
    assert amqp_annotated_message.properties.content_encoding == 'cencoding'
    assert amqp_annotated_message.properties.creation_time == 1
    assert amqp_annotated_message.properties.absolute_expiry_time == 1
    assert amqp_annotated_message.properties.group_id == 'id'
    assert amqp_annotated_message.properties.group_sequence == 1
    assert amqp_annotated_message.properties.reply_to_group_id == 'id'

    amqp_annotated_message = AmqpAnnotatedMessage(
        value_body=None,
        header={"priority": 1, "delivery_count": 1, "time_to_live": 1, "first_acquirer": True, "durable": True},
        properties={
            "message_id": "id",
            "user_id": "id",
            "to": "to",
            "subject": "sub",
            "correlation_id": "cid",
            "content_type": "ctype",
            "content_encoding": "cencoding",
            "creation_time": 1,
            "absolute_expiry_time": 1,
            "group_id": "id",
            "group_sequence": 1,
            "reply_to_group_id": "id"
        },
        footer={"key": "value"},
        delivery_annotations={"key": "value"},
        annotations={"key": "value"},
        application_properties={"key": "value"}
    )

    assert amqp_annotated_message.body_type == AmqpMessageBodyType.VALUE
    assert amqp_annotated_message.header.priority == 1
    assert amqp_annotated_message.header.delivery_count == 1
    assert amqp_annotated_message.header.time_to_live == 1
    assert amqp_annotated_message.header.first_acquirer
    assert amqp_annotated_message.header.durable

    assert amqp_annotated_message.footer == {"key": "value"}
    assert amqp_annotated_message.delivery_annotations == {"key": "value"}
    assert amqp_annotated_message.annotations == {"key": "value"}
    assert amqp_annotated_message.application_properties == {"key": "value"}

    assert amqp_annotated_message.properties.message_id == 'id'
    assert amqp_annotated_message.properties.user_id == 'id'
    assert amqp_annotated_message.properties.to == 'to'
    assert amqp_annotated_message.properties.subject == 'sub'
    assert amqp_annotated_message.properties.correlation_id == 'cid'
    assert amqp_annotated_message.properties.content_type == 'ctype'
    assert amqp_annotated_message.properties.content_encoding == 'cencoding'
    assert amqp_annotated_message.properties.creation_time == 1
    assert amqp_annotated_message.properties.absolute_expiry_time == 1
    assert amqp_annotated_message.properties.group_id == 'id'
    assert amqp_annotated_message.properties.group_sequence == 1
    assert amqp_annotated_message.properties.reply_to_group_id == 'id'


def test_servicebus_message_time_to_live():
    message = ServiceBusMessage(body="hello")
    message.time_to_live = timedelta(seconds=30)
    assert message.time_to_live == timedelta(seconds=30)
    message.time_to_live = timedelta(days=1)
    assert message.time_to_live == timedelta(days=1)



class ServiceBusMessageBackcompatTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_receive_and_delete_databody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = ServiceBusMessage(
            body="hello",
            application_properties={'prop': 'test'},
            session_id="id_session",
            message_id="id_message",
            time_to_live=timedelta(seconds=30),
            content_type="content type",
            correlation_id="correlation",
            subject="github",
            partition_key="id_session",
            to="forward to",
            reply_to="reply to",
            reply_to_session_id="reply to session"
        )

        # TODO: Attribute shouldn't exist until after message has been sent.
        # with pytest.raises(AttributeError):
        #     outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=True)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        assert outgoing_message.message
        with pytest.raises(TypeError):
            outgoing_message.message.accept()
        with pytest.raises(TypeError):
            outgoing_message.message.release()
        with pytest.raises(TypeError):
            outgoing_message.message.reject()
        with pytest.raises(TypeError):
            outgoing_message.message.modify(True, True)
        assert outgoing_message.message.state == uamqp.constants.MessageState.SendComplete
        assert outgoing_message.message.settled
        assert outgoing_message.message.delivery_annotations is None
        assert outgoing_message.message.delivery_no is None
        assert outgoing_message.message.delivery_tag is None
        assert outgoing_message.message.on_send_complete is None
        assert outgoing_message.message.footer is None
        assert outgoing_message.message.retries >= 0
        assert outgoing_message.message.idle_time >= 0
        with pytest.raises(Exception):
            outgoing_message.message.gather()
        assert isinstance(outgoing_message.message.encode_message(), bytes)
        assert outgoing_message.message.get_message_encoded_size() == 208
        assert list(outgoing_message.message.get_data()) == [b'hello']
        assert outgoing_message.message.application_properties == {'prop': 'test'}
        assert outgoing_message.message.get_message()  # C instance.
        assert len(outgoing_message.message.annotations) == 1
        assert list(outgoing_message.message.annotations.values())[0] == 'id_session'
        assert str(outgoing_message.message.header) == str({'delivery_count': None, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
        assert outgoing_message.message.header.get_header_obj().delivery_count is None
        assert outgoing_message.message.properties.message_id == b'id_message'
        assert outgoing_message.message.properties.user_id is None
        assert outgoing_message.message.properties.to == b'forward to'
        assert outgoing_message.message.properties.subject == b'github'
        assert outgoing_message.message.properties.reply_to == b'reply to'
        assert outgoing_message.message.properties.correlation_id == b'correlation'
        assert outgoing_message.message.properties.content_type == b'content type'
        assert outgoing_message.message.properties.content_encoding is None
        assert outgoing_message.message.properties.absolute_expiry_time
        assert outgoing_message.message.properties.creation_time
        assert outgoing_message.message.properties.group_id == b'id_session'
        assert outgoing_message.message.properties.group_sequence is None
        assert outgoing_message.message.properties.reply_to_group_id == b'reply to session'
        assert outgoing_message.message.properties.get_properties_obj().message_id
    
        # TODO: Test updating message and resending
        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            assert incoming_message.message.delivery_annotations == {}
            assert incoming_message.message.delivery_no >= 1
            assert incoming_message.message.delivery_tag is None
            assert incoming_message.message.on_send_complete is None
            assert incoming_message.message.footer is None
            assert incoming_message.message.retries >= 0
            assert incoming_message.message.idle_time == 0
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert isinstance(incoming_message.message.encode_message(), bytes)
            # TODO: Pyamqp has size at 266
            # assert incoming_message.message.get_message_encoded_size() == 267
            assert list(incoming_message.message.get_data()) == [b'hello']
            assert incoming_message.message.application_properties == {b'prop': b'test'}
            assert incoming_message.message.get_message()  # C instance.
            assert len(incoming_message.message.annotations) == 3
            assert incoming_message.message.annotations[b'x-opt-enqueued-time'] > 0
            assert incoming_message.message.annotations[b'x-opt-sequence-number'] > 0
            assert incoming_message.message.annotations[b'x-opt-partition-key'] == b'id_session'
            # TODO: Pyamqp has header {'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None}
            # assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': True, 'durable': True, 'priority': 4})
            assert incoming_message.message.header.get_header_obj().delivery_count == 0
            assert incoming_message.message.properties.message_id == b'id_message'
            assert incoming_message.message.properties.user_id is None
            assert incoming_message.message.properties.to == b'forward to'
            assert incoming_message.message.properties.subject == b'github'
            assert incoming_message.message.properties.reply_to == b'reply to'
            assert incoming_message.message.properties.correlation_id == b'correlation'
            assert incoming_message.message.properties.content_type == b'content type'
            assert incoming_message.message.properties.content_encoding is None
            assert incoming_message.message.properties.absolute_expiry_time
            assert incoming_message.message.properties.creation_time
            assert incoming_message.message.properties.group_id == b'id_session'
            assert incoming_message.message.properties.group_sequence is None
            assert incoming_message.message.properties.reply_to_group_id == b'reply to session'
            assert incoming_message.message.properties.get_properties_obj().message_id
            assert not incoming_message.message.accept()
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

            # TODO: Test updating message and resending

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_peek_lock_databody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = ServiceBusMessage(
            body="hello",
            application_properties={'prop': 'test'},
            session_id="id_session",
            message_id="id_message",
            time_to_live=timedelta(seconds=30),
            content_type="content type",
            correlation_id="correlation",
            subject="github",
            partition_key="id_session",
            to="forward to",
            reply_to="reply to",
            reply_to_session_id="reply to session"
        )

        # TODO: Attribute shouldn't exist until after message has been sent.
        # with pytest.raises(AttributeError):
        #     outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=True)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        assert outgoing_message.message
        with pytest.raises(TypeError):
            outgoing_message.message.accept()
        with pytest.raises(TypeError):
            outgoing_message.message.release()
        with pytest.raises(TypeError):
            outgoing_message.message.reject()
        with pytest.raises(TypeError):
            outgoing_message.message.modify(True, True)
        assert outgoing_message.message.state == uamqp.constants.MessageState.SendComplete
        assert outgoing_message.message.settled
        assert outgoing_message.message.delivery_annotations is None
        assert outgoing_message.message.delivery_no is None
        assert outgoing_message.message.delivery_tag is None
        assert outgoing_message.message.on_send_complete is None
        assert outgoing_message.message.footer is None
        assert outgoing_message.message.retries >= 0
        assert outgoing_message.message.idle_time >= 0
        with pytest.raises(Exception):
            outgoing_message.message.gather()
        assert isinstance(outgoing_message.message.encode_message(), bytes)
        assert outgoing_message.message.get_message_encoded_size() == 208
        assert list(outgoing_message.message.get_data()) == [b'hello']
        assert outgoing_message.message.application_properties == {'prop': 'test'}
        assert outgoing_message.message.get_message()  # C instance.
        assert len(outgoing_message.message.annotations) == 1
        assert list(outgoing_message.message.annotations.values())[0] == 'id_session'
        assert str(outgoing_message.message.header) == str({'delivery_count': None, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
        assert outgoing_message.message.header.get_header_obj().delivery_count is None
        assert outgoing_message.message.properties.message_id == b'id_message'
        assert outgoing_message.message.properties.user_id is None
        assert outgoing_message.message.properties.to == b'forward to'
        assert outgoing_message.message.properties.subject == b'github'
        assert outgoing_message.message.properties.reply_to == b'reply to'
        assert outgoing_message.message.properties.correlation_id == b'correlation'
        assert outgoing_message.message.properties.content_type == b'content type'
        assert outgoing_message.message.properties.content_encoding is None
        assert outgoing_message.message.properties.absolute_expiry_time
        assert outgoing_message.message.properties.creation_time
        assert outgoing_message.message.properties.group_id == b'id_session'
        assert outgoing_message.message.properties.group_sequence is None
        assert outgoing_message.message.properties.reply_to_group_id == b'reply to session'
        assert outgoing_message.message.properties.get_properties_obj().message_id
    
        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()       
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
            assert not incoming_message.message.settled
            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
            assert incoming_message.message.delivery_no >= 1
            assert incoming_message.message.delivery_tag
            assert incoming_message.message.on_send_complete is None
            assert incoming_message.message.footer is None
            assert incoming_message.message.retries >= 0
            assert incoming_message.message.idle_time == 0
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert isinstance(incoming_message.message.encode_message(), bytes)
            # TODO: Pyamqp has size at 336
            # assert incoming_message.message.get_message_encoded_size() == 334
            assert list(incoming_message.message.get_data()) == [b'hello']
            assert incoming_message.message.application_properties == {b'prop': b'test'}
            assert incoming_message.message.get_message()  # C instance.
            assert len(incoming_message.message.annotations) == 4
            assert incoming_message.message.annotations[b'x-opt-enqueued-time'] > 0
            assert incoming_message.message.annotations[b'x-opt-sequence-number'] > 0
            assert incoming_message.message.annotations[b'x-opt-partition-key'] == b'id_session'
            assert incoming_message.message.annotations[b'x-opt-locked-until']
            # TODO: Pyamqp has header {'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None}
            # assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': True, 'durable': True, 'priority': 4})
            assert str(incoming_message.message.header) == str({'delivery_count': 0, 'time_to_live': 30000, 'first_acquirer': None, 'durable': None, 'priority': None})
            assert incoming_message.message.header.get_header_obj().delivery_count == 0
            assert incoming_message.message.properties.message_id == b'id_message'
            assert incoming_message.message.properties.user_id is None
            assert incoming_message.message.properties.to == b'forward to'
            assert incoming_message.message.properties.subject == b'github'
            assert incoming_message.message.properties.reply_to == b'reply to'
            assert incoming_message.message.properties.correlation_id == b'correlation'
            assert incoming_message.message.properties.content_type == b'content type'
            assert incoming_message.message.properties.content_encoding is None
            assert incoming_message.message.properties.absolute_expiry_time
            assert incoming_message.message.properties.creation_time
            assert incoming_message.message.properties.group_id == b'id_session'
            assert incoming_message.message.properties.group_sequence is None
            assert incoming_message.message.properties.reply_to_group_id == b'reply to session'
            assert incoming_message.message.properties.get_properties_obj().message_id
            assert incoming_message.message.accept()
            # TODO: State isn't updated if settled correctly via the receiver.
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_receive_and_delete_valuebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = AmqpAnnotatedMessage(value_body={b"key": b"value"})

        with pytest.raises(AttributeError):
            outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=False)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        with pytest.raises(AttributeError):
            outgoing_message.message

        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert incoming_message.message.get_data() == {b"key": b"value"}
            assert not incoming_message.message.accept()
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_peek_lock_valuebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = AmqpAnnotatedMessage(value_body={b"key": b"value"})

        with pytest.raises(AttributeError):
            outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=False)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        with pytest.raises(AttributeError):
            outgoing_message.message

        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()       
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
            assert not incoming_message.message.settled
            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
            assert incoming_message.message.delivery_no >= 1
            assert incoming_message.message.delivery_tag
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert incoming_message.message.get_data() == {b"key": b"value"}
            assert incoming_message.message.accept()
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_receive_and_delete_sequencebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = AmqpAnnotatedMessage(sequence_body=[1, 2, 3])

        with pytest.raises(AttributeError):
            outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=False)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        with pytest.raises(AttributeError):
            outgoing_message.message

        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert list(incoming_message.message.get_data()) == [[1, 2, 3]]
            assert not incoming_message.message.accept()
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    def test_message_backcompat_peek_lock_sequencebody(self, servicebus_namespace_connection_string, servicebus_queue, **kwargs):
        queue_name = servicebus_queue.name
        outgoing_message = AmqpAnnotatedMessage(sequence_body=[1, 2, 3])

        with pytest.raises(AttributeError):
            outgoing_message.message

        sb_client = ServiceBusClient.from_connection_string(
        servicebus_namespace_connection_string, logging_enable=False)
        with sb_client.get_queue_sender(queue_name) as sender:
            sender.send_messages(outgoing_message)

        with pytest.raises(AttributeError):
            outgoing_message.message

        with sb_client.get_queue_receiver(queue_name,
                                            receive_mode=ServiceBusReceiveMode.PEEK_LOCK,
                                            max_wait_time=10) as receiver:
            batch = receiver.receive_messages()       
            incoming_message = batch[0]
            assert incoming_message.message
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedUnsettled
            assert not incoming_message.message.settled
            assert incoming_message.message.delivery_annotations[b'x-opt-lock-token']
            assert incoming_message.message.delivery_no >= 1
            assert incoming_message.message.delivery_tag
            with pytest.raises(Exception):
                incoming_message.message.gather()
            assert list(incoming_message.message.get_data()) == [[1, 2, 3]]
            assert incoming_message.message.accept()
            assert incoming_message.message.state == uamqp.constants.MessageState.ReceivedSettled
            assert incoming_message.message.settled
            assert not incoming_message.message.release()
            assert not incoming_message.message.reject()
            assert not incoming_message.message.modify(True, True)

    # TODO: Add batch message backcompat tests
