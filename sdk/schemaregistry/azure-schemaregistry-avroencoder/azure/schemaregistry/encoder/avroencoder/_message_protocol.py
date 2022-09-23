# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any
from typing_extensions import Protocol, TypedDict  # type: ignore


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
        :rtype: ~azure.schemaregistry.encoder.avroencoder.MessageType
        """
        ...

    def __message_content__(self) -> MessageContent:
        """A MessageContent object, with `content` and `content_type` set to
         the values of their respective properties on the MessageType object.

        :rtype: ~azure.schemaregistry.encoder.avroencoder.MessageContent
        """
        ...
