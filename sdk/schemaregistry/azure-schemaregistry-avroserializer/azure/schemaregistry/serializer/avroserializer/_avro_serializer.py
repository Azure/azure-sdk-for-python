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
from typing import BinaryIO, Union, TypeVar, Dict
from io import BytesIO
import avro
from avro.io import DatumWriter, DatumReader, BinaryDecoder, BinaryEncoder

ObjectType = TypeVar("ObjectType")


class AvroObjectSerializer(object):

    def __init__(self, codec=None):
        """A Avro serializer using avro lib from Apache.
        :param str codec: The writer codec. If None, let the avro library decides.
        """
        self._writer_codec = codec
        self._schema_writer_cache = {}  # type: Dict[str, DatumWriter]
        self._schema_reader_cache = {}  # type: Dict[str, DatumReader]

    def serialize(
        self,
        data,  # type: ObjectType
        schema,  # type: Union[str, bytes, avro.schema.Schema]
    ):
        # type: (ObjectType, Union[str, bytes, avro.schema.Schema]) -> bytes
        """Convert the provided value to it's binary representation and write it to the stream.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param data: An object to serialize
        :type data: ObjectType
        :param schema: An Avro RecordSchema
        :type schema: Union[str, bytes, avro.schema.Schema]
        :returns: Encoded bytes
        :rtype: bytes
        """
        if not schema:
            raise ValueError("Schema is required in Avro serializer.")

        if not isinstance(schema, avro.schema.Schema):
            schema = avro.schema.parse(schema)

        try:
            writer = self._schema_writer_cache[str(schema)]
        except KeyError:
            writer = DatumWriter(schema)
            self._schema_writer_cache[str(schema)] = writer

        stream = BytesIO()
        with stream:
            writer.write(data, BinaryEncoder(stream))
            encoded_data = stream.getvalue()
        return encoded_data

    def deserialize(
        self,
        data,  # type: Union[bytes, BinaryIO]
        schema,  # type:  Union[str, bytes, avro.schema.Schema]
    ):
        # type: (Union[bytes, BinaryIO], Union[str, bytes, avro.schema.Schema]) -> ObjectType
        """Read the binary representation into a specific type.
        Return type will be ignored, since the schema is deduced from the provided bytes.
        :param data: A stream of bytes or bytes directly
        :type data: BinaryIO or bytes
        :param schema: An Avro RecordSchema
        :type schema: Union[str, bytes, avro.schema.Schema]
        :returns: An instantiated object
        :rtype: ObjectType
        """
        if not hasattr(data, 'read'):
            data = BytesIO(data)

        if not isinstance(schema, avro.schema.Schema):
            schema = avro.schema.parse(schema)

        try:
            reader = self._schema_reader_cache[str(schema)]
        except KeyError:
            reader = DatumReader(writers_schema=schema)
            self._schema_reader_cache[str(schema)] = reader

        with data:
            bin_decoder = BinaryDecoder(data)
            decoded_data = reader.read(bin_decoder)

        return decoded_data
