#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show the usage of connection string parser.
"""

import os
from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage,
    ServiceBusConnectionStringProperties,
    parse_connection_string,
)

conn_str = os.environ['SERVICE_BUS_CONN_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

parse_result = parse_connection_string(conn_str)

fully_qualified_namespace = parse_result.fully_qualified_namespace
print(fully_qualified_namespace)

# the name of the queue/topic
entity_path = parse_result.entity_path

# initialize with DefaultAzureCredential
servicebus_client = ServiceBusClient(
    fully_qualified_namespace,
    DefaultAzureCredential(),
    entity_path
    )
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        sender.send_messages(ServiceBusMessage('Single Message'))

print("Send message is done.")
