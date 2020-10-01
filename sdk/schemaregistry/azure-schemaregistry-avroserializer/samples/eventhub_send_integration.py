#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending event to EventHub with SchemaRegistryAvroSerializer integrated for data serialization.
"""

# pylint: disable=C0111

import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMA_REGISTRY_ENDPOINT = os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP = os.environ['SCHEMA_REGISTRY_GROUP']

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


def send_event_data_batch(producer, serializer):
    event_data_batch = producer.create_batch()

    dict_data = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    # Use the serialize method to convert dict object to bytes with the given avro schema.
    # The serialize method would automatically register the schema into the Schema Registry Service and
    # schema would be cached locally for future usage.
    payload_bytes = serializer.serialize(data=dict_data, schema=SCHEMA_STRING)
    print('The bytes of serialized dict data is {}.'.format(payload_bytes))

    event_data = EventData(body=payload_bytes)  # pass the bytes data to the body of an EventData
    event_data_batch.add(event_data)
    producer.send_batch(event_data_batch)
    print('Send is done.')


# create an EventHubProducerClient instance
eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)


# create a SchemaRegistryAvroSerializer instance
avro_serializer = SchemaRegistryAvroSerializer(
    schema_registry=SchemaRegistryClient(
        endpoint=SCHEMA_REGISTRY_ENDPOINT,
        credential=DefaultAzureCredential()
    ),
    schema_group=SCHEMA_GROUP
)


with eventhub_producer, avro_serializer:
    send_event_data_batch(eventhub_producer, avro_serializer)
