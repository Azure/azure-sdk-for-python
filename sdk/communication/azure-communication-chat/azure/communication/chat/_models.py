# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from ._generated.models import ChatParticipant as ChatParticipantAutorest
from ._generated.models import ChatMessageType
from ._communication_identifier_serializer import serialize_identifier, deserialize_identifier

# pylint: disable=unused-import,ungrouped-imports
from ._shared.models import CommunicationIdentifier

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple


class ChatParticipant(object):
    """A participant of the chat thread.

    All required parameters must be populated in order to send to Azure.

    :ivar identifier: Required. The communication identifier.
    :type identifier: CommunicationIdentifier
    :ivar display_name: Display name for the chat thread participant.
    :type display_name: str
    :ivar share_history_time: Time from which the chat history is shared with the participant. The
     timestamp is in ISO8601 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type share_history_time: ~datetime.datetime
    """

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None

        self.identifier = kwargs['identifier']
        self.display_name = kwargs.get('display_name', None)
        self.share_history_time = kwargs.get('share_history_time', None)

    @classmethod
    def _from_generated(cls, chat_thread_participant):
        return cls(
            identifier=deserialize_identifier(chat_thread_participant.communication_identifier),
            display_name=chat_thread_participant.display_name,
            share_history_time=chat_thread_participant.share_history_time
        )

    def _to_generated(self):
        return ChatParticipantAutorest(
            communication_identifier=serialize_identifier(self.identifier),
            display_name=self.display_name,
            share_history_time=self.share_history_time
        )


class ChatMessage(object): # pylint: disable=too-many-instance-attributes
    """Chat message.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The id of the chat message. This id is server generated.
    :vartype id: str
    :ivar type: Type of the chat message. Possible values include: "text", "html",
     "topicUpdated", "participantAdded", "participantRemoved".
    :type type: ~azure.communication.chat.models.ChatMessageType
    :ivar sequence_id: Sequence of the chat message in the conversation.
    :type sequence_id: str
    :ivar version: Version of the chat message.
    :vartype version: str
    :ivar content: Content of the chat message.
    :type content: ~azure.communication.chat.models.ChatMessageContent
    :ivar sender_display_name: The display name of the chat message sender. This property is used
     to populate sender name for push notifications.
    :type sender_display_name: str
    :ivar created_on: The timestamp when the chat message arrived at the server. The timestamp is
     in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type created_on: ~datetime.datetime
    :ivar sender: The chat message sender.
    :type sender: CommunicationIdentifier
    :ivar deleted_on: The timestamp when the chat message was deleted. The timestamp is in RFC3339
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type deleted_on: ~datetime.datetime
    :ivar edited_on: The last timestamp (if applicable) when the message was edited. The timestamp
     is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type edited_on: ~datetime.datetime
    :ivar metadata: Message metadata.
    :type metadata: dict[str, str]
    """

    def __init__(
            self,
            **kwargs # type: Any
    ):
        # type: (...) -> None

        self.id = kwargs['id']
        self.type = kwargs['type']
        self.sequence_id = kwargs['sequence_id']
        self.version = kwargs['version']
        self.content = kwargs['content']
        self.sender_display_name = kwargs['sender_display_name']
        self.created_on = kwargs['created_on']
        self.sender = kwargs['sender']
        self.deleted_on = kwargs['deleted_on']
        self.edited_on = kwargs['edited_on']
        self.metadata = kwargs.get('metadata')

    @classmethod
    def _get_message_type(cls, chat_message_type):
        for message_type in ChatMessageType:
            value = message_type.value
            if value == chat_message_type:
                return message_type
        raise AttributeError(chat_message_type)

    @classmethod
    def _from_generated(cls, chat_message):

        sender_communication_identifier = chat_message.sender_communication_identifier
        if sender_communication_identifier is not None:
            sender_communication_identifier = deserialize_identifier(chat_message.sender_communication_identifier)

        return cls(
            id=chat_message.id,
            type=cls._get_message_type(chat_message.type),
            sequence_id=chat_message.sequence_id,
            version=chat_message.version,
            content=ChatMessageContent._from_generated(chat_message.content), # pylint:disable=protected-access
            sender_display_name=chat_message.sender_display_name,
            created_on=chat_message.created_on,
            sender=sender_communication_identifier,
            deleted_on=chat_message.deleted_on,
            edited_on=chat_message.edited_on,
            metadata=chat_message.metadata
        )


class ChatMessageContent(object):
    """Content of a chat message.

    :ivar message: Chat message content for messages of types text or html.
    :type message: str
    :ivar topic: Chat message content for messages of type topicUpdated.
    :type topic: str
    :ivar participants: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type participants: List[~azure.communication.chat.models.ChatParticipant]
    :ivar initiator: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type initiator: CommunicationIdentifier
    """

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None

        self.message = kwargs.get('message', None)
        self.topic = kwargs.get('topic', None)
        self.participants = kwargs.get('participants', None)
        self.initiator = kwargs.get('initiator', None)

    @classmethod
    def _from_generated(cls, chat_message_content):
        participants_list = chat_message_content.participants
        if participants_list is not None and len(participants_list) > 0:
            participants = [
                ChatParticipant._from_generated(participant) for participant in  # pylint:disable=protected-access
                participants_list
            ]
        else:
            participants = []

        initiator = chat_message_content.initiator_communication_identifier
        # check if initiator is populated
        if initiator is not None:
            initiator = deserialize_identifier(chat_message_content.initiator_communication_identifier)

        return cls(
            message=chat_message_content.message,
            topic=chat_message_content.topic,
            participants=participants,
            initiator=initiator
        )


class ChatThreadProperties(object):
    """ChatThreadProperties.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Chat thread id.
    :vartype id: str
    :ivar topic: Chat thread topic.
    :type topic: str
    :ivar created_on: The timestamp when the chat thread was created. The timestamp is in ISO8601
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_on: ~datetime.datetime
    :ivar created_by: the chat thread owner.
    :vartype created_by: CommunicationIdentifier
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.id = kwargs['id']
        self.topic = kwargs.get('topic', None)
        self.created_on = kwargs['created_on']
        self.created_by = kwargs['created_by']

    @classmethod
    def _from_generated(cls, chat_thread):

        created_by = chat_thread.created_by_communication_identifier
        if created_by is not None:
            created_by = deserialize_identifier(chat_thread.created_by_communication_identifier)

        return cls(
            id=chat_thread.id,
            topic=chat_thread.topic,
            created_on=chat_thread.created_on,
            created_by=created_by
        )


class ChatMessageReadReceipt(object):
    """A chat message read receipt indicates the time a chat message was read by a recipient.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar sender: Read receipt sender.
    :vartype sender: CommunicationIdentifier
    :ivar chat_message_id: Id for the chat message that has been read. This id is generated by the
     server.
    :vartype chat_message_id: str
    :ivar read_on: Read receipt timestamp. The timestamp is in ISO8601 format: ``yyyy-MM-
     ddTHH:mm:ssZ``.
    :vartype read_on: ~datetime.datetime
    """

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.sender = kwargs['sender']
        self.chat_message_id = kwargs['chat_message_id']
        self.read_on = kwargs['read_on']

    @classmethod
    def _from_generated(cls, read_receipt):
        sender = read_receipt.sender_communication_identifier
        if sender is not None:
            sender = deserialize_identifier(read_receipt.sender_communication_identifier)

        return cls(
            sender=sender,
            chat_message_id=read_receipt.chat_message_id,
            read_on=read_receipt.read_on
        )

class CreateChatThreadResult(object):
    """Result of the create chat thread operation.

    :ivar chat_thread: Chat thread.
    :type chat_thread: ~azure.communication.chat.ChatThreadProperties
    :ivar errors: Errors encountered during the creation of the chat thread.
    :type errors: List[Tuple[~azure.communication.chat.ChatParticipant, ~azure.communication.chat.ChatError]]
    """

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.chat_thread = kwargs['chat_thread']
        self.errors = kwargs.get('errors', None)
