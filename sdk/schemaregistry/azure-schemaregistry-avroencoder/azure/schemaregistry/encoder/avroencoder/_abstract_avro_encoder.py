# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import BinaryIO, Dict, Union, Any, Mapping
from abc import abstractmethod


class AbstractAvroObjectEncoder(object):
    """
    An Avro encoder used for encoding/decoding an Avro RecordSchema.
    """

    @abstractmethod
    def get_schema_fullname(
        self,
        schema: str,
    ) -> str:
        """
        Returns the namespace-qualified name of the provided schema.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param schema: An Avro RecordSchema
        :type schema: str
        :rtype: str
        """

    @abstractmethod
    def encode(
        self,
        content: Mapping[str, Any],
        schema: str,
    ) -> bytes:
        """Convert the provided value to it's binary representation and write it to the stream.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param content: A mapping to encode
        :type content: mapping[str, Any]
        :param schema: An Avro RecordSchema
        :type schema: str
        :returns: Encoded bytes
        :rtype: bytes
        """

    @abstractmethod
    def decode(self, content: Union[bytes, BinaryIO], reader: Any) -> Dict[str, Any]:
        """Read the binary representation into a specific type.
        Return type will be ignored, since the schema is deduced from the provided bytes.
        :param content: A stream of bytes or bytes directly
        :type content: BinaryIO or bytes
        :keyword reader: The data reader.
        :paramtype reader: Any 
        :returns: The content dict.
        :rtype: dict[str, Any]
        """
