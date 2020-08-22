# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.identity import ClientSecretCredential
from azure.schemaregistry.serializer.avro_serializer import SchemaRegistryAvroSerializer

TENANT_ID=os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
CLIENT_ID=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
CLIENT_SECRET=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT=os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP=os.environ['SCHEMA_REGISTRY_GROUP']
SCHEMA_STRING="""
{"namespace":"example.avro","type":"record","name":
"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}
"""

token_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)


def serialize(serializer, schema):
    dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    bytes = serializer.serialize(dict_data, schema)
    return bytes


def deserialize(serializer, dict_data):
    return serializer.deserialize(dict_data)

serializer = SchemaRegistryAvroSerializer(token_credential, SCHEMA_REGISTRY_ENDPOINT, SCHEMA_GROUP)
payload_bytes = serialize(serializer, SCHEMA_STRING)
print(payload_bytes)
dict_data = deserialize(serializer, payload_bytes)
print(dict_data)

