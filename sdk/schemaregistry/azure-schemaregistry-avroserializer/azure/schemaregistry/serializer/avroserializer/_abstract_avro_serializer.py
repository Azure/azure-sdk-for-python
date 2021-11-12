# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import BinaryIO, TypeVar, Union
from abc import abstractmethod

ObjectType = TypeVar("ObjectType")

class AbstractAvroObjectSerializer(object):
    """
    An Avro serializer used for serializing/deserializing an Avro RecordSchema.
    """

    @abstractmethod
    def get_schema_fullname(
        self,
        schema,  # type: str
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
    def serialize(
        self,
        data,  # type: ObjectType
        schema,  # type: str
    ):
        # type: (ObjectType, str) -> bytes
        """Convert the provided value to it's binary representation and write it to the stream.
        Schema must be a Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema
        :param data: An object to serialize
        :type data: ObjectType
        :param schema: An Avro RecordSchema
        :type schema: str
        :returns: Encoded bytes
        :rtype: bytes
        """

    @abstractmethod
    def deserialize(
        self,
        data,  # type: Union[bytes, BinaryIO]
        schema,  # type:  str
    ):
        # type: (Union[bytes, BinaryIO], str) -> ObjectType
        """Read the binary representation into a specific type.
        Return type will be ignored, since the schema is deduced from the provided bytes.
        :param data: A stream of bytes or bytes directly
        :type data: BinaryIO or bytes
        :param schema: An Avro RecordSchema
        :type schema: str
        :returns: An instantiated object
        :rtype: ObjectType
        """
