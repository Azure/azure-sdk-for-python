#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub asynchronously.
"""

import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient


CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def on_event(partition_context, event):
    # Put your code here.
    # If the operation is i/o intensive, async will have better performance.
    print("Received event from partition: {}.".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)


async def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))


async def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(
        partition_context.partition_id,
        reason
    ))


async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            partition_context.partition_id,
            error
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


async def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
        eventhub_name=EVENTHUB_NAME
    )
    async with client:
        await client.receive(
            on_event=on_event,
            on_error=on_error,
            on_partition_close=on_partition_close,
            on_partition_initialize=on_partition_initialize,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )


async def localplay():
    from azure.eventhub.aio import EventHubProducerClient
    from azure.eventhub import EventDataBatch, EventData
    import logging
    logging.basicConfig(level=logging.INFO)

    client = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME, idle_timeout=10, retry_total=0, logging_enable=True)
    async with client:
        ed = EventData('data')
        sender = client._create_producer(partition_id='0')
        async with sender:
            await sender._open_with_retry()
            await asyncio.sleep(11)
            sender._unsent_events = [ed.message]
            #with pytest.raises(error.AMQPConnectionError):
            await sender._send_event_data()
            #await sender._send_event_data_with_retry()

def localplaysync():
    import threading, time
    client = EventHubConsumerClient.from_connection_string(CONNECTION_STR, eventhub_name=EVENTHUB_NAME, consumer_group='$default')
    def on_event_batch(partition_context, event_batch):
        on_event_batch.event_batch = event_batch

    on_event_batch.event_batch = None

    max_wait_time=3
    sleep_time=10000
    expected_result=[]
    with client:
        worker = threading.Thread(target=client.receive_batch, args=(on_event_batch,), kwargs={
            "max_wait_time": max_wait_time, "starting_position": "-1"
        })
        worker.start()
        time.sleep(sleep_time)
        assert on_event_batch.event_batch == expected_result
    worker.join()


if __name__ == '__main__':
    asyncio.run(localplay())
