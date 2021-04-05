import pytest
import uamqp
from azure.servicebus import ServiceBusMessage, ServiceBusReceivedMessage
from azure.servicebus._common.constants import (
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_SCHEDULED_ENQUEUE_TIME
)

def test_servicebus_message_repr():
    message = ServiceBusMessage("hello")
    assert message.__repr__() == "ServiceBusMessage(body=hello)"

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
    assert "ServiceBusReceivedMessage(received_timestamp_utc=" in received_message.__repr__()
    assert "settled=False, body=data)" in received_message.__repr__()
