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


async def send_single_message(sender):
    message = ServiceBusMessage("Single Message")
    await sender.send_messages(message)


async def main():
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential, logging_enable=True)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            print("Creating tasks")
            tasks = [
                asyncio.create_task(send_single_message(sender)),
                asyncio.create_task(send_single_message(sender)),
                asyncio.create_task(send_single_message(sender)),
                asyncio.create_task(send_single_message(sender)),
                asyncio.create_task(send_single_message(sender)),
            ]
            await asyncio.gather(*tasks)

    print("Send message is done.")


asyncio.run(main())
