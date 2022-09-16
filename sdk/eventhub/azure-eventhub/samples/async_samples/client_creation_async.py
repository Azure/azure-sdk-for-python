#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show how to create async EventHubProducerClient/EventHubConsumerClient.
"""
import asyncio
import os
from azure.eventhub import TransportType
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient, EventHubSharedKeyCredential


CONNECTION_STRING = os.environ['EVENT_HUB_CONN_STR']
FULLY_QUALIFIED_NAMESPACE = os.environ['EVENT_HUB_HOSTNAME']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
SAS_POLICY = os.environ['EVENT_HUB_SAS_POLICY']
SAS_KEY = os.environ['EVENT_HUB_SAS_KEY']
CONSUMER_GROUP = "$Default"


async def create_producer_client():
    print('Examples showing how to create producer client.')

    # Create producer client from connection string.

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING  # connection string contains EventHub name.
    )

    # Illustration of commonly used parameters.
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        eventhub_name=EVENTHUB_NAME,  # EventHub name should be specified if it doesn't show up in connection string.
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp  # Use Amqp as the underlying transport protocol.
    )

    # Create producer client from constructor.

    producer_client = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=EventHubSharedKeyCredential(
            policy=SAS_POLICY,
            key=SAS_KEY
        ),
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp  # Use Amqp as the underlying transport protocol.
    )

    async with producer_client:
        print("Calling producer client get eventhub properties:", await producer_client.get_eventhub_properties())


async def create_consumer_client():
    print('Examples showing how to create consumer client.')

    # Create consumer client from connection string.

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STRING,  # connection string contains EventHub name.
        consumer_group=CONSUMER_GROUP
    )

    # Illustration of commonly used parameters.
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENTHUB_NAME,  # EventHub name should be specified if it doesn't show up in connection string.
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp  # Use Amqp as the underlying transport protocol.
    )

    # Create consumer client from constructor.

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        consumer_group=CONSUMER_GROUP,
        credential=EventHubSharedKeyCredential(
            policy=SAS_POLICY,
            key=SAS_KEY
        ),
        logging_enable=False,  # To enable network tracing log, set logging_enable to True.
        retry_total=3,  # Retry up to 3 times to re-do failed operations.
        transport_type=TransportType.Amqp  # Use Amqp as the underlying transport protocol.
    )

    async with consumer_client:
        print("Calling consumer client get eventhub properties:", await consumer_client.get_eventhub_properties())


asyncio.run(create_producer_client())
asyncio.run(create_consumer_client())
