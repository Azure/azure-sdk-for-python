# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional

import datetime
from ._generated.models import ChatParticipant as ChatParticipantAutorest
from ._generated.models import ChatMessageType
from ._communication_identifier_serializer import serialize_identifier, deserialize_identifier

from ._shared.models import CommunicationIdentifier


class ChatParticipant:
    """A participant of the chat thread.

    All required parameters must be populated in order to send to Azure.

    :ivar identifier: Required. The communication identifier.
    :vartype identifier: ~azure.communication.chat.CommunicationIdentifier
    :ivar display_name: Display name for the chat thread participant.
    :vartype display_name: str or None
    :ivar share_history_time: Time from which the chat history is shared with the participant.
    :vartype share_history_time: ~datetime.datetime or None
    """

    def __init__(  # pylint: disable=unused-argument
        self,
        *,
        identifier: CommunicationIdentifier,
        display_name: Optional[str] = None,
        share_history_time: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword identifier: Identifies a participant in Azure Communication services. A
         participant is, for example, a phone number or an Azure communication user. This model is
         polymorphic: Apart from kind and rawId, at most one further property may be set which must
         match the kind enum value. Required.
        :paramtype identifier: ~azure.communication.chat.CommunicationIdentifier
        :keyword display_name: Display name for the chat participant.
        :paramtype display_name: str or None
        :keyword share_history_time: Time from which the chat history is shared with the participant.
        :paramtype share_history_time: ~datetime.datetime or None
        """
        self.identifier = identifier
        self.display_name = display_name
        self.share_history_time = share_history_time

    @classmethod
    def _from_generated(cls, chat_thread_participant):
        return cls(
            identifier=deserialize_identifier(chat_thread_participant.communication_identifier),
            display_name=chat_thread_participant.display_name,
            share_history_time=chat_thread_participant.share_history_time,
        )

    def _to_generated(self):
        return ChatParticipantAutorest(
            communication_identifier=serialize_identifier(self.identifier),
            display_name=self.display_name,
            share_history_time=self.share_history_time,
        )


class ChatAttachment:
    """An attachment in a chat message.

    All required parameters must be populated in order to send to Azure.

    :ivar id: Id of the attachment. Required.
    :vartype id: str
    :ivar attachment_type: The type of attachment. Required. Known values are: "image" and "file".
    :vartype attachment_type: str or ~azure.communication.chat.models.ChatAttachmentType
    :ivar name: The name of the attachment content.
    :vartype name: str or None
    :ivar url: The URL where the attachment can be downloaded.
    :vartype url: str or None
    :ivar preview_url: The URL where the preview of attachment can be downloaded.
    :vartype preview_url: str or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs["id"]
        self.attachment_type = kwargs["attachment_type"]
        self.name = kwargs.get("name", None)
        self.url = kwargs.get("url", None)
        self.preview_url = kwargs.get("preview_url", None)

    @classmethod
    def _from_generated(cls, chat_attachment):
        return cls(
            id=chat_attachment.id,
            attachment_type=chat_attachment.attachment_type,
            name=chat_attachment.name,
            url=chat_attachment.url,
            preview_url=chat_attachment.preview_url,
        )


class ChatMessage:  # pylint: disable=too-many-instance-attributes
    """Chat message.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The id of the chat message. This id is server generated.
    :vartype id: str
    :ivar type: Type of the chat message. Possible values include: "text", "html",
     "topicUpdated", "participantAdded", "participantRemoved".
    :vartype type: str or ~azure.communication.chat.ChatMessageType
    :ivar sequence_id: Sequence of the chat message in the conversation.
    :vartype sequence_id: str
    :ivar version: Version of the chat message.
    :vartype version: str
    :ivar content: Content of the chat message.
    :vartype content: ~azure.communication.chat.ChatMessageContent or None
    :ivar sender_display_name: The display name of the chat message sender. This property is used
     to populate sender name for push notifications.
    :vartype sender_display_name: str or None
    :ivar created_on: The timestamp when the chat message arrived at the server.
    :vartype created_on: ~datetime.datetime
    :ivar sender: The chat message sender.
    :vartype sender: ~azure.communication.chat.CommunicationIdentifier or None
    :ivar deleted_on: The timestamp when the chat message was deleted.
    :vartype deleted_on: ~datetime.datetime or None
    :ivar edited_on: The last timestamp (if applicable) when the message was edited.
    :vartype edited_on: ~datetime.datetime or None
    :ivar metadata: Message metadata.
    :vartype metadata: dict[str, str] or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs["id"]
        self.type = kwargs["type"]
        self.sequence_id = kwargs["sequence_id"]
        self.version = kwargs["version"]
        self.content = kwargs["content"]
        self.sender_display_name = kwargs["sender_display_name"]
        self.created_on = kwargs["created_on"]
        self.sender = kwargs["sender"]
        self.deleted_on = kwargs["deleted_on"]
        self.edited_on = kwargs["edited_on"]
        self.metadata = kwargs.get("metadata")

    @classmethod
    def _from_generated(cls, chat_message):

        sender_communication_identifier = chat_message.sender_communication_identifier
        if sender_communication_identifier is not None:
            sender_communication_identifier = deserialize_identifier(chat_message.sender_communication_identifier)
        try:
            message_type = ChatMessageType(chat_message.type)
        except ValueError:
            message_type = chat_message.type
        content = (
            ChatMessageContent._from_generated(chat_message.content)  # pylint:disable=protected-access
            if chat_message.content
            else None
        )
        return cls(
            id=chat_message.id,
            type=message_type,
            sequence_id=chat_message.sequence_id,
            version=chat_message.version,
            content=content,
            sender_display_name=chat_message.sender_display_name,
            created_on=chat_message.created_on,
            sender=sender_communication_identifier,
            deleted_on=chat_message.deleted_on,
            edited_on=chat_message.edited_on,
            metadata=chat_message.metadata,
        )


class ChatMessageContent:
    """Content of a chat message.

    :ivar message: Chat message content for messages of types text or html.
    :vartype message: str or None
    :ivar topic: Chat message content for messages of type topicUpdated.
    :vartype topic: str or None
    :ivar participants: Chat message content for messages of types participantAdded or
     participantRemoved.
    :vartype participants: List[~azure.communication.chat.ChatParticipant]
    :ivar initiator: Chat message content for messages of types participantAdded or
     participantRemoved.
    :vartype initiator: ~azure.communication.chat.CommunicationIdentifier or None
    :ivar attachments: Chat message content for messages of type text or html
    :vartype attachments: List[~azure.communication.chat.ChatAttachment]
    """

    def __init__(self, **kwargs: Any) -> None:
        self.message = kwargs.get("message", None)
        self.topic = kwargs.get("topic", None)
        self.participants = kwargs.get("participants", None)
        self.initiator = kwargs.get("initiator", None)
        self.attachments = kwargs.get("attachments", None)

    @classmethod
    def _from_generated(cls, chat_message_content):
        participants_list = chat_message_content.participants
        if participants_list:
            participants = [
                ChatParticipant._from_generated(participant)  # pylint:disable=protected-access
                for participant in participants_list
            ]
        else:
            participants = []

        attachments_list = chat_message_content.attachments
        if attachments_list:
            attachments = [
                ChatAttachment._from_generated(attachment)  # pylint:disable=protected-access
                for attachment in attachments_list
            ]
        else:
            attachments = []

        initiator = chat_message_content.initiator_communication_identifier
        # check if initiator is populated
        if initiator is not None:
            initiator = deserialize_identifier(chat_message_content.initiator_communication_identifier)

        return cls(
            message=chat_message_content.message,
            topic=chat_message_content.topic,
            participants=participants,
            initiator=initiator,
            attachments=attachments,
        )


class ChatThreadProperties:
    """ChatThreadProperties.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Chat thread id.
    :vartype id: str
    :ivar topic: Chat thread topic.
    :vartype topic: str
    :ivar created_on: The timestamp when the chat thread was created.
    :vartype created_on: ~datetime.datetime
    :ivar created_by: the chat thread owner.
    :vartype created_by: ~azure.communication.chat.CommunicationIdentifier
    """

    # pylint:disable=protected-access

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs["id"]
        self.topic = kwargs.get("topic", None)
        self.created_on = kwargs["created_on"]
        self.created_by = kwargs["created_by"]

    @classmethod
    def _from_generated(cls, chat_thread):

        created_by = chat_thread.created_by_communication_identifier
        if created_by is not None:
            created_by = deserialize_identifier(chat_thread.created_by_communication_identifier)

        return cls(id=chat_thread.id, topic=chat_thread.topic, created_on=chat_thread.created_on, created_by=created_by)


class ChatMessageReadReceipt:
    """A chat message read receipt indicates the time a chat message was read by a recipient.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar sender: Read receipt sender.
    :vartype sender: ~azure.communication.chat.CommunicationIdentifier
    :ivar chat_message_id: Id for the chat message that has been read. This id is generated by the
     server.
    :vartype chat_message_id: str
    :ivar read_on: Read receipt timestamp.
    :vartype read_on: ~datetime.datetime
    """

    def __init__(self, **kwargs: Any) -> None:
        self.sender = kwargs["sender"]
        self.chat_message_id = kwargs["chat_message_id"]
        self.read_on = kwargs["read_on"]

    @classmethod
    def _from_generated(cls, read_receipt):
        sender = read_receipt.sender_communication_identifier
        if sender is not None:
            sender = deserialize_identifier(read_receipt.sender_communication_identifier)

        return cls(sender=sender, chat_message_id=read_receipt.chat_message_id, read_on=read_receipt.read_on)


class CreateChatThreadResult:
    """Result of the create chat thread operation.

    :ivar chat_thread: Chat thread.
    :vartype chat_thread: ~azure.communication.chat.ChatThreadProperties
    :ivar errors: Errors encountered during the creation of the chat thread.
    :vartype errors: List[Tuple[~azure.communication.chat.ChatParticipant, ~azure.communication.chat.ChatError]] or None
    """

    def __init__(self, **kwargs: Any) -> None:
        self.chat_thread = kwargs["chat_thread"]
        self.errors = kwargs.get("errors", None)
