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
try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache
from io import BytesIO
from typing import Any, Dict, Mapping
import avro

from ._constants import SCHEMA_ID_START_INDEX, SCHEMA_ID_LENGTH, DATA_START_INDEX
from ._avro_serializer import AvroObjectSerializer


class AvroSerializer(object):
    """
    AvroSerializer provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :keyword client: Required. The schema registry client
     which is used to register schema and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.SchemaRegistryClient
    :keyword str group_name: Required. Schema group under which schema should be registered.
    :keyword bool auto_register_schemas: When true, register new schemas passed to serialize.
     Otherwise, and by default, fail if it has not been pre-registered in the registry.

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
                else self._schema_registry_client.get_schema_id
            )

    def __enter__(self):
        # type: () -> SchemaRegistryAvroSerializer
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._schema_registry_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._schema_registry_client.close()

    @lru_cache(maxsize=128)
    def _get_schema_id(self, schema_name, schema_str, **kwargs):
        # type: (str, str, Any) -> str
        """
        Get schema id from local cache with the given schema.
        If there is no item in the local cache, get schema id from the service and cache it.

        :param schema_name: Name of the schema
        :type schema_name: str
        :param schema: Schema object
        :type schema: avro.schema.Schema
        :return: Schema Id
        :rtype: str
        """
        schema_id = self._auto_register_schema_func(
            self._schema_group, schema_name, "Avro", schema_str, **kwargs
        ).schema_id
        return schema_id

    @lru_cache(maxsize=128)
    def _get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> str
        """
        Get schema content from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema content
        """
        schema_str = self._schema_registry_client.get_schema(
            schema_id, **kwargs
        ).schema_content
        return schema_str

    @lru_cache(maxsize=128)
    def _parse_schema(self, schema):
        return avro.schema.parse(schema)

    def serialize(self, value, **kwargs):
        # type: (Mapping[str, Any], Any) -> bytes
        """
        Encode data with the given schema. The returns bytes are consisted of: The first 4 bytes
        denoting record format identifier. The following 32 bytes denoting schema id returned by schema registry
        service. The remaining bytes are the real data payload.

        :param value: The data to be encoded.
        :type value: Mapping[str, Any]
        :keyword schema: Required. The schema used to encode the data.
        :paramtype schema: str
        :rtype: bytes
        """
        try:
            raw_input_schema = kwargs.pop("schema")
        except KeyError as e:
            raise TypeError("'{}' is a required keyword.".format(e.args[0]))

        cached_schema = self._parse_schema(raw_input_schema)
        record_format_identifier = b"\0\0\0\0"
        schema_id = self._get_schema_id(cached_schema.fullname, str(cached_schema), **kwargs)
        data_bytes = self._avro_serializer.serialize(value, cached_schema)

        stream = BytesIO()

        stream.write(record_format_identifier)
        stream.write(schema_id.encode("utf-8"))
        stream.write(data_bytes)
        stream.flush()

        payload = stream.getvalue()
        stream.close()
        return payload

    def deserialize(self, value, **kwargs):
        # type: (bytes, Any) -> Dict[str, Any]
        """
        Decode bytes data.

        :param bytes value: The bytes data needs to be decoded.
        :rtype: Dict[str, Any]
        """
        # record_format_identifier = data[0:4]  # The first 4 bytes are retained for future record format identifier.
        schema_id = value[
            SCHEMA_ID_START_INDEX : (SCHEMA_ID_START_INDEX + SCHEMA_ID_LENGTH)
        ].decode("utf-8")
        schema_content = self._get_schema(schema_id, **kwargs)

        dict_value = self._avro_serializer.deserialize(
            value[DATA_START_INDEX:], schema_content
        )
        return dict_value
