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
from azure.servicebus import ServiceBusClient, Message

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SESSION_ID = "<your session id>"


def send_single_message(sender):
    message = Message("DATA" * 64, session_id=SESSION_ID)
    sender.send(message)


def send_batch_message(sender):
    batch_message = sender.create_batch()
    while True:
        try:
            message = Message("DATA" * 256, session_id=SESSION_ID)
            batch_message.add(message)
        except ValueError:
            # BatchMessage object reaches max_size.
            # New BatchMessage object can be created here to send more data.
            break
    sender.send(batch_message)


def receive_batch_message(receiver):
    session = receiver.session
    session.set_session_state("START")
    print("Session state:", session.get_session_state())
    received_msgs = receiver.receive(max_batch_size=10, max_wait_time=5)
    for msg in received_msgs:
        print(str(msg))
        msg.complete()
        session.renew_lock()
    session.set_session_state("END")
    print("Session state:", session.get_session_state())


if __name__ == '__main__':
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            send_single_message(sender)
            send_batch_message(sender)

        print("Send message is done.")

        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, session_id=SESSION_ID, prefetch=10)
        with receiver:
            receive_batch_message(receiver)

        print("Receive is done.")


