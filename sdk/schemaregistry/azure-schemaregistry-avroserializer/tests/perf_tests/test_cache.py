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
import time
import json
import sys

from azure.identity import ClientSecretCredential
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer

TENANT_ID=os.environ['SCHEMA_REGISTRY_AZURE_TENANT_ID']
CLIENT_ID=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_ID']
CLIENT_SECRET=os.environ['SCHEMA_REGISTRY_AZURE_CLIENT_SECRET']

SCHEMA_REGISTRY_ENDPOINT=os.environ['SCHEMA_REGISTRY_ENDPOINT']
GROUP_NAME=os.environ['SCHEMA_REGISTRY_GROUP']


token_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

cached_call_count = 100
num_long_schema_entries = 10000

SCHEMA_STRING_SHORT = """
{"namespace": "example.short.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"}
 ]
}"""
SCHEMA_DICT_LONG = {"namespace": "example.med.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_color", "type": "string"}
 ]
}
for i in range(num_long_schema_entries):
    SCHEMA_DICT_LONG["fields"].append({"name": f"num{i}", "type": "int"})
SCHEMA_STRING_LONG = json.dumps(SCHEMA_DICT_LONG)


def serialize(serializer, dict_data_a, dict_data_b, schema_str):

    # Schema would be automatically registered into Schema Registry and cached locally.
    st1 = time.time()
    payload_ben = serializer.serialize(dict_data_b, schema_str)
    et1 = time.time()
    # The second call won't trigger a service call.
    st2 = time.time()
    for _ in range(cached_call_count):
        payload_alice = serializer.serialize(dict_data_a, schema_str)
    et2 = time.time()

    print("time to serialize one value with uncached schema: {}".format(et1-st1))
    print("avg time to serialize one value with cached schema: {}".format((et2-st2)/cached_call_count))
    return [payload_ben, payload_alice]


def deserialize(serializer, bytes_payload_a, bytes_payload_b):
    # serializer.deserialize would extract the schema id from the payload,
    # retrieve schema from Schema Registry and cache the schema locally.
    # If the schema id is the local cache, the call won't trigger a service call.
    st1 = time.time()
    dict_data_b = serializer.deserialize(bytes_payload_b)
    et1 = time.time()

    st2 = time.time()
    for _ in range(cached_call_count):
        dict_data_a = serializer.deserialize(bytes_payload_a)
    et2 = time.time()
    print("time to deserialize one value with uncached schema: {}".format(et1-st1))
    print("avg time to deserialize one value with cached schema: {}".format((et2-st2)/cached_call_count))


def serialize_perf(serializer):
    dict_data_alice_short = {"name": u"Alice"}
    dict_data_ben_short = {"name": u"Ben"}
    print("=================SHORT=================")
    serialize(serializer, dict_data_alice_short, dict_data_ben_short, SCHEMA_STRING_SHORT)
    print("=======================================")
    dict_data_alice_long = {"name": u"Alice", "favorite_color": u"green"}
    dict_data_ben_long = {"name": u"Ben", "favorite_color": u"red"}
    for i in range(num_long_schema_entries):
        dict_data_alice_long[f'num{i}']= i
        dict_data_ben_long[f'num{i}'] = i

    print("=================LONG==================")
    serialize(serializer, dict_data_alice_long, dict_data_ben_long, SCHEMA_STRING_LONG)
    print("=======================================")


def deserialize_perf(serializer):
    # SHORT: get encoded payload
    dict_data_alice_short = {"name": u"Alice"}
    dict_data_ben_short = {"name": u"Ben"}
    short_payload_ben = serializer.serialize(dict_data_ben_short, SCHEMA_STRING_SHORT)
    short_payload_alice = serializer.serialize(dict_data_alice_short, SCHEMA_STRING_SHORT)

    # LONG: get encoded payload
    dict_data_alice_long = {"name": u"Alice", "favorite_color": u"green"}
    dict_data_ben_long = {"name": u"Ben", "favorite_color": u"red"}
    for i in range(num_long_schema_entries):
        dict_data_alice_long[f'num{i}'] = i
        dict_data_ben_long[f'num{i}'] = i
    long_payload_ben = serializer.serialize(dict_data_ben_long, SCHEMA_STRING_LONG)
    long_payload_alice = serializer.serialize(dict_data_alice_long, SCHEMA_STRING_LONG)
    print("=================SHORT=================")
    deserialize(serializer, short_payload_alice, short_payload_ben)
    print("=======================================")
    print("=================LONG==================")
    deserialize(serializer, long_payload_alice, long_payload_ben)
    print("=======================================")


if __name__ == '__main__':
    print(f'bytes size of short schema: {sys.getsizeof(SCHEMA_STRING_SHORT)}')
    print(f'bytes size of long schema: {sys.getsizeof(SCHEMA_STRING_LONG)}')
    schema_registry = SchemaRegistryClient(endpoint=SCHEMA_REGISTRY_ENDPOINT, credential=token_credential)
    serializer = SchemaRegistryAvroSerializer(schema_registry, GROUP_NAME, auto_register_schemas=True)
    serialize_perf(serializer)
    deserialize_perf(serializer)
    serializer.close()
