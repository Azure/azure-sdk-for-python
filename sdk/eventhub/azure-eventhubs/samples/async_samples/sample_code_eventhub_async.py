#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import logging
import asyncio


def create_async_eventhub_producer_client():
    # [START create_eventhub_producer_client_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR,
                                                             event_hub_path=EVENT_HUB)
    # [END create_eventhub_producer_client_async]
    return producer


def create_async_eventhub_consumer_client():
    # [START create_eventhub_consumer_client_async]
    import os

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    from azure.eventhub.aio import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        event_hub_path=EVENT_HUB
    )
    # [END create_eventhub_consumer_client_async]
    return consumer


async def example_eventhub_async_send_and_receive(live_eventhub_config):
    producer = create_async_eventhub_producer_client()
    consumer = create_async_eventhub_consumer_client()
    try:
        # [START eventhub_producer_client_create_batch_async]
        from azure.eventhub import EventData
        event_data_batch = await producer.create_batch(max_size=10000)
        while True:
            try:
                event_data_batch.try_add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        # [END eventhub_producer_client_create_batch_async]

        # [START eventhub_producer_client_send_async]
        async with producer:
            event_data = EventData(b"A single event")
            await producer.send(event_data)
        # [END eventhub_producer_client_send_async]
        await asyncio.sleep(1)

        # [START eventhub_consumer_client_receive_async]
        logger = logging.getLogger("azure.eventhub")

        async def on_event(partition_context, events):
            logger.info("Received {} messages from partition: {}".format(
                len(events), partition_context.partition_id))
            # Do ops on received events
        async with consumer:
            task = asyncio.ensure_future(consumer.receive(on_event=on_event, consumer_group="$default"))
            await asyncio.sleep(3)  # keep receiving for 3 seconds
            task.cancel()  # stop receiving
        # [END eventhub_consumer_client_receive_async]
    finally:
        pass


async def example_eventhub_async_producer_ops(live_eventhub_config, connection_str):
    # [START eventhub_producer_client_close_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient
    from azure.eventhub import EventData

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR,
                                                             event_hub_path=EVENT_HUB)
    try:
        await producer.send(EventData(b"A single event"))
    finally:
        # Close down the producer handler.
        await producer.close()
    # [END eventhub_producer_client_close_async]


async def example_eventhub_async_consumer_ops(live_eventhub_config, connection_str):
    # [START eventhub_consumer_client_close_sync]
    import os

    EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENT_HUB = os.environ['EVENT_HUB_NAME']

    from azure.eventhub.aio import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR,
        event_hub_path=EVENT_HUB
    )

    logger = logging.getLogger("azure.eventhub")

    async def on_event(partition_context, events):
        logger.info("Received {} messages from partition: {}".format(
            len(events), partition_context.partition_id))
        # Do ops on received events

    recv_task = asyncio.ensure_future(consumer.receive(on_event=on_event, consumer_group='$Default'))
    await asyncio.sleep(3)  # keep receiving for 3 seconds
    recv_task.cancel()  # stop receiving

    # Close down the consumer handler explicitly.
    await consumer.close()
    # [END eventhub_consumer_client_close_sync]
