#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message through http proxy to a Service Bus Queue.
"""

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname.
    'proxy_port': 8899,  # proxy port.
    'username': 'admin',  # username used for proxy authentication if needed.
    'password': '123456'  # password used for proxy authentication if needed.
}


def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)


servicebus_client = ServiceBusClient.from_connection_string(
    conn_str=CONNECTION_STR,
    http_proxy=HTTP_PROXY
)

with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        send_single_message(sender)

print("Send message is done.")
