#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Subscription under specific Topic asynchronously.
"""

import os
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
TOPIC_NAME = os.environ["SERVICEBUS_TOPIC_NAME"]
SUBSCRIPTION_NAME = os.environ["SERVICEBUS_SUBSCRIPTION_NAME"]


async def main():
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

    async with servicebus_client:
        receiver = servicebus_client.get_subscription_receiver(
            topic_name=TOPIC_NAME, subscription_name=SUBSCRIPTION_NAME
        )
        async with receiver:
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            for msg in received_msgs:
                print(str(msg))
                await receiver.complete_message(msg)


asyncio.run(main())
