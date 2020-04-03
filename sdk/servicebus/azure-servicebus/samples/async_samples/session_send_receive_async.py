#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to and receiving messages from a Service Bus Queue with session enabled. asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus import Message
from azure.servicebus.aio import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SESSION_ID = "<your session id>"


async def send_single_message(sender):
    message = Message("DATA" * 64)
    message.session_id = SESSION_ID
    await sender.send(message)


async def send_batch_message(sender):
    batch_message = await sender.create_batch()
    while True:
        try:
            message = Message("DATA" * 256)
            message.session_id = SESSION_ID
            batch_message.add(message)
        except ValueError:
            # BatchMessage object reaches max_size.
            # New BatchMessage object can be created here to send more data.
            break
    await sender.send(batch_message)


async def receive_batch_messages(receiver):
    session = receiver.session
    await session.set_session_state("START")
    print("Session state:", await session.get_session_state())
    received_msgs = await receiver.receive(max_batch_size=10, max_wait_time=5)
    for msg in received_msgs:
        print(str(msg))
        await msg.complete()
        await session.renew_lock()
    await session.set_session_state("END")
    print("Session state:", await session.get_session_state())


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            await send_single_message(sender)
            await send_batch_message(sender)

        print("Send message is done.")

        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, session_id=SESSION_ID, prefetch=10)
        async with receiver:
            await receive_batch_messages(receiver)

        print("Receive is done.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
