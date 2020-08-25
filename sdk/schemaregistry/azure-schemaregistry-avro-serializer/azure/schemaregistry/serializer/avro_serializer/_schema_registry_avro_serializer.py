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
import avro

from azure.schemaregistry import SchemaRegistryClient, SerializationType

from ._avro_serializer import AvroObjectSerializer


class SchemaRegistryAvroSerializer(object):
    """

    """
    def __init__(self, credential, endpoint, schema_group, **kwargs):
        self._schema_group = schema_group
        self._avro_serializer = AvroObjectSerializer()
        self._schema_registry_client = SchemaRegistryClient(credential=credential, endpoint=endpoint)
        self._id_to_schema = {}
        self._schema_to_id = {}

    def _get_schema_id(self, schema_name, schema_str):
        """

        :param schema_name:
        :param schema_str:
        :return:
        """
        try:
            return self._schema_to_id[schema_str]
        except KeyError:
            schema_id = self._schema_registry_client.register_schema(
                self._schema_group,
                schema_name,
                SerializationType.AVRO,
                schema_str
            )
            self._schema_to_id[schema_str] = schema_id
            self._id_to_schema[schema_id] = str(schema_str)
            return schema_id

    def _get_schema(self, schema_id):
        """

        :param str schema_id:
        :return:
        """
        try:
            return self._id_to_schema[schema_id]
        except KeyError:
            schema_str = self._schema_registry_client.get_schema(schema_id)
            self._id_to_schema[schema_id] = schema_str
            self._schema_to_id[schema_str] = schema_id
            return schema_str

    def serialize(self, data, schema):
        """

        :param schema:  # TODO: support schema object/str/bytes?
        :param dict data:
        :return:
        """
        # TODO: schema name generated through schema namespace + name
        if not isinstance(schema, avro.schema.Schema):
            schema = avro.schema.parse(schema)

        schema_id = self._get_schema_id(schema.fullname, str(schema))
        stream = BytesIO()
        self._avro_serializer.serialize(stream, data, schema)
        res = schema_id.encode('utf-8') + stream.getvalue()
        return res

    def deserialize(self, data):
        """

        :param dict data:
        :return:
        """
        schema_id = data[0:32].decode('utf-8')
        schema_str = self._get_schema(schema_id)
        dict_data = self._avro_serializer.deserialize(data[32:])  # TODO: do validation
        return dict_data

