#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message through http proxy to a Service Bus Queue asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname.
    'proxy_port': 8899,  # proxy port.
    'username': 'admin',  # username used for proxy authentication if needed.
    'password': '123456'  # password used for proxy authentication if needed.
}


async def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    await sender.send_messages(message)


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=CONNECTION_STR,
        http_proxy=HTTP_PROXY
    )

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            await send_single_message(sender)

    print("Send message is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
