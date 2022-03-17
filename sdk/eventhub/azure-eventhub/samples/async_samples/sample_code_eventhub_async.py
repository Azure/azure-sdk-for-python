#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
Examples to show basic async use case of python azure-eventhub SDK, including:
    - Create EventHubProducerClient
    - Create EventHubConsumerClient
    - Create EventData
    - Create EventDataBatch
    - Send EventDataBatch
    - Receive EventData
    - Close EventHubProducerClient
    - Close EventHubConsumerClient
"""

import logging
import asyncio


def example_create_async_eventhub_producer_client():
    # [START create_eventhub_producer_client_from_conn_str_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient
    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name = os.environ['EVENT_HUB_NAME']
    producer = EventHubProducerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    # [END create_eventhub_producer_client_from_conn_str_async]

    # [START create_eventhub_producer_client_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient, EventHubSharedKeyCredential

    fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
    eventhub_name = os.environ['EVENT_HUB_NAME']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    producer = EventHubProducerClient(fully_qualified_namespace=fully_qualified_namespace,
                                      eventhub_name=eventhub_name,
                                      credential=EventHubSharedKeyCredential(shared_access_policy, shared_access_key))
    # [END create_eventhub_producer_client_async]
    return producer


def example_create_async_eventhub_consumer_client():
    # [START create_eventhub_consumer_client_from_conn_str_async]
    import os
    from azure.eventhub.aio import EventHubConsumerClient
    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name = os.environ['EVENT_HUB_NAME']
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        consumer_group='$Default',
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    # [END create_eventhub_consumer_client_from_conn_str_async]

    # [START create_eventhub_consumer_client_async]
    import os
    from azure.eventhub.aio import EventHubConsumerClient, EventHubSharedKeyCredential

    fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
    eventhub_name = os.environ['EVENT_HUB_NAME']
    shared_access_policy = os.environ['EVENT_HUB_SAS_POLICY']
    shared_access_key = os.environ['EVENT_HUB_SAS_KEY']

    consumer = EventHubConsumerClient(fully_qualified_namespace=fully_qualified_namespace,
                                      consumer_group='$Default',
                                      eventhub_name=eventhub_name,
                                      credential=EventHubSharedKeyCredential(shared_access_policy, shared_access_key))
    # [END create_eventhub_consumer_client_async]
    return consumer


async def example_eventhub_async_send_and_receive():
    producer = example_create_async_eventhub_producer_client()
    consumer = example_create_async_eventhub_consumer_client()
    try:
        # [START eventhub_producer_client_create_batch_async]
        from azure.eventhub import EventData
        event_data_batch = await producer.create_batch()
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        # [END eventhub_producer_client_create_batch_async]

        # [START eventhub_producer_client_send_async]
        async with producer:
            event_data_batch = await producer.create_batch()
            while True:
                try:
                    event_data_batch.add(EventData('Message inside EventBatchData'))
                except ValueError:
                    # The EventDataBatch object reaches its max_size.
                    # You can send the full EventDataBatch object and create a new one here.
                    break
            await producer.send_batch(event_data_batch)
        # [END eventhub_producer_client_send_async]
        await asyncio.sleep(1)

        # [START eventhub_consumer_client_receive_async]
        logger = logging.getLogger("azure.eventhub")

        async def on_event(partition_context, event):
            # Put your code here.
            # If the operation is i/o intensive, async will have better performance.
            logger.info("Received event from partition: {}".format(partition_context.partition_id))

        async with consumer:
            await consumer.receive(
                on_event=on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
        # [END eventhub_consumer_client_receive_async]

        consumer = example_create_async_eventhub_consumer_client()
        # [START eventhub_consumer_client_receive_batch_async]
        logger = logging.getLogger("azure.eventhub")

        async def on_event_batch(partition_context, event_batch):
            # Put your code here.
            # If the operation is i/o intensive, async will have better performance.
            logger.info(
                "{} events received from partition: {}".format(len(event_batch), partition_context.partition_id)
            )

        async with consumer:
            await consumer.receive_batch(
                on_event_batch=on_event_batch,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
        # [END eventhub_consumer_client_receive_batch_async]

    finally:
        pass


async def example_eventhub_async_producer_send_and_close():
    # [START eventhub_producer_client_close_async]
    import os
    from azure.eventhub.aio import EventHubProducerClient
    from azure.eventhub import EventData

    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name = os.environ['EVENT_HUB_NAME']

    producer = EventHubProducerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )
    try:
        event_data_batch = await producer.create_batch()
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # The EventDataBatch object reaches its max_size.
                # You can send the full EventDataBatch object and create a new one here.
                break
        await producer.send_batch(event_data_batch)
    finally:
        # Close down the producer handler.
        await producer.close()
    # [END eventhub_producer_client_close_async]


async def example_eventhub_async_consumer_receive_and_close():
    # [START eventhub_consumer_client_close_async]
    import os

    event_hub_connection_str = os.environ['EVENT_HUB_CONN_STR']
    eventhub_name = os.environ['EVENT_HUB_NAME']

    from azure.eventhub.aio import EventHubConsumerClient
    consumer = EventHubConsumerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        consumer_group='$Default',
        eventhub_name=eventhub_name  # EventHub name should be specified if it doesn't show up in connection string.
    )

    logger = logging.getLogger("azure.eventhub")

    async def on_event(partition_context, event):
        # Put your code here.
        # If the operation is i/o intensive, async will have better performance.
        logger.info("Received event from partition: {}".format(partition_context.partition_id))

    # The receive method is a coroutine which will be blocking when awaited.
    # It can be executed in an async task for non-blocking behavior, and combined with the 'close' method.

    recv_task = asyncio.ensure_future(consumer.receive(on_event=on_event))
    await asyncio.sleep(3)  # keep receiving for 3 seconds
    recv_task.cancel()  # stop receiving

    # Close down the consumer handler explicitly.
    await consumer.close()
    # [END eventhub_consumer_client_close_async]

if __name__ == '__main__':
    asyncio.run(example_eventhub_async_consumer_receive_and_close())
    asyncio.run(example_eventhub_async_producer_send_and_close())
    asyncio.run(example_eventhub_async_send_and_receive())
