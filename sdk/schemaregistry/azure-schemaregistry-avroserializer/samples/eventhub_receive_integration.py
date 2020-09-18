#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show receiving events from EventHub with SchemaRegistryAvroSerializer integrated for data deserialization.
"""

# pylint: disable=C0111
import os
from azure.eventhub import EventHubConsumerClient
from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMA_REGISTRY_ENDPOINT = os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP = os.environ['SCHEMA_REGISTRY_GROUP']


def on_event(partition_context, event):
    print("Received event from partition: {}.".format(partition_context.partition_id))

    bytes_payload = b"".join(b for b in event.body)
    print('The received bytes of the EventData is {}.'.format(bytes_payload))

    # Use the deserialize method to convert bytes to dict object.
    # The deserialize method would extract the schema id from the payload, and automatically retrieve the Avro Schema
    # from the Schema Registry Service. The schema would be cached locally for future usage.
    deserialized_data = avro_serializer.deserialize(bytes_payload)
    print('The dict data after deserialization is {}'.format(deserialized_data))


# create an EventHubConsumerClient instance
eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
)


# create a SchemaRegistryAvroSerializer instance
avro_serializer = SchemaRegistryAvroSerializer(
    schema_registry=SchemaRegistryClient(
        endpoint=SCHEMA_REGISTRY_ENDPOINT,
        credential=DefaultAzureCredential()
    ),
    schema_group=SCHEMA_GROUP
)


try:
    with eventhub_consumer, avro_serializer:
        eventhub_consumer.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
except KeyboardInterrupt:
    print('Stopped receiving.')
