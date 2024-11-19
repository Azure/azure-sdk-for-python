#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving deferred message from a Service Bus Queue.
"""

import os
from typing import List
from azure.servicebus import ServiceBusMessage, ServiceBusClient
from azure.identity import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]

credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    messages = [ServiceBusMessage("Message to be deferred") for _ in range(10)]
    with sender:
        sender.send_messages(messages)

    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    with receiver:
        received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        deferred_sequenced_numbers = []
        for msg in received_msgs:
            print("Deferring msg: {}".format(str(msg)))
            if msg.sequence_number:
                deferred_sequenced_numbers.append(msg.sequence_number)
            receiver.defer_message(msg)

        if deferred_sequenced_numbers:
            received_deferred_msg = receiver.receive_deferred_messages(sequence_numbers=deferred_sequenced_numbers)

            for msg in received_deferred_msg:
                print("Completing deferred msg: {}".format(str(msg)))
                receiver.complete_message(msg)
        else:
            print("No messages received.")

print("Receive is done.")
