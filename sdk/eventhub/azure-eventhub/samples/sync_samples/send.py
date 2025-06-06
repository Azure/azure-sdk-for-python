#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub partition.

WARNING: EventHubProducerClient and EventDataBatch are not thread-safe!
Do not share these instances across threads. If you need to send from multiple threads,
create separate client instances for each thread or use proper synchronization mechanisms.
"""

import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from azure.eventhub import EventHubProducerClient, EventData
from azure.eventhub.exceptions import EventHubError
from azure.identity import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]


# [START send_event_data_batch]
def send_event_data_batch(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData("Single message"))
    producer.send_batch(event_data_batch)


# [END send_event_data_batch]


def send_event_data_batch_with_limited_size(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch_with_limited_size = producer.create_batch(max_size_in_bytes=1000)

    while True:
        try:
            event_data_batch_with_limited_size.add(EventData("Message inside EventBatchData"))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data.
            break

    producer.send_batch(event_data_batch_with_limited_size)


def send_event_data_batch_with_partition_key(producer):
    # Specifying partition_key.
    event_data_batch_with_partition_key = producer.create_batch(partition_key="pkey")
    event_data_batch_with_partition_key.add(
        EventData("Message will be sent to a partition determined by the partition key")
    )

    producer.send_batch(event_data_batch_with_partition_key)


def send_event_data_batch_with_partition_id(producer):
    # Specifying partition_id.
    event_data_batch_with_partition_id = producer.create_batch(partition_id="0")
    event_data_batch_with_partition_id.add(EventData("Message will be sent to target-id partition"))

    producer.send_batch(event_data_batch_with_partition_id)


def send_event_data_batch_with_properties(producer):
    event_data_batch = producer.create_batch()
    event_data = EventData("Message with properties")
    event_data.properties = {"prop_key": "prop_value"}
    event_data_batch.add(event_data)
    producer.send_batch(event_data_batch)


def send_event_data_list(producer):
    # If you know beforehand that the list of events you have will not exceed the
    # size limits, you can use the `send_batch()` api directly without creating an EventDataBatch

    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.

    event_data_list = [EventData("Event Data {}".format(i)) for i in range(10)]
    try:
        producer.send_batch(event_data_list)
    except ValueError:  # Size exceeds limit. This shouldn't happen if you make sure before hand.
        print("Size of the event data list exceeds the size limit of a single send")
    except EventHubError as eh_err:
        print("Sending error: ", eh_err)


def send_concurrent_with_threads_safe(credentials):
    """
    Example showing thread-safe concurrent sending using separate producers per thread.
    WARNING: Do NOT share EventHubProducerClient instances across threads!
    """
    def send_from_thread(thread_id):
        # Create a separate producer for each thread - clients are NOT thread-safe
        producer = EventHubProducerClient(
            fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
            eventhub_name=EVENTHUB_NAME,
            credential=credentials,
        )
        try:
            with producer:
                batch = producer.create_batch()
                batch.add(EventData(f"Message from thread {thread_id}"))
                producer.send_batch(batch)
                print(f"Thread {thread_id} sent message successfully")
        except Exception as e:
            print(f"Thread {thread_id} failed: {e}")

    # Use ThreadPoolExecutor to manage threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(send_from_thread, i) for i in range(3)]
        # Wait for all threads to complete
        for future in futures:
            future.result()


def send_concurrent_with_shared_client_and_lock():
    """
    Example showing concurrent sending with a shared client using locks.
    This is less efficient than separate clients but demonstrates thread synchronization.
    """
    send_lock = threading.Lock()
    
    producer = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
    )

    def send_with_lock(thread_id):
        try:
            # Use lock to ensure thread-safe sending
            with send_lock:
                batch = producer.create_batch()
                batch.add(EventData(f"Synchronized message from thread {thread_id}"))
                producer.send_batch(batch)
                print(f"Thread {thread_id} sent synchronized message successfully")
        except Exception as e:
            print(f"Thread {thread_id} failed: {e}")

    with producer:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(send_with_lock, i) for i in range(3)]
            # Wait for all threads to complete
            for future in futures:
                future.result()


producer = EventHubProducerClient(
    fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
    eventhub_name=EVENTHUB_NAME,
    credential=DefaultAzureCredential(),
)

start_time = time.time()
with producer:
    send_event_data_batch(producer)
    send_event_data_batch_with_limited_size(producer)
    send_event_data_batch_with_partition_key(producer)
    send_event_data_batch_with_partition_id(producer)
    send_event_data_batch_with_properties(producer)
    send_event_data_list(producer)

print("Send messages in {} seconds.".format(time.time() - start_time))

# Demonstrate concurrent sending
print("\nDemonstrating concurrent sending with separate producers...")
send_concurrent_with_threads_safe(DefaultAzureCredential())

print("\nDemonstrating concurrent sending with shared client and locks...")
send_concurrent_with_shared_client_and_lock()
