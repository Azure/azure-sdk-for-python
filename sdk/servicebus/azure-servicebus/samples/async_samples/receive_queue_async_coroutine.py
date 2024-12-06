#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show sending message(s) to a Service Bus Queue asynchronously.
"""

import os
import asyncio
import logging
import sys
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import DefaultAzureCredential

logger = logging.getLogger("azure.servicebus")
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("[%(thread)d.%(threadName)s] - %(name)-12s  >>>>>>   %(message)s"))


FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
QUEUE_NAME = os.environ["SERVICEBUS_QUEUE_NAME"]


async def receive_single_message(receiver):
    message = await receiver.receive_messages()
    await asyncio.sleep(12 * 60)
    await receiver.complete_message(message[0])


async def main():
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)

    async with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
        async with receiver:
            print("Creating tasks")
            tasks = [
                asyncio.create_task(receive_single_message(receiver)),
                asyncio.create_task(receive_single_message(receiver)),
                # asyncio.create_task(receive_single_message(receiver)),
                # asyncio.create_task(receive_single_message(receiver)),
                # asyncio.create_task(receive_single_message(receiver)),
            ]
            await asyncio.gather(*tasks)

    print("Receive messages is done.")


asyncio.run(main())
