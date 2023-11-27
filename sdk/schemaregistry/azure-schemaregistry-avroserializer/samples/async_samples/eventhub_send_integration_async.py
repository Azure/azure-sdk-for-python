#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending event to EventHub with AvroSerializer integrated for data serialization.
"""

# pylint: disable=C0111

import os
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer.aio import AvroSerializer

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
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

# create an EventHubProducerClient instance
eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)
# create a AvroSerializer instance
azure_credential = DefaultAzureCredential()
avro_serializer = AvroSerializer(
    client=SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=azure_credential
    ),
    group_name=GROUP_NAME,
    auto_register_schemas=True
)

async def send_event_data_batch(producer, serializer):
    event_data_batch = await producer.create_batch()

    dict_data = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    # Use the serialize method to convert dict object to bytes with the given avro schema.
    # The serialize method would automatically register the schema into the Schema Registry Service and
    # schema would be cached locally for future usage.
    payload_bytes = await serializer.serialize(value=dict_data, schema=SCHEMA_STRING)
    print('The bytes of serialized dict data is {}.'.format(payload_bytes))

    event_data = EventData(body=payload_bytes)  # pass the bytes data to the body of an EventData
    event_data_batch.add(event_data)
    await producer.send_batch(event_data_batch)
    print('Send is done.')


async def main():

    await send_event_data_batch(eventhub_producer, avro_serializer)
    await avro_serializer.close()
    await azure_credential.close()
    await eventhub_producer.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
