#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition with EventHubConsumerClient tracking
the last enqueued event properties of specific partition.
"""

import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def on_event(partition_context, event):
    print("Received events from partition: {}.".format(partition_context.partition_id))
    # Do some sync or async operations. If the operation is i/o intensive, async will have better performance.
    print(event)

    print("Last enqueued event properties from partition: {} is: {}.".format(
        partition_context.partition_id,
        partition_context.last_enqueued_event_properties)
    )
    await partition_context.update_checkpoint(event)


async def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
        eventhub_name=EVENTHUB_NAME,
    )
    async with client:
        await client.receive(
            on_event=on_event,
            partition_id='0',
            track_last_enqueued_event_properties=True,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )


if __name__ == '__main__':
    asyncio.run(main())
