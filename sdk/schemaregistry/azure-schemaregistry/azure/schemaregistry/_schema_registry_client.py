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
from typing import Any, TYPE_CHECKING, Union

from ._common._constants import SerializationType
from ._common._schema import Schema, SchemaProperties
from ._common._response_handlers import (
    _parse_response_schema,
    _parse_response_schema_properties,
)
from ._generated._azure_schema_registry import AzureSchemaRegistry
from ._generated.rest import schema as schema_rest


if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class SchemaRegistryClient(object):
    """
    SchemaRegistryClient is as a central schema repository for enterprise-level data infrastructure,
    complete with support for versioning and management.

    :param str endpoint: The Schema Registry service endpoint, for example my-namespace.servicebus.windows.net.
    :param credential: To authenticate to manage the entities of the SchemaRegistry namespace.
    :type credential: TokenCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START create_sr_client_sync]
            :end-before: [END create_sr_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the SchemaRegistryClient.

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Any) -> None
        self._generated_client = AzureSchemaRegistry(
            credential=credential, endpoint=endpoint, **kwargs
        )
        self._description_to_properties = {}
        self._id_to_schema = {}

    def __enter__(self):
        # type: () -> SchemaRegistryClient
        self._generated_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._generated_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._generated_client.close()

    def register_schema(
        self, group_name, name, content, serialization_type, **kwargs
    ):
        # type: (str, str, str, Union[str, SerializationType], Any) -> SchemaProperties
        """
        Register new schema. If schema of specified name does not exist in specified group,
        schema is created at version 1. If schema of specified name exists already in specified group,
        schema is created at latest version + 1.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema being registered.
        :param str content: String representation of the schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
         For now Avro is the only supported serialization type by the service.
        :type serialization_type: Union[str, SerializationType]
        :keyword content_type: The content type of the request. Default value is 'application/json'.
        :paramtype content_type: str
        :rtype: SchemaProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START register_schema_sync]
                :end-before: [END register_schema_sync]
                :language: python
                :dedent: 4
                :caption: Register a new schema.

        """
        try:
            serialization_type = serialization_type.value
        except AttributeError:
            pass

        request = schema_rest.build_register_request(
            group_name=group_name,
            schema_name=name,
            content=content,
            serialization_type=serialization_type,
            content_type=kwargs.pop("content_type", "application/json"),
            **kwargs
        )

        response = self._generated_client.send_request(request)
        response.raise_for_status()
        schema_properties = _parse_response_schema_properties(response)

        schema_description = (
            group_name,
            name,
            content,
            serialization_type,
        )
        self._id_to_schema[schema_properties.id] = Schema(
            content, schema_properties
        )
        self._description_to_properties[schema_description] = schema_properties

        return schema_properties

    def get_schema(self, id, **kwargs):  # pylint:disable=redefined-builtin
        # type: (str, Any) -> Schema
        """
        Gets a registered schema by its unique ID.
        Azure Schema Registry guarantees that ID is unique within a namespace.

        :param str id: References specific schema in registry namespace.
        :rtype: Schema

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_sync]
                :end-before: [END get_schema_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        try:
            return self._id_to_schema[id]
        except KeyError:
            request = schema_rest.build_get_by_id_request(schema_id=id)
            response = self._generated_client.send_request(request, **kwargs)
            response.raise_for_status()
            schema = _parse_response_schema(response)
            self._id_to_schema[id] = schema
            return schema

    def get_schema_properties(
        self, group_name, name, content, serialization_type, **kwargs
    ):
        # type: (str, str, str, Union[str, SerializationType], Any) -> SchemaProperties
        """
        Gets the ID referencing an existing schema within the specified schema group,
        as matched by schema content comparison.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema being registered.
        :param str content: String representation of the schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
        :type serialization_type: Union[str, SerializationType]
        :keyword content_type: The content type of the request. Default value is 'application/json'.
        :paramtype content_type: str
        :rtype: SchemaProperties

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_id_sync]
                :end-before: [END get_schema_id_sync]
                :language: python
                :dedent: 4
                :caption: Get schema id.

        """
        try:
            serialization_type = serialization_type.value
        except AttributeError:
            pass

        try:
            properties = self._description_to_properties[
                (group_name, name, content, serialization_type)
            ]
            return properties
        except KeyError:
            request = schema_rest.build_query_id_by_content_request(
                group_name=group_name,
                schema_name=name,
                content=content,
                serialization_type=serialization_type,
                content_type=kwargs.pop("content_type", "application/json"),
                **kwargs
            )

            response = self._generated_client.send_request(request, **kwargs)
            response.raise_for_status()
            schema_properties = _parse_response_schema_properties(response)

            if not self._id_to_schema.get(schema_properties.id):
                self._id_to_schema[schema_properties.id] = Schema(content, schema_properties)
            else:
                schema_properties = self._id_to_schema[schema_properties.id].properties
            self._description_to_properties[
                (group_name, name, content, serialization_type)
            ] = schema_properties
            return schema_properties
