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
import logging
from io import BytesIO
from typing import Any, Callable, Dict, Mapping, Union, Optional
from ._async_lru import alru_cache
from .._constants import (
    SCHEMA_ID_START_INDEX,
    SCHEMA_ID_LENGTH,
    CONTENT_START_INDEX,
    AVRO_MIME_TYPE,
    RECORD_FORMAT_IDENTIFIER_LENGTH,
)
from .._message_protocol import MessageType, MessageContent
from .._apache_avro_encoder import ApacheAvroObjectEncoder as AvroObjectEncoder
from ..exceptions import (
    SchemaParseError,
    SchemaEncodeError,
    SchemaDecodeError,
)

_LOGGER = logging.getLogger(__name__)

class AvroEncoder(object):
    """
    AvroEncoder provides the ability to encode and decode content according
    to the given avro schema. It would automatically register, get and cache the schema.

    :keyword client: Required. The schema registry client
     which is used to register schema and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.aio.SchemaRegistryClient
    :keyword str group_name: Required. Schema group under which schema should be registered.
    :keyword bool auto_register_schemas: When true, register new schemas passed to encode.
     Otherwise, and by default, encode will fail if the schema has not been pre-registered in the registry.

    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        try:
            self._schema_group = kwargs.pop("group_name")
            self._schema_registry_client = kwargs.pop(
                "client"
            )  # type: "SchemaRegistryClient"
        except KeyError as e:
            raise TypeError("'{}' is a required keyword.".format(e.args[0]))
        self._avro_encoder = AvroObjectEncoder(codec=kwargs.get("codec"))
        self._auto_register_schemas = kwargs.get("auto_register_schemas", False)
        self._auto_register_schema_func = (
            self._schema_registry_client.register_schema
            if self._auto_register_schemas
            else self._schema_registry_client.get_schema_properties
        )

    async def __aenter__(self):
        # type: () -> AvroEncoder
        await self._schema_registry_client.__aenter__()
        return self

    async def __aexit__(self, *exc_details):
        # type: (Any) -> None
        await self._schema_registry_client.__aexit__(*exc_details)

    async def close(self):
        # type: () -> None
        """This method is to close the sockets opened by the client.
        It need not be used when using with a context manager.
        """
        await self._schema_registry_client.close()

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema_id(self, schema_name, schema_str, **kwargs):
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
        schema_properties = await self._auto_register_schema_func(
            self._schema_group, schema_name, schema_str, "Avro", **kwargs
        )
        return schema_properties.id

    @alru_cache(maxsize=128, cache_exceptions=False)
    async def _get_schema(self, schema_id, **kwargs):
        # type: (str, Any) -> str
        """
        Get schema definition from local cache with the given schema id.
        If there is no item in the local cache, get schema from the service and cache it.

        :param str schema_id: Schema id
        :return: Schema definition
        """
        schema = await self._schema_registry_client.get_schema(schema_id, **kwargs)
        return schema.definition

    async def encode(
        self,
        content: Mapping[str, Any],
        *,
        schema: str,
        message_type: Optional[Callable] = None,
        request_kwargs: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Union[MessageType, MessageContent]:

        """
        Encode content with the given schema. Create content type value, which consists of the Avro Mime Type string
         and the schema ID corresponding to given schema. If provided with a message constructor callback,
         pass encoded content and content type to create message object. If not provided, return the following dict:
         {"content": Avro encoded value, "content_type": Avro mime type string + schema ID}.

        If `message_type` is set, then additional keyword arguments will be passed to the message callback
         function provided.

        Schema must be an Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param content: The content to be encoded.
        :type content: Mapping[str, Any]
        :keyword schema: Required. The schema used to encode the content.
        :paramtype schema: str
        :keyword message_type: The callback function or message class to construct the message. If message class,
         it must be a subtype of the azure.schemaregistry.encoder.avroencoder.MessageType protocol.
         If callback function, it must have the following method signature:
         `(content: bytes, content_type: str, **kwargs) -> MessageType`, where `content` and `content_type`
         are positional parameters.
        :paramtype message_type: Callable or None
        :keyword request_kwargs: The keyword arguments for http requests to be passed to the client.
        :paramtype request_kwargs: Dict[str, Any]
        :rtype: MessageType or MessageContent
        :raises ~azure.schemaregistry.encoder.avroencoder.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.encoder.avroencoder.exceptions.SchemaEncodeError:
            Indicates an issue with encoding content for provided schema.
        """

        raw_input_schema = schema

        try:
            schema_fullname = self._avro_encoder.get_schema_fullname(raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaParseError(
                f"Cannot parse schema: {raw_input_schema}", error=e
            ).raise_with_traceback()

        cache_misses = self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        request_kwargs = request_kwargs or {}
        schema_id = await self._get_schema_id(schema_fullname, raw_input_schema, **request_kwargs)
        new_cache_misses = self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter disable=no-member
        if new_cache_misses > cache_misses:
            cache_size = self._get_schema_id.cache_info().currsize  # pylint: disable=no-value-for-parameter disable=no-member
            _LOGGER.info("New entry has been added to schema ID cache. Cache size: %s", str(cache_size))
        content_type = f"{AVRO_MIME_TYPE}+{schema_id}"

        try:
            content_bytes = self._avro_encoder.encode(content, raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaEncodeError(
                "Cannot encode value '{}' for schema: {}".format(
                    content, raw_input_schema
                ),
                error=e,
            ).raise_with_traceback()

        stream = BytesIO()

        stream.write(content_bytes)
        stream.flush()

        payload = stream.getvalue()
        stream.close()
        if message_type:
            try:
                return message_type.from_message_content(payload, content_type, **kwargs)
            except AttributeError:
                try:
                    return message_type(payload, content_type, **kwargs)
                except TypeError as e:
                    SchemaEncodeError(
                        f"""The content model {str(message_type)} is not a Callable that takes `content`
                            and `content_type` or a subtype of the MessageType protocol.
                            If using an Azure SDK model class, please check the README.md for the full list
                            of supported Azure SDK models and their corresponding versions."""
                    ).raise_with_traceback()

        return {"content": payload, "content_type": content_type}

    def _convert_preamble_format(self, content, content_type):  # pylint: disable=no-self-use
        record_format_identifier = b"\0\0\0\0"
        if content[0:RECORD_FORMAT_IDENTIFIER_LENGTH] == record_format_identifier:
            schema_id = content[
                SCHEMA_ID_START_INDEX : (SCHEMA_ID_START_INDEX + SCHEMA_ID_LENGTH)
            ].decode("utf-8")
            content_type = f"{AVRO_MIME_TYPE}+{schema_id}"
            content = content[CONTENT_START_INDEX:]

        return content, content_type

    async def decode(
        self,
        message: Union[MessageType, MessageContent],
        *,
        readers_schema: Optional[str] = None,
        request_kwargs: Dict[str, Any] = None,
        **kwargs,   # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """
        Decode bytes content using schema ID in the content type field. `message` must be one of the following:
            1) A object of subtype of the MessageType protocol.
            2) A dict {"content": ..., "content_type": ...}, where "content" is bytes and "content_type" is string.
            3) If using to decode content that was serialized with the AvroSerializer, a dict
                {"content": ..., "content_type": None}, where "content" is bytes and "content_type" is None.
        Content must follow format of associated Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param message: The message object which holds the content to be decoded and content type
         containing the schema ID.
        :type message: MessageType or MessageContent
        :keyword readers_schema: An optional reader's schema as defined by the Apache Avro specification.
        :paramtype readers_schema: str or None
        :keyword request_kwargs: The keyword arguments for http requests to be passed to the client.
        :paramtype request_kwargs: Dict[str, Any]
        :rtype: Dict[str, Any]
        :raises ~azure.schemaregistry.encoder.avroencoder.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.encoder.avroencoder.exceptions.SchemaDecodeError:
            Indicates an issue with decoding value.
        """

        try:
            message_content_dict = message.__message_content__()
            content = message_content_dict["content"]
            content_type = message_content_dict["content_type"]
        except AttributeError:
            try:
                content = message["content"]
                content_type = message["content_type"]
            except (KeyError, TypeError):
                SchemaDecodeError(
                    f"""The content model {str(message)} is not a subtype of the MessageType protocol or type
                        MessageContent.  If using an Azure SDK model class, please check the README.md
                        for the full list of supported Azure SDK models and their corresponding versions."""
                ).raise_with_traceback()

        # include in first preview for back compatibility
        content, content_type = self._convert_preamble_format(content, content_type)

        schema_id = content_type.split("+")[1]

        cache_misses = self._get_schema.cache_info().misses # pylint: disable=no-value-for-parameter disable=no-member
        request_kwargs = request_kwargs or {}
        schema_definition = await self._get_schema(schema_id, **request_kwargs)
        new_cache_misses = self._get_schema.cache_info().misses # pylint: disable=no-value-for-parameter disable=no-member
        if new_cache_misses > cache_misses:
            cache_size = self._get_schema.cache_info().currsize  # pylint: disable=no-value-for-parameter disable=no-member
            _LOGGER.info("New entry has been added to schema cache. Cache size: %s", str(cache_size))

        try:
            dict_value = self._avro_encoder.decode(content, schema_definition, readers_schema=readers_schema)
        except Exception as e:  # pylint:disable=broad-except
            error_message = (
                f"Cannot decode value '{content}' for schema: {schema_definition}\nand readers schema: {readers_schema}"
                if readers_schema
                else f"Cannot decode value '{content}' for schema: {schema_definition}"
            )
            SchemaDecodeError(
                error_message,
                error=e,
            ).raise_with_traceback()
        return dict_value
