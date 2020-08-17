#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show usage of AutoLockRenew:
    1. Automatically renew locks on messages received from non-sessionful entity
    2. Automatically renew locks on the session of sessionful entity
"""

# pylint: disable=C0111

import os
import time

from azure.servicebus import ServiceBusClient, AutoLockRenew, Message
from azure.servicebus.exceptions import MessageLockExpired

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SESSION_QUEUE_NAME = os.environ['SERVICE_BUS_SESSION_QUEUE_NAME']


def renew_lock_on_message_received_from_non_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    with servicebus_client:
        with servicebus_client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            msgs_to_send = [Message("message: {}".format(i)) for i in range(10)]
            sender.send_messages(msgs_to_send)
            print('Send messages to non-sessionful queue.')
        
        # Can also be called via "with AutoLockRenew() as renewer" to automate shutdown.
        renewer = AutoLockRenew()

        with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch_count=10) as receiver:
            received_msgs = receiver.receive_messages(max_batch_size=10, max_wait_time=5)

            for msg in received_msgs:
                # automatically renew the lock on each message for 100 seconds
                renewer.register(msg, timeout=100)
            print('Register messages into AutoLockRenew done.')

            time.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                msg.complete() # Settling the message deregisters it from the AutoLockRenewer
            print('Complete messages.')

        renewer.close()


def renew_lock_on_session_of_the_sessionful_entity():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    with servicebus_client:

        with servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME) as sender:
            msgs_to_send = [Message("session message: {}".format(i), session_id='SESSION') for i in range(10)]
            sender.send_messages(msgs_to_send)
            print('Send messages to sessionful queue.')

        renewer = AutoLockRenew()

        with servicebus_client.get_queue_session_receiver(
            queue_name=SESSION_QUEUE_NAME,
            session_id='SESSION',
            prefetch_count=10
        ) as receiver:

            # automatically renew the lock on the session for 100 seconds
            renewer.register(receiver.session, timeout=100)
            print('Register session into AutoLockRenew.')

            received_msgs = receiver.receive_messages(max_batch_size=10, max_wait_time=5)
            time.sleep(100)  # message handling for long period (E.g. application logic)

            for msg in received_msgs:
                msg.complete()

            print('Complete messages.')

        renewer.close()


def renew_lock_with_lock_renewal_failure_callback():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    with servicebus_client:
        with servicebus_client.get_queue_sender(queue_name=QUEUE_NAME) as sender:
            sender.send_messages(Message("message"))
        
        with AutoLockRenew() as renewer:
            # For this sample we're going to set the renewal recurrence of the autolockrenewer to greater than the
            # service side message lock duration, to demonstrate failure.  Normally, this should not be adjusted.
            renewer._sleep_time = 40
            with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch_count=10) as receiver:

                def on_lock_renew_failure_callback(renewable, error):
                    # If auto-lock-renewal fails, this function will be called.
                    # If failure is due to an error, the second argument will be populated, otherwise
                    # it will default to `None`.
                    # This callback can be an ideal location to log the failure, or take action to safely
                    # handle any processing on the message or session that was in progress.
                    print("Intentionally failed to renew lock on {} due to {}".format(renewable, error))

                received_msgs = receiver.receive_messages(max_batch_size=1, max_wait_time=5)

                for msg in received_msgs:
                    # automatically renew the lock on each message for 120 seconds
                    renewer.register(msg, timeout=90, on_lock_renew_failure=on_lock_renew_failure_callback)
                print('Register messages into AutoLockRenew done.')

                # Cause the messages and autorenewal to time out.
                # Other reasons for renew failure could include a network or service outage.
                time.sleep(80)

                try:
                    for msg in received_msgs:
                        msg.complete()
                except MessageLockExpired as e:
                    print('Messages cannot be settled if they have timed out. (This is expected)')
                
                print('Lock renew failure demonstration complete.')


renew_lock_on_message_received_from_non_sessionful_entity()
renew_lock_on_session_of_the_sessionful_entity()
renew_lock_with_lock_renewal_failure_callback()