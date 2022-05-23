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
FILE: encode_and_decode_with_message_content_async.py
DESCRIPTION:
    This sample demonstrates the following:
     - Authenticating an async SchemaRegistryClient to be used by the AvroEncoder.
     - Passing in content and schema to the AvroEncoder, which will return a dict containing
      encoded content and corresponding content type.
     - Passing in a dict containing Avro-encoded content and corresponding content type to
      the AvroEncoder, which will return the decoded content.
USAGE:
    python encode_and_decode_with_message_content_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TENANT_ID - The ID of the service principal's tenant. Also called its 'directory' ID.
    2) AZURE_CLIENT_ID - The service principal's client ID. Also called its 'application' ID.
    3) AZURE_CLIENT_SECRET - One of the service principal's client secrets.
    4) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    5) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses ClientSecretCredential, which requests a token from Azure Active Directory.
For more information on ClientSecretCredential, see:
    https://docs.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
"""
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
