# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, Mapping, Union, TYPE_CHECKING, overload, Optional, Type
from typing_extensions import Protocol, TypedDict  # type: ignore

if TYPE_CHECKING:
    from ._schema_registry_client import SchemaRegistryClient


class SchemaContentValidate(Protocol):
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
        :rtype: ~azure.schemaregistry.encoder.jsonencoder.MessageType
        :returns: The MessageType object with encoded content and content type.
        """

    def __message_content__(self) -> MessageContent:
        """A MessageContent object, with `content` and `content_type` set to
         the values of their respective properties on the MessageType object.

        :rtype: ~azure.schemaregistry.encoder.jsonencoder.MessageContent
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
         azure.schemaregistry.encoder.MessageType protocol.
        :paramtype message_type: type[MessageType]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :rtype: MessageContent
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
         azure.schemaregistry.encoder.MessageType protocol.
        :paramtype message_type: type[MessageType]
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :rtype: MessageContent
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
        :keyword message_type: The message class to construct the message. Must be a subtype of the
         azure.schemaregistry.encoder.MessageType protocol.
        :paramtype message_type: type[MessageType] or None
        :keyword request_options: The keyword arguments for http requests to be passed to the client.
        :paramtype request_options: dict[str, any] or None
        :rtype: MessageType or MessageContent
        :raises ~azure.schemaregistry.encoder.InvalidContentError:
            Indicates an issue with encoding content with schema.
        """

    def decode(
        self,  # pylint: disable=unused-argument
        message: "MessageType",
        *,
        request_options: Dict[str, Any] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Returns the decoded data with the schema format specified by the `content-type` property.
         If `validate` callable was passed to constructor, will validate content against schema after decoding.
        """
