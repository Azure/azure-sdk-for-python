#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Topic asynchronously.

WARNING: ServiceBusClient, ServiceBusSender, ServiceBusReceiver, and ServiceBusMessageBatch are NOT coroutine-safe!
- Do NOT share ServiceBusClient, ServiceBusSender, or ServiceBusReceiver instances between coroutines
- Do NOT share ServiceBusMessageBatch instances between coroutines
- Use proper async locking mechanisms when accessing clients from multiple coroutines
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


# [START concurrent_sending_to_topic_with_asyncio]
async def send_messages_to_topic_concurrently_with_gather():
    """
    Example of concurrent sending to topic using asyncio.gather with separate clients.
    RECOMMENDED: Use separate ServiceBusClient instances for each coroutine.
    """
    async def send_messages_from_coroutine(coroutine_id):
        # Create a separate client for each coroutine (recommended approach)
        coroutine_credential = DefaultAzureCredential()
        coroutine_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, coroutine_credential)
        async with coroutine_client:
            async with coroutine_client.get_topic_sender(topic_name=TOPIC_NAME) as coroutine_sender:
                for i in range(5):
                    message = ServiceBusMessage(f"Topic message {i} from coroutine {coroutine_id}")
                    await coroutine_sender.send_messages(message)
        print(f"Coroutine {coroutine_id} completed sending to topic")

    # Launch multiple coroutines concurrently
    await asyncio.gather(*[send_messages_from_coroutine(i) for i in range(3)])


async def send_topic_messages_with_shared_client_and_lock():
    """
    Example of using a shared client with proper async locking for topic.
    NOT RECOMMENDED: Better to use separate clients per coroutine.
    """
    lock = asyncio.Lock()
    shared_credential = DefaultAzureCredential()
    shared_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, shared_credential)

    async def send_with_lock(coroutine_id):
        async with lock:
            # Only one coroutine can use the client at a time
            async with shared_client.get_topic_sender(topic_name=TOPIC_NAME) as sender:
                message = ServiceBusMessage(f"Locked topic message from coroutine {coroutine_id}")
                await sender.send_messages(message)
        print(f"Coroutine {coroutine_id} sent message to topic with lock")

    async with shared_client:
        await asyncio.gather(*[send_with_lock(i) for i in range(3)])

# [END concurrent_sending_to_topic_with_asyncio]


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


async def run_concurrent_examples():
    """Run concurrent sending examples (uncomment calls in main to run)"""
    print("Running concurrent topic sending examples...")
    await send_messages_to_topic_concurrently_with_gather()
    await send_topic_messages_with_shared_client_and_lock()


asyncio.run(main())

# Example of concurrent sending to topic (uncomment to run)
# asyncio.run(run_concurrent_examples())
