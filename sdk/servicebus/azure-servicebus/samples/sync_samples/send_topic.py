#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Topic.

WARNING: ServiceBusClient, ServiceBusSender, ServiceBusReceiver, and ServiceBusMessageBatch are NOT thread-safe!
- Do NOT share ServiceBusClient, ServiceBusSender, or ServiceBusReceiver instances between threads
- Do NOT share ServiceBusMessageBatch instances between threads
- Use proper locking mechanisms when accessing clients from multiple threads
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
TOPIC_NAME = os.environ["SERVICEBUS_TOPIC_NAME"]


def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    sender.send_messages(message)


def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Message in list") for _ in range(10)]
    sender.send_messages(messages)


def send_batch_message(sender):
    batch_message = sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Message inside ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    sender.send_messages(batch_message)


# [START concurrent_sending_to_topic_with_threading]
def send_messages_to_topic_concurrently_with_threads():
    """
    Example of concurrent sending to topic using multiple threads with separate clients.
    RECOMMENDED: Use separate ServiceBusClient instances per thread.
    """
    def send_messages_from_thread(thread_id):
        # Create a separate client for each thread (recommended approach)
        thread_credential = DefaultAzureCredential()
        thread_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, thread_credential)
        with thread_client:
            with thread_client.get_topic_sender(topic_name=TOPIC_NAME) as thread_sender:
                for i in range(5):
                    message = ServiceBusMessage(f"Topic message {i} from thread {thread_id}")
                    thread_sender.send_messages(message)
        print(f"Thread {thread_id} completed sending to topic")

    # Launch multiple threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(send_messages_from_thread, i) for i in range(3)]
        for future in futures:
            future.result()


def send_topic_messages_with_shared_client_and_lock():
    """
    Example of using a shared client with proper locking for topic.
    NOT RECOMMENDED: Better to use separate clients per thread.
    """
    lock = threading.Lock()
    shared_credential = DefaultAzureCredential()
    shared_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, shared_credential)

    def send_with_lock(thread_id):
        with lock:
            # Only one thread can use the client at a time
            with shared_client.get_topic_sender(topic_name=TOPIC_NAME) as sender:
                message = ServiceBusMessage(f"Locked topic message from thread {thread_id}")
                sender.send_messages(message)
        print(f"Thread {thread_id} sent message to topic with lock")

    with shared_client:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_with_lock, i) for i in range(3)]
            for future in futures:
                future.result()

# [END concurrent_sending_to_topic_with_threading]


credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
    with sender:
        send_single_message(sender)
        send_a_list_of_messages(sender)
        send_batch_message(sender)

print("Send message is done.")

# Example of concurrent sending to topic (uncomment to run)
# print("Running concurrent topic sending examples...")
# send_messages_to_topic_concurrently_with_threads()
# send_topic_messages_with_shared_client_and_lock()
