#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending, receiving and parsing amqp annotated message(s) to a Service Bus Queue.
"""

import os
from azure.servicebus import ServiceBusClient
from azure.servicebus.amqp import AmqpAnnotatedMessage, AmqpMessageBodyType


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


def send_data_message(sender):
    data_body = [b'aa', b'bb', b'cc']
    application_properties = {"body_type": "data"}
    delivery_annotations = {"delivery_annotation_key": "value"}
    data_message = AmqpAnnotatedMessage(
        data_body=data_body,
        delivery_annotations=delivery_annotations,
        application_properties=application_properties
    )
    sender.send_messages(data_message)
    print("Message of data body sent.")


def send_sequence_message(sender):
    sequence_body = [b'message', 123.456, True]
    footer = {'footer_key': 'footer_value'}
    properties = {"subject": "sequence"}
    application_properties = {"body_type": "sequence"}
    sequence_message = AmqpAnnotatedMessage(
        sequence_body=sequence_body,
        footer=footer,
        properties=properties,
        application_properties=application_properties
    )
    sender.send_messages(sequence_message)
    print("Message of sequence body sent.")


def send_value_message(sender):
    value_body = {b"key": [-123, b'data', False]}
    header = {"priority": 10}
    annotations = {"annotation_key": "value"}
    application_properties = {"body_type": "value"}
    value_message = AmqpAnnotatedMessage(
        value_body=value_body,
        header=header,
        annotations=annotations,
        application_properties=application_properties
    )
    sender.send_messages(value_message)
    print("Message of value body sent.")


def receive_and_parse_message(receiver):
    for message in receiver:
        raw_amqp_message = message.raw_amqp_message
        if raw_amqp_message.body_type == AmqpMessageBodyType.DATA:
            print("Message of data body received. Body is:")
            for data_section in raw_amqp_message.body:
                print(data_section)
        elif raw_amqp_message.body_type == AmqpMessageBodyType.SEQUENCE:
            print("Message of sequence body received. Body is:")
            for sequence_section in raw_amqp_message.body:
                print(sequence_section)
        elif raw_amqp_message.body_type == AmqpMessageBodyType.VALUE:
            print("Message of value body received. Body is:")
            print(raw_amqp_message.body)
        receiver.complete_message(message)


servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=10)
    with sender, receiver:
        send_data_message(sender)
        send_sequence_message(sender)
        send_value_message(sender)
        receive_and_parse_message(receiver)
