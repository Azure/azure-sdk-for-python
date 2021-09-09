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
from azure.schemaregistry import SerializationType

TENANT_ID = os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
CLIENT_ID = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
CLIENT_SECRET = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT = os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP = os.environ['SCHEMA_REGISTRY_GROUP']
SCHEMA_NAME = 'your-schema-name'
SERIALIZATION_TYPE = SerializationType.AVRO
SCHEMA_STRING = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""


async def register_schema(client, schema_group, schema_name, schema_string, serialization_type):
    print("Registering schema...")
    schema_properties = await client.register_schema(schema_group, schema_name, schema_string, serialization_type)
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = await client.get_schema(schema_id)
    print("The schema string of schema id: {} string is {}".format(schema_id, schema.content))
    print("Schema properties are {}".format(schema_id))
    return schema.content


async def get_schema_id(client, schema_group, schema_name, schema_string, serialization_type):
    print("Getting schema id...")
    schema_properties = await client.get_schema_properties(schema_group, schema_name, schema_string, serialization_type)
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


async def main():
    token_credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    schema_registry_client = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
    async with token_credential, schema_registry_client:
        schema_id = await register_schema(schema_registry_client, SCHEMA_GROUP, SCHEMA_NAME, SCHEMA_STRING, SERIALIZATION_TYPE)
        schema_str = await get_schema_by_id(schema_registry_client, schema_id)
        schema_id = await get_schema_id(schema_registry_client, SCHEMA_GROUP, SCHEMA_NAME, SCHEMA_STRING, SERIALIZATION_TYPE)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
