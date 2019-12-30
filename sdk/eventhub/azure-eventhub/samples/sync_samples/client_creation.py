#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show how to create EventHubProducerClient/EventHubConsumerClient
"""
import os
from azure.eventhub import (
    EventHubProducerClient,
    EventHubConsumerClient,
    TransportType,
    EventHubSharedKeyCredential
)


connection_string = os.environ['EVENT_HUB_CONN_STR']
fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
eventhub_name = os.environ['EVENT_HUB_NAME']
sas_policy = os.environ['EVENT_HUB_SAS_POLICY']
sas_key = os.environ['EVENT_HUB_SAS_KEY']
consumer_group = "$Default"


def create_producer_client():
    print('Examples showing how to create producer client.')

    # Create producer client from connection string

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=connection_string  # connection string contains EventHub name
    )

    # Illustration of commonly used parameters
    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=connection_string,
        logging_enable=True,  # Enable log for network tracing
        eventhub_name=eventhub_name,  # EventHub name should be specified if it doesn't show up in connection string
        retry_total=3,  # Retry up to 3 times to re-do failed operations
        transport_type=TransportType.AmqpOverWebsocket  # Use websocket as the underlying transport protocol
    )

    # Create producer client from constructor

    producer_client = EventHubProducerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        credential=EventHubSharedKeyCredential(
            policy=sas_policy,
            key=sas_key
        ),
        logging_enable=True,  # Enable network tracing log
        retry_total=3,  # Retry up to 3 times to re-do failed operations
        transport_type=TransportType.AmqpOverWebsocket  # Use websocket as the underlying transport protocol
    )

    print("Calling producer client get eventhub properties:", producer_client.get_eventhub_properties())


def create_consumer_client():
    print('Examples showing how to create consumer client.')

    # Create consumer client from connection string

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=connection_string,  # connection string contains EventHub name
        consumer_group=consumer_group
    )

    # Illustration of commonly used parameters
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=connection_string,
        consumer_group=consumer_group,
        eventhub_name=eventhub_name,  # EventHub name should be specified if it doesn't show up in connection string
        logging_enable=True,  # Enable log for network tracing
        retry_total=3,  # Retry up to 3 times to re-do failed operations
        transport_type=TransportType.AmqpOverWebsocket  # Use websocket as the underlying transport protocol
    )

    # Create consumer client from constructor

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=fully_qualified_namespace,
        eventhub_name=eventhub_name,
        consumer_group=consumer_group,
        credential=EventHubSharedKeyCredential(
            policy=sas_policy,
            key=sas_key
        ),
        logging_enable=True,  # Enable network tracing log
        retry_total=3,  # Retry up to 3 times to re-do failed operations
        transport_type=TransportType.AmqpOverWebsocket  # Use websocket as the underlying transport protocol
    )

    print("Calling consumer client get eventhub properties:", consumer_client.get_eventhub_properties())


create_producer_client()
create_consumer_client()
