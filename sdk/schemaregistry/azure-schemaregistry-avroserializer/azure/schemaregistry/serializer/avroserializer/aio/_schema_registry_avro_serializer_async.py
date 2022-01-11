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
from io import BytesIO
from typing import Any, Dict, Mapping
from ._async_lru import alru_cache
from .._constants import SCHEMA_ID_START_INDEX, SCHEMA_ID_LENGTH, DATA_START_INDEX
from .._apache_avro_serializer import ApacheAvroObjectSerializer as AvroObjectSerializer
from ..exceptions import (
    SchemaParseError,
    SchemaSerializationError,
    SchemaDeserializationError,
)


class AvroSerializer(object):
    """
    AvroSerializer provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :keyword client: Required. The schema registry client
     which is used to register schema and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.aio.SchemaRegistryClient
    :keyword str group_name: Required. Schema group under which schema should be registered.
    :keyword bool auto_register_schemas: When true, register new schemas passed to serialize.
     Otherwise, and by default, serialization will fail if the schema has not been pre-registered in the registry.

    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        try:
            self._schema_group = kwargs.pop("group_name")
            self._schema_registry_client = kwargs.pop("client") # type: "SchemaRegistryClient"
        except KeyError as e:
            raise TypeError("'{}' is a required keyword.".format(e.args[0]))
        self._avro_serializer = AvroObjectSerializer(codec=kwargs.get("codec"))
        self._auto_register_schemas = kwargs.get("auto_register_schemas", False)
        self._auto_register_schema_func = (
                self._schema_registry_client.register_schema
                if self._auto_register_schemas
                else self._schema_registry_client.get_schema_properties
            )

    async def __aenter__(self):
        # type: () -> AvroSerializer
        await self._schema_registry_client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        # type: (Any) -> None
        await self._schema_registry_client.__aexit__(*exc_details)

    async def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._schema_registry_client.close()

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema_id(self, schema_name, schema_str, **kwargs):
        # type: (str, str, Any) -> str
        """
        Get schema id from local cache with the given schema.
        If there is no item in the local cache, get schema id from the service and cache it.

        :param schema_name: Name of the schema
        :type schema_name: str
        :param str schema_str: Schema string
        :return: Schema Id
        :rtype: str
        """
        schema_properties = await self._auto_register_schema_func(
            self._schema_group, schema_name, schema_str, "Avro", **kwargs
        )
        return schema_properties.id

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> str
        """
        Get schema definition from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema definition
        """
        schema = await self._schema_registry_client.get_schema(
            schema_id, **kwargs
        )
        return schema.definition

    async def serialize(self, value, **kwargs):
        # type: (Mapping[str, Any], Any) -> bytes
        """
        Encode data with the given schema. The returns bytes are consisted of: The first 4 bytes
        denoting record format identifier. The following 32 bytes denoting schema id returned by schema registry
        service. The remaining bytes are the real data payload.

        Schema must be an Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param value: The data to be encoded.
        :type value: Mapping[str, Any]
        :keyword schema: Required. The schema used to encode the data.
        :paramtype schema: str
        :rtype: bytes
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaSerializationError:
            Indicates an issue with serializing data for provided schema.
        """
        try:
            raw_input_schema = kwargs.pop("schema")
        except KeyError as e:
            raise TypeError("'{}' is a required keyword.".format(e.args[0]))
        record_format_identifier = b"\0\0\0\0"

        try:
            schema_fullname = self._avro_serializer.get_schema_fullname(raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaParseError("Cannot parse schema: {}".format(raw_input_schema), error=e).raise_with_traceback()

        schema_id = await self._get_schema_id(schema_fullname, raw_input_schema, **kwargs)
        try:
            data_bytes = self._avro_serializer.serialize(value, raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaSerializationError(
                "Cannot serialize value '{}' for schema: {}".format(value, raw_input_schema),
                error=e
            ).raise_with_traceback()

        stream = BytesIO()

        stream.write(record_format_identifier)
        stream.write(schema_id.encode("utf-8"))
        stream.write(data_bytes)
        stream.flush()

        payload = stream.getvalue()
        stream.close()
        return payload

    async def deserialize(self, value, **kwargs):
        # type: (bytes, Any) -> Dict[str, Any]
        """
        Decode bytes data.

        Data must follow format of associated Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param bytes value: The bytes data needs to be decoded.
        :rtype: Dict[str, Any]
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaDeserializationError:
            Indicates an issue with deserializing value.
        """
        # record_format_identifier = data[0:4]  # The first 4 bytes are retained for future record format identifier.
        schema_id = value[
            SCHEMA_ID_START_INDEX : (SCHEMA_ID_START_INDEX + SCHEMA_ID_LENGTH)
        ].decode("utf-8")
        schema_definition = await self._get_schema(schema_id, **kwargs)

        try:
            dict_value = self._avro_serializer.deserialize(
                value[DATA_START_INDEX:], schema_definition
            )
        except Exception as e:  # pylint:disable=broad-except
            SchemaDeserializationError(
                "Cannot deserialize value '{}' for schema: {}".format(value[DATA_START_INDEX], schema_definition),
                error=e
            ).raise_with_traceback()
        return dict_value
