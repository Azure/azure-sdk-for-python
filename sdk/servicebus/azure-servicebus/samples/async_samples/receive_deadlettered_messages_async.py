#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving dead-lettered messages from a Service Bus Queue asynchronously.
"""

import os
import asyncio
from azure.servicebus import ServiceBusMessage, ServiceBusSubQueue
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]


async def main():
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        messages = [ServiceBusMessage("Message to be deadlettered") for _ in range(10)]
        async with sender:
            await sender.send_messages(messages)

        print("dead lettering messages")
        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
        async with receiver:
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            for msg in received_msgs:
                print(str(msg))
                await receiver.dead_letter_message(msg)

        print("receiving deadlettered messages")
        dlq_receiver = servicebus_client.get_queue_receiver(
            queue_name=QUEUE_NAME, sub_queue=ServiceBusSubQueue.DEAD_LETTER, prefetch_count=10
        )
        async with dlq_receiver:
            received_msgs = await dlq_receiver.receive_messages(max_message_count=10, max_wait_time=5)
            for msg in received_msgs:
                print(str(msg))
                await dlq_receiver.complete_message(msg)


asyncio.run(main())
