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
from azure.schemaregistry import SchemaRegistryClient, SerializationType
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
import json
import avro.schema

TENANT_ID=os.environ['AZURE_TENANT_ID']
CLIENT_ID=os.environ['AZURE_CLIENT_ID']
CLIENT_SECRET=os.environ['AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT=os.environ['SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE']
SCHEMA_GROUP=os.environ['SCHEMAREGISTRY_GROUP']
SCHEMA_NAME = 'your-schema-name'
SERIALIZATION_TYPE = SerializationType.AVRO

SCHEMA_STR3 = '''
{"type":"int","name":"ExampleSchema3","namespace":"example.avro"}
'''
SCHEMA_RESERVED_PROPS = (
    "type",
    "name",
    "namespace",
    "fields",  # Record
    "items",  # Array
    "size",  # Fixed
    "symbols",  # Enum
    "values",  # Map
    "doc",
)
def get_other_props(all_props, reserved_props):
    return {k: v for k, v in all_props.items() if k not in reserved_props}

#print(dir(parsed))
#print(parsed.fullname)
#print(parsed.to_json())
json_data = json.loads(SCHEMA_STR3)
other_props = get_other_props(json_data, SCHEMA_RESERVED_PROPS)
print(other_props)

parsed2 = avro.schema.parse(SCHEMA_STR3)
print("\n______________STRING SCHEMA________________")
print(dir(parsed2))
print(str(parsed2.fullname))
print(parsed2.check_props)
print(parsed2.props)
print(parsed2.to_json())
token_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

#def serialize(serializer):
#    dict_data_ben = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
#    dict_data_alice = {"name": u"Alice", "favorite_number": 15, "favorite_color": u"green"}
#
#    # Schema would be automatically registered into Schema Registry and cached locally.
#    payload_ben = serializer.serialize(dict_data_ben, SCHEMA_STRING)
#    # The second call won't trigger a service call.
#    payload_alice = serializer.serialize(dict_data_alice, SCHEMA_STRING)
#
#    print('Encoded bytes are: ', payload_ben)
#    print('Encoded bytes are: ', payload_alice)
#    return [payload_ben, payload_alice]
#
def serialize_primitive(serializer):
    string_data_hello = 3
    payload_hello = serializer.serialize(string_data_hello, SCHEMA_STR3)
    print(payload_hello)
#
#def deserialize(serializer, bytes_payload):
#    # serializer.deserialize would extract the schema id from the payload,
#    # retrieve schema from Schema Registry and cache the schema locally.
#    # If the schema id is the local cache, the call won't trigger a service call.
#    dict_data = serializer.deserialize(bytes_payload)
#
#    print('Deserialized data is: ', dict_data)
#    return dict_data
#
#
if __name__ == '__main__':
    schema_registry = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
    #try:
    #    schema_properties = schema_registry.register_schema(SCHEMA_GROUP, SCHEMA_NAME, SERIALIZATION_TYPE, SCHEMA_STR3)
    #    schema = schema_registry.get_schema(schema_properties.schema_id)
    #    print(schema.schema_properties.schema_id)
    #    print(schema.schema_content)
    #except Exception as e:
    #    print(dir(e))
    #    print(e.message)
    #    print(e.inner_exception)
    #    print(e.reason)
    #    print(e.exc_value)
    serializer = SchemaRegistryAvroSerializer(client=schema_registry, group_name=SCHEMA_GROUP)
    #bytes_data_ben, bytes_data_alice = serialize(serializer)
    #dict_data_ben = deserialize(serializer, bytes_data_ben)
    #dict_data_alice = deserialize(serializer, bytes_data_alice)
    #serialize_primitive(serializer)
    #serializer.close()
