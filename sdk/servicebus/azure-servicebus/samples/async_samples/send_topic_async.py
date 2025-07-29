#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Topic asynchronously.

WARNING: ServiceBusClient, ServiceBusSender, and ServiceBusMessageBatch are not coroutine-safe.
Do not share these instances between coroutines without proper coroutine-safe management using mechanisms like asyncio.Lock.
"""

import os
import asyncio
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
TOPIC_NAME = os.environ["SERVICEBUS_TOPIC_NAME"]


async def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    await sender.send_messages(message)


async def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Message in list") for _ in range(10)]
    await sender.send_messages(messages)


async def send_batch_message(sender):
    batch_message = await sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Message inside a ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    await sender.send_messages(batch_message)





async def send_concurrent_with_shared_client_and_lock():
    """
    Example showing concurrent sending with a shared client using asyncio.Lock.
    """
    send_lock = asyncio.Lock()
    
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, DefaultAzureCredential())

    async def send_with_lock(task_id):
        try:
            # Use lock to ensure coroutine-safe sending
            async with send_lock:
                sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
                async with sender:
                    message = ServiceBusMessage(f"Synchronized message from coroutine {task_id}")
                    await sender.send_messages(message)
                    print(f"Coroutine {task_id} sent synchronized message successfully")
        except Exception as e:
            print(f"Coroutine {task_id} failed: {e}")

    async with servicebus_client:
        # Use asyncio.gather to run coroutines concurrently with lock synchronization
        await asyncio.gather(*[send_with_lock(i) for i in range(3)])


async def main():
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)

    async with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
        async with sender:
            await send_single_message(sender)
            await send_a_list_of_messages(sender)
            await send_batch_message(sender)

    print("Send message is done.")



    print("\nDemonstrating concurrent sending with shared client and locks...")
    await send_concurrent_with_shared_client_and_lock()


asyncio.run(main())
