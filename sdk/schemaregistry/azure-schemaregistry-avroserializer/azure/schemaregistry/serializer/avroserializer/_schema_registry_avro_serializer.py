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
from functools import lru_cache
from io import BytesIO
from typing import Any, Dict, Mapping, Optional, Union, Callable

from .exceptions import (
    SchemaParseError,
    SchemaSerializationError,
    SchemaDeserializationError,
)
from ._apache_avro_serializer import ApacheAvroObjectSerializer as AvroObjectSerializer
from ._message_protocol import MessageMetadataDict, MessageType
from ._constants import (
    SCHEMA_ID_START_INDEX,
    SCHEMA_ID_LENGTH,
    DATA_START_INDEX,
    AVRO_MIME_TYPE,
    RECORD_FORMAT_IDENTIFIER_LENGTH,
)

_LOGGER = logging.getLogger(__name__)

class AvroSerializer(object):
    """
    AvroSerializer provides the ability to serialize and deserialize data according
    to the given avro schema. It would automatically register, get and cache the schema.

    :keyword client: Required. The schema registry client
     which is used to register schema and retrieve schema from the service.
    :paramtype client: ~azure.schemaregistry.SchemaRegistryClient
    :keyword str group_name: Required. Schema group under which schema should be registered.
    :keyword bool auto_register_schemas: When true, register new schemas passed to serialize.
     Otherwise, and by default, serialize will fail if the schema has not been pre-registered in the registry.

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
        self._avro_serializer = AvroObjectSerializer(codec=kwargs.get("codec"))
        self._auto_register_schemas = kwargs.get("auto_register_schemas", False)
        self._auto_register_schema_func = (
            self._schema_registry_client.register_schema
            if self._auto_register_schemas
            else self._schema_registry_client.get_schema_properties
        )

    def __enter__(self):
        # type: () -> AvroSerializer
        self._schema_registry_client.__enter__()
        return self

    def __exit__(self, *exc_details):
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
            self._schema_group, schema_name, schema_str, "Avro", **kwargs
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

    def serialize(
        self,
        data: Mapping[str, Any],
        *,
        schema: str,
        message_type: Optional[Callable] = None,
        client_request_kwargs: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Union[MessageType, MessageMetadataDict]:
        """
        Serialize data with the given schema. Create content type value, which consists of the Avro Mime Type string
         and the schema ID corresponding to given schema. If provided with a message constructor callback,
         pass serialized data and content type to create message object. If not provided, return the following dict:
         {"data": Avro serialized value, "content_type": Avro mime type string + schema ID}.

        If `message_type` is set, then additional keyword arguments will be passed to the message callback
         function provided.

        Schema must be an Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param data: The data to be serialized.
        :type data: Mapping[str, Any]
        :keyword schema: Required. The schema used to serialize the data.
        :paramtype schema: str
        :keyword message_type: The callback function or message class to construct the message. If message class,
         it must be a subtype of the azure.schemaregistry.serializer.avroserializer.MessageType protocol.
         If callback function, it must have the following method signature:
         `(data: bytes, content_type: str, **kwargs) -> MessageType`, where `data` and `content_type`
         are positional parameters.
        :paramtype message_type: Callable or None
        :keyword client_request_kwargs: The keyword arguments to be passed to the SchemaRegistryClient.
        :paramtype client_request_kwargs: Dict[str, Any]
        :rtype: MessageType or MessageMetadataDict
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaSerializationError:
            Indicates an issue with serializing data for provided schema.
        """

        raw_input_schema = schema

        try:
            schema_fullname = self._avro_serializer.get_schema_fullname(raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaParseError(
                f"Cannot parse schema: {raw_input_schema}", error=e
            ).raise_with_traceback()

        cache_misses = self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter
        client_request_kwargs = client_request_kwargs or {}
        schema_id = self._get_schema_id(schema_fullname, raw_input_schema, **client_request_kwargs)
        new_cache_misses = self._get_schema_id.cache_info().misses  # pylint: disable=no-value-for-parameter
        if new_cache_misses > cache_misses:
            # if more misses, "missed collision" and new element has been added to cache
            cache_size = self._get_schema_id.cache_info().currsize  # pylint: disable=no-value-for-parameter
            _LOGGER.info("New entry has been added to schema ID cache. Cache size: %s", str(cache_size))

        content_type = f"{AVRO_MIME_TYPE}+{schema_id}"

        try:
            data_bytes = self._avro_serializer.serialize(data, raw_input_schema)
        except Exception as e:  # pylint:disable=broad-except
            SchemaSerializationError(
                "Cannot serialize value '{}' for schema: {}".format(
                    data, raw_input_schema
                ),
                error=e,
            ).raise_with_traceback()

        stream = BytesIO()

        stream.write(data_bytes)
        stream.flush()

        payload = stream.getvalue()
        stream.close()

        if message_type:
            try:
                return message_type.from_message_data(payload, content_type, **kwargs)
            except AttributeError:
                try:
                    return message_type(payload, content_type, **kwargs)
                except TypeError as e:
                    SchemaSerializationError(
                        f"""The data model {str(message_type)} is not a Callable that takes `data`
                            and `content_type` or a subtype of the MessageType protocol.
                            If using an Azure SDK model class, please check the README.md for the full list
                            of supported Azure SDK models and their corresponding versions."""
                    ).raise_with_traceback()

        return {"data": payload, "content_type": content_type}

    def _convert_preamble_format(
        self, data, content_type
    ):  # pylint: disable=no-self-use
        record_format_identifier = b"\0\0\0\0"
        if data[0:RECORD_FORMAT_IDENTIFIER_LENGTH] == record_format_identifier:
            schema_id = data[
                SCHEMA_ID_START_INDEX : (SCHEMA_ID_START_INDEX + SCHEMA_ID_LENGTH)
            ].decode("utf-8")
            content_type = f"{AVRO_MIME_TYPE}+{schema_id}"
            data = data[DATA_START_INDEX:]

        return data, content_type

    def deserialize(
        self,
        message: Union[MessageType, MessageMetadataDict],
        *,
        readers_schema: Optional[str] = None,
        client_request_kwargs: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Deserialize bytes data using schema ID in the content type field. `message` must be one of the following:
            1) A Subtype of the MessageType protocol.
            2) A dict {"data": ..., "content_type": ...}, where "data" is bytes and "content_type" is string.
            3) If using to deserialize data that was serialized with the AvroSerializer, a dict
                {"data": ..., "content_type": None}, where "data" is bytes and "content_type" is None.
        Data must follow format of associated Avro RecordSchema:
        https://avro.apache.org/docs/1.10.0/gettingstartedpython.html#Defining+a+schema

        :param message: The message object which holds the data to be deserialized and content type
         containing the schema ID.
        :type message: MessageType or MessageMetadataDict
        :keyword readers_schema: An optional reader's schema as defined by the Apache Avro specification.
        :paramtype readers_schema: str or None
        :rtype: Dict[str, Any]
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaParseError:
            Indicates an issue with parsing schema.
        :raises ~azure.schemaregistry.serializer.avroserializer.exceptions.SchemaDeserializationError:
            Indicates an issue with decoding value.
        """

        try:
            message_data_dict = message.__message_data__()
            data = message_data_dict["data"]
            content_type = message_data_dict["content_type"]
        except AttributeError:
            try:
                data = message["data"]
                content_type = message["content_type"]
            except (KeyError, TypeError):
                SchemaDeserializationError(
                    f"""The data model {str(message)} is not a subtype of the MessageType protocol or type
                        MessageMetadataDict.  If using an Azure SDK model class, please check the README.md
                        for the full list of supported Azure SDK models and their corresponding versions."""
                ).raise_with_traceback()

        # include in first preview for back compatibility
        data, content_type = self._convert_preamble_format(data, content_type)

        schema_id = content_type.split("+")[1]

        cache_misses = self._get_schema.cache_info().misses # pylint: disable=no-value-for-parameter
        client_request_kwargs = client_request_kwargs or {}
        schema_definition = self._get_schema(schema_id, **client_request_kwargs)
        new_cache_misses = self._get_schema.cache_info().misses # pylint: disable=no-value-for-parameter
        if new_cache_misses > cache_misses:
            # if more misses, "missed collision" and new element has been added to cache
            cache_size = self._get_schema.cache_info().currsize  # pylint: disable=no-value-for-parameter
            _LOGGER.info("New entry has been added to schema cache. Cache size: %s", str(cache_size))

        try:
            dict_value = self._avro_serializer.deserialize(
                data, schema_definition, readers_schema=readers_schema
            )
        except Exception as e:  # pylint:disable=broad-except
            error_message = (
                f"Cannot deserialize value '{data}' for schema: {schema_definition}\n and"
                "reader's schema: {readers_schema}"
                if readers_schema
                else f"Cannot deserialize value '{data}' for schema: {schema_definition}"
            )
            SchemaDeserializationError(
                error_message,
                error=e,
            ).raise_with_traceback()
        return dict_value
