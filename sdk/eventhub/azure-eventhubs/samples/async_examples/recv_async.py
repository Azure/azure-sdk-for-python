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

RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]


async def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    # print(event)


async def event_handler(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        await asyncio.gather(*[do_operation(event) for event in events])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


async def wait_and_close(client, receiving_time):
    await asyncio.sleep(receiving_time)
    print('EventHubConsumer Client Closing.')
    await client.close()
    print('EventHubConsumer Client Closed.')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )
    try:
        tasks = asyncio.gather(*[client.receive(event_handler=event_handler, consumer_group="$default"),
                                 wait_and_close(client, 5)])
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        loop.run_until_complete(client.close())
    finally:
        loop.stop()
