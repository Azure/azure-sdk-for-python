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
from azure.schemaregistry.encoder.avroencoder import MessageContent
from azure.schemaregistry.encoder.avroencoder.aio import AvroEncoder
from azure.eventhub import EventData

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ[
    "SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"
]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
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
    tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)


async def encode_message_content_dict(encoder):
    dict_content_ben = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    encoded_message_content_ben = await encoder.encode(dict_content_ben, schema=SCHEMA_STRING)

    print("Encoded message_content is: ", encoded_message_content_ben)
    return EventData.from_message_content(
        encoded_message_content_ben["content"],
        encoded_message_content_ben["content_type"],
    )

async def decode_with_content_and_content_type(encoder, event_data):
    # get content as bytes
    content = bytearray()
    for d in event_data.body:
        content += d
    content_bytes = bytes(content)
    message_content = MessageContent({"content": content_bytes, "content_type": event_data.content_type})
    decoded_content = await encoder.decode(message_content)

    print("Decoded content is: ", decoded_content)
    return decoded_content


async def main():
    schema_registry = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=token_credential,
    )
    encoder = AvroEncoder(
        client=schema_registry, group_name=GROUP_NAME, auto_register=True
    )
    event_data = await encode_message_content_dict(encoder)
    decoded_content = await decode_with_content_and_content_type(encoder, event_data)
    await encoder.close()
    await token_credential.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
