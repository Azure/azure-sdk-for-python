#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show browsing messages currently pending in the queue.
"""

import os
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]

credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    with receiver:
        received_msgs = receiver.peek_messages(max_message_count=2)
        for msg in received_msgs:
            print(str(msg))

print("Receive is done.")
