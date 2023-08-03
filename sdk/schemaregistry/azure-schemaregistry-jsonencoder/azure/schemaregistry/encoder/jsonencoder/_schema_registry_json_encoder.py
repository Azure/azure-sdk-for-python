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
import logging
import json
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    Type,
    overload,
    Union,
    Callable,
)
from typing_extensions import Literal
from azure.schemaregistry import SchemaFormat

from ._utils import (  # pylint: disable=import-error
    create_message_content,
    parse_message,
    decode_content,
    get_loaded_schema,
    MessageType,
)

from ._message_protocol import (  # pylint: disable=import-error
    MessageContent,
)
from ._exceptions import (  # pylint: disable=import-error
    InvalidContentError,
)

if TYPE_CHECKING:
    from azure.schemaregistry import SchemaRegistryClient

_LOGGER = logging.getLogger(__name__)


class JsonSchemaEncoder(object):
    """
    JsonSchemaEncoder provides the ability to encode and decode content according
    to the given JSON schema. It would automatically register, get, and cache the schema.

    :keyword client: Required. The schema registry client which is used to register schema
     and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.SchemaRegistryClient
    :keyword Optional[str] group_name: Required for encoding. Not used when decoding.
     Schema group under which schema should be registered.
    :keyword bool auto_register: When true, registers new schemas passed to encode.
     Otherwise, and by default, encode will fail if the schema has not been pre-registered in the registry.
    :keyword schema: The schema used to validate the content. Exactly one of `schema` or `schema_id`
     must be passed. If a string is passed in, it must have been pre-registered.
     If a callable is passed in, it must have the following method signature:
     `(content: Mapping[str, Any]) -> Mapping[str, Any]`.
     If an error is raised during generation, an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError
     will be wrapped around it and raised.
    :paramtype schema: str or Callable or None
    :keyword schema_id: The schema ID corresponding to the pre-registered schema to be used for validation. Required if
     `schema` was not passed in. Else, must be None.
    :paramtype schema_id: str or None
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
        validate: Union[Callable[[Mapping[str, Any], Mapping[str, Any]], None], Literal[False]] = False,
    ) -> None:
        self._schema_registry_client = client
        self._validate = validate
        self._schema_group = group_name
        self._auto_register_schema_func = self._schema_registry_client.get_schema_properties

    def __enter__(self) -> "JsonSchemaEncoder":
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._schema_registry_client.__exit__(*exc_details)

    def close(self) -> None:
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._schema_registry_client.close()

    @lru_cache(maxsize=128)
    def _get_schema_id(self, schema_name: str, schema_str: str, **kwargs: Any) -> str:
        """
        Get schema id from local cache with the given schema.
        If there is no item in the local cache, get schema id from the service and cache it.

        :param schema_name: Name of the schema
        :type schema_name: str
        :param str schema_str: Schema string
        :return: Schema Id
        :rtype: str
        """
        schema_id = self._auto_register_schema_func(
            self._schema_group, schema_name, schema_str, SchemaFormat.JSON.value, **kwargs
        ).id
        return schema_id

    @lru_cache(maxsize=128)
    def _get_schema(self, schema_id: str, **kwargs: Any) -> str:
        """
        Get schema content from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema content
        :rtype: str
        """
        schema_str = self._schema_registry_client.get_schema(
            schema_id, **kwargs
        ).definition
        return schema_str

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        schema_id: None = None,
        message_type: Type[MessageType],
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageType:
        ...

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
        ...

    @overload
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        schema_id: None = None,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageContent:
        ...

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
        ...

    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[Union[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]]] = None,
        schema_id: Optional[str] = None,
        message_type: Optional[Type[MessageType]] = None,
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
        :keyword schema: The schema used to encode the content. If None, then `schema` must have been specified
         in the constructor. If passed in, it will override the `schema` value specified in the constructor.
         If a callable is passed in, it must have the following method signature:
         `(content: Mapping[str, Any]) -> Mapping[str, Any]`. Schema must include `title` field as the schema name.
         If an error is raised during generation, an ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError
         will be wrapped around it and raised.
        :paramtype schema: str or Callable or None
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.encoder.jsonencoder.MessageType protocol.
        :paramtype message_type: Type[MessageType] or None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: Dict[str, Any]
        :rtype: MessageType or MessageContent
        :raises ~azure.schemaregistry.encoder.jsonencoder.InvalidContentError:
            Indicates an issue with encoding content with schema or generating the schema if a callable was passed.
        """
        request_options = request_options or {}

        # If schema_id, get schema for validation. If schema, get schema_id for content type.
        if schema_id and not schema:
            cache_misses = (
                self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter
            )
            schema_str = self._get_schema(schema_id, **request_options)
            new_cache_misses = (
                self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter
            )
            if new_cache_misses > cache_misses:
                cache_info = (
                    self._get_schema.cache_info()  # pylint: disable=no-value-for-parameter
                )
                _LOGGER.info(
                    "New entry has been added to schema cache. Cache info: %s",
                    str(cache_info),
                )
            schema_dict = json.loads(schema_str)
        elif schema and not schema_id:
            if not self._schema_group:
                raise TypeError("'group_name' is required in constructor, if 'schema' is passed to encode.")

            schema_fullname, schema_str, schema_dict = get_loaded_schema(self, schema, content)
            cache_misses = (
                self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter
            )
            schema_id = self._get_schema_id(
                schema_fullname, schema_str, **request_options
            )
            new_cache_misses = (
                self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter
            )
            if new_cache_misses > cache_misses:
                cache_info = (
                    self._get_schema_id.cache_info()  # pylint: disable=no-value-for-parameter
                )
                _LOGGER.info(
                    "New entry has been added to schema ID cache. Cache info: %s",
                    str(cache_info),
                )
        else:
            raise TypeError("Exactly one of 'schema' or 'schema_id' is required.")

        return create_message_content(
            content=content,
            schema=schema_dict,
            schema_id=schema_id,
            message_type=message_type,
            validate=self._validate,
            **kwargs,
        )

    def decode(
        self,  # pylint: disable=unused-argument
        message: Union[MessageContent, MessageType],
        *,
        request_options: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Decode bytes content using schema ID in the content type field. `message` must be one of the following:
            1) An object of subtype of the MessageType protocol.
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
            self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter
        )
        request_options = request_options or {}
        schema_definition = self._get_schema(schema_id, **request_options)
        new_cache_misses = (
            self._get_schema.cache_info().misses  # pylint: disable=no-value-for-parameter
        )
        if new_cache_misses > cache_misses:
            cache_info = (
                self._get_schema.cache_info()  # pylint: disable=no-value-for-parameter
            )
            _LOGGER.info(
                "New entry has been added to schema cache. Cache info: %s",
                str(cache_info),
            )

        return decode_content(
            content=content,
            schema_id=schema_id,
            schema_definition=schema_definition,
            validate=self._validate,
            **kwargs
        )
