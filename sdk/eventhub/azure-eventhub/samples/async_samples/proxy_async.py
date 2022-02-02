#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show async sending and receiving events behind a proxy.
"""
import os
import asyncio
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient
from azure.eventhub import EventData

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

HTTP_PROXY = {
    'proxy_hostname': '127.0.0.1',  # proxy hostname.
    'proxy_port': 3128,  # proxy port.
    'username': 'admin',  # username used for proxy authentication if needed.
    'password': '123456'  # password used for proxy authentication if needed.
}


async def on_event(partition_context, event):
    # Put your code here.
    print("received event from partition: {}.".format(partition_context.partition_id))
    print(event)


async def main():
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
        http_proxy=HTTP_PROXY
    )

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME,
        http_proxy=HTTP_PROXY
    )

    async with producer_client:
        event_data_batch = await producer_client.create_batch(max_size_in_bytes=10000)
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # EventDataBatch object reaches max_size.
                # New EventDataBatch object can be created here to send more data.
                break
        await producer_client.send_batch(event_data_batch)
        print('Finished sending.')

    async with consumer_client:
        await consumer_client.receive(on_event=on_event)
        print('Finished receiving.')


asyncio.run(main())
