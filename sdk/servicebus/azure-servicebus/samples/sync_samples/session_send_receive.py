#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to and receiving messages from a Service Bus Queue with session enabled.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
SESSION_QUEUE_NAME = os.environ["SERVICE_BUS_SESSION_QUEUE_NAME"]
SESSION_ID = os.environ['SERVICE_BUS_SESSION_ID']


def send_single_message(sender):
    message = ServiceBusMessage("Single session message", session_id=SESSION_ID)
    sender.send_messages(message)


def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Session Message in list", session_id=SESSION_ID) for _ in range(10)]
    sender.send_messages(messages)


def send_batch_message(sender):
    batch_message = sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Session Message inside a ServiceBusMessageBatch", session_id=SESSION_ID))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    sender.send_messages(batch_message)


def receive_batch_message(receiver):
    session = receiver.session
    session.set_state("START")
    print("Session state:", session.get_state())
    received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
    for msg in received_msgs:
        print(str(msg))
        receiver.complete_message(msg)
        session.renew_lock()
    session.set_state("END")
    print("Session state:", session.get_state())


if __name__ == '__main__':
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME)
        with sender:
            send_single_message(sender)
            send_a_list_of_messages(sender)
            send_batch_message(sender)

        print("Send message is done.")

        receiver = servicebus_client.get_queue_receiver(queue_name=SESSION_QUEUE_NAME, session_id=SESSION_ID)
        with receiver:
            receive_batch_message(receiver)

        print("Receive is done.")


