#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue.
"""

import os
import time
from datetime import datetime, timezone, timedelta
from azure.servicebus import ServiceBusClient, ServiceBusMessage, NEXT_AVAILABLE_SESSION


CONNECTION_STR = os.environ['SERVICEBUS_CONNECTION_STR']
SESSION_QUEUE_NAME = os.environ["SERVICEBUS_SESSION_QUEUE_NAME"]

def send_single_message(sender, i):
    message = ServiceBusMessage(f"Single Message {i}", session_id="0")
    sender.send_messages(message)

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, uamqp_transport=False)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=SESSION_QUEUE_NAME, session_id=NEXT_AVAILABLE_SESSION)
    with sender:
        send_single_message(sender, 1)
        send_single_message(sender, 2)
        send_single_message(sender, 3)
    print(f"All messages sent before {datetime.now(timezone.utc)}")

    receiver = servicebus_client.get_queue_receiver(queue_name=SESSION_QUEUE_NAME, session_id=NEXT_AVAILABLE_SESSION)
    with receiver:

        # Peek before deleting to see enqueued times
        peeked_msgs = receiver.peek_messages(max_message_count=10)
        for msg in peeked_msgs:
            print(f"Message peeked has enqueued time of {msg.enqueued_time_utc}")

        # Deleting Messages
        new_time = datetime.now(timezone.utc) + timedelta(hours=10)
        print(f"Deleting messages that are older than {new_time}")
        deleted_msgs = receiver.delete_messages(
            max_message_count=10,
            before_enqueued_time_utc=new_time
        )
        print(f"{deleted_msgs} messages deleted.")

        # Try to peek after deleting
        peeked_msgs = receiver.peek_messages(max_message_count=10)
        for msg in peeked_msgs:
            print(f"Message peeked has enqueued time of {msg.enqueued_time_utc}")

        # Try to receive after deleting
        received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            print(f"{msg} received.")
            receiver.complete_message(msg)

    print("Receive is done.")
