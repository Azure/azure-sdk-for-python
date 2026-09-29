#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show managing topic entities under a ServiceBus Namespace, including
    - Create a topic
    - Get topic properties and runtime information
    - Read SQL and correlation filter counts using API version 2024-05
    - Update a topic
    - Delete a topic
    - List topics under the given ServiceBus Namespace
"""

import os
import asyncio
import uuid
import datetime
from azure.servicebus.aio.management import ApiVersion, ServiceBusAdministrationClient
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["SERVICEBUS_FULLY_QUALIFIED_NAMESPACE"]
TOPIC_NAME = "sb_mgmt_topic" + str(uuid.uuid4())


async def create_topic(servicebus_mgmt_client):
    print("-- Create Topic")
    await servicebus_mgmt_client.create_topic(TOPIC_NAME)
    print("Topic {} is created.".format(TOPIC_NAME))
    print("")


async def delete_topic(servicebus_mgmt_client):
    print("-- Delete Topic")
    await servicebus_mgmt_client.delete_topic(TOPIC_NAME)
    print("Topic {} is deleted.".format(TOPIC_NAME))
    print("")


async def list_topics(servicebus_mgmt_client):
    print("-- List Topics")
    async for topic_properties in servicebus_mgmt_client.list_topics():
        print("Topic Name:", topic_properties.name)
    print("")


async def get_and_update_topic(servicebus_mgmt_client):
    print("-- Get and Update Topic")
    topic_properties = await servicebus_mgmt_client.get_topic(TOPIC_NAME)
    print("Topic Name:", topic_properties.name)
    print("Please refer to TopicDescription for complete available settings.")
    print("")
    # update by updating the properties in the model
    topic_properties.default_message_time_to_live = datetime.timedelta(minutes=10)
    await servicebus_mgmt_client.update_topic(topic_properties)

    # update by passing keyword arguments
    topic_properties = await servicebus_mgmt_client.get_topic(TOPIC_NAME)
    await servicebus_mgmt_client.update_topic(
        topic_properties, default_message_time_to_live=datetime.timedelta(minutes=15)
    )


async def get_topic_runtime_properties(servicebus_mgmt_client):
    print("-- Get Topic Runtime Properties")
    runtime_properties = await servicebus_mgmt_client.get_topic_runtime_properties(TOPIC_NAME)
    print("Topic Name:", runtime_properties.name)
    print("SQL Filter Count:", runtime_properties.sql_filter_count)
    print("Correlation Filter Count:", runtime_properties.correlation_filter_count)
    print("Please refer to TopicRuntimeProperties from complete available runtime properties.")
    print("")


async def main():
    credential = DefaultAzureCredential()
    async with ServiceBusAdministrationClient(
        FULLY_QUALIFIED_NAMESPACE,
        credential,
        api_version=ApiVersion.V2024_05,
    ) as servicebus_mgmt_client:
        await create_topic(servicebus_mgmt_client)
        await list_topics(servicebus_mgmt_client)
        await get_and_update_topic(servicebus_mgmt_client)
        await get_topic_runtime_properties(servicebus_mgmt_client)
        await delete_topic(servicebus_mgmt_client)


asyncio.run(main())
