#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving deferred message from a Service Bus Queue asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus.aio import ServiceBusReceiverClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = 'testqueue'#os.environ["SERVICE_BUS_QUEUE_NAME"]

receiver_client = ServiceBusReceiverClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME,
    logging_enable=True
)


async def main():
    async with receiver_client:
        received_msgs = await receiver_client.receive(max_batch_size=10, timeout=5)
        deferred_sequenced_numbers = []
        for msg in received_msgs:
            print("Deferring msg: {}".format(str(msg)))
            deferred_sequenced_numbers.append(msg.sequence_number)
            await msg.defer()

        received_deferred_msg = await receiver_client.receive_deferred_messages(
            sequence_numbers=deferred_sequenced_numbers
        )

        for msg in received_deferred_msg:
            print("Completing deferred msg: {}".format(str(msg)))
            await msg.complete()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
print("Receive is done.")
