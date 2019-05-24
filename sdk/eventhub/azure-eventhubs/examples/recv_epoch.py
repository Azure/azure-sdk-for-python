#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition as an epoch receiver.
"""

import os
import sys
import time
import logging
import asyncio
from azure.eventhub import Offset, EventHubClientAsync, AsyncReceiver

import examples
logger = examples.get_logger(logging.INFO)

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')
CONSUMER_GROUP = "$default"
EPOCH = 42
PARTITION = "0"


async def pump(client, epoch):
    receiver = client.add_async_epoch_receiver(CONSUMER_GROUP, PARTITION, epoch=epoch)
    await client.run_async()
    total = 0
    start_time = time.time()
    for event_data in await receiver.receive(timeout=5):
        last_offset = event_data.offset
        last_sn = event_data.sequence_number
        total += 1
    end_time = time.time()
    run_time = end_time - start_time
    await client.stop_async()
    print("Received {} messages in {} seconds".format(total, run_time))

try:
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    loop = asyncio.get_event_loop()
    client = EventHubClientAsync(ADDRESS, debug=False, username=USER, password=KEY)
    loop.run_until_complete(pump(client, 20))
    loop.close()

except KeyboardInterrupt:
    pass
