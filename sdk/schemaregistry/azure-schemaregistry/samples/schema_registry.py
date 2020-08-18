# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.identity import ClientSecretCredential
from azure.schemaregistry import SchemaRegistryClient, SerializationType

TENANT_ID = os.environ['AZURE_TENANT_ID']
CLIENT_ID = os.environ['AZURE_CLIENT_ID']
CLIENT_SECRET = os.environ['AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT = os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP = os.environ['SCHEMA_GROUP']
SCHEMA_NAME = os.environ['SCHEMA_NAME']
SERIALIZATION_TYPE = SerializationType.AVRO
SCHEMA_STRING = """
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""


token_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


def register_schema(client, schema_group, schema_name, serialization_type, schema_string):
    res = client.register_schema(schema_group, schema_name, "AVRO", schema_string)
    print(res)
    pass


def get_schema_by_id():
    pass


def get_schema():
    pass


schema_registry_client = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
register_schema(schema_registry_client, SCHEMA_GROUP, SCHEMA_NAME, SERIALIZATION_TYPE, SCHEMA_STRING)