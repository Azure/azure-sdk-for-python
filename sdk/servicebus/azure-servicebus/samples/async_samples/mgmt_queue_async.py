#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show managing queue entities under a ServiceBus Namespace asynchronously, including
    - Create a queue
    - Get queue description and runtime information
    - Update a queue
    - Delete a queue
    - List queues under the given ServiceBus Namespace
"""

# pylint: disable=C0111

import os
import asyncio
from azure.servicebus.management import QueueDescription
from azure.servicebus.management.aio import ServiceBusManagementClient

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = "sb_mgmt_demo_queue"


async def create_queue(servicebus_mgmt_client):
    print("-- Create Queue")
    queue_description = QueueDescription()
    queue_description.queue_name = QUEUE_NAME
    # You can adjust the settings of a queue when creating.
    # Please refer to the QueueDescription class for available settings.
    queue_description.max_delivery_count = 10
    queue_description.dead_lettering_on_message_expiration = True

    await servicebus_mgmt_client.create_queue(queue_description)
    print("Queue {} is created.".format(QUEUE_NAME))
    print("")


async def delete_queue(servicebus_mgmt_client):
    print("-- Delete Queue")
    await servicebus_mgmt_client.delete_queue(QUEUE_NAME)
    print("Queue {} is deleted.".format(QUEUE_NAME))
    print("")


async def list_queues(servicebus_mgmt_client):
    print("-- List Queues")
    queues = await servicebus_mgmt_client.list_queues()
    print("Number of Queues in the ServiceBus Namespace:", len(queues))
    for queue_description in queues:
        print("Queue Name:", queue_description.queue_name)
    print("")


async def get_and_update_queue(servicebus_mgmt_client):
    print("-- Get and Update Queue")
    queue_description = await servicebus_mgmt_client.get_queue(QUEUE_NAME)
    print("Queue Name:", queue_description.queue_name)
    print("Queue Settings:")
    print("Auto Delete on Idle:", queue_description.auto_delete_on_idle)
    print("Default Message Time to Live:", queue_description.default_message_time_to_live)
    print("Dead Lettering on Message Expiration:", queue_description.dead_lettering_on_message_expiration)
    print("Please refer to QueueDescription for complete available settings.")
    print("")
    queue_description.max_delivery_count = 5
    await servicebus_mgmt_client.update_queue(queue_description)


async def get_queue_runtime_info(servicebus_mgmt_client):
    print("-- Get Queue Runtime Info")
    queue_runtime_info = await servicebus_mgmt_client.get_queue_runtime_info(QUEUE_NAME)
    print("Queue Name:", queue_runtime_info.queue_name)
    print("Queue Runtime Info:")
    print("Updated at:", queue_runtime_info.updated_at)
    print("Size in Bytes:", queue_runtime_info.size_in_bytes)
    print("Message Count:", queue_runtime_info.message_count)
    print("Please refer to QueueRuntimeInfo from complete available runtime information.")
    print("")


servicebus_mgmt_client = ServiceBusManagementClient.from_connection_string(CONNECTION_STR)


async def main():
    await create_queue(servicebus_mgmt_client)
    await list_queues(servicebus_mgmt_client)
    await get_and_update_queue(servicebus_mgmt_client)
    await get_queue_runtime_info(servicebus_mgmt_client)
    await delete_queue(servicebus_mgmt_client)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
