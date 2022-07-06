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
from typing import Any, TYPE_CHECKING, Union, cast

from ._utils import get_http_request_kwargs
from ._common._constants import SchemaFormat, DEFAULT_VERSION
from ._common._schema import Schema, SchemaProperties
from ._common._response_handlers import (
    _parse_response_schema,
    _parse_response_schema_properties,
)
from ._generated._client import AzureSchemaRegistry
from ._generated.rest import schema as schema_rest


if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class SchemaRegistryClient(object):
    """
    SchemaRegistryClient is a client for registering and retrieving schemas from the Azure Schema Registry service.

    :param str fully_qualified_namespace: The Schema Registry service fully qualified host name.
     For example: my-namespace.servicebus.windows.net.
    :param credential: To authenticate managing the entities of the SchemaRegistry namespace.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str api_version: The Schema Registry service API version to use for requests.
     Default value and only accepted value currently is "2021-10".

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START create_sr_client_sync]
            :end-before: [END create_sr_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the SchemaRegistryClient.

    """

    def __init__(self, fully_qualified_namespace, credential, **kwargs):
        # type: (str, TokenCredential, Any) -> None
        api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._generated_client = AzureSchemaRegistry(
            credential=credential,
            endpoint=fully_qualified_namespace,
            api_version=api_version,
            **kwargs
        )

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
        self,
        group_name,
        name,
        definition,
        format,
        **kwargs  # pylint:disable=redefined-builtin
    ):
        # type: (str, str, str, Union[str, SchemaFormat], Any) -> SchemaProperties
        """
        Register new schema. If schema of specified name does not exist in specified group,
        schema is created at version 1. If schema of specified name exists already in specified group,
        schema is created at latest version + 1.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema being registered.
        :param str definition: String representation of the schema being registered.
        :param format: Format for the schema being registered.
         For now Avro is the only supported schema format by the service.
        :type format: Union[str, SchemaFormat]
        :rtype: ~azure.schemaregistry.SchemaProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START register_schema_sync]
                :end-before: [END register_schema_sync]
                :language: python
                :dedent: 4
                :caption: Register a new schema.

        """
        try:
            format = cast(SchemaFormat, format)
            format = format.value
        except AttributeError:
            pass

        format = format.capitalize()
        http_request_kwargs = get_http_request_kwargs(kwargs)
        request = schema_rest.build_register_request(
            group_name=group_name,
            schema_name=name,
            content=definition,
            content_type=kwargs.pop(
                "content_type", "application/json; serialization={}".format(format)
            ),
            **http_request_kwargs
        )

        response = self._generated_client.send_request(request, **kwargs)
        response.raise_for_status()
        return _parse_response_schema_properties(response, format)

    def get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> Schema
        """
        Gets a registered schema by its unique ID.
        Azure Schema Registry guarantees that ID is unique within a namespace.

        :param str schema_id: References specific schema in registry namespace.
        :rtype: ~azure.schemaregistry.Schema
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_sync]
                :end-before: [END get_schema_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        http_request_kwargs = get_http_request_kwargs(kwargs)
        request = schema_rest.build_get_by_id_request(
            id=schema_id, **http_request_kwargs
        )
        response = self._generated_client.send_request(request, **kwargs)
        response.raise_for_status()
        return _parse_response_schema(response)

    def get_schema_by_version(self,version,group_name, schema_name, **kwargs):
        # type: (str,str,str,Any) -> Schema
        """
        Gets a registered schema by its version, group name and schema name.

        :param str version: References schema version for a schema in a schema group.
        :param str group_name: References schema group in registry namespace.
        :param str schema_name: References specific schema in registry namespace.
        :rtype: ~azure.schemaregistry.Schema
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        http_request_kwargs = get_http_request_kwargs(kwargs)
        request = schema_rest.build_get_schema_by_version_request(
           version=version,group_name=group_name,schema_name=schema_name, **http_request_kwargs
        )
        response = self._generated_client.send_request(request, **kwargs)
        response.raise_for_status()
        return _parse_response_schema(response)

    def get_schema_properties(
        self,
        group_name,
        name,
        definition,
        format,
        **kwargs  # pylint:disable=redefined-builtin
    ):
        # type: (str, str, str, Union[str, SchemaFormat], Any) -> SchemaProperties
        """
        Gets the schema properties corresponding to an existing schema within the specified schema group,
        as matched by schema definition comparison.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema for which properties should be retrieved.
        :param str definition: String representation of the schema for which properties should be retrieved.
        :param format: Format for the schema for which properties should be retrieved.
        :type format: Union[str, SchemaFormat]
        :rtype: ~azure.schemaregistry.SchemaProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_id_sync]
                :end-before: [END get_schema_id_sync]
                :language: python
                :dedent: 4
                :caption: Get schema id.

        """
        try:
            format = cast(SchemaFormat, format)
            format = format.value
        except AttributeError:
            pass

        format = format.capitalize()
        http_request_kwargs = get_http_request_kwargs(kwargs)
        request = schema_rest.build_query_id_by_content_request(
            group_name=group_name,
            schema_name=name,
            content=definition,
            content_type=kwargs.pop(
                "content_type", "application/json; serialization={}".format(format)
            ),
            **http_request_kwargs
        )

        response = self._generated_client.send_request(request, **kwargs)
        response.raise_for_status()
        return _parse_response_schema_properties(response, format)
