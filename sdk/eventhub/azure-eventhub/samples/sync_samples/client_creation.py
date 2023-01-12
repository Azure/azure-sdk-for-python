#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show how to create EventHubProducerClient/EventHubConsumerClient.
"""
import os
from azure.eventhub import (
    EventHubProducerClient,
    EventHubConsumerClient,
    TransportType,
    EventHubSharedKeyCredential
)


CONNECTION_STRING = 'Endpoint=sb://kashifk1.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=LmIpx06/gDr+B6NM3rCmRU7jpcUFvFdY6MzwF+ggnhk='
#FULLY_QUALIFIED_NAMESPACE = os.envi
EVENTHUB_NAME = 'test'



def create_producer_client():
    print('Examples showing how to create producer client.')

    # Create producer client from connection string.

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        eventhub_name= EVENTHUB_NAME

    )


    print("Calling producer client get eventhub properties:", producer_client.get_eventhub_properties())


def create_consumer_client():
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

    print("Calling consumer client get eventhub properties:", consumer_client.get_eventhub_properties())


create_producer_client()
#create_consumer_client()
# 