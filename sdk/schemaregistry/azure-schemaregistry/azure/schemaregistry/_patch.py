# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from __future__ import annotations
from functools import partial
from enum import Enum
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
    Type,
    Optional,
)
from typing_extensions import Protocol, TypedDict

from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, ResourceNotModifiedError, map_error
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from ._operations._operations import ClsType
from ._serialization import Serializer
from ._client import SchemaRegistryClient as ServiceClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline import PipelineResponse
    from azure.core.rest import HttpResponse, AsyncHttpResponse

_SERIALIZER = Serializer()

###### Response Handlers ######

def _parse_schema_properties_dict(
    response_headers: Mapping[str, Union[str, int]]
) -> Dict[str, Union[str, int]]:
    return {
        "id": response_headers["Schema-Id"],
        "group_name": response_headers["Schema-Group-Name"],
        "name": response_headers["Schema-Name"],
        "version": int(response_headers["Schema-Version"]),
    }


def _get_format(content_type: str) -> SchemaFormat:
    # pylint:disable=redefined-builtin
    try:
        format = content_type.split("serialization=")[1]
        try:
            format = SchemaFormat(format)
        except ValueError:
            format = SchemaFormat(format.capitalize())
    except IndexError:
        format = SchemaFormat.CUSTOM
    return format


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
    # TODO: content type is not being added to the response headers b/c of
    properties_dict["format"] = _get_format(
        cast(str, response_headers.get("Content-Type"))
    )
    pipeline_response.http_response.raise_for_status()
    return pipeline_response.http_response, properties_dict


###### Request Helper Functions ######


def get_http_request_kwargs(kwargs):
    http_request_keywords = ["params", "headers", "json", "data", "files"]
    http_request_kwargs = {
        key: kwargs.pop(key, None) for key in http_request_keywords if key in kwargs
    }
    return http_request_kwargs


def get_content_type(format: str):  # pylint:disable=redefined-builtin
    if format.lower() == SchemaFormat.CUSTOM.value.lower():
        return "text/plain; charset=utf-8"
    return f"application/json; serialization={format}"


def get_case_insensitive_format(
    format: Union[str, SchemaFormat]  # pylint:disable=redefined-builtin
) -> str:
    try:
        format = cast(SchemaFormat, format)
        format = format.value
    except AttributeError:
        pass
    return format.capitalize()


def build_schema_registry_get_schema_id_by_content_request(  # pylint: disable=name-too-long
    group_name: str,
    name: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    content_type: str = kwargs.pop('content_type')
    api_version: str = kwargs.pop('api_version', _params.pop('api-version', "2022-10"))
    accept = _headers.pop('Accept', "application/json")

    # Construct URL
    _url = "/$schemaGroups/{groupName}/schemas/{name}:get-id"
    path_format_arguments = {
        "groupName": _SERIALIZER.url("group_name", group_name, 'str'),
        "name": _SERIALIZER.url("name", name, 'str'),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    _headers['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        **kwargs
    )


def build_schema_registry_register_schema_request(  # pylint: disable=name-too-long
    group_name: str,
    name: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    content_type: str = kwargs.pop('content_type')
    api_version: str = kwargs.pop('api_version', _params.pop('api-version', "2022-10"))
    accept = _headers.pop('Accept', "application/json")

    # Construct URL
    _url = "/$schemaGroups/{groupName}/schemas/{name}"
    path_format_arguments = {
        "groupName": _SERIALIZER.url("group_name", group_name, 'str'),
        "name": _SERIALIZER.url("name", name, 'str'),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    _headers['Content-Type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    return HttpRequest(
        method="PUT",
        url=_url,
        params=_params,
        headers=_headers,
        **kwargs
    )

class GeneratedClient(ServiceClientGenerated):
    """
    Generated client to add custom methods.
    """

    @distributed_trace
    def get_schema_id_by_content(  # pylint: disable=inconsistent-return-statements
        self,
        group_name: str,
        name: str,
        schema_content: bytes,
        **kwargs: Any
    ) -> None:
        """Get ID for existing schema.

        Gets the ID referencing an existing schema within the specified schema group, as matched by
        schema content comparison.

        :param group_name: Name of schema group. Required.
        :type group_name: str
        :param name: Name of schema. Required.
        :type name: str
        :param schema_content: String representation (UTF-8) of the registered schema. Required.
        :type schema_content: bytes
        :keyword content_type: The content type for given schema. Default value is "text/plain;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError
        }
        error_map.update(kwargs.pop('error_map', {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: str = kwargs.pop('content_type', _headers.pop('Content-Type', "text/plain; charset=utf-8"))
        cls: ClsType[None] = kwargs.pop(
            'cls', None
        )

        _content = schema_content

        request = build_schema_registry_get_schema_id_by_content_request(
            group_name=group_name,
            name=name,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = self._client._pipeline.run(   # pylint: disable=protected-access
            request,
            stream=_stream,
            **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers['Location']=self._deserialize('str', response.headers.get('Location'))
        response_headers['Schema-Id']=self._deserialize('str', response.headers.get('Schema-Id'))
        response_headers['Schema-Id-Location']=self._deserialize('str', response.headers.get('Schema-Id-Location'))
        response_headers['Schema-Group-Name']=self._deserialize('str', response.headers.get('Schema-Group-Name'))
        response_headers['Schema-Name']=self._deserialize('str', response.headers.get('Schema-Name'))
        response_headers['Schema-Version']=self._deserialize('int', response.headers.get('Schema-Version'))


        if cls:
            return cls(pipeline_response, None, response_headers)

    @distributed_trace
    def register_schema(  # pylint: disable=inconsistent-return-statements
        self,
        group_name: str,
        name: str,
        content: bytes,
        **kwargs: Any
    ) -> None:
        """Register new schema.

        Register new schema. If schema of specified name does not exist in specified group, schema is
        created at version 1. If schema of specified name exists already in specified group, schema is
        created at latest version + 1.

        :param group_name: Name of schema group. Required.
        :type group_name: str
        :param name: Name of schema. Required.
        :type name: str
        :param content: String representation (UTF-8) of the schema. Required.
        :type content: bytes
        :keyword content_type: The content type for given schema. Default value is "text/plain;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError
        }
        error_map.update(kwargs.pop('error_map', {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: str = kwargs.pop('content_type', _headers.pop('Content-Type', "text/plain; charset=utf-8"))
        cls: ClsType[None] = kwargs.pop(
            'cls', None
        )

        _content = content

        request = build_schema_registry_register_schema_request(
            group_name=group_name,
            name=name,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = self._client._pipeline.run(   # pylint: disable=protected-access
            request,
            stream=_stream,
            **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204]:
            if _stream:
                 response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        response_headers = {}
        response_headers['Location']=self._deserialize('str', response.headers.get('Location'))
        response_headers['Schema-Id']=self._deserialize('str', response.headers.get('Schema-Id'))
        response_headers['Schema-Id-Location']=self._deserialize('str', response.headers.get('Schema-Id-Location'))
        response_headers['Schema-Group-Name']=self._deserialize('str', response.headers.get('Schema-Group-Name'))
        response_headers['Schema-Name']=self._deserialize('str', response.headers.get('Schema-Name'))
        response_headers['Schema-Version']=self._deserialize('int', response.headers.get('Schema-Version'))


        if cls:
            return cls(pipeline_response, None, response_headers)


###### Wrapper Class ######
class SchemaRegistryClient(object):
    """
    SchemaRegistryClient is a client for registering and retrieving schemas from the Azure Schema Registry service.

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

    def __init__(
        self, fully_qualified_namespace: str, credential: TokenCredential, **kwargs: Any
    ) -> None:
        # using composition (not inheriting from generated client) to allow
        # calling different operations conditionally within one method
        if "https://" not in fully_qualified_namespace:
            fully_qualified_namespace = f"https://{fully_qualified_namespace}"
        api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._generated_client = GeneratedClient(
            endpoint=fully_qualified_namespace,
            credential=credential,
            api_version=api_version,
            **kwargs,
        )

    def __enter__(self) -> "SchemaRegistryClient":
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
    def register_schema(  # pylint:disable=arguments-differ
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
         For now Avro is the only supported schema format by the service.
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
        schema_properties: Dict[
            str, Union[int, str]
        ] = self._generated_client.register_schema(
            group_name=group_name,
            name=name,
            content=cast(IO[Any], definition),
            content_type=kwargs.pop("content_type", get_content_type(format)),
            cls=partial(prepare_schema_properties_result, format),
            **http_request_kwargs,
        )
        return SchemaProperties(**schema_properties)

    @overload
    def get_schema(self, schema_id: str, **kwargs: Any) -> Schema:
        ...

    @overload
    def get_schema(
        self, *, group_name: str, name: str, version: int, **kwargs: Any
    ) -> Schema:
        ...

    @distributed_trace
    def get_schema(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword
        self, *args: str, **kwargs: Any
    ) -> Schema:
        """Gets a registered schema. There are two ways to call this method:

        1) To get a registered schema by its unique ID, pass the `schema_id` parameter and any optional
        keyword arguments. Azure Schema Registry guarantees that ID is unique within a namespace.

        2) To get a specific version of a schema within the specified schema group, pass in the required
        keyword arguments `group_name`, `name`, and `version` and any optional keyword arguments.

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
            http_response, schema_properties = self._generated_client.get_schema_by_id(  # type: ignore
                id=schema_id,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types in response are supported
                    "Accept": """application/json; serialization=Avro, application/json; \
                        serialization=json, text/plain; charset=utf-8"""
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
            http_response, schema_properties = self._generated_client.get_schema_by_version(  # type: ignore
                group_name=group_name,
                name=name,
                schema_version=version,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types in response are supported
                    "Accept": """application/json; serialization=Avro, application/json; \
                        serialization=json, text/plain; charset=utf-8"""
                },
                stream=True,
                **http_request_kwargs,
            )
        http_response.read()
        return Schema(
            definition=http_response.text(),
            properties=SchemaProperties(**schema_properties),
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
        schema_properties: Dict[
            str, Union[int, str]
        ] = self._generated_client.get_schema_id_by_content(  # type: ignore
            group_name=group_name,
            name=name,
            schema_content=cast(IO[Any], definition),
            content_type=kwargs.pop("content_type", get_content_type(format)),
            cls=partial(prepare_schema_properties_result, format),
            **http_request_kwargs,
        )
        return SchemaProperties(**schema_properties)


class SchemaProperties(object):
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
        self.id = kwargs.pop("id")
        self.format = kwargs.pop("format")
        self.group_name = kwargs.pop("group_name")
        self.name = kwargs.pop("name")
        self.version = kwargs.pop("version")

    def __repr__(self):
        return (
            f"SchemaProperties(id={self.id}, format={self.format}, "
            f"group_name={self.group_name}, name={self.name}, version={self.version})"[
                :1024
            ]
        )


class Schema(object):
    """
    The schema content of a schema, along with id and meta properties.

    :ivar definition: The content of the schema.
    :vartype definition: str
    :ivar properties: The properties of the schema.
    :vartype properties: SchemaProperties
    """

    def __init__(self, **kwargs: Any) -> None:
        self.definition = kwargs.pop("definition")
        self.properties = kwargs.pop("properties")

    def __repr__(self):
        return f"Schema(definition={self.definition}, properties={self.properties})"[
            :1024
        ]


class SchemaFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Represents the format of the schema to be stored by the Schema Registry service.
    """

    AVRO = "Avro"
    """Represents the Apache Avro schema format."""

    JSON = "Json"
    """Represents the JSON schema format."""

    CUSTOM = "Custom"
    """Represents a custom schema format."""


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Represents the Schema Registry API version to use for requests.
    """

    V2021_10 = "2021-10"
    V2022_10 = "2022-10"
    """This is the default version."""


DEFAULT_VERSION = ApiVersion.V2022_10


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


class MessageType(Protocol):
    """Message Types that set and get content and content type values internally."""

    @classmethod
    def from_message_content(
        cls, content: bytes, content_type: str, **kwargs: Any
    ) -> "MessageType":
        """Creates an object that is a subtype of MessageType, given content type and
         a content value to be set on the object.

        :param bytes content: The content value to be set as the body of the message.
        :param str content_type: The content type to be set on the message.
        :rtype: ~azure.schemaregistry.MessageType
        :returns: The MessageType object with encoded content and content type.
        """

    def __message_content__(self) -> MessageContent:
        """A MessageContent object, with `content` and `content_type` set to
         the values of their respective properties on the MessageType object.

        :rtype: ~azure.schemaregistry.MessageContent
        :returns: TypedDict of the content and content type from the MessageType object.
        """


class SchemaEncoder(Protocol):
    """
    Provides the ability to encode and decode content according to a provided schema or schema ID
     corresponding to a schema in a Schema Registry group.
    """

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        schema_id: None = None,
        message_type: Type[MessageType],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageType:
        """Encodes content after validating against the pre-registered schema. Encoded content and content
         type will be passed to the provided MessageType callback to create message object.

        If `message_type` is set, then additional keyword arguments for building MessageType will be passed to the
         MessageType.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: Required. The pre-registered schema used to validate the content. `schema_id`
         must not be passed.
        :paramtype schema: str
        :keyword schema_id: None.
        :paramtype schema_id: None
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.MessageType protocol.
        :paramtype message_type: type[MessageType]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The MessageType object with encoded content and content type.
        :rtype: MessageType
        """

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        schema: None = None,
        message_type: Type[MessageType],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageType:
        """Encodes content after validating against the pre-registered schema corresponding to
         the provided schema ID. Encoded content and content type will be passed to the provided
         MessageType callback to create message object.

        If `message_type` is set, then additional keyword arguments for building MessageType will be passed to the
         MessageType.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: None.
        :paramtype schema: None
        :keyword schema_id: Required. The schema ID corresponding to the pre-registered schema to be used
         for validation. `schema` must not be passed.
        :paramtype schema_id: str
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.MessageType protocol.
        :paramtype message_type: type[MessageType]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The MessageType object with encoded content and content type.
        :rtype: MessageType
        """

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        schema_id: None = None,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageContent:
        """Encodes content after validating against the pre-registered schema. The following dict will be returned:
         {"content": encoded value, "content_type": schema format mime type string + schema ID}.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: Required. The pre-registered schema used to validate the content. `schema_id`
         must not be passed.
        :paramtype schema: str
        :keyword schema_id: None.
        :paramtype schema_id: None
        :keyword message_type: None.
        :paramtype message_type: None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type.
        :rtype: MessageContent
        """

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        schema: None = None,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageContent:
        """Encodes content after validating against the pre-registered schema corresponding to
         the provided schema ID. The following dict will be returned:
         {"content": encoded value, "content_type": schema format mime type string + schema ID}.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: None.
        :paramtype schema: None
        :keyword schema_id: Required. The schema ID corresponding to the pre-registered schema to be used
         for validation. `schema` must not be passed.
        :paramtype schema_id: str
        :keyword message_type: None.
        :paramtype message_type: None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type.
        :rtype: MessageContent
        """

    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[str] = None,
        schema_id: Optional[str] = None,
        message_type: Optional[Type["MessageType"]] = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union["MessageType", "MessageContent"]:
        """Encodes content after validating against the provided pre-registered schema or the one corresponding to
         the provided schema ID. If provided with a MessageType subtype, encoded content and content type will be
         passed to create the message object. If not provided, the following dict will be returned:
         {"content": encoded value, "content_type": schema format mime type string + schema ID}.

        If `message_type` is set, then additional keyword arguments for building MessageType will be passed to the
         MessageType.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: The pre-registered schema used to validate the content. Exactly one of
         `schema` or `schema_id` must be passed.
        :paramtype schema: str or None
        :keyword schema_id: The schema ID corresponding to the pre-registered schema to be used
         for validation. Exactly one of `schema` or `schema_id` must be passed.
        :paramtype schema_id: str or None
        :keyword message_type: The message class to construct the message. If passed, must be a subtype of the
         azure.schemaregistry.MessageType protocol.
        :paramtype message_type: type[MessageType] or None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type if `message_type` is not set, otherwise the
         constructed message object.
        :rtype: MessageType or MessageContent
        """

    def decode(
        self,  # pylint: disable=unused-argument
        message: Union["MessageType", "MessageContent"],
        *,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Returns the decoded data with the schema format specified by the `content-type` property.
         If `validate` callable was passed to constructor, will validate content against schema retrieved
         from the registry after decoding.
        :param message: The message object which holds the content to be decoded and content type
         containing the schema ID.
        :type message: MessageType or MessageContent
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The decoded content.
        :rtype: dict[str, any]
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
    "ApiVersion",
    "DEFAULT_VERSION",
    "SchemaEncoder",
    "SchemaContentValidate",
    "MessageContent",
    "MessageType",
]  # Add all objects you want publicly available to users at this package level
