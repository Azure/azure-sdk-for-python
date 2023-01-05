#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from Event Hub partitions with custom starting position asynchronously.
"""
import os
import asyncio
from typing import TYPE_CHECKING, Optional, Dict, Any
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient
from azure.eventhub import EventData

if TYPE_CHECKING:
    from azure.eventhub.aio import PartitionContext
    from azure.eventhub import CloseReason, EventDataBatch

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def on_partition_initialize(partition_context: PartitionContext) -> None:
    # Put your code here.
    print(f"Partition: {partition_context.partition_id} has been initialized.")


async def on_partition_close(partition_context: PartitionContext, reason: CloseReason) -> None:
    # Put your code here.
    print(f"Partition: {partition_context.partition_id} has been closed, reason for closing: {reason}.")


async def on_error(partition_context: PartitionContext, error: Exception) -> None:
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print(f"An exception: {partition_context.partition_id} occurred during receiving from Partition: {error}.")
    else:
        print(f"An exception: {error} occurred during the load balance process.")


async def on_event(partition_context: PartitionContext, event: Optional[EventData]) -> None:
    # Put your code here.
    print(f"Received event: {event.body_as_str()} from partition: {partition_context.partition_id}.")
    await partition_context.update_checkpoint(event)


async def main() -> None:
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME,
    )

    async with producer_client:
        event_data_batch_to_partition_0: EventDataBatch = await producer_client.create_batch(partition_id='0')
        event_data_batch_to_partition_0.add(EventData("First event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Second event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Third event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Forth event in partition 0"))
        await producer_client.send_batch(event_data_batch_to_partition_0)

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
    )

    partition_0_prop: Dict[str, Any] = await consumer_client.get_partition_properties("0")
    partition_0_last_enqueued_sequence_number = partition_0_prop["last_enqueued_sequence_number"]

    # client will receive messages from the position of the third from last event on partition 0.
    starting_position = {
        "0": partition_0_last_enqueued_sequence_number - 3,
    }

    async with consumer_client:
        await consumer_client.receive(
            partition_id="0",
            on_event=on_event,
            on_partition_initialize=on_partition_initialize,
            on_partition_close=on_partition_close,
            on_error=on_error,
            starting_position=starting_position
        )


if __name__ == '__main__':
    asyncio.run(main())
