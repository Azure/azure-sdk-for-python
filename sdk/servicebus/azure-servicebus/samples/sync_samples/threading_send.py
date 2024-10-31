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
import time
import logging
import threading
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger("azure.servicebus")
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("[%(thread)d.%(threadName)s] - %(name)-12s  >>>>>>   %(message)s"))


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]


def send_single_message(sender):
    print(f"Sending a single message on {threading.current_thread().name}")
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)
    print(f"Sent a single message on {threading.current_thread().name}")
    time.sleep(12 * 60)
    print(f"Sending a single message after sleep {threading.current_thread().name}")
    sender.send_messages(message)
    print(f"Sent a single message after sleep {threading.current_thread().name}")


def send_a_list_of_messages(sender):
    print(f"Sending a list of messages on {threading.current_thread().name}")
    messages = [ServiceBusMessage("Message in list") for _ in range(10)]
    sender.send_messages(messages)
    print(f"Sent a list of messages on {threading.current_thread().name}")


def send_batch_message(sender):
    print(f"Sending a batch of messages on {threading.current_thread().name}")
    batch_message = sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Message inside a ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    sender.send_messages(batch_message)
    print(f"Sent a batch of messages on {threading.current_thread().name}")


credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        with ThreadPoolExecutor(max_workers=5) as exe:
            exe.submit(send_single_message, sender)
            exe.submit(send_single_message, sender)
            exe.submit(send_single_message, sender)
            # exe.submit(send_a_list_of_messages, sender)
            # exe.submit(send_batch_message, sender)
            # exe.submit(send_batch_message, sender)

print("Send message is done.")
