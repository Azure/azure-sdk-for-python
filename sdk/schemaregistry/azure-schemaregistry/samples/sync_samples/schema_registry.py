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
Example to show basic usage of schema registry:
    - register a schema
    - get schema by id
    - get schema id
"""


import os
import json

from azure.identity import ClientSecretCredential
from azure.schemaregistry import SchemaRegistryClient, SerializationType

TENANT_ID = os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
CLIENT_ID = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
CLIENT_SECRET = os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT = os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP = os.environ['SCHEMA_REGISTRY_GROUP']
SCHEMA_NAME = 'your-schema-name'
SERIALIZATION_TYPE = SerializationType.AVRO

SCHEMA_JSON = {
    "namespace": "example.avro",
    "type": "record",
    "name": "User",
    "fields": [
        {
            "name": "name",
            "type": "string"
        },
        {
            "name": "favorite_number",
            "type": ["int", "null"]},
        {
            "name": "favorite_color",
            "type": ["string", "null"]
        }
    ]
}

SCHEMA_STRING = json.dumps(SCHEMA_JSON, separators=(',', ':'))


def register_schema(client, schema_group, schema_name, schema_string, serialization_type):
    print("Registering schema...")
    schema_properties = client.register_schema(schema_group, schema_name, schema_string, serialization_type)
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = client.get_schema(schema_id)
    print("The schema string of schema id: {} string is {}".format(schema_id, schema.content))
    print("Schema properties are {}".format(schema_id))
    return schema.content


def get_schema_id(client, schema_group, schema_name, schema_string, serialization_type):
    print("Getting schema id...")
    schema_properties = client.get_schema_properties(schema_group, schema_name, schema_string, serialization_type)
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


if __name__ == '__main__':
    token_credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    schema_registry_client = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
    with schema_registry_client:
        schema_id = register_schema(schema_registry_client, SCHEMA_GROUP, SCHEMA_NAME, SCHEMA_STRING, SERIALIZATION_TYPE)
        schema_str = get_schema_by_id(schema_registry_client, schema_id=schema_id)
        schema_id = get_schema_id(schema_registry_client, SCHEMA_GROUP, SCHEMA_NAME, SCHEMA_STRING, SERIALIZATION_TYPE)

