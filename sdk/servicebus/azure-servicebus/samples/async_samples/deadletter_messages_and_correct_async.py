#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Comprehensive dead-letter queue example to show moving dead-lettered messages to a Service Bus
Queue, retrieving messages from it, and resubmitting corrected messages back into main queue asynchronously.

For an example of basic usage for receiving from a dead-letter queue asynchronously, please refer
to the sample `receive_deadlettered_messages_async.py`.
"""

import os
import asyncio
from azure.servicebus import ServiceBusMessage, ServiceBusSubQueue
from azure.servicebus.aio import ServiceBusClient


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

async def send_messages(servicebus_client, num_messages):
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    async with sender:
        msg = [
            ServiceBusMessage(
                "Message to be deadlettered number: {}".format(i),
                subject="{}".format("Bad" if i % 2 == 0 else "Good"),
            )
            for i in range(num_messages)
        ]
        await sender.send_messages(msg)
        print("Messages sent")

async def exceed_max_delivery(servicebus_client):
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    dlq_receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, 
                                                        sub_queue=ServiceBusSubQueue.DEAD_LETTER)
    async with receiver:
        received_msgs = await receiver.receive_messages(max_wait_time=5)
        while len(received_msgs) > 0:
            for msg in received_msgs:
                print("Message delivery_count: {}".format(msg.delivery_count))
                await receiver.abandon_message(msg)
            received_msgs = await receiver.receive_messages(max_wait_time=5)

    async with dlq_receiver:
        received_msgs = await dlq_receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            print("Deadletter message:")
            print(msg)
            await dlq_receiver.complete_message(msg)
    
async def receive_messages(servicebus_client):
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    async with receiver:
        received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            if msg.subject and msg.subject == "Good":
                await receiver.complete_message(msg)
            else:
                await receiver.dead_letter_message(
                    msg,
                    reason="ProcessingError",
                    error_description="Don't know what to do with this message.",
                )

async def fix_deadletters(servicebus_client):
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    dlq_receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, 
                                                        sub_queue=ServiceBusSubQueue.DEAD_LETTER)
    msgs_to_send = []
    async with dlq_receiver:
        received_dlq_msgs = await dlq_receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_dlq_msgs:
            if msg.subject and msg.subject == "Bad":
                msg_copy = ServiceBusMessage(str(msg), subject="Good")
                msgs_to_send.append(msg_copy)
                print("Fixing message: Body={}, Subject={}".format(next(msg.body), msg.subject))
            await dlq_receiver.complete_message(msg)
    async with sender:
        print("Resending fixed messages")
        await sender.send_messages(msgs_to_send)
    async with receiver:
        received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            if msg.subject and msg.subject == "Good":
                print("Received fixed message: Body={}, Subject={}".format(next(msg.body), msg.subject))
                await receiver.complete_message(msg)

async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    dlq_receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, 
                                                        sub_queue=ServiceBusSubQueue.DEAD_LETTER)

    # Scenario 1: Send, retrieve, and abandon message until maximum delivery count is exhausted.
    # The message is automatically dead-lettered.
    await send_messages(servicebus_client, 1)
    await exceed_max_delivery(servicebus_client)

    # Scenario 2: Send messages and dead-letter messages that don't match some criterion and 
    # would not be processed correctly. The messages are picked up from the dead-letter queue,
    # automatically corrected, and resubmitted.
    await send_messages(servicebus_client, 10)
    await receive_messages(servicebus_client)
    await fix_deadletters(servicebus_client)

    await servicebus_client.close()

asyncio.run(main())
