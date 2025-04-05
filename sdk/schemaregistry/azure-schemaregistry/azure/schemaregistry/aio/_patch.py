# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from __future__ import annotations
from typing import (
    List,
    Any,
    TYPE_CHECKING,
    Union,
    overload,
    cast,
    IO,
    Dict,
)
from functools import partial
from typing_extensions import Self

from azure.core.tracing.decorator_async import distributed_trace_async

from .._patch import (
    get_http_request_kwargs,
    get_case_insensitive_format,
    get_content_type,
    Schema,
    SchemaProperties,
    prepare_schema_result,
    prepare_schema_properties_result,
)
from ..models._patch import SchemaFormat
from ._client import SchemaRegistryClient as GeneratedServiceClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.rest import AsyncHttpResponse
    from .._patch import SchemaPropertiesDict


###### Wrapper Class ######


class SchemaRegistryClient:
    """
    SchemaRegistryClient is a client for registering and retrieving schemas from the Azure Schema Registry service.

    :param str fully_qualified_namespace: The Schema Registry service fully qualified host name.
     For example: my-namespace.servicebus.windows.net.
    :param credential: To authenticate managing the entities of the SchemaRegistry namespace.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str api_version: The Schema Registry service API version to use for requests.
     Default value is "2022-10".

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
            :start-after: [START create_sr_client_async]
            :end-before: [END create_sr_client_async]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the SchemaRegistryClient.

    """

    def __init__(
        self,
        fully_qualified_namespace: str,
        credential: "AsyncTokenCredential",
        **kwargs: Any,
    ) -> None:
        # using composition (not inheriting from generated client) to allow
        # calling different operations conditionally within one method
        self._generated_client = GeneratedServiceClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            **kwargs,
        )

    async def __aenter__(self) -> Self:
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._generated_client.__aexit__(*args)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._generated_client.close()

    @distributed_trace_async
    async def register_schema(
        self,
        group_name: str,
        name: str,
        definition: str,
        format: Union[str, SchemaFormat],  # pylint:disable=redefined-builtin
        **kwargs: Any,
    ) -> SchemaProperties:
        """
        Register new schema. If schema of specified name does not exist in specified group,
        schema is created at version 1. If schema of specified name exists already in specified group,
        schema is created at latest version + 1.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema being registered.
        :param str definition: String representation of the schema being registered.
        :param format: Format for the schema being registered.
        :type format: Union[str, ~azure.schemaregistry.SchemaFormat]
        :return: The SchemaProperties associated with the registered schema.
        :rtype: ~azure.schemaregistry.SchemaProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START register_schema_async]
                :end-before: [END register_schema_async]
                :language: python
                :dedent: 4
                :caption: Register a new schema.

        """
        format = get_case_insensitive_format(format)
        http_request_kwargs = get_http_request_kwargs(kwargs)
        # ignoring return type because the generated client operations are not annotated w/ cls return type
        schema_properties: Dict[str, Union[int, str]] = (
            await self._generated_client._register_schema(  # type: ignore # pylint:disable=protected-access
                group_name=group_name,
                schema_name=name,
                schema_content=cast(IO[Any], definition),
                content_type=kwargs.pop("content_type", get_content_type(format)),
                cls=partial(prepare_schema_properties_result, format),
                **http_request_kwargs,
            )
        )

        properties = cast("SchemaPropertiesDict", schema_properties)
        return SchemaProperties(**properties)

    @overload
    async def get_schema(self, schema_id: str, **kwargs: Any) -> Schema:
        """Gets a registered schema.

        To get a registered schema by its unique ID, pass the `schema_id` parameter and any optional
        keyword arguments. Azure Schema Registry guarantees that ID is unique within a namespace.

        WARNING: If retrieving a schema format that is unsupported by this client version, upgrade to a client
         version that supports the schema format. Otherwise, the content MIME type string will be returned as
         the `format` value in the `properties` of the returned Schema.

        :param str schema_id: References specific schema in registry namespace. Required if `group_name`,
         `name`, and `version` are not provided.
        :return: The schema stored in the registry associated with the provided arguments.
        :rtype: ~azure.schemaregistry.Schema
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START get_schema_async]
                :end-before: [END get_schema_async]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        ...

    @overload
    async def get_schema(self, *, group_name: str, name: str, version: int, **kwargs: Any) -> Schema:
        """Gets a registered schema.

        To get a specific version of a schema within the specified schema group, pass in the required
        keyword arguments `group_name`, `name`, and `version` and any optional keyword arguments.

        WARNING: If retrieving a schema format that is unsupported by this client version, upgrade to a client
         version that supports the schema format. Otherwise, the content MIME type string will be returned as
         the `format` value in the `properties` of the returned Schema.

        :keyword str group_name: Name of schema group that contains the registered schema.
        :keyword str name: Name of schema which should be retrieved.
        :keyword int version: Version of schema which should be retrieved.
        :return: The schema stored in the registry associated with the provided arguments.
        :rtype: ~azure.schemaregistry.Schema
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START get_schema_by_version_async]
                :end-before: [END get_schema_by_version_async]
                :language: python
                :dedent: 4
                :caption: Get schema by version.
        """
        ...

    @distributed_trace_async
    async def get_schema(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword,docstring-keyword-should-match-keyword-only
        self, *args: str, **kwargs: Any
    ) -> Schema:
        """Gets a registered schema. There are two ways to call this method:

        1) To get a registered schema by its unique ID, pass the `schema_id` parameter and any optional
        keyword arguments. Azure Schema Registry guarantees that ID is unique within a namespace.

        2) To get a specific version of a schema within the specified schema group, pass in the required
        keyword arguments `group_name`, `name`, and `version` and any optional keyword arguments.

        WARNING: If retrieving a schema format that is unsupported by this client version, upgrade to a client
         version that supports the schema format. Otherwise, the content MIME type string will be returned as
         the `format` value in the `properties` of the returned Schema.

        :param str schema_id: References specific schema in registry namespace. Required if `group_name`,
         `name`, and `version` are not provided.
        :keyword str group_name: Name of schema group that contains the registered schema.
        :keyword str name: Name of schema which should be retrieved.
        :keyword int version: Version of schema which should be retrieved.
        :return: The schema stored in the registry associated with the provided arguments.
        :rtype: ~azure.schemaregistry.Schema
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START get_schema_async]
                :end-before: [END get_schema_async]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START get_schema_by_version_async]
                :end-before: [END get_schema_by_version_async]
                :language: python
                :dedent: 4
                :caption: Get schema by version.
        """
        http_request_kwargs = get_http_request_kwargs(kwargs)
        http_response: "AsyncHttpResponse"
        schema_properties: Dict[str, Union[int, str]]
        try:
            # Check positional args for schema_id.
            # Else, check if schema_id was passed in with keyword.
            try:
                schema_id = args[0]
            except IndexError:
                schema_id = kwargs.pop("schema_id")
            schema_id = cast(str, schema_id)
            # ignoring return type because the generated client operations are not annotated w/ cls return type
            (
                http_response,
                schema_properties,
            ) = await self._generated_client._get_schema_by_id(  # type: ignore # pylint:disable=protected-access
                id=schema_id,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types are supported
                    "Accept": """application/json; serialization=Avro, application/json; """
                    """serialization=json, text/plain; charset=utf-8"""
                },
                stream=True,
                **http_request_kwargs,
            )

        except KeyError:
            # If group_name, name, and version aren't passed in as kwargs, raise error.
            try:
                group_name = kwargs.pop("group_name")
                name = kwargs.pop("name")
                version = kwargs.pop("version")
            except KeyError:
                raise TypeError(  # pylint:disable=raise-missing-from
                    """Missing required argument(s). Specify either `schema_id` """
                    """or `group_name`, `name`, `version."""
                )
            # ignoring return type because the generated client operations are not annotated w/ cls return type
            http_response, schema_properties = await self._generated_client._get_schema_by_version(  # type: ignore # pylint:disable=protected-access
                group_name=group_name,
                schema_name=name,
                schema_version=version,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types are supported
                    "Accept": """application/json; serialization=Avro, application/json; """
                    """serialization=json, text/plain; charset=utf-8"""
                },
                stream=True,
                **http_request_kwargs,
            )

        await http_response.read()
        properties = cast("SchemaPropertiesDict", schema_properties)
        return Schema(
            definition=http_response.text(),
            properties=SchemaProperties(**properties),
        )

    @distributed_trace_async
    async def get_schema_properties(
        self,
        group_name: str,
        name: str,
        definition: str,
        format: Union[str, SchemaFormat],  # pylint:disable=redefined-builtin
        **kwargs: Any,
    ) -> SchemaProperties:
        """
        Gets the schema properties corresponding to an existing schema within the specified schema group,
        as matched by schema defintion comparison.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema for which properties should be retrieved.
        :param str definition: String representation of the schema for which properties should be retrieved.
        :param format: Format for the schema for which properties should be retrieved.
        :type format: Union[str, SchemaFormat]
        :return: The SchemaProperties associated with the provided schema metadata.
        :rtype: ~azure.schemaregistry.SchemaProperties
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_code_schemaregistry_async.py
                :start-after: [START get_schema_id_async]
                :end-before: [END get_schema_id_async]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        format = get_case_insensitive_format(format)
        http_request_kwargs = get_http_request_kwargs(kwargs)
        # ignoring return type because the generated client operations are not annotated w/ cls return type
        schema_properties: Dict[str, Union[int, str]] = (
            await self._generated_client._get_schema_properties_by_content(  # type: ignore # pylint:disable=protected-access
                group_name=group_name,
                schema_name=name,
                schema_content=cast(IO[Any], definition),
                content_type=kwargs.pop("content_type", get_content_type(format)),
                cls=partial(prepare_schema_properties_result, format),
                **http_request_kwargs,
            )
        )
        properties = cast("SchemaPropertiesDict", schema_properties)
        return SchemaProperties(**properties)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "SchemaRegistryClient",
]  # Add all objects you want publicly available to users at this package level
