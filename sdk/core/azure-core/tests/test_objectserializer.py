# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
from io import BytesIO

import avro.schema

from azure.core.serialization import (
    ObjectSerializer,
    JsonObjectSerializer,
    AvroObjectSerializer,
)


def test_serialize_basic():

    class Foo:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    serializer = JsonObjectSerializer(
        serializer_kwargs={
            'default': lambda o: o.__dict__
        }
    )

    stream = BytesIO()

    serializer.serialize(stream, Foo(42, "bar"), None)

    assert stream.getvalue() == b'{"a": 42, "b": "bar"}'

def test_deserialize_basic():

    class Foo:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    serialized = b'{"a": 42, "b": "bar"}'

    serializer = JsonObjectSerializer(
        deserializer_kwargs={
            'object_hook': lambda d: Foo(d["a"], d["b"])
        }
    )

    obj = serializer.deserialize(serialized, None)
    assert obj.a == 42
    assert obj.b == "bar"


def test_serialize_basic_avro():

    avro_schema_bytes = b"""
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""

    schema = avro.schema.parse(avro_schema_bytes)

    serializer = AvroObjectSerializer()

    stream = BytesIO()

    serializer.serialize(
        stream,
        {"name": "Ben", "favorite_number": 7, "favorite_color": "red"},
        schema
    )

    print(stream.getvalue())
    assert stream.getvalue().startswith(b'Obj\x01\x04\x14')


def test_deserialize_basic_avro():

    serialized_avro = b'Obj\x01\x04\x14avro.codec\x08null\x16avro.schema\xba\x03{"type": "record", "name": "User", "namespace": "example.avro", "fields": [{"type": "string", "name": "name"}, {"type": ["int", "null"], "name": "favorite_number"}, {"type": ["string", "null"], "name": "favorite_color"}]}\x00\xda\xb1\xaa~\xd6\xd0\nME$\xbb\xe4L\xf6\xaf\xdc\x02\x16\x06Ben\x00\x0e\x00\x06red\xda\xb1\xaa~\xd6\xd0\nME$\xbb\xe4L\xf6\xaf\xdc'

    avro_schema_bytes = b"""
{"namespace": "example.avro",
 "type": "record",
 "name": "User",
 "fields": [
     {"name": "name", "type": "string"},
     {"name": "favorite_number",  "type": ["int", "null"]},
     {"name": "favorite_color", "type": ["string", "null"]}
 ]
}"""
    schema = avro.schema.parse(avro_schema_bytes)

    deserializer = AvroObjectSerializer()

    obj = deserializer.deserialize(serialized_avro, schema)

    assert obj['name'] == "Ben"
    assert obj['favorite_number'] == 7
    assert obj['favorite_color'] == "red"
