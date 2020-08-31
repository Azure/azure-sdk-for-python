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
from typing import Any, Dict, Union
import avro

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry import SerializationType

from .._avro_serializer import AvroObjectSerializer


class SchemaRegistryAvroSerializer:
    """
    SchemaRegistryAvroSerializer provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :param str endpoint: The Schema Registry service endpoint, for example my-namespace.servicebus.windows.net.
    :param credential: To authenticate to manage the entities of the SchemaRegistry namespace.
    :type credential: TokenCredential
    :param str schema_group

    """
    def __init__(self, endpoint, credential, schema_group, **kwargs):
        self._schema_group = schema_group
        self._avro_serializer = AvroObjectSerializer()
        self._schema_registry_client = SchemaRegistryClient(endpoint=endpoint, credential=credential)
        self._id_to_schema = {}
        self._schema_to_id = {}

    async def __aenter__(self) -> "SchemaRegistryAvroSerializer":
        await self._schema_registry_client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._schema_registry_client.__aexit__(*args)

    async def close(self) -> None:
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._schema_registry_client.close()

    async def _get_schema_id(self, schema_name: str, schema_str: str) -> str:
        """

        :param schema_name:
        :param schema_str:
        :return:
        """
        try:
            return self._schema_to_id[schema_str]
        except KeyError:
            schema_id = (await self._schema_registry_client.register_schema(
                self._schema_group,
                schema_name,
                SerializationType.AVRO,
                schema_str
            )).id
            self._schema_to_id[schema_str] = schema_id
            self._id_to_schema[schema_id] = str(schema_str)
            return schema_id

    async def _get_schema(self, schema_id: str) -> str:
        """

        :param str schema_id:
        :return:
        """
        try:
            return self._id_to_schema[schema_id]
        except KeyError:
            schema_str = (await self._schema_registry_client.get_schema(schema_id)).content
            self._id_to_schema[schema_id] = schema_str
            self._schema_to_id[schema_str] = schema_id
            return schema_str

    async def serialize(self, data: Dict[str, Any], schema: Union[str, bytes]) -> bytes:
        """
        Encode dict data with the given schema.

        :param data: The dict data to be encoded.
        :param schema: The schema used to encode the data.  # TODO: support schema object/str/bytes?
        :type schema: Union[str, bytes]
        :return:
        """
        if not isinstance(schema, avro.schema.Schema):
            schema = avro.schema.parse(schema)

        schema_id = await self._get_schema_id(schema.fullname, str(schema))
        data_bytes = self._avro_serializer.serialize(data, schema)
        # TODO: Arthur:  We are adding 4 bytes to the beginning of each SR payload.
        # This is intended to become a record format identifier in the future.
        # Right now, you can just put \x00\x00\x00\x00.
        record_format_identifier = b'\0\0\0\0'
        payload = record_format_identifier + schema_id.encode('utf-8') + data_bytes
        return payload

    async def deserialize(self, data: bytes) -> Dict[str, Any]:
        """
        Decode bytes data.

        :param bytes data: The bytes data needs to be decoded.
        :rtype: Dict[str, Any]
        """
        # TODO: Arthur:  We are adding 4 bytes to the beginning of each SR payload.
        # This is intended to become a record format identifier in the future.
        # Right now, you can just put \x00\x00\x00\x00.
        record_format_identifier = data[0:4]
        schema_id = data[4:36].decode('utf-8')
        schema_content = await self._get_schema(schema_id)

        schema = avro.schema.parse(schema_content)
        dict_data = self._avro_serializer.deserialize(data[36:], schema)
        return dict_data
