#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import datetime
import os
import time
import logging
import asyncio

from azure.eventhub import EventHubError, EventData


@pytest.mark.asyncio
async def test_example_eventhub_async_send_and_receive(live_eventhub_config):
    # [START create_eventhub_client_async]
    from azure.eventhub.aio import EventHubClient
    import os
    connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        os.environ['EVENT_HUB_HOSTNAME'],
        os.environ['EVENT_HUB_SAS_POLICY'],
        os.environ['EVENT_HUB_SAS_KEY'],
        os.environ['EVENT_HUB_NAME'])
    client = EventHubClient.from_connection_string(connection_str)
    # [END create_eventhub_client_async]

    from azure.eventhub import EventData, EventPosition

    # [START create_eventhub_client_async_sender]
    client = EventHubClient.from_connection_string(connection_str)
    # Create an async producer.
    producer = client.create_producer(partition_id="0")
    # [END create_eventhub_client_async_sender]

    # [START create_eventhub_client_async_receiver]
    client = EventHubClient.from_connection_string(connection_str)
    # Create an async consumer.
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    # Create an exclusive async consumer.
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'), owner_level=1)
    # [END create_eventhub_client_async_receiver]

    client = EventHubClient.from_connection_string(connection_str)
    producer = client.create_producer(partition_id="0")
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))

    await consumer.receive(timeout=1)

    # [START eventhub_client_async_create_batch]
    event_data_batch = await producer.create_batch(max_size=10000)
    while True:
        try:
            event_data_batch.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            # The EventDataBatch object reaches its max_size.
            # You can send the full EventDataBatch object and create a new one here.
            break
    # [END eventhub_client_async_create_batch]

    # [START eventhub_client_async_send]
    async with producer:
        event_data = EventData(b"A single event")
        await producer.send(event_data)
    # [END eventhub_client_async_send]

        await asyncio.sleep(1)

    # [START eventhub_client_async_receive]
    logger = logging.getLogger("azure.eventhub")
    async with consumer:
        received = await consumer.receive(timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
    # [END eventhub_client_async_receive]
        assert len(received) > 0
        assert received[0].body_as_str() == "A single event"
        assert list(received[-1].body)[0] == b"A single event"


@pytest.mark.asyncio
async def test_example_eventhub_async_producer_ops(live_eventhub_config, connection_str):
    from azure.eventhub.aio import EventHubClient
    from azure.eventhub import EventData

    # [START eventhub_client_async_sender_close]
    client = EventHubClient.from_connection_string(connection_str)
    producer = client.create_producer(partition_id="0")
    try:
        await producer.send(EventData(b"A single event"))
    finally:
        # Close down the send handler.
        await producer.close()
    # [END eventhub_client_async_sender_close]


@pytest.mark.asyncio
async def test_example_eventhub_async_consumer_ops(live_eventhub_config, connection_str):
    from azure.eventhub.aio import EventHubClient
    from azure.eventhub import EventPosition

    # [START eventhub_client_async_receiver_close]
    client = EventHubClient.from_connection_string(connection_str)
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    try:
        # Open and receive
        await consumer.receive(timeout=1)
    except:
        raise
    finally:
        # Close down the receive handler.
        await consumer.close()
    # [END eventhub_client_async_receiver_close]
