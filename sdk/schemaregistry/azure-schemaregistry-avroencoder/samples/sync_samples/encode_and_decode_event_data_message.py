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
from azure.schemaregistry.encoder.avroencoder import AvroEncoder
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


def encode_to_event_data_message(encoder):
    dict_content_ben = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    dict_content_alice = {"name": "Alice", "favorite_number": 15, "favorite_color": "green"}

    # Schema would be automatically registered into Schema Registry and cached locally.
    event_data_ben = encoder.encode(
        dict_content_ben, schema=SCHEMA_STRING, message_type=EventData
    )

    # The second call won't trigger a service call.
    event_data_alice = encoder.encode(
        dict_content_alice, schema=SCHEMA_STRING, message_type=EventData
    )

    print("Encoded content is: ", next(event_data_ben.body))
    print("Encoded content is: ", next(event_data_alice.body))

    print("Encoded content type is: ", event_data_ben.content_type)
    print("Encoded content type is: ", event_data_alice.content_type)
    return [event_data_ben, event_data_alice]


def decode_event_data_message(encoder, event_data):
    # encoder.decode would extract the schema id from the content_type,
    # retrieve schema from Schema Registry and cache the schema locally.
    # If the schema id is in the local cache, the call won't trigger a service call.
    decoded_content = encoder.decode(event_data)

    print("Decoded data is: ", decoded_content)
    return decoded_content


if __name__ == "__main__":
    schema_registry = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE,
        credential=token_credential,
    )
    encoder = AvroEncoder(
        client=schema_registry, group_name=GROUP_NAME, auto_register=True
    )
    event_data_ben, event_data_alice = encode_to_event_data_message(encoder)
    decoded_content_ben = decode_event_data_message(encoder, event_data_ben)
    decoded_content_alice = decode_event_data_message(encoder, event_data_alice)
    encoder.close()
