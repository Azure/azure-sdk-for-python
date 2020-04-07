#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus import Message
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


async def send_single_message(sender):
    message = Message("DATA" * 64)
    await sender.send(message)


async def send_batch_message(sender):
    batch_message = await sender.create_batch()
    while True:
        try:
            batch_message.add(Message("DATA" * 256))
        except ValueError:
            # BatchMessage object reaches max_size.
            # New BatchMessage object can be created here to send more data.
            break
    await sender.send(batch_message)


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            await send_single_message(sender)
            await send_batch_message(sender)

    print("Send message is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
