#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using aad credentials asynchronously
"""

import os
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import EnvironmentCredential


fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
eventhub_name = os.environ['EVENT_HUB_NAME']


async def run():
    credential = EnvironmentCredential()
    producer = EventHubProducerClient(fully_qualified_namespace=fully_qualified_namespace,
                                      eventhub_name=eventhub_name,
                                      credential=credential)

    async with producer:
        event_data_batch = await producer.create_batch(max_size_in_bytes=10000)
        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # EventDataBatch object reaches max_size.
                # New EventDataBatch object can be created here to send more data
                break
        await producer.send_batch(event_data_batch)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
print('Send finished.')
