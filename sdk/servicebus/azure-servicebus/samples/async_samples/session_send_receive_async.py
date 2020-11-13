#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to and receiving messages from a Service Bus Queue with session enabled asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
SESSION_QUEUE_NAME = os.environ["SERVICE_BUS_SESSION_QUEUE_NAME"]
SESSION_ID = os.environ['SERVICE_BUS_SESSION_ID']


async def send_single_message(sender):
    message = ServiceBusMessage("Single session message", session_id=SESSION_ID)
    await sender.send_messages(message)


async def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Session Message in list", session_id=SESSION_ID) for _ in range(10)]
    await sender.send_messages(messages)


async def send_batch_message(sender):
    batch_message = await sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Session Message inside a ServiceBusMessageBatch", session_id=SESSION_ID))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    await sender.send_messages(batch_message)


async def receive_batch_messages(receiver):
    session = receiver.session
    await session.set_state("START")
    print("Session state:", await session.get_state())
    received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
    for msg in received_msgs:
        print(str(msg))
        await receiver.complete_message(msg)
        await session.renew_lock()
    await session.set_state("END")
    print("Session state:", await session.get_state())


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME)
        async with sender:
            await send_single_message(sender)
            await send_a_list_of_messages(sender)
            await send_batch_message(sender)

        print("Send message is done.")

        receiver = servicebus_client.get_queue_receiver(queue_name=SESSION_QUEUE_NAME, session_id=SESSION_ID)
        async with receiver:
            await receive_batch_messages(receiver)

        print("Receive is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
