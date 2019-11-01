#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import time
import logging


def create_eventhub_producer_client():
    # [START create_eventhub_producer_client_sync]
    import os
    from azure.eventhub import EventHubProducerClient

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR,
                                                             event_hub_path=EVENT_HUB)
    # [END create_eventhub_producer_client_sync]
    return producer


def create_eventhub_consumer_client():
    # [START create_eventhub_consumer_client_sync]
    import os

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    from azure.eventhub import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        event_hub_path=EVENT_HUB
    )
    # [END create_eventhub_consumer_client_sync]
    return consumer


def example_eventhub_sync_send_and_receive():
    producer = create_eventhub_producer_client()
    consumer = create_eventhub_consumer_client()
    try:
        logger = logging.getLogger("azure.eventhub")

        # [START create_event_data]
        from azure.eventhub import EventData

        event_data = EventData("String data")
        event_data = EventData(b"Bytes data")
        event_data = EventData([b"A", b"B", b"C"])

        list_data = ['Message {}'.format(i) for i in range(10)]
        event_data = EventData(body=list_data)
        # [END create_event_data]

        # [START eventhub_producer_client_create_batch_sync]
        event_data_batch = producer.create_batch(max_size=10000)
        while True:
            try:
                event_data_batch.try_add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        # [END eventhub_producer_client_create_batch_sync]

        # [START eventhub_producer_client_send_sync]
        with producer:
            event_data = EventData(b"A single event")
            producer.send(event_data)
        # [END eventhub_producer_client_send_sync]
        time.sleep(1)

        # [START eventhub_consumer_client_receive_sync]
        logger = logging.getLogger("azure.eventhub")

        def on_event(partition_context, events):
            logger.info("Received {} messages from partition: {}".format(
                len(events), partition_context.partition_id))
            # Do ops on received events

        with consumer:
            consumer.receive(on_event=on_event, consumer_group='$Default')
        # [END eventhub_consumer_client_receive_sync]
    finally:
        pass


def example_eventhub_producer_ops():
    # [START eventhub_producer_client_close_sync]
    import os
    from azure.eventhub import EventHubProducerClient, EventData

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR,
                                                             event_hub_path=EVENT_HUB)
    try:
        producer.send(EventData(b"A single event"))
    finally:
        # Close down the producer handler.
        producer.close()
    # [END eventhub_producer_client_close_sync]


def example_eventhub_consumer_ops():
    # [START eventhub_consumer_client_close_sync]
    import os
    import threading

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    from azure.eventhub import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        event_hub_path=EVENT_HUB
    )

    logger = logging.getLogger("azure.eventhub")

    def on_event(partition_context, events):
        logger.info("Received {} messages from partition: {}".format(
            len(events), partition_context.partition_id))
        # Do ops on received events

    # The receive method is blocking call, so execute it in a thread to
    # better demonstrate how to stop the receiving by calling he close method.

    worker = threading.Thread(target=consumer.receive,
                              kwargs={"on_event": on_event,
                                      "consumer_group": "$Default"})
    worker.start()
    time.sleep(10)  # Keep receiving for 10s then close.
    # Close down the consumer handler explicitly.
    consumer.close()
    # [END eventhub_consumer_client_close_sync]


if __name__ == '__main__':
    example_eventhub_producer_ops()
    example_eventhub_consumer_ops()
    # example_eventhub_sync_send_and_receive()
