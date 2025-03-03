# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from __future__ import annotations
from functools import partial
from typing import (
    cast,
    Tuple,
    Mapping,
    Dict,
    TYPE_CHECKING,
    Iterator,
    AsyncIterator,
    Union,
    List,
    Any,
    overload,
    IO,
)
from enum import Enum
from typing_extensions import Protocol, TypedDict, Self
from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace

from ._client import SchemaRegistryClient as GeneratedServiceClient
from .models._patch import SchemaFormat, NormalizedSchemaContentTypes

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineResponse
    from azure.core.rest import HttpResponse, AsyncHttpResponse

    class SchemaPropertiesDict(TypedDict):  # needed for use with spread operator
        """
        Typing for SchemaProperties dict.
        """

        id: str
        format: "SchemaFormat"
        group_name: str
        name: str
        version: int


###### Response Handlers ######


def _parse_schema_properties_dict(response_headers: Mapping[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
    return {
        "id": response_headers["Schema-Id"],
        "group_name": response_headers["Schema-Group-Name"],
        "name": response_headers["Schema-Name"],
        "version": int(response_headers["Schema-Version"]),
    }


def _normalize_content_type(content_type: str) -> str:
    return content_type.replace(" ", "").lower()


def _get_format(content_type: str) -> Union[SchemaFormat, str]:
    # Exception cases may be due to forward compatibility.
    # i.e. Getting a schema with a content type from a future API version.
    # In this case, we default to returning the content type string.

    # remove whitespace and case from string
    normalized_content_type = _normalize_content_type(content_type)
    if normalized_content_type == NormalizedSchemaContentTypes.AVRO.value:
        return SchemaFormat.AVRO
    if normalized_content_type == NormalizedSchemaContentTypes.JSON.value:
        return SchemaFormat.JSON
    if normalized_content_type == NormalizedSchemaContentTypes.CUSTOM.value:
        return SchemaFormat.CUSTOM
    return content_type


def prepare_schema_properties_result(  # pylint:disable=unused-argument,redefined-builtin
    format: str,
    pipeline_response: "PipelineResponse",
    deserialized: Union[Iterator[bytes], AsyncIterator[bytes]],
    response_headers: Mapping[str, Union[str, int]],
) -> Dict[str, Union[str, int]]:
    properties_dict = _parse_schema_properties_dict(response_headers)
    properties_dict["format"] = SchemaFormat(format)
    pipeline_response.http_response.raise_for_status()
    return properties_dict


def prepare_schema_result(  # pylint:disable=unused-argument
    pipeline_response: "PipelineResponse",
    deserialized: Union[Iterator[bytes], AsyncIterator[bytes]],
    response_headers: Mapping[str, Union[str, int]],
) -> Tuple[Union["HttpResponse", "AsyncHttpResponse"], Dict[str, Union[int, str]]]:
    properties_dict = _parse_schema_properties_dict(response_headers)
    # re-generate after multi-content type response fix: https://github.com/Azure/autorest.python/issues/2122
    properties_dict["format"] = _get_format(cast(str, response_headers.get("Content-Type")))
    pipeline_response.http_response.raise_for_status()
    return pipeline_response.http_response, properties_dict


###### Request Helper Functions ######


def get_http_request_kwargs(kwargs):
    http_request_keywords = ["params", "headers", "json", "data", "files"]
    http_request_kwargs = {key: kwargs.pop(key, None) for key in http_request_keywords if key in kwargs}
    return http_request_kwargs


def get_content_type(format: str):  # pylint:disable=redefined-builtin
    if format.lower() == SchemaFormat.CUSTOM.value.lower():
        return "text/plain; charset=utf-8"
    return f"application/json; serialization={format}"


def get_case_insensitive_format(format: Union[str, SchemaFormat]) -> str:  # pylint:disable=redefined-builtin
    try:
        format = cast(SchemaFormat, format)
        format = format.value
    except AttributeError:
        pass
    return format.capitalize()


###### Wrapper Class ######


class SchemaRegistryClient:
    """
    SchemaRegistryClient is a client for registering and retrieving schemas from the
     Azure Schema Registry service.

    :param str fully_qualified_namespace: The Schema Registry service fully qualified host name.
     For example: my-namespace.servicebus.windows.net.
    :param credential: To authenticate managing the entities of the SchemaRegistry namespace.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword str api_version: The Schema Registry service API version to use for requests.
     Default value is "2022-10".

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
            :start-after: [START create_sr_client_sync]
            :end-before: [END create_sr_client_sync]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the SchemaRegistryClient.

    """

    def __init__(self, fully_qualified_namespace: str, credential: TokenCredential, **kwargs: Any) -> None:
        # using composition (not inheriting from generated client) to allow
        # calling different operations conditionally within one method
        self._generated_client = GeneratedServiceClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            **kwargs,
        )

    def __enter__(self) -> Self:
        self._generated_client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._generated_client.__exit__(*exc_details)

    def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._generated_client.close()

    @distributed_trace
    def register_schema(
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
        :type format: Union[str, SchemaFormat]
        :return: The SchemaProperties associated with the registered schema.
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
        format = get_case_insensitive_format(format)
        http_request_kwargs = get_http_request_kwargs(kwargs)
        # ignoring return type because the generated client operations are not annotated w/ cls return type
        schema_properties: Dict[str, Union[int, str]] = (
            self._generated_client._register_schema(  # type:ignore # pylint:disable=protected-access
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
    def get_schema(self, schema_id: str, **kwargs: Any) -> Schema:
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

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_sync]
                :end-before: [END get_schema_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

        """
        ...

    @overload
    def get_schema(self, *, group_name: str, name: str, version: int, **kwargs: Any) -> Schema:
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

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_by_version_sync]
                :end-before: [END get_schema_by_version_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by version.
        """
        ...

    @distributed_trace
    def get_schema(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword,docstring-keyword-should-match-keyword-only
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

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_sync]
                :end-before: [END get_schema_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by id.

            .. literalinclude:: ../samples/sync_samples/sample_code_schemaregistry.py
                :start-after: [START get_schema_by_version_sync]
                :end-before: [END get_schema_by_version_sync]
                :language: python
                :dedent: 4
                :caption: Get schema by version.
        """
        http_request_kwargs = get_http_request_kwargs(kwargs)
        http_response: "HttpResponse"
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
            ) = self._generated_client._get_schema_by_id(  # type:ignore # pylint:disable=protected-access
                id=schema_id,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types in response are supported
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
            http_response, schema_properties = self._generated_client._get_schema_by_version(  # type: ignore # pylint:disable=protected-access
                group_name=group_name,
                schema_name=name,
                schema_version=version,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types in response are supported
                    "Accept": """application/json; serialization=Avro, application/json; """
                    """serialization=json, text/plain; charset=utf-8"""
                },
                stream=True,
                **http_request_kwargs,
            )  # type:ignore
        http_response.read()
        properties = cast("SchemaPropertiesDict", schema_properties)
        return Schema(
            definition=http_response.text(),
            properties=SchemaProperties(**properties),
        )

    @distributed_trace
    def get_schema_properties(
        self,
        group_name: str,
        name: str,
        definition: str,
        format: Union[str, SchemaFormat],  # pylint:disable=redefined-builtin
        **kwargs: Any,
    ) -> SchemaProperties:
        """
        Gets the schema properties corresponding to an existing schema within the specified schema group,
        as matched by schema definition comparison.

        :param str group_name: Schema group under which schema should be registered.
        :param str name: Name of schema for which properties should be retrieved.
        :param str definition: String representation of the schema for which properties should be retrieved.
        :param format: Format for the schema for which properties should be retrieved.
        :type format: Union[str, SchemaFormat]
        :return: The SchemaProperties associated with the provided schema metadata.
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
        format = get_case_insensitive_format(format)
        http_request_kwargs = get_http_request_kwargs(kwargs)
        # ignoring return type because the generated client operations are not annotated w/ cls return type
        schema_properties: Dict[str, Union[int, str]] = (
            self._generated_client._get_schema_properties_by_content(  # type: ignore # pylint:disable=protected-access
                group_name=group_name,
                schema_name=name,
                schema_content=cast(IO[Any], definition),
                content_type=kwargs.pop("content_type", get_content_type(format)),
                cls=partial(prepare_schema_properties_result, format),
                **http_request_kwargs,
            )
        )  # type:ignore
        properties = cast("SchemaPropertiesDict", schema_properties)
        return SchemaProperties(**properties)


class SchemaProperties:
    """
    Meta properties of a schema.

    :ivar id: References specific schema in registry namespace.
    :vartype id: str
    :ivar format: Format for the schema being stored.
    :vartype format: ~azure.schemaregistry.SchemaFormat
    :ivar group_name: Schema group under which schema is stored.
    :vartype group_name: str
    :ivar name: Name of schema.
    :vartype name: str
    :ivar version: Version of schema.
    :vartype version: int
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id: str = kwargs.pop("id")
        self.format: SchemaFormat = kwargs.pop("format")
        self.group_name: str = kwargs.pop("group_name")
        self.name: str = kwargs.pop("name")
        self.version: int = kwargs.pop("version")

    def __repr__(self) -> str:
        return (
            f"SchemaProperties(id={self.id}, format={self.format}, "
            f"group_name={self.group_name}, name={self.name}, version={self.version})"[:1024]
        )


class Schema:
    """
    The schema content of a schema, along with id and meta properties.

    :ivar definition: The content of the schema.
    :vartype definition: str
    :ivar properties: The properties of the schema.
    :vartype properties: SchemaProperties
    """

    def __init__(self, **kwargs: Any) -> None:
        self.definition: str = kwargs.pop("definition")
        self.properties: SchemaProperties = kwargs.pop("properties")

    def __repr__(self) -> str:
        return f"Schema(definition={self.definition}, properties={self.properties})"[:1024]


# ApiVersion was added to a previously GA'd version. However, newer libraries should not
# accept ApiVersion enums and only take strings. Leaving this here for backwards compatibility.
class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Represents the Schema Registry API version to use for requests.
    """

    V2021_10 = "2021-10"
    V2022_10 = "2022-10"
    """This is the default version."""


###### Encoder Protocols ######


class SchemaContentValidate(Protocol):
    # TODO: make __call__ a public API so that docs show, until then, keep below docstring

    """
    Callable protocol which validates content against provided schema. If invalid, raises Exception.
     Else, returns None.

    :param mapping[str, any] schema: The schema to validate against.
    :param mapping[str, any] content: The content to validate.

    :rtype: None
    :returns: None if valid.
    :raises: Exception if content is invalid against provided schema.
    """

    def __call__(self, schema: Mapping[str, Any], content: Mapping[str, Any]) -> None:
        """
        Validates content against provided schema. If invalid, raises Exception.
         Else, returns None.

        :param mapping[str, any] schema: The schema to validate against.
        :param mapping[str, any] content: The content to validate.

        :rtype: None
        :returns: None if valid.
        :raises: Exception if content is invalid against provided schema.
        """


class MessageContent(TypedDict):
    """A dict with required keys:
    - `content`: bytes
    - `content_type`: str
    """

    content: bytes
    content_type: str


class OutboundMessageContent(Protocol):
    """Protocol for classes that set content and content type values internally."""

    @classmethod
    def from_message_content(cls, content: bytes, content_type: str, **kwargs: Any) -> Self:
        """Creates an object that is a subtype of OutboundMessageContent, given content type and
         a content value to be set on the object.

        :param bytes content: The content value to be set as the body of the message.
        :param str content_type: The content type to be set on the message.
        :rtype: ~azure.schemaregistry.OutboundMessageContent
        :returns: The OutboundMessageContent object with encoded content and content type.
        """


class InboundMessageContent(Protocol):
    """Message Types that get content and content type values internally."""

    def __message_content__(self) -> MessageContent:
        """A MessageContent object, with `content` and `content_type` set to
         the values of their respective properties on the InboundMessageContent object.

        :rtype: ~azure.schemaregistry.MessageContent
        :returns: TypedDict of the content and content type from the InboundMessageContent object.
        """


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "SchemaRegistryClient",
    "SchemaProperties",
    "Schema",
    "SchemaFormat",
    "SchemaContentValidate",
    "MessageContent",
    "OutboundMessageContent",
    "InboundMessageContent",
]  # Add all objects you want publicly available to users at this package level
