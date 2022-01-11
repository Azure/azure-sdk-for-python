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
"""
FILE: sample_code_schemaregistry.py
DESCRIPTION:
    This sample demonstrates authenticating the SchemaRegistryClient and registering a schema,
     retrieving a schema by its ID, and retrieving schema properties.
USAGE:
    python sample_code_schemaregistry.py
    Set the environment variables with your own values before running the sample:
    1) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    2) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
import json

from azure.schemaregistry import SchemaRegistryClient
from azure.identity import DefaultAzureCredential


def create_client():
    # [START create_sr_client_sync]
    SCHEMAREGISTRY_FQN = os.environ["SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"]
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
    )
    # [END create_sr_client_sync]
    return schema_registry_client


def register_schema(schema_registry_client):
    # [START register_schema_sync]
    GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
    NAME = "your-schema-name"
    FORMAT = "Avro"
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
    DEFINTION = json.dumps(SCHEMA_JSON, separators=(",", ":"))
    schema_properties = schema_registry_client.register_schema(
        GROUP_NAME, NAME, DEFINTION, FORMAT
    )
    schema_id = schema_properties.id
    # [END register_schema_sync]
    return schema_id


def get_schema(schema_registry_client, schema_id):
    # [START get_schema_sync]
    schema = schema_registry_client.get_schema(schema_id)
    definition = schema.definition
    properties = schema.properties
    # [END get_schema_sync]
    print(definition)
    print(properties)
    return schema


def get_schema_id(schema_registry_client):
    # [START get_schema_id_sync]
    group_name = os.environ["SCHEMAREGISTRY_GROUP"]
    name = "your-schema-name"
    format = "Avro"
    schema_json = {
        "namespace": "example.avro",
        "type": "record",
        "name": "User",
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "favorite_number", "type": ["int", "null"]},
            {"name": "favorite_color", "type": ["string", "null"]},
        ],
    }
    definition = json.dumps(schema_json, separators=(",", ":"))
    schema_properties = schema_registry_client.get_schema_properties(
        group_name, name, definition, format
    )
    schema_id = schema_properties.id
    # [END get_schema_id_sync]
    return schema_id


if __name__ == "__main__":
    client = create_client()
    with client:
        schema_id = register_schema(client)
        schema = get_schema(client, schema_id)
        schema_id = get_schema_id(client)
