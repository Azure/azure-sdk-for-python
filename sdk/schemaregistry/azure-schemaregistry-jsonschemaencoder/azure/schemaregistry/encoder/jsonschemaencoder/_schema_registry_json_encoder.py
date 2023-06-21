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
from typing import Callable
import logging
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
)
import json

from ._utils import (  # pylint: disable=import-error
    create_message_content,
    parse_message,
    decode_content,
    MessageType,
)

from ._message_protocol import (  # pylint: disable=import-error
    MessageContent,
)
from ._exceptions import (  # pylint: disable=import-error
    InvalidSchemaError,
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
    :keyword validate: Callable that validates the given content against the given schema. Must validate against
     schema draft version supported by the Schema Registry service. It must have the following method signature:
     `(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None`.
     If valid, then method must return None. If invalid, method must raise an error which will be wrapped
     and raised as an ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidContentError.
    :paramtype validate: Callable or None
    :keyword generate_schema: Callable that generates a schema from the given content. It must have
     the following method signature: `(content: Mapping[str, Any]) -> Mapping[str, Any]`.
     If an error is raised during generation, an ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidContentError
     will be wrapped around it and raised.
    :paramtype generate_schema: Callable or None

    """

    def __init__(
        self,
        *,
        client: "SchemaRegistryClient",
        group_name: Optional[str] = None,
        auto_register: bool = False,
        validate: Optional[Callable[[Mapping[str, Any], Mapping[str, Any]], None]] = None,
        generate_schema: Optional[Callable[[Mapping[str, Any]], Mapping[str, Any]]] = None,
    ) -> None:
        self._schema_registry_client = client
        self._validate = validate
        self._generate_schema = generate_schema
        self._schema_group = group_name
        self._auto_register = auto_register
        self._auto_register_schema_func = (
            self._schema_registry_client.register_schema
            if self._auto_register
            else self._schema_registry_client.get_schema_properties
        )

    def __enter__(self):
        # type: () -> JsonSchemaEncoder
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details: Any):
        # type: (Any) -> None
        self._schema_registry_client.__exit__(*exc_details)

    def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        self._schema_registry_client.close()

    @lru_cache(maxsize=128)
    def _get_schema_id(self, schema_name, schema_str, **kwargs):
        # type: (str, str, Any) -> str
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
            self._schema_group, schema_name, schema_str, "Json", **kwargs
        ).id
        return schema_id

    @lru_cache(maxsize=128)
    def _get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> str
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
        schema: str,
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
        schema: str,
        message_type: None = None,
        request_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MessageContent:
        ...

    # TODO: do we want schema type to be str or Mapping?
    def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: Optional[str] = None,
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
        :keyword schema: The schema used to encode the content. Required if `generate_schema` was not passed in during
         JsonSchemaEncoder construction or `schema_id` was not passed in.
        :paramtype schema: str or None
        :keyword schema_id: The schema ID to a registered schema to be used. Required if `generate_schema` was not
         passed in during JsonSchemaEncoder construction or `schema` was not passed in.
        :paramtype schema_id: str or None
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.encoder.jsonschemaencoder.MessageType protocol.
        :paramtype message_type: Type[MessageType] or None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: Dict[str, Any]
        :rtype: MessageType or MessageContent
        :raises ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidSchemaError:
            Indicates an issue with validating schema.
        :raises ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidContentError:
            Indicates an issue with encoding content with schema.
        """

        if not self._schema_group:
            raise TypeError("'group_name' in constructor cannot be None, if encoding.")
        if not schema and not self._generate_schema and not schema_id:
            raise TypeError("""One of 'schema' or 'schema_id' is """
                            """required if 'generate_schema' callable was not passed to constructor.""")

        if schema:
            schema_dict = json.loads(schema)
        elif schema_id:
            # TODO: get schema from schema id
            pass
        else:
            try:
                schema_dict = self._generate_schema(content)
            except Exception as exc:
                raise InvalidSchemaError(
                    f"Cannot generate schema with callable given the following content: {content}"
                ) from exc

        try:
            schema_fullname = schema_dict['$id'] # TODO: should this be 'title'?
        except KeyError:
            raise ValueError("Schema must have '$id' property.")

        cache_misses = (
            self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter
        )
        request_options = request_options or {}
        schema_id = self._get_schema_id(
            schema_fullname, schema, **request_options
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
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: Dict[str, Any]
        :rtype: Dict[str, Any]
        :raises ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidSchemaError:
            Indicates an issue with validating schemas.
        :raises ~azure.schemaregistry.encoder.jsonschemaencoder.InvalidContentError:
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
