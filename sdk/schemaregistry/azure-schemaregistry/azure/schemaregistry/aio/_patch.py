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
    Mapping,
    Optional,
    Type,
)
from functools import partial
from typing_extensions import Protocol  # type: ignore


from azure.core.tracing.decorator_async import distributed_trace_async

from .._patch import (
    get_http_request_kwargs,
    get_case_insensitive_format,
    get_content_type,
    SchemaFormat,
    DEFAULT_VERSION,
    Schema,
    SchemaProperties,
    prepare_schema_result,
    prepare_schema_properties_result,
)
from ._client import SchemaRegistryClient as ServiceClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.rest import AsyncHttpResponse
    from .._patch import MessageType, MessageContent


###### Wrapper Class ######


class SchemaRegistryClient(object):
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
        if "https://" not in fully_qualified_namespace:
            fully_qualified_namespace = f"https://{fully_qualified_namespace}"
        api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._generated_client = ServiceClientGenerated(
            endpoint=fully_qualified_namespace,
            credential=credential,
            api_version=api_version,
            **kwargs,
        )

    async def __aenter__(self):
        await self._generated_client.__aenter__()
        return self

    async def __aexit__(self, *args):
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
         For now Avro is the only supported schema format by the service.
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
        schema_properties: Dict[
            str, Union[int, str]
        ] = await self._generated_client.register_schema(
            group_name=group_name,
            name=name,
            content=cast(IO[Any], definition),
            content_type=kwargs.pop("content_type", get_content_type(format)),
            cls=partial(prepare_schema_properties_result, format),
            headers={  # TODO: fix - currently `Accept: "*/*""`
                "Accept": "application/json"
            },
            **http_request_kwargs,
        )

        return SchemaProperties(**schema_properties)

    @overload
    async def get_schema(self, schema_id: str, **kwargs: Any) -> Schema:
        ...

    @overload
    async def get_schema(
        self, *, group_name: str, name: str, version: int, **kwargs: Any
    ) -> Schema:
        ...

    @distributed_trace_async
    async def get_schema(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword
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
            http_response, schema_properties = await self._generated_client.get_schema_by_id(  # type: ignore
                id=schema_id,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types are supported
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
            http_response, schema_properties = await self._generated_client.get_schema_by_version(  # type: ignore
                group_name=group_name,
                name=name,
                schema_version=version,
                cls=prepare_schema_result,
                headers={  # TODO: remove when multiple content types are supported
                    "Accept": """application/json; serialization=Avro, application/json; \
                        serialization=json, text/plain; charset=utf-8"""
                },
                stream=True,
                **http_request_kwargs,
            )

        await http_response.read()
        return Schema(
            definition=http_response.text(),
            properties=SchemaProperties(**schema_properties),
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
        schema_properties: Dict[
            str, Union[int, str]
        ] = await self._generated_client.get_schema_id_by_content(  # type: ignore
            group_name=group_name,
            name=name,
            schema_content=cast(IO[Any], definition),
            content_type=kwargs.pop("content_type", get_content_type(format)),
            cls=partial(prepare_schema_properties_result, format),
            headers={  # TODO: fix - currently `Accept: "*/*""`
                "Accept": "application/json"
            },
            **http_request_kwargs,
        )
        return SchemaProperties(**schema_properties)


###### Encoder Protocols ######


class SchemaEncoder(Protocol):
    """
    Provides the ability to encode and decode content according to a provided schema or schema ID
     corresponding to a schema in a Schema Registry group.
    """

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        schema_id: None = None,
        message_type: Type["MessageType"],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageType":
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
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        schema: None = None,
        message_type: Type["MessageType"],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageType":
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
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        schema_id: None = None,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageContent":
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
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        schema: None = None,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageContent":
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

    async def encode(
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

    async def decode(
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
    "SchemaEncoder",
]  # Add all objects you want publicly available to users at this package level
