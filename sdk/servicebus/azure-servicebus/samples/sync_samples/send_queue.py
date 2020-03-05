#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending single message to a Service Bus Queue.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusClient, Message

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

sender = servicebus_client.get_queue_sender(
    queue_name=QUEUE_NAME
)

message = Message("Single message")

with servicebus_client:
    with sender:
        sender.send(message)

print("Send message is done.")
