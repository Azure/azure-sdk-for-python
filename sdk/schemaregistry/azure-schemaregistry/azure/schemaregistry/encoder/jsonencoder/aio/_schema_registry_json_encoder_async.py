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
    TYPE_CHECKING, Any, Dict, Mapping, Optional, overload, Type, Union, Callable
)
from typing_extensions import Literal
from .._utils import (  # pylint: disable=import-error
    create_message_content,
    parse_message,
    decode_content,
    MessageType,
)
from .._exceptions import (  # pylint: disable=import-error
    InvalidSchemaError,
)
from ._async_lru import alru_cache  # pylint: disable=import-error
from .._message_protocol import (
    MessageContent,
)  # pylint: disable=import-error

if TYPE_CHECKING:
    from azure.schemaregistry.aio import SchemaRegistryClient

_LOGGER = logging.getLogger(__name__)


class JsonSchemaEncoder(object):
    """
    JsonSchemaEncoder provides the ability to encode and decode content according
    to the given json schema. It would automatically register, get, and cache the schema.

    :keyword client: Required. The schema registry client which is used to register schema
     and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.aio.SchemaRegistryClient
    :keyword Optional[str] group_name: Required for encoding. Not used when decoding.
     Schema group under which schema should be registered.
    :keyword schema: The schema used to encode the content by default. The `schema` argument passed into the `encode`
     method will override this value. If None, then `schema` must be passed into `encode`.
     If a callable is passed in, it must have the following method signature:
     `(content: Mapping[str, Any]) -> Mapping[str, Any]`.
     If an error is raised during generation, an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError
     will be wrapped around it and raised.
    :paramtype schema: str or bytes or Callable or None
    :keyword validate: Callable that validates the given content against the given schema. Must validate against
     schema draft version supported by the Schema Registry service. It must have the following method signature:
     `(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None`.
     If valid, then method must return None. If invalid, method must raise an error which will be wrapped
     and raised as an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError. When False is passed in,
     and by default, validation will be turned off.
    :paramtype validate: Callable or False

    """

    def __init__(
        self,
        *,
        client: "SchemaRegistryClient",
        group_name: Optional[str] = None,
        schema: Optional[Union[str, bytes, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        validate: Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]] = False,
    ):
        self._schema_registry_client = client
        self._validate = validate
        self._schema = schema
        self._schema_group = group_name
        self._schema_id_client_op = self._schema_registry_client.get_schema_properties

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
        schema_properties = await self._auto_register_schema_func(
            self._schema_group, schema_name, schema_str, "Json", **kwargs
        )
        return schema_properties.id

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema(self, schema_id: str, **kwargs: Any) -> str:
        """
        Get schema definition from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema definition
        """
        schema = await self._schema_registry_client.get_schema(schema_id, **kwargs)
        return schema.definition

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, bytes, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        message_type: Type[MessageType],
        validate: Optional[Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]]] = False,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageType:
        ...

    @overload
    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, bytes, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        message_type: None = None,
        validate: Optional[Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]]] = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageContent:
        ...

    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, bytes, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        message_type: Optional[Type[MessageType]] = None,
        validate: Optional[Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]]] = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[MessageType, MessageContent]:

        """Encode content after validating against the given schema. Create content type value,
         which consists of the JSON Mime Type string and the schema ID corresponding to given schema.
         If provided with a MessageType subtype, encoded content and content type will be passed to
         create message object. If not provided, the following dict will be returned:
         {"content": JSON encoded value, "content_type": JSON mime type string + schema ID}.

        If `message_type` is set, then additional keyword arguments will be passed to the message callback
         function provided.

        Schema must be a Draft 4 JSON Schema:
        https://json-schema.org/specification-links.html#draft-4

        :param content: The content to be encoded.
        :type content: Mapping[str, Any]
        :keyword schema: The schema used to encode the content. If None, then `schema` must have been specified in
         the constructor. If passed in, it will override the `schema` value specified in the constructor.
         If a callable is passed in, it must have the following method signature:
         `(content: Mapping[str, Any]) -> Mapping[str, Any]`.
         If an error is raised during generation, an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError
         will be wrapped around it and raised.
        :paramtype schema: str or bytes or Callable or None
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.encoder.jsonencoder.MessageType protocol.
        :paramtype message_type: Type[MessageType] or None
        :keyword validate: Callable that validates the given content against the given schema. Must validate against
         schema draft version supported by the Schema Registry service. It must have the following method signature:
         `(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None`.
         If valid, then method must return None. If invalid, method must raise an error which will be wrapped
         and raised as an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError. When False is passed in,
         validation will be turned off. If None, and by default, `schema` set in constructor will be used.
        :paramtype validate: Callable or False
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: Dict[str, Any]
        :rtype: MessageType or MessageContent
        :raises ~azure.schemaregistry.encoder.jsonencoder.InvalidSchemaError:
            Indicates an issue with validating schema.
        :raises ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError:
            Indicates an issue with encoding content with schema.
        """

        if not self._schema_group:
            raise TypeError("'group_name' in constructor cannot be None when encoding.")

        # if schema not passed in, get default schema
        schema = schema or self._schema
        if not schema:
            raise TypeError("'schema' is required if 'schema' was not passed to constructor.")
        try:
            # str or bytes
            schema_dict = json.loads(schema)
            if isinstance(schema, bytes):
                schema_str = schema.decode()
            else:
                schema_str = schema
        except TypeError:
            # callable
            try:
                schema_dict = schema(content)
            except Exception as exc:
                raise InvalidSchemaError(
                    f"Cannot generate schema with callable given the following content: {content}"
                ) from exc
            schema_str = json.dumps(schema_dict)

        try:
            schema_fullname = schema_dict['title']
        except KeyError:
            raise ValueError("Schema must have 'title' property.")

        cache_misses = (
            self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        )
        request_options = request_options or {}
        schema_id = await self._get_schema_id(
            schema_fullname, schema_str, **request_options
        )
        new_cache_misses = (
            self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        )
        if new_cache_misses > cache_misses:
            cache_info = (
                self._get_schema_id.cache_info()  # pylint: disable=no-value-for-parameter disable=no-member
            )
            _LOGGER.info(
                "New entry has been added to schema ID cache. Cache info: %s",
                str(cache_info),
            )
        return create_message_content(
            content=content,
            schema=schema_dict,
            schema_id=schema_id,
            message_type=message_type,
            validate=validate if validate is not None else self._validate,
            **kwargs,
        )

    async def decode(
        self,  # pylint: disable=unused-argument
        message: Union[MessageContent, MessageType],
        *,
        validate: Optional[Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]]] = None,
        request_options: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Decode bytes content using schema ID in the content type field. `message` must be one of the following:
            1) A object of subtype of the MessageType protocol.
            2) A dict {"content": ..., "content_type": ...}, where "content" is bytes and "content_type" is string.
        Schema must be a Draft 4 JSON Schema:
        https://json-schema.org/specification-links.html#draft-4

        :param message: The message object which holds the content to be decoded and content type
         containing the schema ID.
        :type message: MessageType or MessageContent
        :keyword validate: Callable that validates the given content against the given schema. Must validate against
         schema draft version supported by the Schema Registry service. It must have the following method signature:
         `(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None`.
         If valid, then method must return None. If invalid, method must raise an error which will be wrapped
         and raised as an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError.  When False is passed in,
         validation will be turned off. If None, and by default, `schema` set in constructor will be used.
        :paramtype validate: Callable or False
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: Dict[str, Any]
        :rtype: Dict[str, Any]
        :raises ~azure.schemaregistry.encoder.jsonencoder.InvalidSchemaError:
            Indicates an issue with validating schemas.
        :raises ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError:
            Indicates an issue with decoding content.
        """

        schema_id, content = parse_message(message)
        cache_misses = (
            self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        )
        request_options = request_options or {}
        schema_definition = await self._get_schema(schema_id, **request_options)
        new_cache_misses = (
            self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        )
        if new_cache_misses > cache_misses:
            cache_info = (
                self._get_schema.cache_info()  # pylint: disable=no-value-for-parameter disable=no-member
            )
            _LOGGER.info(
                "New entry has been added to schema cache. Cache info: %s",
                str(cache_info),
            )

        return decode_content(
            content=content,
            schema_id=schema_id,
            schema_definition=schema_definition,
            validate=validate if validate is not None else self._validate,
            **kwargs
        )
