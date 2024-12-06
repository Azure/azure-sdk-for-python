#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving batch messages from a Service Bus Queue.
"""

import os
import threading
import logging
import sys
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("azure.servicebus")
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("[%(thread)d.%(threadName)s] - %(name)-12s  >>>>>>   %(message)s"))


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]

credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)


def receive(receiver):
    print(f"Receiving messages on {threading.current_thread().name}")
    received_msgs = receiver.receive_messages(max_message_count=1, max_wait_time=5)
    print(f"Receive is done on {threading.current_thread().name}")
    for msg in received_msgs:
        print(str(msg))
        print(f"Completing message on {threading.current_thread().name}")
        receiver.complete_message(msg)
        print(f"Completed message on {threading.current_thread().name}")


with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
    with receiver:
        with ThreadPoolExecutor(max_workers=5) as exe:
            exe.submit(receive, receiver)
            exe.submit(receive, receiver)


print("Receive is done.")
