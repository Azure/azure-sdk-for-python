#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show receiving deferred message from a Service Bus Queue asynchronously.
"""

import os
import asyncio
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        messages = [ServiceBusMessage("Message to be deferred") for _ in range(10)]
        async with sender:
            await sender.send_messages(messages)

        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
        async with receiver:
            received_msgs = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
            deferred_sequenced_numbers = []
            for msg in received_msgs:
                print("Deferring msg: {}".format(str(msg)))
                deferred_sequenced_numbers.append(msg.sequence_number)
                await receiver.defer_message(msg)

            if deferred_sequenced_numbers:
                received_deferred_msg = await receiver.receive_deferred_messages(
                    sequence_numbers=deferred_sequenced_numbers
                )

                for msg in received_deferred_msg:
                    print("Completing deferred msg: {}".format(str(msg)))
                    await receiver.complete_message(msg)
            else:
                print("No messages received.")


asyncio.run(main())
print("Receive is done.")
