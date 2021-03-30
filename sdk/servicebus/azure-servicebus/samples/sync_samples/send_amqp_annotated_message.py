#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending amqp annotated message(s) to a Service Bus Queue.
"""

# pylint: disable=C0111

import os
import logging
logging.basicConfig(level=logging.INFO)
from azure.servicebus import ServiceBusClient, AMQPAnnotatedMessage


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


def send_data_message(sender):
    data_body = [b'aa', b'bb', b'cc']
    data_app_prop = {"body_type": "data"}
    del_anno = {"delann_key": "delann_value"}
    data_message = AMQPAnnotatedMessage(
        data_body=data_body,
        delivery_annotations=del_anno,
        application_properties=data_app_prop
    )
    sender.send_messages(data_message)


def send_sequence_message(sender):
    sequence_body = [b'message', 123.456, True]
    footer = {'footer_key': 'footer_value'}
    prop = {"subject": "sequence"}
    seq_app_prop = {"body_type": "sequence"}
    sequence_message = AMQPAnnotatedMessage(
        sequence_body=sequence_body,
        footer=footer,
        properties=prop,
        application_properties=seq_app_prop
    )
    sender.send_messages(sequence_message)


def send_value_message(sender):
    value_body = {b"key": [-123, b'data', False]}
    header = {"priority": 10}
    anno = {"ann_key": "ann_key"}
    value_app_prop = {"body_type": "sequence"}
    value_message = AMQPAnnotatedMessage(
        value_body=value_body,
        header=header,
        annotations=anno,
        application_properties=value_app_prop
    )
    sender.send_messages(value_message)


servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        send_data_message(sender)
        send_sequence_message(sender)
        send_value_message(sender)

print("Send message is done.")
