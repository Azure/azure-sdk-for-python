#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import asyncio


def create_async_eventhub_producer_client():
    # [START create_eventhub_producer_client_from_conn_str_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient
    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    event_hub = os.environ['EVENT_HUB_NAME']
    producer = EventHubProducerClient.from_connection_string(conn_str=event_hub_connection_str,
                                                             event_hub_path=event_hub)
    # [END create_eventhub_producer_client_from_conn_str_async]

    # [START create_eventhub_producer_client_async]
    import os
    from azure.eventhub import EventHubSharedKeyCredential
    from azure.eventhub.aio import EventHubProducerClient

    hostname = os.environ['EVENT_HUB_HOSTNAME']
    event_hub = os.environ['EVENT_HUB_NAME']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    producer = EventHubProducerClient(host=hostname,
                                      event_hub_path=event_hub,
                                      credential=EventHubSharedKeyCredential(shared_access_policy, shared_access_key))
    # [END create_eventhub_producer_client_async]
    return producer


def create_async_eventhub_consumer_client():
    # [START create_eventhub_consumer_client_from_conn_str_async]
    import os
    from azure.eventhub.aio import EventHubConsumerClient
    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    event_hub = os.environ['EVENT_HUB_NAME']
    consumer = EventHubConsumerClient.from_connection_string(conn_str=event_hub_connection_str,
                                                             event_hub_path=event_hub)
    # [END create_eventhub_consumer_client_from_conn_str_async]

    # [START create_eventhub_consumer_client_async]
    import os
    from azure.eventhub import EventHubSharedKeyCredential
    from azure.eventhub.aio import EventHubConsumerClient

    hostname = os.environ['EVENT_HUB_HOSTNAME']
    event_hub = os.environ['EVENT_HUB_NAME']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    consumer = EventHubConsumerClient(host=hostname,
                                      event_hub_path=event_hub,
                                      credential=EventHubSharedKeyCredential(shared_access_policy, shared_access_key))
    # [END create_eventhub_consumer_client_async]
    return consumer


async def example_eventhub_async_send_and_receive():
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

        async def on_events(partition_context, events):
            logger.info("Received {} messages from partition: {}".format(
                len(events), partition_context.partition_id))
            # Do ops on received events
        async with consumer:
            await consumer.receive(on_events=on_events, consumer_group="$default")
        # [END eventhub_consumer_client_receive_async]
    finally:
        pass


async def example_eventhub_async_producer_ops():
    # [START eventhub_producer_client_close_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient
    from azure.eventhub import EventData

    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    event_hub = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(conn_str=event_hub_connection_str,
                                                             event_hub_path=event_hub)
    try:
        await producer.send(EventData(b"A single event"))
    finally:
        # Close down the producer handler.
        await producer.close()
    # [END eventhub_producer_client_close_async]


async def example_eventhub_async_consumer_ops():
    # [START eventhub_consumer_client_close_async]
    import os

    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    event_hub = os.environ['EVENT_HUB_NAME']

    from azure.eventhub.aio import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        event_hub_path=event_hub
    )

    logger = logging.getLogger("azure.eventhub")

    async def on_events(partition_context, events):
        logger.info("Received {} messages from partition: {}".format(
            len(events), partition_context.partition_id))
        # Do ops on received events

    # The receive method is a coroutine method which can be called by `await consumer.receive(...)` and it will block.
    # so execute it in an async task to better demonstrate how to stop the receiving by calling he close method.

    recv_task = asyncio.ensure_future(consumer.receive(on_events=on_events, consumer_group='$Default'))
    await asyncio.sleep(3)  # keep receiving for 3 seconds
    recv_task.cancel()  # stop receiving

    # Close down the consumer handler explicitly.
    await consumer.close()
    # [END eventhub_consumer_client_close_async]

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example_eventhub_async_producer_ops())
    loop.run_until_complete(example_eventhub_async_consumer_ops())
    # loop.run_until_complete(example_eventhub_async_send_and_receive())
