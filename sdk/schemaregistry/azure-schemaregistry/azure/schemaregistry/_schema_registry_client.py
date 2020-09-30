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
from ._common._response_handlers import _parse_response_schema, _parse_response_schema_id
from ._generated._azure_schema_registry import AzureSchemaRegistry

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
    def __init__(
        self,
        endpoint,
        credential,
        **kwargs
    ):
        # type: (str, TokenCredential, Any) -> None
        self._generated_client = AzureSchemaRegistry(credential=credential, endpoint=endpoint, **kwargs)

    def __enter__(self):
        # type: () -> SchemaRegistryClient
        self._generated_client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._generated_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """ This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._generated_client.close()

    def register_schema(self, schema_group, schema_name, serialization_type, schema_content, **kwargs):
        # type: (str, str, Union[str, SerializationType], str, Any) -> SchemaProperties
        """
        Register new schema. If schema of specified name does not exist in specified group,
        schema is created at version 1. If schema of specified name exists already in specified group,
        schema is created at latest version + 1.

        :param str schema_group: Schema group under which schema should be registered.
        :param str schema_name: Name of schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
         For now Avro is the only supported serialization type by the service.
        :type serialization_type: Union[str, SerializationType]
        :param str schema_content: String representation of the schema being registered.
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

        return self._generated_client.schema.register(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_content,
            x_schema_type=serialization_type,
            cls=_parse_response_schema_id,
            **kwargs
        )

    def get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> Schema
        """
        Gets a registered schema by its unique ID.
        Azure Schema Registry guarantees that ID is unique within a namespace.

        :param str schema_id: References specific schema in registry namespace.
        :rtype: Schema

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_sync]
                :end-before: [END get_schema_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        return self._generated_client.schema.get_by_id(
            schema_id,
            cls=_parse_response_schema,
            **kwargs
        )

    def get_schema_id(self, schema_group, schema_name, serialization_type, schema_content, **kwargs):
        # type: (str, str, Union[str, SerializationType], str, Any) -> SchemaProperties
        """
        Gets the ID referencing an existing schema within the specified schema group,
        as matched by schema content comparison.

        :param str schema_group: Schema group under which schema should be registered.
        :param str schema_name: Name of schema being registered.
        :param serialization_type: Serialization type for the schema being registered.
         The
        :type serialization_type: Union[str, SerializationType]
        :param str schema_content: String representation of the schema being registered.
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

        return self._generated_client.schema.query_id_by_content(
            group_name=schema_group,
            schema_name=schema_name,
            schema_content=schema_content,
            x_schema_type=serialization_type,
            cls=_parse_response_schema_id,
            **kwargs
        )
