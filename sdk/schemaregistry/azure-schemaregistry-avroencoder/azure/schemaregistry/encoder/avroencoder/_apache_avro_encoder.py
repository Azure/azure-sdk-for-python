# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from functools import lru_cache
from typing import BinaryIO, Union, TypeVar
from io import BytesIO
import avro
from avro.io import DatumWriter, DatumReader, BinaryDecoder, BinaryEncoder

from ._abstract_avro_encoder import AbstractAvroObjectEncoder

ObjectType = TypeVar("ObjectType")


class ApacheAvroObjectEncoder(AbstractAvroObjectEncoder):

    def __init__(self, codec=None):
        """A Avro encoder using avro lib from Apache.
        :param str codec: The writer codec. If None, let the avro library decides.
        """
        self._writer_codec = codec

    @lru_cache(maxsize=128)
    def parse_schema(self, schema):   # pylint: disable=no-self-use
        return avro.schema.parse(schema)

    def get_schema_fullname(self, schema):
        parsed_schema = self.parse_schema(schema)
        return parsed_schema.fullname

    @lru_cache(maxsize=128)
    def get_schema_writer(self, schema):   # pylint: disable=no-self-use
        schema = self.parse_schema(schema)
        return DatumWriter(schema)

    @lru_cache(maxsize=128)
    def get_schema_reader(self, schema, readers_schema):   # pylint: disable=no-self-use
        schema = self.parse_schema(schema)
        if readers_schema:
            readers_schema = self.parse_schema(readers_schema)
        return DatumReader(writers_schema=schema, readers_schema=readers_schema)

    # pylint: disable=no-self-use
    def encode(
        self,
        data,  # type: ObjectType
        schema,  # type: Union[str, bytes, avro.schema.Schema]
    ) -> bytes:
        """Convert the provided value to it's binary representation and write it to the stream.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param data: An object to encode
        :type data: ObjectType
        :param schema: An Avro RecordSchema
        :type schema: str
        :returns: Encoded bytes
        :rtype: bytes
        """
        if not schema:
            raise ValueError("Schema is required in Avro encoder.")

        writer = self.get_schema_writer(schema)

        stream = BytesIO()
        with stream:
            writer.write(data, BinaryEncoder(stream))
            encoded_data = stream.getvalue()
        return encoded_data

    # pylint: disable=no-self-use
    def decode(
        self,
        data,  # type: Union[bytes, BinaryIO]
        schema,  # type:  Union[str, bytes, avro.schema.Schema]
        *,
        readers_schema=None,  # type:  Optional[Union[str, bytes, avro.schema.Schema]]
    ) -> ObjectType:
        """Read the binary representation into a specific type.
        Return type will be ignored, since the schema is deduced from the provided bytes.
        :param data: A stream of bytes or bytes directly
        :type data: BinaryIO or bytes
        :param schema: An Avro RecordSchema
        :type schema: str
        :keyword readers_schema: An optional reader's schema as defined by the Apache Avro specification.
        :paramtype readers_schema: str or None
        :returns: An instantiated object
        :rtype: ObjectType
        """
        if not hasattr(data, 'read'):
            data = BytesIO(data)

        reader = self.get_schema_reader(schema, readers_schema)

        with data:
            bin_decoder = BinaryDecoder(data)
            decoded_data = reader.read(bin_decoder)

        return decoded_data
