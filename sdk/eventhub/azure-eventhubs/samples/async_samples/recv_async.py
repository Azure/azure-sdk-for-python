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


async def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    # print(event)


async def on_events(partition_context, events):
    # put your code here
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    await asyncio.gather(*[do_operation(event) for event in events])


async def receive(client):
    try:
        await client.receive(on_events=on_events,
                             consumer_group="$default")
    except KeyboardInterrupt:
        await client.close()


async def main():
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
    )
    async with client:
        await receive(client)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
