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
from azure.servicebus import ServiceBusSenderClient, Message

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

sender_client = ServiceBusSenderClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME,
    logging_enable=True
)

message = Message("Single message")

with sender_client:
    sender_client.send(message)

print("Send message is done.")
