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
        - getting a schema by its version.
        - getting schema id.
USAGE:
    python schema_registry_async.py
    Set the environment variables with your own values before running the sample:
    1) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    2) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses the async DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on the async DefaultAzureCredential, see
 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
import asyncio
import json

from azure.identity.aio import DefaultAzureCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry import SchemaFormat

SCHEMAREGISTRY_FQN = os.environ["SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
NAME = "your-schema-name"
FORMAT = SchemaFormat.JSON

JSON_SCHEMA = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "firstName": {"type": "string", "description": "The person's first name."},
        "lastName": {"type": "string", "description": "The person's last name."},
        "age": {
            "description": "Age in years which must be equal to or greater than zero.",
            "type": "integer",
            "minimum": 0,
        },
    },
}
NEW_JSON_SCHEMA = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person2",
    "type": "object",
    "properties": {
        "firstName": {"type": "string", "description": "The person's first name."},
        "lastName": {"type": "string", "description": "The person's last name."},
        "age": {
            "description": "Age in years which must be equal to or greater than zero.",
            "type": "integer",
            "minimum": 0,
        },
    },
}

DEFINITION = json.dumps(JSON_SCHEMA, separators=(",", ":"))
NEW_DEFINITION = json.dumps(NEW_JSON_SCHEMA, separators=(",", ":"))


async def register_schema(client, group_name, name, definition, format):
    print("Registering schema...")
    schema_properties = await client.register_schema(group_name, name, definition, format)
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties


async def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = await client.get_schema(schema_id)
    print("The schema string of schema id: {} is {}".format(schema_id, schema.definition))
    print("Schema properties are {}".format(schema.properties))
    return schema.definition


async def get_schema_by_version(client, group_name, name, version):
    print("Getting schema by version...")
    schema = await client.get_schema(group_name=group_name, name=name, version=version)
    print("The schema string of schema id: {} is {}".format(schema.properties.id, schema.definition))
    print("Schema properties are {}".format(schema.properties))
    return schema.definition


async def get_old_schema_by_version(client, group_name, name, new_definition):
    updated_schema_properties = await client.register_schema(group_name, name, new_definition, FORMAT)
    print(f"Registered new schema of version: {updated_schema_properties.version}")
    old_version = updated_schema_properties.version - 1
    schema = await client.get_schema(group_name=group_name, name=name, version=old_version)
    print(f"Retrieving old schema v{schema.properties.version}: {schema.definition}")
    return schema.definition


async def get_schema_id(client, group_name, name, definition, format):
    print("Getting schema id...")
    schema_properties = await client.get_schema_properties(group_name, name, definition, format)
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def main():
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
    )
    async with token_credential, schema_registry_client:
        schema_properties = await register_schema(schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT)
        schema_str = await get_schema_by_id(schema_registry_client, schema_properties.id)
        schema_str = await get_schema_by_version(schema_registry_client, GROUP_NAME, NAME, schema_properties.version)
        schema_str = await get_old_schema_by_version(schema_registry_client, GROUP_NAME, NAME, NEW_DEFINITION)
        schema_id = await get_schema_id(schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT)


asyncio.run(main())
