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

from azure.core.serialization import ObjectSerializer, JsonObjectSerializer


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

    serializer.serialize(stream, Foo(42, "bar"))

    assert stream.getvalue() == b'{"a": 42, "b": "bar"}'

def test_deserialize_basic():

    class Foo:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    serialized = b'{"a": 42, "b": "bar"}'

    serializer = JsonObjectSerializer(
    )

    obj = serializer.deserialize(serialized, None)

