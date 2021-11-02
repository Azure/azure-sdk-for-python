# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Example to show basic usage of schema registry asynchronously:
    - register a schema
    - get schema by id
    - get schema id
"""

import asyncio
import os

from azure.identity.aio import ClientSecretCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry import SchemaFormat

TENANT_ID = os.environ['AZURE_TENANT_ID']
CLIENT_ID = os.environ['AZURE_CLIENT_ID']
CLIENT_SECRET = os.environ['AZURE_CLIENT_SECRET']

SCHEMAREGISTRY_FQN = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']
NAME = 'your-schema-name'
FORMAT = SchemaFormat.AVRO
SCHEMA_STRING = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""


async def register_schema(client, group_name, name, schema_string, format):
    print("Registering schema...")
    schema_properties = await client.register_schema(group_name, name, schema_string, format)
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def get_schema_by_id(client, id):
    print("Getting schema by id...")
    schema = await client.get_schema(id, logging_enable=True)
    print("The schema string of schema id: {} string is {}".format(id, schema.schema_definition))
    print("Schema properties are {}".format(id))
    return schema.schema_definition


async def get_schema_id(client, group_name, name, schema_string, format):
    print("Getting schema id...")
    schema_properties = await client.get_schema_properties(group_name, name, schema_string, format)
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def main():
    token_credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential, logging_enable=True)
    async with token_credential, schema_registry_client:
        schema_id = await register_schema(schema_registry_client, GROUP_NAME, NAME, SCHEMA_STRING, FORMAT)
        schema_str = await get_schema_by_id(schema_registry_client, schema_id)
        schema_id = await get_schema_id(schema_registry_client, GROUP_NAME, NAME, SCHEMA_STRING, FORMAT)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
