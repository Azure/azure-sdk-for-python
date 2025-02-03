#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
FILE: eventhub_send_integration_async.py
DESCRIPTION:
    Examples to show sending events asynchronously to EventHub with JsonSchemaEncoder integrated for content encoding.
USAGE:
    python eventhub_send_integration_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TENANT_ID - Required for use of the credential. The ID of the service principal's tenant.
     Also called its 'directory' ID.
    2) AZURE_CLIENT_ID - Required for use of the credential. The service principal's client ID.
     Also called its 'application' ID.
    3) AZURE_CLIENT_SECRET - Required for use of the credential. One of the service principal's client secrets.
    4) SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    5) SCHEMAREGISTRY_GROUP - The name of the JSON schema group.
    6) EVENT_HUB_CONN_STR - The connection string of the Event Hubs namespace to send events to.
    7) EVENT_HUB_NAME - The name of the Event Hub in the Event Hubs namespace to send events to.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
    https://learn.microsoft.com/python/api/azure-identity/azure.identity.aio.defaultazurecredential?view=azure-python
"""
import os
import asyncio
import json
from typing import cast, Iterator

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder.aio import JsonSchemaEncoder

EVENTHUB_CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ["SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]

SCHEMA_JSON = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Person's name."},
        "favorite_color": {"type": "string", "description": "Favorite color."},
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        },
    },
}
SCHEMA_STRING = json.dumps(SCHEMA_JSON)


async def pre_register_schema(schema_registry: SchemaRegistryClient):
    schema_properties = await schema_registry.register_schema(
        group_name=GROUP_NAME, name=cast(str, SCHEMA_JSON["title"]), definition=SCHEMA_STRING, format="Json"
    )
    return schema_properties.id


async def send_event_data_batch(producer: EventHubProducerClient, encoder: JsonSchemaEncoder, schema_id: str):
    event_data_batch = await producer.create_batch()
    dict_content = {"name": "Bob", "favorite_number": 7, "favorite_color": "red"}
    # Use the encode method to convert dict object to bytes with the given json schema and set body of EventData.
    # The encode method will automatically register the schema into the Schema Registry Service and
    # schema will be cached locally for future usage.
    event_data = await encoder.encode(content=dict_content, schema_id=schema_id, message_type=EventData)
    print(f"The bytes of encoded dict content is {next(cast(Iterator[bytes], event_data.body))!r}.")

    event_data_batch.add(event_data)
    await producer.send_batch(event_data_batch)
    print("Send is done.")


async def main():

    # create an EventHubProducerClient instance
    eventhub_producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENTHUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME
    )
    azure_credential = DefaultAzureCredential()

    # pre-register the schema
    sr_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE, credential=azure_credential
    )
    schema_id = await pre_register_schema(sr_client)

    # create a JsonSchemaEncoder instance
    json_schema_encoder = JsonSchemaEncoder(client=sr_client, validate=cast(str, SCHEMA_JSON["$schema"]))
    await send_event_data_batch(eventhub_producer, json_schema_encoder, schema_id)
    await json_schema_encoder.close()
    await azure_credential.close()
    await eventhub_producer.close()


if __name__ == "__main__":
    asyncio.run(main())
