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
from azure.schemaregistry import SerializationType
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential


def create_client():
    # [START create_sr_client_async]
    schema_registry_endpoint = os.environ['SCHEMA_REGISTRY_ENDPOINT']
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(endpoint=schema_registry_endpoint, credential=token_credential)
    # [END create_sr_client_async]
    tenant_id = os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
    client_id = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
    client_secret = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']
    token_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    schema_registry_client = SchemaRegistryClient(endpoint=schema_registry_endpoint, credential=token_credential)
    return schema_registry_client, token_credential


async def register_scehma(schema_registry_client):
    # [START register_schema_async]
    schema_group = os.environ['SCHEMA_REGISTRY_GROUP']
    schema_name = 'your-schema-name'
    serialization_type = SerializationType.AVRO
    schema_content = """
    {"namespace": "example.avro",
     "type": "record",
     "name": "User",
     "fields": [
         {"name": "name", "type": "string"},
         {"name": "favorite_number",  "type": ["int", "null"]},
         {"name": "favorite_color", "type": ["string", "null"]}
     ]
    }"""
    schema_properties = await schema_registry_client.register_schema(schema_group, schema_name, serialization_type, schema_content)
    schem_id = schema_properties.schema_id
    # [END register_schema_async]
    return schem_id


async def get_schema(schema_registry_client, schema_id):
    # [START get_schema_async]
    schema = await schema_registry_client.get_schema(schema_id)
    schema_content = schema.schema_content
    # [END get_schema_async]


async def get_schema_id(schema_registry_client):
    schema_group = os.environ['SCHEMA_REGISTRY_GROUP']
    schema_name = 'your-schema-name'
    serialization_type = SerializationType.AVRO
    schema_content = """
    {"namespace": "example.avro",
     "type": "record",
     "name": "User",
     "fields": [
         {"name": "name", "type": "string"},
         {"name": "favorite_number",  "type": ["int", "null"]},
         {"name": "favorite_color", "type": ["string", "null"]}
     ]
    }"""

    # [START get_schema_id_async]
    schema_properties = await schema_registry_client.get_schema_id(schema_group, schema_name, serialization_type, schema_content)
    schem_id = schema_properties.schema_id
    # [END get_schema_id_async]


async def main():
    client, credential = create_client()
    async with client, credential:
        id = await register_scehma(client)
        schema = await get_schema(client, id)
        id = await get_schema_id(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

