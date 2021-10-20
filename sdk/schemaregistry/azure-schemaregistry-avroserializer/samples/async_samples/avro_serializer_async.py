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

from azure.identity.aio import ClientSecretCredential
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer.aio import AvroSerializer

TENANT_ID=os.environ['AZURE_TENANT_ID']
CLIENT_ID=os.environ['AZURE_CLIENT_ID']
CLIENT_SECRET=os.environ['AZURE_CLIENT_SECRET']

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE=os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
GROUP_NAME=os.environ['SCHEMAREGISTRY_GROUP']
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


async def serialize(serializer):
    dict_data_ben = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
    dict_data_alice = {"name": u"Alice", "favorite_number": 15, "favorite_color": u"green"}

    # Schema would be automatically registered into Schema Registry and cached locally.
    payload_ben = await serializer.serialize(dict_data_ben, schema=SCHEMA_STRING)
    # The second call won't trigger a service call.
    payload_alice = await serializer.serialize(dict_data_alice, schema=SCHEMA_STRING)

    print('Encoded bytes are: ', payload_ben)
    print('Encoded bytes are: ', payload_alice)
    return [payload_ben, payload_alice]


async def deserialize(serializer, bytes_payload):
    # serializer.deserialize would extract the schema id from the payload,
    # retrieve schema from Schema Registry and cache the schema locally.
    # If the schema id is the local cache, the call won't trigger a service call.
    dict_data = await serializer.deserialize(bytes_payload)

    print('Deserialized data is: ', dict_data)
    return dict_data


async def main():
    schema_registry = SchemaRegistryClient(fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE, credential=token_credential)
    serializer = AvroSerializer(client=schema_registry, group_name=GROUP_NAME, auto_register_schemas=True)
    bytes_data_ben, bytes_data_alice = await serialize(serializer)
    dict_data_ben = await deserialize(serializer, bytes_data_ben)
    dict_data_alice = await deserialize(serializer, bytes_data_alice)
    await serializer.close()
    await token_credential.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
