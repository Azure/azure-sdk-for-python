#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Subscription under specific Topic asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
TOPIC_NAME = os.environ["SERVICE_BUS_TOPIC_NAME"]
SUBSCRIPTION_NAME = os.environ["SERVICE_BUS_SUBSCRIPTION_NAME"]


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        receiver = servicebus_client.get_subscription_receiver(
            topic_name=TOPIC_NAME,
            subscription_name=SUBSCRIPTION_NAME
        )
        async with receiver:
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            for msg in received_msgs:
                print(str(msg))
                await receiver.complete_message(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
