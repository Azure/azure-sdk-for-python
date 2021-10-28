#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show receiving events from EventHub with AvroSerializer integrated for data deserialization.
"""

# pylint: disable=C0111
import os
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer.aio import AvroSerializer

EVENTHUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']


# create an EventHubConsumerClient instance
eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STR,
    consumer_group='$Default',
    eventhub_name=EVENTHUB_NAME,
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

async def on_event(partition_context, event):
    print("Received event from partition: {}.".format(partition_context.partition_id))

    bytes_payload = b"".join(b for b in event.body)
    print('The received bytes of the EventData is {}.'.format(bytes_payload))

    # Use the deserialize method to convert bytes to dict object.
    # The deserialize method would extract the schema id from the payload, and automatically retrieve the Avro Schema
    # from the Schema Registry Service. The schema would be cached locally for future usage.
    deserialized_data = await avro_serializer.deserialize(bytes_payload)
    print('The dict data after deserialization is {}'.format(deserialized_data))


async def main():
    try:
        async with eventhub_consumer, avro_serializer:
            await eventhub_consumer.receive(
                on_event=on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
    except KeyboardInterrupt:
        print('Stopped receiving.')
    finally:
        await avro_serializer.close()
        await azure_credential.close()
        await eventhub_consumer.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
