#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue.

WARNING: ServiceBusClient, ServiceBusSender, and ServiceBusMessageBatch are not thread-safe.
Do not share these instances between threads without proper thread-safe management using mechanisms like threading.Lock.
"""

import os
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]


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
            batch_message.add_message(ServiceBusMessage("Message inside a ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    sender.send_messages(batch_message)





def send_concurrent_with_shared_client_and_lock():
    """
    Example showing concurrent sending with a shared client using threading.Lock.
    Note: Native async APIs should be used instead of running in a ThreadPoolExecutor, if possible.
    """
    send_lock = threading.Lock()
    
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)

    def send_with_lock(thread_id):
        try:
            # Use lock to ensure thread-safe sending
            with send_lock:
                sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
                with sender:
                    message = ServiceBusMessage(f"Synchronized message from thread {thread_id}")
                    sender.send_messages(message)
                    print(f"Thread {thread_id} sent synchronized message successfully")
        except Exception as e:
            print(f"Thread {thread_id} failed: {e}")

    with servicebus_client:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_with_lock, i) for i in range(3)]
            # Wait for all threads to complete
            for future in futures:
                future.result()


def send_with_run_in_executor():
    """
    Example showing how to use asyncio.run_in_executor for sync operations in async context.
    This is useful when you need to call sync Service Bus operations from async code.
    """
    async def async_main():
        loop = asyncio.get_event_loop()
        
        def sync_send_operation():
            credential = DefaultAzureCredential()
            servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)
            with servicebus_client:
                sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
                with sender:
                    message = ServiceBusMessage("Message sent via run_in_executor")
                    sender.send_messages(message)
                    return "Message sent successfully"
        
        # Run the synchronous operation in an executor
        result = await loop.run_in_executor(None, sync_send_operation)
        print(f"run_in_executor result: {result}")
    
    asyncio.run(async_main())


credential = DefaultAzureCredential()
servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        send_single_message(sender)
        send_a_list_of_messages(sender)
        send_batch_message(sender)

print("Send message is done.")



print("\nDemonstrating concurrent sending with shared client and locks...")
send_concurrent_with_shared_client_and_lock()

print("\nDemonstrating run_in_executor pattern...")
send_with_run_in_executor()
