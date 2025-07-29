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
from __future__ import annotations
import json
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    overload,
    Type,
    Union,
    cast,
)
from ...._patch import SchemaFormat

from .._utils import (
    create_message_content,
    parse_message,
    decode_content,
    get_loaded_schema,
    get_jsonschema_validator,
    InboundMessageContent,
    OutboundMessageContent,
)
from ._async_lru import alru_cache

if TYPE_CHECKING:
    import azure.schemaregistry.aio
    from ...._patch import MessageContent, SchemaContentValidate

_LOGGER = logging.getLogger(__name__)


class JsonSchemaEncoder(object):
    """
    JsonSchemaEncoder provides the ability to encode and decode content according to the given JSON schema.
     It will check the registry for the pre-registered schema and cache the schema locally.

    :keyword client: Required. The schema registry client which is used to retrieve schema from the service.
     and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.aio.SchemaRegistryClient
    :keyword validate: Required. Used for validation in encode and decode.
     If a JSON Schema meta-schema `$schema` string is provided, for example
     `"https://json-schema.org/draft/2020-12/schema"`, the corresponding validator from `jsonschema` will be used.
     In this case, `jsonschema` must be installed with `jsonencoder` extras:
     `pip install azure-schemaregistry[jsonencoder]`. For a list of supported `jsonschema` validators,
     please refer to the `jsonschema` documentation:
     https://python-jsonschema.readthedocs.io/en/stable/api/jsonschema/validators/index.html
     If a callable is provided, the schema and content will be passed in for validation.
    :paramtype validate: str or ~azure.schemaregistry.SchemaContentValidate
    :keyword Optional[str] group_name: Schema group under which schema should be registered.
     Required if `schema`, not `schema_id`, is provided to `encode`.
    """

    def __init__(
        self,
        *,
        client: "azure.schemaregistry.aio.SchemaRegistryClient",
        validate: Union[str, "SchemaContentValidate"],
        group_name: Optional[str] = None,
    ) -> None:
        self._schema_registry_client = client
        if isinstance(validate, str):
            self._validate = get_jsonschema_validator(validate)
        else:
            self._validate = validate
        self._schema_group = group_name

    async def __aenter__(self) -> "JsonSchemaEncoder":
        await self._schema_registry_client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._schema_registry_client.__aexit__(*exc_details)

    async def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._schema_registry_client.close()

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema_id(self, schema_name: str, schema_str: str, **kwargs: Any) -> str:
        """
        Get schema id from local cache with the given schema.
        If there is no item in the local cache, get schema id from the service and cache it.

        :param schema_name: Name of the schema
        :type schema_name: str
        :param str schema_str: Schema string
        :return: Schema Id
        :rtype: str
        """
        schema_properties = await self._schema_registry_client.get_schema_properties(
            cast(str, self._schema_group),
            schema_name,
            schema_str,
            SchemaFormat.JSON.value,
            **kwargs,
        )
        return schema_properties.id

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema(self, schema_id: str, **kwargs: Any) -> str:
        """
        Get schema definition from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema definition
        :rtype: str
        """
        schema = await self._schema_registry_client.get_schema(schema_id, **kwargs)
        return schema.definition

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        message_type: Type[OutboundMessageContent],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> OutboundMessageContent:
        """Encodes content after validating against the pre-registered JSON schema. Encoded content and content
         type will be passed to the provided OutboundMessageContent class to create message object.

        If `message_type` is set, then additional keyword arguments for building OutboundMessageContent will
         be passed to the OutboundMessageContent.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: Required. The pre-registered schema used to validate the content. `schema_id`
         must not be passed.
        :paramtype schema: str
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.OutboundMessageContent protocol.
        :paramtype message_type: type[OutboundMessageContent]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The OutboundMessageContent object with encoded content and content type.
        :rtype: OutboundMessageContent
        :raises: ~azure.schemaregistry.encoder.InvalidContentError if there is an issue with encoding content
         or validating it against the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        message_type: Type[OutboundMessageContent],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> OutboundMessageContent:
        """Encodes content after validating against the pre-registered JSON schema corresponding to
         the provided schema ID. Encoded content and content type will be passed to the provided
         OutboundMessageContent class to create message object.

        If `message_type` is set, then additional keyword arguments for building OutboundMessageContent
         will be passed to the OutboundMessageContent.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema_id: Required. The schema ID corresponding to the pre-registered schema to be used
         for validation. `schema` must not be passed.
        :paramtype schema_id: str
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.OutboundMessageContent protocol.
        :paramtype message_type: type[OutboundMessageContent]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The OutboundMessageContent object with encoded content and content type.
        :rtype: OutboundMessageContent
        :raises: ~azure.schemaregistry.encoder.InvalidContentError if there is an issue with encoding content
         or validating it against the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageContent":
        """Encodes content after validating against the pre-registered schema. The following dict will be returned:
         {"content": JSON encoded value, "content_type": JSON mime type string + schema ID}.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: Required. The pre-registered schema used to validate the content. `schema_id`
         must not be passed.
        :paramtype schema: str
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type.
        :rtype: MessageContent
        :raises: ~azure.schemaregistry.encoder.InvalidContentError if there is an issue with encoding content
         or validating it against the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema_id: str,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> "MessageContent":
        """Encodes content after validating against the pre-registered schema corresponding to
         the provided schema ID. The following dict will be returned:
         {"content": JSON encoded value, "content_type": JSON mime type string + schema ID}.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema_id: Required. The schema ID corresponding to the pre-registered schema to be used
         for validation. `schema` must not be passed.
        :paramtype schema_id: str
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type.
        :rtype: MessageContent
        :raises: ~azure.schemaregistry.encoder.InvalidContentError if there is an issue with encoding content
         or validating it against the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """

    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[str] = None,
        schema_id: Optional[str] = None,
        message_type: Optional[Type[OutboundMessageContent]] = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[OutboundMessageContent, "MessageContent"]:
        """Encodes content after validating against the provided pre-registered schema or the one corresponding to
         the provided schema ID. If provided with a OutboundMessageContent subtype, encoded content and content type
         will be passed to create message object. If not provided, the following dict will be returned:
         {"content": JSON encoded value, "content_type": JSON mime type string + schema ID}.

        If `message_type` is set, then additional keyword arguments for building OutboundMessageContent will be passed
         to the OutboundMessageContent.from_message_content() method.

        :param content: The content to be encoded.
        :type content: mapping[str, any]
        :keyword schema: The pre-registered schema used to validate the content. Exactly one of
         `schema` or `schema_id` must be passed.
        :paramtype schema: str or None
        :keyword schema_id: The schema ID corresponding to the pre-registered schema to be used
         for validation. Exactly one of `schema` or `schema_id` must be passed.
        :paramtype schema_id: str or None
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.encoder.OutboundMessageContent protocol.
        :keyword message_type: The message class to construct the message. If passed, must be a subtype of the
         azure.schemaregistry.OutboundMessageContent protocol.
        :paramtype message_type: type[OutboundMessageContent] or None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: TypedDict of encoded content and content type if `message_type` is not set, otherwise the
         constructed message object.
        :rtype: OutboundMessageContent or MessageContent
        :raises: ~azure.schemaregistry.encoder.InvalidContentError if there is an issue with encoding content
         or validating it against the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """
        request_options = request_options or {}

        # If schema_id, get schema for validation. If schema, get schema_id for content type.
        if schema_id and not schema:
            cache_misses = self._get_schema.cache_info().misses
            schema_str = await self._get_schema(schema_id, **request_options)
            new_cache_misses = self._get_schema.cache_info().misses
            if new_cache_misses > cache_misses:
                cache_info = self._get_schema.cache_info()
                _LOGGER.info(
                    "New entry has been added to schema cache. Cache info: %s",
                    str(cache_info),
                )
            schema_dict = json.loads(schema_str)
        elif schema and not schema_id:
            if not self._schema_group:
                raise TypeError("'group_name' is required in constructor, if 'schema' is passed to encode.")

            schema_fullname, schema_str, schema_dict = get_loaded_schema(schema, content)
            cache_misses = self._get_schema_id.cache_info().misses
            schema_id = await self._get_schema_id(schema_fullname, schema_str, **request_options)
            new_cache_misses = self._get_schema_id.cache_info().misses
            if new_cache_misses > cache_misses:
                cache_info = self._get_schema_id.cache_info()
                _LOGGER.info(
                    "New entry has been added to schema ID cache. Cache info: %s",
                    str(cache_info),
                )
        else:
            raise TypeError("Exactly one of 'schema' or 'schema_id' is required.")

        return create_message_content(
            content=content,
            schema=schema_dict,
            schema_id=cast(str, schema_id),
            validate=self._validate,
            message_type=message_type,
            **kwargs,
        )

    async def decode(
        self,
        message: Union["MessageContent", InboundMessageContent],
        *,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Decode bytes content using schema ID in the content type field.

        :param message: The message object which holds the content to be decoded and content type
         containing the schema ID.
        :type message: InboundMessageContent or MessageContent
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :returns: The decoded content.
        :rtype: dict[str, any]
        :raises: ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError if there is
         an issue with decoding content or validating it with the schema.
        :raises: ~azure.core.exceptions.HttpResponseError if there is an issue with the request to get the schema
         from the registry.
        """
        schema_id, content = parse_message(message)
        cache_misses = self._get_schema.cache_info().misses
        request_options = request_options or {}
        schema_definition = await self._get_schema(schema_id, **request_options)
        new_cache_misses = self._get_schema.cache_info().misses
        if new_cache_misses > cache_misses:
            cache_info = self._get_schema.cache_info()
            _LOGGER.info(
                "New entry has been added to schema cache. Cache info: %s",
                str(cache_info),
            )

        return decode_content(
            content=content,
            schema_id=schema_id,
            schema_definition=schema_definition,
            validate=self._validate,
            **kwargs,
        )
