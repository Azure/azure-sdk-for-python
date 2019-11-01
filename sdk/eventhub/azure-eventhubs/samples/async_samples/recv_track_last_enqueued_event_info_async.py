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

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]


async def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    # print(event)


async def on_event(partition_context, events):
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    await asyncio.gather(*[do_operation(event) for event in events])

    print("Last enqueued event properties from partition: {} is: {}".
          format(partition_context.partition_id,
                 events[-1].last_enqueued_event_properties))


async def receive_for_a_while(client, duration):
    task = asyncio.ensure_future(client.receive(on_event=on_event,
                                                consumer_group="$default",
                                                partition_id='0'))
    await asyncio.sleep(duration)
    task.cancel()


async def receive_forever(client):
    try:
        await client.receive(on_event=on_event,
                             consumer_group="$default",
                             partition_id='0')
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )
    try:
        loop.run_until_complete(receive_for_a_while(client, 5))
        # loop.run_until_complete(receive_forever(client))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(client.close())
        loop.stop()
