# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from io import BytesIO

from azure.schemaregistry import SchemaRegistryClient

from ._avro_serializer import AvroObjectSerializer


class SchemaRegistryAvroSerializer:
    def __init__(self, credential, endpoint, schema_group, **kwargs):
        self._schema_group = schema_group
        self._avro_serializer = AvroObjectSerializer()
        self._scheme_registry_client = SchemaRegistryClient(credential=credential, endpoint=endpoint)

        self._schema_dict = {}

    def _get_schema_id(self, schema):
        if schema in self._schema_dict:
            return self._schema_dict[schema]
        else:
            self._scheme_registry_client.register_schema()

    def serialize(self, data, schema_name, schema):
        """

        :param schema:
        :param data:
        :return:
        """
        stream = BytesIO()
        data_payload = self._avro_serializer.serialize(stream, data, schema)


    def deserialize(self):
        pass
