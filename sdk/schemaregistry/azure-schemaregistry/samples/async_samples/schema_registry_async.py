# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: schema_registry_async.py
DESCRIPTION:
    This sample demonstrates asynchronously authenticating the SchemaRegistryClient and basic usage, including:
        - registering a schema
        - getting a schema by its ID
        - getting schema id.
USAGE:
    python schema_registry_async.py
    Set the environment variables with your own values before running the sample:
    1) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    2) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses the async DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on the async DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
import asyncio
import json

from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry import SchemaFormat

SCHEMAREGISTRY_FQN = os.environ["SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
NAME = "your-schema-name"
FORMAT = SchemaFormat.AVRO
SCHEMA_JSON = {
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "name", "type": "string"},
        {"name": "favorite_number", "type": ["int", "null"]},
        {"name": "favorite_color", "type": ["string", "null"]},
    ],
}
DEFINITION = json.dumps(SCHEMA_JSON, separators=(",", ":"))


async def register_schema(client, group_name, name, definition, format):
    print("Registering schema...")
    schema_properties = await client.register_schema(
        group_name, name, definition, format
    )
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = await client.get_schema(schema_id)
    print(
        "The schema string of schema id: {} string is {}".format(
            schema_id, schema.definition
        )
    )
    print("Schema properties are {}".format(schema_id))
    return schema.definition


async def get_schema_id(client, group_name, name, definition, format):
    print("Getting schema id...")
    schema_properties = await client.get_schema_properties(
        group_name, name, definition, format
    )
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def main():
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
    )
    async with token_credential, schema_registry_client:
        schema_id = await register_schema(
            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
        )
        schema_str = await get_schema_by_id(schema_registry_client, schema_id)
        schema_id = await get_schema_id(
            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
        )


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
