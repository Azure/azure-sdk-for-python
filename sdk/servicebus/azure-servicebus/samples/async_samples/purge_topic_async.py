#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show deleting message(s) from a Service Bus Topic.
"""

import os
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.core.exceptions import ResourceExistsError


CONNECTION_STR = os.environ['SERVICEBUS_CONNECTION_STR']
TOPIC_NAME = os.environ["SERVICEBUS_TOPIC_NAME"]

def create_subscription(servicebus_mgmt_client, subscription_name):
    try:
        servicebus_mgmt_client.create_subscription(TOPIC_NAME, subscription_name)
    except ResourceExistsError:
        pass
    print("Subscription {} is created.".format(subscription_name))


async def send_a_list_of_messages(sender):
    messages = [ServiceBusMessage("Message in list") for _ in range(10)]
    await sender.send_messages(messages)


async def send_batch_message(sender):
    batch_message = await sender.create_message_batch()
    for _ in range(10):
        try:
            batch_message.add_message(ServiceBusMessage("Message inside ServiceBusMessageBatch"))
        except ValueError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            break
    await sender.send_messages(batch_message)

async def main():
    servicebus_mgmt_client = ServiceBusAdministrationClient.from_connection_string(CONNECTION_STR)
    
    # Create subscriptions.
    create_subscription(servicebus_mgmt_client, 'sb-allmsgs-sub')
    
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)
    async with servicebus_client:
        sender = servicebus_client.get_topic_sender(topic_name=TOPIC_NAME)
        async with sender:
            await send_a_list_of_messages(sender)
            await send_batch_message(sender)

        receiver = servicebus_client.get_subscription_receiver(
                topic_name=TOPIC_NAME,
                subscription_name='sb-allmsgs-sub'
            )

        async with receiver:
            deleted_msgs = await receiver.purge_messages()
            print(deleted_msgs)

    print("Delete message is done.")

asyncio.run(main())