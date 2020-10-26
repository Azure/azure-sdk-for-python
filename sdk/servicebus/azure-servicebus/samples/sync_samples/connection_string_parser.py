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
    Message,
    ServiceBusConnectionStringProperties,
    ServiceBusConnectionStringParser,
)

from azure.servicebus._base_handler import ServiceBusSharedKeyCredential

conn_str = os.environ['SERVICE_BUS_CONN_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

parse_result = ServiceBusConnectionStringParser(conn_str).parse()

fully_qualified_namespace = parse_result.fully_qualified_namespace
credential = ServiceBusSharedKeyCredential(parse_result.shared_access_key_name, parse_result.shared_access_key)

servicebus_client = ServiceBusClient(fully_qualified_namespace, credential)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        sender.send_messages(Message('Single Message'))

print("Send message is done.")
