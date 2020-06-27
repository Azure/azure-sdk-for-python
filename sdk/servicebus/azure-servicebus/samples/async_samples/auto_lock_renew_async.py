#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show usage of AutoLockRenew asynchronously:
    1. Automatically renew locks on messages received from non-sessionful entity
    2. Automatically renew locks on the session of sessionful entity
"""

# pylint: disable=C0111

import os
import asyncio

from azure.servicebus import Message
from azure.servicebus.aio import ServiceBusClient, AutoLockRenew

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SESSION_QUEUE_NAME = os.environ['SERVICE_BUS_SESSION_QUEUE_NAME']


async def renew_lock_on_message_received_from_non_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        async with servicebus_client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            msgs_to_send = [Message("session message: {}".format(i)) for i in range(10)]
            await sender.send(msgs_to_send)
            print('Send messages to non-sessionful queue.')

        # Can also be called via "with AutoLockRenew() as renewer" to automate shutdown.
        renewer = AutoLockRenew()

        async with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch=10) as receiver:
            received_msgs = await receiver.receive(max_batch_size=10, max_wait_time=5)

            for msg in received_msgs:
                # automatically renew the lock on each message for 100 seconds
                renewer.register(msg, timeout=100)
            print('Register messages into AutoLockRenew done.')

            await asyncio.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                await msg.complete()
            print('Complete messages.')

        await renewer.shutdown()


async def renew_lock_on_session_of_the_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:

        async with servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME) as sender:
            msgs_to_send = [Message("session message: {}".format(i), session_id='SESSION') for i in range(10)]
            await sender.send(msgs_to_send)
            print('Send messages to sessionful queue.')

        renewer = AutoLockRenew()

        async with servicebus_client.get_queue_session_receiver(
            queue_name=SESSION_QUEUE_NAME,
            session_id='SESSION',
            prefetch=10
        ) as receiver:
            # automatically renew the lock on the session for 100 seconds
            renewer.register(receiver.session, timeout=100)
            print('Register session into AutoLockRenew.')

            received_msgs = await receiver.receive(max_batch_size=10, max_wait_time=5)
            await asyncio.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                await msg.complete()
            print('Complete messages.')

        await renewer.shutdown()


loop = asyncio.get_event_loop()
loop.run_until_complete(renew_lock_on_message_received_from_non_sessionful_entity())
loop.run_until_complete(renew_lock_on_session_of_the_sessionful_entity())
