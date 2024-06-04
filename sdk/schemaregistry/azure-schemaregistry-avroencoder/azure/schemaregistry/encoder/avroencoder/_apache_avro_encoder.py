# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from functools import lru_cache
from typing import BinaryIO, Union, cast, IO, Dict, Any, Mapping, TYPE_CHECKING
from io import BytesIO
import avro  # type: ignore
from avro.io import DatumWriter, DatumReader, BinaryDecoder, BinaryEncoder  # type: ignore
from ._abstract_avro_encoder import (  # pylint: disable=import-error
    AbstractAvroObjectEncoder,
    AvroDataReader
)

if TYPE_CHECKING:
    from avro import schema


class ApacheAvroObjectEncoder(AbstractAvroObjectEncoder):
    def __init__(self, codec=None):
        """A Avro encoder using avro lib from Apache.
        :param str codec: The writer codec. If None, let the avro library decides.
        """
        self._writer_codec = codec

    @lru_cache(maxsize=128)
    def parse_schema(self, schema):
        return avro.schema.parse(schema)

    def get_schema_fullname(self, schema):
        parsed_schema = self.parse_schema(schema)
        return parsed_schema.fullname

    @lru_cache(maxsize=128)
    def get_schema_writer(self, schema):
        schema = self.parse_schema(schema)
        return DatumWriter(schema)

    @lru_cache(maxsize=128)
    def get_schema_reader(
        self, schema, readers_schema=None
    ):
        schema = self.parse_schema(schema)
        if readers_schema:
            readers_schema = self.parse_schema(readers_schema)
        return DatumReader(writers_schema=schema, readers_schema=readers_schema)

    def encode(
        self,
        content: Mapping[str, Any],
        schema: Union[str, bytes, "schema.Schema"],
    ) -> bytes:
        """Convert the provided value to it's binary representation and write it to the stream.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param content: A mapping to encode
        :type content: mapping[str, any]
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
            writer.write(content, BinaryEncoder(stream))
            encoded_content = stream.getvalue()
        return encoded_content

    def decode(
        self,
        content: Union[bytes, BinaryIO],
        reader: AvroDataReader,
    ) -> Dict[str, Any]:
        """Read the binary representation into a specific type.
        Return type will be ignored, since the schema is deduced from the provided bytes.
        :param content: A stream of bytes or bytes directly
        :type content: BinaryIO or bytes
        :param reader: The Apache Avro data reader.
        :type reader: DatumReader
        :returns: The content dict.
        :rtype: dict[str, any]
        """
        if not hasattr(content, "read"):
            content = cast(bytes, content)
            content = BytesIO(content)

        with content:  # type: ignore
            bin_decoder = BinaryDecoder(cast(IO[bytes], content))
            decoded_content = cast(Dict[str, Any], reader.read(bin_decoder))

        return decoded_content
