# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import asyncio

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry import SchemaFormat
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential


def create_client():
    # [START create_sr_client_async]
    SCHEMA_REGISTRY_FQN = os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=SCHEMA_REGISTRY_FQN, credential=token_credential)
    # [END create_sr_client_async]
    TENANT_ID = os.environ['AZURE_TENANT_ID']
    CLIENT_ID = os.environ['AZURE_CLIENT_ID']
    CLIENT_SECRET = os.environ['AZURE_CLIENT_SECRET']
    token_credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    schema_registry_client = SchemaRegistryClient(fully_qualified_namespace=SCHEMA_REGISTRY_FQN, credential=token_credential)
    return schema_registry_client, token_credential


async def register_schema(schema_registry_client):
    # [START register_schema_async]
    GROUP_NAME = os.environ['SCHEMAREGISTRY_GROUP']
    NAME = 'your-schema-name'
    FORMAT = SchemaFormat.AVRO
    SCHEMA_DEFINITION = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
    schema_properties = await schema_registry_client.register_schema(GROUP_NAME, NAME, SCHEMA_DEFINITION, FORMAT)
    schema_id = schema_properties.id
    # [END register_schema_async]
    return schema_id


async def get_schema(schema_registry_client, id):
    # [START get_schema_async]
    schema = await schema_registry_client.get_schema(id)
    schema_definition = schema.schema_definition
    # [END get_schema_async]
    return schema_definition


async def get_schema_id(schema_registry_client):
    group_name = os.environ['SCHEMAREGISTRY_GROUP']
    name = 'your-schema-name'
    format = SchemaFormat.AVRO
    schema_definition = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""

    # [START get_schema_id_async]
    schema_properties = await schema_registry_client.get_schema_properties(group_name, name, schema_definition, format)
    schema_id = schema_properties.id
    # [END get_schema_id_async]
    return schema_id


async def main():
    client, credential = create_client()
    async with client, credential:
        id = await register_schema(client)
        schema = await get_schema(client, id)
        id = await get_schema_id(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
