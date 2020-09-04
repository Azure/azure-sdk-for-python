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

from azure.identity import ClientSecretCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer

TENANT_ID=os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
CLIENT_ID=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
CLIENT_SECRET=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT=os.environ['SCHEMA_REGISTRY_ENDPOINT']
SCHEMA_GROUP=os.environ['SCHEMA_REGISTRY_GROUP']
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


def serialize(serializer):
    dict_data_ben = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
    dict_data_alice = {"name": u"Alice", "favorite_number": 15, "favorite_color": u"green"}

    # Schema would be automatically registered into Schema Registry and cached locally.
    payload_ben = serializer.serialize(dict_data_ben, SCHEMA_STRING)
    # The second call won't trigger a service call.
    payload_alice = serializer.serialize(dict_data_alice, SCHEMA_STRING)

    print('Encoded bytes are: ', payload_ben)
    print('Encoded bytes are: ', payload_alice)
    return [payload_ben, payload_alice]


def deserialize(serializer, bytes_payload):
    # serializer.deserialize would extract the schema id from the payload,
    # retrieve schema from Schema Registry and cache the schema locally.
    # If the schema id is the local cache, the call won't trigger a service call.
    dict_data = serializer.deserialize(bytes_payload)

    print('Deserialized data is: ', dict_data)
    return dict_data


if __name__ == '__main__':
    schema_registry = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
    serializer = SchemaRegistryAvroSerializer(schema_registry, SCHEMA_GROUP)
    bytes_data_ben, bytes_data_alice = serialize(serializer)
    dict_data_ben = deserialize(serializer, bytes_data_ben)
    dict_data_alice = deserialize(serializer, bytes_data_alice)
    serializer.close()
