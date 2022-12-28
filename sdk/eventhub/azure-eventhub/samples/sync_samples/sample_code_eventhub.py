#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
Examples to show basic use case of python azure-eventhub SDK, including:
    - Create EventHubProducerClient
    - Create EventHubConsumerClient
    - Create EventData
    - Create EventDataBatch
    - Send EventDataBatch
    - Receive EventData
    - Close EventHubProducerClient
    - Close EventHubConsumerClient
"""

import time
import logging
import os
from typing import TYPE_CHECKING
from azure.eventhub import EventHubConsumerClient, EventHubProducerClient, EventHubSharedKeyCredential

if TYPE_CHECKING:
    from typing import Optional, List
    from azure.eventhub import EventData, EventDataBatch, PartitionContext

def example_create_eventhub_producer_client() -> EventHubProducerClient:
    # [START create_eventhub_producer_client_from_conn_str_sync]
    event_hub_connection_str: str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name: str = os.environ['EVENT_HUB_NAME']
    producer: EventHubProducerClient = EventHubProducerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    # [END create_eventhub_producer_client_from_conn_str_sync]

    # [START create_eventhub_producer_client_sync]

    fully_qualified_namespace: str = os.environ['EVENT_HUB_HOSTNAME']
    eventhub_name = os.environ['EVENT_HUB_NAME']
    shared_access_policy: str = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key: str = os.environ['EVENT_HUB_SAS_KEY']

    credential: EventHubSharedKeyCredential = EventHubSharedKeyCredential(shared_access_policy, shared_access_key)
    producer = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,  # EventHub name should be specified if it doesn't show up in connection string.
        credential=credential
    )
    # [END create_eventhub_producer_client_sync]
    return producer


def example_create_eventhub_consumer_client():
    # [START create_eventhub_consumer_client_from_conn_str_sync] 
    event_hub_connection_str: str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name: str = os.environ['EVENT_HUB_NAME']
    consumer: EventHubProducerClient = EventHubConsumerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        consumer_group='$Default',
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    # [END create_eventhub_consumer_client_from_conn_str_sync]

    # [START create_eventhub_consumer_client_sync]
    
    fully_qualified_namespace: str = os.environ['EVENT_HUB_HOSTNAME']
    eventhub_name: str = os.environ['EVENT_HUB_NAME']
    shared_access_policy: str = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key: str = os.environ['EVENT_HUB_SAS_KEY']

    credential: EventHubSharedKeyCredential = EventHubSharedKeyCredential(shared_access_policy, shared_access_key)
    consumer: EventHubConsumerClient = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group='$Default',
        credential=credential)
    # [END create_eventhub_consumer_client_sync]
    return consumer


def example_eventhub_sync_send_and_receive() -> None:
    producer: EventHubProducerClient = example_create_eventhub_producer_client()
    consumer: EventHubConsumerClient = example_create_eventhub_consumer_client()
    try:
        logger = logging.getLogger("azure.eventhub")

        # [START create_event_data]

        event_data: EventData = EventData("String data")
        event_data = EventData(b"Bytes data")

        # [END create_event_data]

        # [START eventhub_producer_client_create_batch_sync]
        event_data_batch: EventDataBatch = producer.create_batch()
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        # [END eventhub_producer_client_create_batch_sync]

        # [START eventhub_producer_client_send_sync]
        with producer:
            event_data_batch = producer.create_batch()

            while True:
                try:
                    event_data_batch.add(EventData('Message inside EventBatchData'))
                except ValueError:
                    # EventDataBatch object reaches max_size.
                    # New EventDataBatch object can be created here to send more data
                    break

            producer.send_batch(event_data_batch)
        # [END eventhub_producer_client_send_sync]
        time.sleep(1)

        # [START eventhub_consumer_client_receive_sync]
        logger = logging.getLogger("azure.eventhub")

        def on_event(partition_context: PartitionContext, event: Optional[EventData]) -> None:
            # Put your code here.
            # If the operation is i/o intensive, multi-thread will have better performance.
            logger.info("Received event from partition: {}".format(partition_context.partition_id))

        with consumer:
            consumer.receive(on_event=on_event)
        # [END eventhub_consumer_client_receive_sync]

        # [START eventhub_consumer_client_receive_batch_sync]
        logger = logging.getLogger("azure.eventhub")

        def on_event_batch(partition_context: PartitionContext, event_batch: List[EventData]):
            # Put your code here.
            # If the operation is i/o intensive, multi-thread will have better performance.
            logger.info("Received events from partition: {}".format(partition_context.partition_id))

        with consumer:
            consumer.receive_batch(on_event_batch=on_event_batch)
        # [END eventhub_consumer_client_receive_batch_sync]
    finally:
        pass


def example_eventhub_producer_send_and_close():
    # [START eventhub_producer_client_close_sync]
    event_hub_connection_str: str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name: str = os.environ['EVENT_HUB_NAME']

    producer: EventHubProducerClient = EventHubProducerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    try:
        event_data_batch: EventDataBatch = producer.create_batch()

        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # EventDataBatch object reaches max_size.
                # New EventDataBatch object can be created here to send more data
                break

        producer.send_batch(event_data_batch)
    finally:
        # Close down the producer handler.
        producer.close()
    # [END eventhub_producer_client_close_sync]


def example_eventhub_consumer_receive_and_close():
    # [START eventhub_consumer_client_close_sync]
    import threading

    event_hub_connection_str: str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name: str = os.environ['EVENT_HUB_NAME']

    consumer: EventHubConsumerClient = EventHubConsumerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        consumer_group="$Default",
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )

    logger = logging.getLogger("azure.eventhub")

    def on_event(partition_context: PartitionContext, event: Optional[EventData]) -> None:
        # Put your code here.
        # If the operation is i/o intensive, multi-thread will have better performance.
        logger.info("Received event from partition: {}".format(partition_context.partition_id))

    # The 'receive' method is a blocking call, it can be executed in a thread for
    # non-blocking behavior, and combined with the 'close' method.

    worker = threading.Thread(
        target=consumer.receive,
        kwargs={
            "on_event": on_event,
            "starting_position": "-1",  # "-1" is from the beginning of the partition.
        }
    )
    worker.start()
    time.sleep(10)  # Keep receiving for 10s then close.
    # Close down the consumer handler explicitly.
    consumer.close()
    # [END eventhub_consumer_client_close_sync]


if __name__ == '__main__':
    example_eventhub_producer_send_and_close()
    example_eventhub_consumer_receive_and_close()
    example_eventhub_sync_send_and_receive()
