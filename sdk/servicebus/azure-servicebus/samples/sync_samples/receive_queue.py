#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Queue.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, prefetch=10)
    with receiver:
        received_msgs = receiver.receive(max_batch_size=10, max_wait_time=5)
        for msg in received_msgs:
            print(str(msg))
            msg.complete()

print("Receive is done.")
