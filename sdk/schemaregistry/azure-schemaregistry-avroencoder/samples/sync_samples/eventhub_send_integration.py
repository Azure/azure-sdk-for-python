#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
FILE: eventhub_send_integration.py
DESCRIPTION:
    Examples to show sending events synchronously to EventHub with AvroEncoder integrated for content encoding.
USAGE:
    python eventhub_send_integration.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TENANT_ID - Required for use of the credential. The ID of the service principal's tenant.
     Also called its 'directory' ID.
    2) AZURE_CLIENT_ID - Required for use of the credential. The service principal's client ID.
     Also called its 'application' ID.
    3) AZURE_CLIENT_SECRET - Required for use of the credential. One of the service principal's client secrets.
    4) SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    5) SCHEMAREGISTRY_GROUP - The name of the schema group.
    6) EVENT_HUB_CONN_STR - The connection string of the Event Hubs namespace to send events to.
    7) EVENT_HUB_NAME - The name of the Event Hub in the Event Hubs namespace to send events to.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder import AvroEncoder

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_AVRO_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']

SCHEMA_STRING = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""


def send_event_data_batch(producer, encoder):
    event_data_batch = producer.create_batch()
    dict_content = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    # Use the encode method to convert dict object to bytes with the given avro schema and set body of EventData.
    # The encode method will automatically register the schema into the Schema Registry Service and
    # schema will be cached locally for future usage.
    event_data = encoder.encode(content=dict_content, schema=SCHEMA_STRING, message_type=EventData)
    print(f'The bytes of encoded dict content is {next(event_data.body)}.')

    event_data_batch.add(event_data)
    producer.send_batch(event_data_batch)
    print('Send is done.')


# create an EventHubProducerClient instance
eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
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


with eventhub_producer, avro_encoder:
    send_event_data_batch(eventhub_producer, avro_encoder)
