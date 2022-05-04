#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
FILE: eventhub_receive_integration.py
DESCRIPTION:
    Examples to show receiving events synchronously from EventHub with AvroEncoder integrated for content decoding.
USAGE:
    python eventhub_receive_integration.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TENANT_ID - Required for use of the credential. The ID of the service principal's tenant.
     Also called its 'directory' ID.
    2) AZURE_CLIENT_ID - Required for use of the credential. The service principal's client ID.
     Also called its 'application' ID.
    3) AZURE_CLIENT_SECRET - Required for use of the credential. One of the service principal's client secrets.
    4) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    5) SCHEMAREGISTRY_GROUP - The name of the schema group.
    6) EVENT_HUB_CONN_STR - The connection string of the Event Hubs namespace to receive events from.
    7) EVENT_HUB_NAME - The name of the Event Hub in the Event Hubs namespace to receive events from.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder import AvroEncoder

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']


def on_event(partition_context, event):
    print(f"Received event from partition: {partition_context.partition_id}.")

    bytes_payload = b"".join(b for b in event.body)
    print(f'The received bytes of the EventData is {bytes_payload}.')

    # Use the decode method to decode the payload of the event.
    # The decode method will extract the schema id from the content_type, and automatically retrieve the Avro Schema
    # from the Schema Registry Service. The schema will be cached locally for future usage.
    decoded_content = avro_encoder.decode(event)
    print(f'The dict content after decoding is {decoded_content}')


# create an EventHubConsumerClient instance
eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
)


# create a AvroEncoder instance
avro_encoder = AvroEncoder(
    client=SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=DefaultAzureCredential()
    ),
    group_name=GROUP_NAME,
    auto_register=True
)


try:
    with eventhub_consumer, avro_encoder:
        eventhub_consumer.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
except KeyboardInterrupt:
    print('Stopped receiving.')
