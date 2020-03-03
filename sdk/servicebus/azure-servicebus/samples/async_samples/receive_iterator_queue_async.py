#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show iterator receiving from a Service Bus Queue asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus.aio import ServiceBusReceiverClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

receiver_client = ServiceBusReceiverClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME
)


async def main():
    async with receiver_client:
        async for msg in receiver_client:
            print(str(msg))
            await msg.complete()
    print("Receive is done.")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
