#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending single message to a Service Bus Queue asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus.aio import ServiceBusClient, Message

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=CONNECTION_STR
    )

    async with servicebus_client:
        sender = await servicebus_client.get_queue_sender(
            queue_name=QUEUE_NAME
        )

        async with sender:
            message = Message("Single message")
            await sender.send(message)

    print("Send message is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
