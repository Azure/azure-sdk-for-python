# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import BinaryIO, TypeVar, Union, Optional
from abc import abstractmethod

ObjectType = TypeVar("ObjectType")

class AbstractAvroObjectEncoder(object):
    """
    An Avro encoder used for encoding/decoding an Avro RecordSchema.
    """

    @abstractmethod
    def get_schema_fullname(
        self,
        schema,
    ):
        # type: (str) -> str
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
        data,
        schema,
    ):
        # type: (ObjectType, str) -> bytes
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

    @abstractmethod
    def decode(
        self,
        data: Union[bytes, BinaryIO],
        schema: str,
        *,
        readers_schema: Optional[str]
    ):
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
