#!/usr/bin/env python

"""
An example to show sending events asynchronously to an Event Hub with partition keys.
"""

# pylint: disable=C0111

import sys
import logging
import time
import asyncio
import os

from azure.eventhub import EventData, EventHubClientAsync, AsyncSender

import examples
logger = examples.get_logger(logging.INFO)

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')


async def run(client):
    sender = client.add_async_sender()
    await client.run_async()
    await send(sender, 4)


async def send(snd, count):
    for i in range(count):
        logger.info("Sending message: {}".format(i))
        data = EventData(str(i))
        data.partition_key = b'SamplePartitionKey'
        await snd.send(data)

try:
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    loop = asyncio.get_event_loop()
    client = EventHubClientAsync(ADDRESS, debug=True, username=USER, password=KEY)
    tasks = asyncio.gather(
        run(client),
        run(client))
    start_time = time.time()
    loop.run_until_complete(tasks)
    loop.run_until_complete(client.stop_async())
    end_time = time.time()
    run_time = end_time - start_time
    logger.info("Runtime: {} seconds".format(run_time))
    loop.close()

except KeyboardInterrupt:
    pass
