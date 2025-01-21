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
FILE: encode_and_decode_event_data_message.py
DESCRIPTION:
    This sample demonstrates the following:
     - Authenticating a sync SchemaRegistryClient to be used by the JsonSchemaEncoder.
     - Registering a schema with the SchemaRegistryClient.
     - Passing in content, schema ID, and EventData class to the JsonSchemaEncoder, which will return an
      EventData object containing validated and encoded content and corresponding content type.
     - Passing in an `EventData` object with `body` set to encoded content and `content_type`
      set to JSON Schema Format MIME type and schema ID to the JsonSchemaEncoder for decoding content.
USAGE:
    python encode_and_decode_event_data_message.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_TENANT_ID - The ID of the service principal's tenant. Also called its 'directory' ID.
    2) AZURE_CLIENT_ID - The service principal's client ID. Also called its 'application' ID.
    3) AZURE_CLIENT_SECRET - One of the service principal's client secrets.
    4) SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    5) SCHEMAREGISTRY_GROUP - The name of the JSON schema group.

This example uses ClientSecretCredential, which requests a token from Azure Active Directory.
For more information on ClientSecretCredential, see:
    https://learn.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
"""
import os
import json
from typing import cast, Iterator

from azure.identity import ClientSecretCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder
from azure.eventhub import EventData

TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE = os.environ["SCHEMAREGISTRY_JSON_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
SCHEMA_JSON = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Person's name."},
        "favorite_color": {"type": "string", "description": "Favorite color."},
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        },
    },
}
SCHEMA_STRING = json.dumps(SCHEMA_JSON)

token_credential = ClientSecretCredential(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def pre_register_schema(schema_registry: SchemaRegistryClient):
    schema_properties = schema_registry.register_schema(
        group_name=GROUP_NAME, name=cast(str, SCHEMA_JSON["title"]), definition=SCHEMA_STRING, format="Json"
    )
    return schema_properties.id


def encode_to_event_data_message(encoder: JsonSchemaEncoder, schema_id: str):
    dict_content_ben = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
    dict_content_alice = {"name": "Alice", "favorite_number": 15, "favorite_color": "green"}

    # Schema would be automatically registered into Schema Registry and cached locally.
    event_data_ben = encoder.encode(dict_content_ben, schema_id=schema_id, message_type=EventData)

    # The second call won't trigger a service call.
    event_data_alice = encoder.encode(dict_content_alice, schema_id=schema_id, message_type=EventData)

    print("Encoded content is: ", next(cast(Iterator[bytes], event_data_ben.body)))
    print("Encoded content is: ", next(cast(Iterator[bytes], event_data_alice.body)))

    print("Encoded content type is: ", event_data_ben.content_type)
    print("Encoded content type is: ", event_data_alice.content_type)
    return [event_data_ben, event_data_alice]


def decode_event_data_message(encoder: JsonSchemaEncoder, event_data: EventData):
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
    schema_id = pre_register_schema(schema_registry)
    encoder = JsonSchemaEncoder(client=schema_registry, validate=cast(str, SCHEMA_JSON["$schema"]))
    event_data_ben, event_data_alice = encode_to_event_data_message(encoder, schema_id)
    decoded_content_ben = decode_event_data_message(encoder, event_data_ben)
    decoded_content_alice = decode_event_data_message(encoder, event_data_alice)
    encoder.close()
