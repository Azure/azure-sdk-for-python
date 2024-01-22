#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue.
"""

import os
import sys
import datetime
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusReceiveMode


CONNECTION_STR = os.environ['SERVICEBUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]

logger = logging.getLogger('azure.servicebus')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)

servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, retry_total=1)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        send_single_message(sender)
        send_single_message(sender)
        send_single_message(sender)
        time = datetime.datetime.utcnow()

    print("Send message is done.")

    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE)
    with receiver:
        received_msgs = receiver.delete_batch_messages(max_message_count=100, enqueued_time_older_than_utc=time)
        print(received_msgs)

    print("Receive is done.")
