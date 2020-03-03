#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving deferred message from a Service Bus Queue.
"""

# pylint: disable=C0111

import os
from azure.servicebus import ServiceBusReceiverClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

receiver_client = ServiceBusReceiverClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME,
    logging_enable=True
)

with receiver_client:
    received_msgs = receiver_client.receive(max_batch_size=10, timeout=5)
    deferred_sequenced_numbers = []
    for msg in received_msgs:
        print("Deferring msg: {}".format(str(msg)))
        deferred_sequenced_numbers.append(msg.sequence_number)
        msg.defer()

    received_deferred_msg = receiver_client.receive_deferred_messages(
        sequence_numbers=deferred_sequenced_numbers
    )

    for msg in received_deferred_msg:
        print("Completing deferred msg: {}".format(str(msg)))
        msg.complete()

print("Receive is done.")
