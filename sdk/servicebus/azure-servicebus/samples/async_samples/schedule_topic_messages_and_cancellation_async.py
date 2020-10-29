#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show scheduling messages to and cancelling messages from a Service Bus Topic asynchronously.
"""

# pylint: disable=C0111

import os
import asyncio
import datetime
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

CONNECTION_STR = os.environ["SERVICE_BUS_CONNECTION_STR"]
TOPIC_NAME = os.environ["SERVICE_BUS_TOPIC_NAME"]


async def schedule_single_message(sender):
    message = ServiceBusMessage("Message to be scheduled")
    scheduled_time_utc = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    sequence_number = await sender.schedule_messages(message, scheduled_time_utc)
    return sequence_number


async def schedule_multiple_messages(sender):
    messages_to_schedule = []
    for _ in range(10):
        messages_to_schedule.append(ServiceBusMessage("Message to be scheduled"))

    scheduled_time_utc = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    sequence_numbers = await sender.schedule_messages(
        messages_to_schedule, scheduled_time_utc
    )
    return sequence_numbers


async def main():
    servicebus_client = ServiceBusClient.from_connection_string(
        conn_str=CONNECTION_STR, logging_enable=True
    )
    async with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
        async with sender:
            sequence_number = await schedule_single_message(sender)
            print(
                "Single message is scheduled and sequence number is {}".format(
                    sequence_number
                )
            )
            sequence_numbers = await schedule_multiple_messages(sender)
            print(
                "Multiple messages are scheduled and sequence numbers are {}".format(
                    sequence_numbers
                )
            )

            await sender.cancel_scheduled_messages(sequence_number)
            await sender.cancel_scheduled_messages(sequence_numbers)
            print("All scheduled messages are cancelled.")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
