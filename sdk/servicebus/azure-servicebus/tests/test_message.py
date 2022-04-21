import uamqp
from datetime import datetime, timedelta
from azure.servicebus import ServiceBusMessage, ServiceBusReceivedMessage, ServiceBusMessageState
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
