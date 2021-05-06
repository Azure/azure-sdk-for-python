import pytest
import uamqp
from datetime import datetime, timedelta
from azure.servicebus import ServiceBusMessage, ServiceBusReceivedMessage
from azure.servicebus._common.constants import (
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_SCHEDULED_ENQUEUE_TIME
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
    assert "application_properties=None, session_id=None" in received_message.__repr__()
    assert "content_type=None, correlation_id=None, to=None, reply_to=None, reply_to_session_id=None, subject=None,"
    assert "partition_key=r_key, scheduled_enqueue_time_utc" in received_message.__repr__()

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