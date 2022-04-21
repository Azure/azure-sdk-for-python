#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to demonstrate utilizing AzureNamedKeyCredential to authenticate with Event Hubs asynchronously.
"""

import os
import asyncio
import time
from azure.core.credentials import AzureNamedKeyCredential
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

# Target namespace and hub must also be specified.
FULLY_QUALIFIED_NAMESPACE = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

EVENTHUB_POLICY_NAME = os.environ['EVENT_HUB_SAS_POLICY']
EVENTHUB_KEY = os.environ['EVENT_HUB_SAS_KEY']

credential = AzureNamedKeyCredential(EVENTHUB_POLICY_NAME, EVENTHUB_KEY)

producer_client = EventHubProducerClient(
    fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
    eventhub_name=EVENTHUB_NAME,
    credential=credential,
    logging_enable=True
)

start_time = time.time()
async def authenticate_with_named_key():
    async with producer_client:
        event_data_batch = await producer_client.create_batch()
        event_data_batch.add(EventData('Single message'))
        await producer_client.send_batch(event_data_batch)

start_time = time.time()
asyncio.run(authenticate_with_named_key())
print("Send messages in {} seconds.".format(time.time() - start_time))
