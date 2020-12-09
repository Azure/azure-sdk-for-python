#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show usage of AutoLockRenewer asynchronously:
    1. Automatically renew locks on messages received from non-sessionful entity
    2. Automatically renew locks on the session of sessionful entity
"""

# pylint: disable=C0111

import os
import asyncio

from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient, AutoLockRenewer
from azure.servicebus.exceptions import ServiceBusError

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SESSION_QUEUE_NAME = os.environ['SERVICE_BUS_SESSION_QUEUE_NAME']


async def renew_lock_on_message_received_from_non_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        async with servicebus_client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            msgs_to_send = [ServiceBusMessage("session message: {}".format(i)) for i in range(10)]
            await sender.send_messages(msgs_to_send)
            print('Send messages to non-sessionful queue.')

        # Can also be called via "with AutoLockRenewer() as renewer" to automate shutdown.
        renewer = AutoLockRenewer()

        async with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch_count=10) as receiver:
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)

            for msg in received_msgs:
                # automatically renew the lock on each message for 100 seconds
                renewer.register(receiver, msg, max_lock_renewal_duration=100)
            print('Register messages into AutoLockRenewer done.')

            await asyncio.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                await receiver.complete_message(msg)
            print('Complete messages.')

        await renewer.close()


async def renew_lock_on_session_of_the_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:

        async with servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME) as sender:
            msgs_to_send = [ServiceBusMessage("session message: {}".format(i), session_id='SESSION') for i in range(10)]
            await sender.send_messages(msgs_to_send)
            print('Send messages to sessionful queue.')

        renewer = AutoLockRenewer()

        async with servicebus_client.get_queue_receiver(
            queue_name=SESSION_QUEUE_NAME,
            session_id='SESSION',
            prefetch_count=10
        ) as receiver:
            # automatically renew the lock on the session for 100 seconds
            renewer.register(receiver, receiver.session, max_lock_renewal_duration=100)
            print('Register session into AutoLockRenewer.')

            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            await asyncio.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                await receiver.complete_message(msg)
            print('Complete messages.')


async def renew_lock_with_lock_renewal_failure_callback():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        async with servicebus_client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            await sender.send_messages(ServiceBusMessage("message"))
        
        async with AutoLockRenewer() as renewer:
            # For this sample we're going to set the renewal recurrence of the autolockrenewer to greater than the
            # service side message lock duration, to demonstrate failure.  Normally, this should not be adjusted.
            renewer._sleep_time = 40
            async with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch_count=10) as receiver:

                async def on_lock_renew_failure_callback(renewable, error):
                    # If auto-lock-renewal fails, this function will be called.
                    # If failure is due to an error, the second argument will be populated, otherwise
                    # it will default to `None`.
                    # This callback can be an ideal location to log the failure, or take action to safely
                    # handle any processing on the message or session that was in progress.
                    print("Intentionally failed to renew lock on {} due to {}".format(renewable, error))

                received_msgs = await receiver.receive_messages(max_message_count=1, max_wait_time=5)

                for msg in received_msgs:
                    # automatically renew the lock on each message for 120 seconds
                    renewer.register(receiver,
                                     msg,
                                     max_lock_renewal_duration=90,
                                     on_lock_renew_failure=on_lock_renew_failure_callback)
                print('Register messages into AutoLockRenewer done.')

                # Cause the messages and autorenewal to time out.
                # Other reasons for renew failure could include a network or service outage.
                await asyncio.sleep(80)

                try:
                    for msg in received_msgs:
                        await receiver.complete_message(msg)
                except ServiceBusError as e:
                    print('Messages cannot be settled if they have timed out. (This is expected)')
                
                print('Lock renew failure demonstration complete.')



loop = asyncio.get_event_loop()
loop.run_until_complete(renew_lock_on_message_received_from_non_sessionful_entity())
loop.run_until_complete(renew_lock_on_session_of_the_sessionful_entity())
loop.run_until_complete(renew_lock_with_lock_renewal_failure_callback())