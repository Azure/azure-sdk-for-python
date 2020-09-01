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

from azure.schemaregistry import SchemaRegistryClient, SerializationType

from ._avro_serializer import AvroObjectSerializer

# TODO: inherit from context manager
class SchemaRegistryAvroSerializer():  # suffix Client?
    """
    SchemaRegistryAvroSerializer provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :param str endpoint: The Schema Registry service endpoint, for example my-namespace.servicebus.windows.net.
    :param credential: To authenticate to manage the entities of the SchemaRegistry namespace.
    :type credential: TokenCredential
    :param str schema_group: Schema group under which schema should be registered.

    """
    def __init__(self, endpoint, credential, schema_group, **kwargs):
        self._schema_group = schema_group
        self._avro_serializer = AvroObjectSerializer()
        self._schema_registry_client = SchemaRegistryClient(credential=credential, endpoint=endpoint)
        self._id_to_schema = {}
        self._schema_to_id = {}
        self._user_input_schema_cache = {}

    def __enter__(self):
        # type: () -> SchemaRegistryAvroSerializer
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._schema_registry_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._schema_registry_client.close()

    def _get_schema_id(self, schema_name, schema):
        # type: (str, avro.schema.Schema) -> str
        """

        :param schema_name:
        :param schema:
        :return:
        """
        schema_str = str(schema)
        try:
            return self._schema_to_id[schema_str]
        except KeyError:
            schema_id = self._schema_registry_client.register_schema(
                self._schema_group,
                schema_name,
                SerializationType.AVRO,
                schema_str
            ).id
            self._schema_to_id[schema_str] = schema_id
            self._id_to_schema[schema_id] = schema_str
            return schema_id

    def _get_schema(self, schema_id):
        # type: (str) -> str
        """

        :param str schema_id:
        :return:
        """
        try:
            return self._id_to_schema[schema_id]
        except KeyError:
            schema_str = self._schema_registry_client.get_schema(schema_id).content
            self._id_to_schema[schema_id] = schema_str
            self._schema_to_id[schema_str] = schema_id
            return schema_str

    def serialize(self, data, schema):
        # type: (Dict[str, Any], Union[str, bytes]) -> bytes
        """
        Encode dict data with the given schema.

        :param data: The dict data to be encoded.
        :param schema: The schema used to encode the data.
        :type schema: Union[str, bytes]
        :return:
        """
        try:
            schema = self._user_input_schema_cache[schema]
        except KeyError:
            if not isinstance(schema, avro.schema.Schema):
                schema = avro.schema.parse(schema)
            self._user_input_schema_cache[schema] = schema

        record_format_identifier = b'\0\0\0\0'  # TODO: BytesIO to append bytes zero
        schema_id = self._get_schema_id(schema.fullname, schema)
        data_bytes = self._avro_serializer.serialize(data, schema)

        stream = BytesIO()

        stream.write(record_format_identifier)
        stream.write(schema_id.encode('utf-8'))
        stream.write(data_bytes)
        stream.flush()

        payload = stream.getvalue()
        stream.close()
        return payload

    def deserialize(self, data):
        # type: (bytes) -> Dict[str, Any]  # TODO: add Io/generator support in the future
        """
        Decode bytes data.

        :param bytes data: The bytes data needs to be decoded.
        :rtype: Dict[str, Any]
        """
        record_format_identifier = data[0:4]
        schema_id = data[4:36].decode('utf-8')
        schema_content = self._get_schema(schema_id)

        dict_data = self._avro_serializer.deserialize(data[36:], schema_content)
        return dict_data
