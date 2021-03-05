#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving dead-lettered messages from a Service Bus Queue.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusSubQueue

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    messages = [ServiceBusMessage("Message to be deadlettered") for _ in range(10)]
    with sender:
        sender.send_messages(messages)

    print('dead lettering messages')
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    with receiver:
        received_msgs = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            print(str(msg))
            receiver.dead_letter_message(msg)

    print('receiving deadlettered messages')
    dlq_receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, sub_queue=ServiceBusSubQueue.DEAD_LETTER)
    with dlq_receiver:
        received_msgs = dlq_receiver.receive_messages(max_message_count=10, max_wait_time=5)
        for msg in received_msgs:
            print(str(msg))
            dlq_receiver.complete_message(msg)

print("Receive is done.")
