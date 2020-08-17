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
from azure.servicebus import Message
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
SESSION_QUEUE_NAME = os.environ["SERVICE_BUS_SESSION_QUEUE_NAME"]
SESSION_ID = os.environ['SERVICE_BUS_SESSION_ID']


async def send_single_message(sender):
    message = Message("Single session message", session_id=SESSION_ID)
    await sender.send_messages(message)


async def send_a_list_of_messages(sender):
    messages = [Message("Session Message in list", session_id=SESSION_ID) for _ in range(10)]
    await sender.send_messages(messages)


async def send_batch_message(sender):
    batch_message = await sender.create_batch()
    for _ in range(10):
        try:
            batch_message.add(Message("Session Message inside a BatchMessage", session_id=SESSION_ID))
        except ValueError:
            # BatchMessage object reaches max_size.
            # New BatchMessage object can be created here to send more data.
            break
    await sender.send_messages(batch_message)


async def receive_batch_messages(receiver):
    session = receiver.session
    await session.set_state("START")
    print("Session state:", await session.get_state())
    received_msgs = await receiver.receive_messages(max_batch_size=10, max_wait_time=5)
    for msg in received_msgs:
        print(str(msg))
        await msg.complete()
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

        receiver = servicebus_client.get_queue_session_receiver(queue_name=SESSION_QUEUE_NAME, session_id=SESSION_ID)
        async with receiver:
            await receive_batch_messages(receiver)

        print("Receive is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
