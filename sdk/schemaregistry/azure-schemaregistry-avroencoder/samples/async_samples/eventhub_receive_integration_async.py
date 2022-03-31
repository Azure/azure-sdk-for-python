#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show receiving events from EventHub with AvroEncoder integrated for content decoding.
"""

# pylint: disable=C0111
import os
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder.aio import AvroEncoder

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
# create a AvroEncoder instance
azure_credential = DefaultAzureCredential()
avro_encoder = AvroEncoder(
    client=SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=azure_credential
    ),
    group_name=GROUP_NAME,
    auto_register=True
)

async def on_event(partition_context, event):
    print(f"Received event from partition: {partition_context.partition_id}.")

    bytes_payload = b"".join(b for b in event.body)
    print(f'The received bytes of the EventData is {bytes_payload}.')

    # Use the decode method to decode the payload of the event.
    # The decode method will extract the schema id from the content_type, and automatically retrieve the Avro Schema
    # from the Schema Registry Service. The schema will be cached locally for future usage.
    decoded_content= await avro_encoder.decode(event)
    print(f'The dict content after decoding is {decoded_content}')


async def main():
    try:
        async with eventhub_consumer, avro_encoder:
            await eventhub_consumer.receive(
                on_event=on_event,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
    except KeyboardInterrupt:
        print('Stopped receiving.')
    finally:
        await avro_encoder.close()
        await azure_credential.close()
        await eventhub_consumer.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
