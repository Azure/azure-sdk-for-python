#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using AzureNamedKeyCredential.
"""

import os
import asyncio
from azure.core.credentials import AzureNamedKeyCredential
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage


FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]
SAS_POLICY = os.environ['SERVICE_BUS_SAS_POLICY']
SERVICEBUS_SAS_KEY = os.environ['SERVICE_BUS_SAS_KEY']


credential = AzureNamedKeyCredential(SAS_POLICY, SERVICEBUS_SAS_KEY)

async def send_message():
    async with ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential) as client:
        async with client.get_queue_sender(QUEUE_NAME) as sender:
            await sender.send_messages([ServiceBusMessage("hello")])

asyncio.run(send_message())
