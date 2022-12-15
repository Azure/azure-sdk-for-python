#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from azure.eventhub._pyamqp.message import Message
from azure.eventhub._pyamqp.utils import AMQPTypes
from azure.eventhub._pyamqp._encode import encode_payload
from azure.eventhub._pyamqp._decode import decode_payload
from azure.eventhub.amqp._amqp_message import AmqpMessageProperties


def test_message():
    value = Message(value="test_message")

    assert value.data == None
    assert value.value == "test_message"


def test_body_value():
    message = Message(value="test_message")
    body_value = b"body"

    message = message._replace(data=body_value)
    assert message.data == body_value

    output = bytearray()
    encode_payload(output, message)

    message = decode_payload(memoryview(output))
    output = bytearray()
    
    body = message.data
    assert body[0].get(b"TYPE").decode("utf-8") == AMQPTypes.binary


def test_delivery_tag():
    message = Message(value="test_message")
    assert not message.delivery_annotations


def test_message_properties():

    value = AmqpMessageProperties()
    assert not value.user_id

    value =  AmqpMessageProperties()
    value.user_id = bytearray(b'testuseridlongstring')
    assert value.user_id == b'testuseridlongstring'

    value =  AmqpMessageProperties()
    value.user_id = bytearray(b'')
    assert value.user_id == b''

    value = AmqpMessageProperties()
    value.user_id =bytearray(b'short')
    assert value.user_id == b'short'

    value = AmqpMessageProperties()
    value.user_id = bytearray(b'!@#$%^&*()+_?')
    assert value.user_id == b'!@#$%^&*()+_?'

    value = AmqpMessageProperties()
    value.user_id = bytearray(b'\nweird\0user\1id\0\t')
    assert value.user_id == b'\nweird\0user\1id\0\t'