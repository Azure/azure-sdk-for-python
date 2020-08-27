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
import asyncio
import os

from azure.identity.aio import ClientSecretCredential
from azure.schemaregistry.serializer.avro_serializer.aio import SchemaRegistryAvroSerializer

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


async def serialize(serializer, schema, dict_data):
    bytes = await serializer.serialize(dict_data, schema)
    print('Encoded bytes are: ', bytes)
    return bytes


async def deserialize(serializer, bytes):
    dict_data = await serializer.deserialize(bytes)
    print('Deserialized data is: ', dict_data)
    return dict_data


async def main():
    token_credential = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )

    serializer = SchemaRegistryAvroSerializer(token_credential, SCHEMA_REGISTRY_ENDPOINT, SCHEMA_GROUP)
    async with serializer:
        dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
        payload_bytes = await serialize(serializer, SCHEMA_STRING, dict_data)
        dict_data = await deserialize(serializer, payload_bytes)

    await token_credential.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())