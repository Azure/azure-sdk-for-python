#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Topic.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusClient, Message

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
TOPIC_NAME = os.environ["SERVICE_BUS_TOPIC_NAME"]


def send_single_message(sender):
    message = Message("DATA" * 64)
    sender.send(message)


def send_batch_message(sender):
    batch_message = sender.create_batch()
    while True:
        try:
            batch_message.add(Message("DATA" * 256))
        except ValueError:
            # BatchMessage object reaches max_size.
            # New BatchMessage object can be created here to send more data.
            break
    sender.send(batch_message)


servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
    with sender:
        send_single_message(sender)
        send_batch_message(sender)

print("Send message is done.")
