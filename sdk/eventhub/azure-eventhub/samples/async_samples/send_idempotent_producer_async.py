#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show idempotent publishing events to an Event Hub partition asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
PARTITION_ID = "0"


async def send_event_data_batch(idempotent_producer, partition_id):
    # The partition_id must be set when creating an EventDataBatch object
    # when performing idempotent publishing as idempotency works on partitions.
    event_data_batch = await idempotent_producer.create_batch(partition_id=partition_id)
    for i in range(10):
        event_data_batch.add(EventData('Single message'))
    await idempotent_producer.send_batch(event_data_batch)

    starting_published_sequence_number = event_data_batch.starting_published_sequence_number
    ending_published_sequence_number = starting_published_sequence_number + len(event_data_batch) - 1
    # Inspect starting_published_sequence_number of the EventDataBatch object
    print("The starting published sequence number of the EventDataBatch is {}".format(starting_published_sequence_number))
    print("The ending published sequence number of the EventDataBatch is {}".format(ending_published_sequence_number))


async def send_event_data_list(idempotent_producer, partition_id):

    event_data_list = [EventData('Event Data {}'.format(i)) for i in range(10)]
    # The partition_id must be set when sending a list of EventData
    # when performing idempotent publishing as idempotency works on partitions.
    await idempotent_producer.send_batch(event_data_list, partition_id=partition_id)

    # Inspect published_sequence_number of the events in the list
    for event_data in event_data_list:
        print(
            "The published sequence number of the EventData: {} is: {}".format(
                event_data.body_as_str(),
                event_data.published_sequence_number
            )
        )

async def main():
    idempotent_producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME,
        enable_idempotent_partitions=True
    )

    async with idempotent_producer:
        await send_event_data_batch(idempotent_producer, PARTITION_ID)
        await send_event_data_list(idempotent_producer, PARTITION_ID)

        # Inspect the state of publishing for a partition
        partition_publishing_properties = await idempotent_producer.get_partition_publishing_properties(PARTITION_ID)
        print(
            "The state of publishing for partition {} is: {}".format(
                PARTITION_ID,
                partition_publishing_properties
            )
        )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
