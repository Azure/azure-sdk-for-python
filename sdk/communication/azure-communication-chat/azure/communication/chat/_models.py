# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import ChatParticipant as ChatParticipantAutorest
from ._generated.models import ChatMessageType
from ._utils import CommunicationUserIdentifierConverter

# pylint: disable=unused-import,ungrouped-imports
from ._shared.models import CommunicationUserIdentifier

class ChatThreadParticipant(object):
    """A participant of the chat thread.

    All required parameters must be populated in order to send to Azure.

    :ivar user: Required. The CommunicationUserIdentifier.
    :type user: CommunicationUserIdentifier
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

        self.user = kwargs['user']
        self.display_name = kwargs.get('display_name', None)
        self.share_history_time = kwargs.get('share_history_time', None)

    @classmethod
    def _from_generated(cls, chat_thread_participant):
        return cls(
            user=CommunicationUserIdentifierConverter.from_identifier_model(
                chat_thread_participant.communication_identifier),
            display_name=chat_thread_participant.display_name,
            share_history_time=chat_thread_participant.share_history_time
        )

    def _to_generated(self):
        return ChatParticipantAutorest(
            communication_identifier=CommunicationUserIdentifierConverter.to_identifier_model(self.user),
            display_name=self.display_name,
            share_history_time=self.share_history_time
        )


class ChatMessage(object):
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
    :ivar sender_communication_identifier: The chat message sender.
    :type sender_communication_identifier: CommunicationUserIdentifier
    :ivar deleted_on: The timestamp when the chat message was deleted. The timestamp is in RFC3339
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type deleted_on: ~datetime.datetime
    :ivar edited_on: The last timestamp (if applicable) when the message was edited. The timestamp
     is in RFC3339 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type edited_on: ~datetime.datetime
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
        self.sender_communication_identifier = kwargs['sender_communication_identifier']
        self.deleted_on = kwargs['deleted_on']
        self.edited_on = kwargs['edited_on']

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
            sender_communication_identifier = CommunicationUserIdentifierConverter.from_identifier_model(
                chat_message.sender_communication_identifier)

        return cls(
            id=chat_message.id,
            type=cls._get_message_type(chat_message.type),
            sequence_id=chat_message.sequence_id,
            version=chat_message.version,
            content=ChatMessageContent._from_generated(chat_message.content), # pylint:disable=protected-access
            sender_display_name=chat_message.sender_display_name,
            created_on=chat_message.created_on,
            sender_communication_identifier=sender_communication_identifier,
            deleted_on=chat_message.deleted_on,
            edited_on=chat_message.edited_on
        )


class ChatMessageContent(object):
    """Content of a chat message.

    :ivar message: Chat message content for messages of types text or html.
    :type message: str
    :ivar topic: Chat message content for messages of type topicUpdated.
    :type topic: str
    :ivar participants: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type participants: list[~azure.communication.chat.models.ChatParticipant]
    :ivar initiator_communication_identifier: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type initiator_communication_identifier: CommunicationUserIdentifier
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
                ChatThreadParticipant._from_generated(participant) for participant in  # pylint:disable=protected-access
                participants_list
            ]
        else:
            participants = []

        initiator = chat_message_content.initiator_communication_identifier
        # check if initiator is populated
        if initiator is not None:
            initiator = CommunicationUserIdentifierConverter.from_identifier_model(
                chat_message_content.initiator_communication_identifier)

        return cls(
            message=chat_message_content.message,
            topic=chat_message_content.topic,
            participants=participants,
            initiator=initiator
        )


class ChatThread(object):
    """ChatThread.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Chat thread id.
    :vartype id: str
    :ivar topic: Chat thread topic.
    :type topic: str
    :ivar created_on: The timestamp when the chat thread was created. The timestamp is in ISO8601
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_on: ~datetime.datetime
    :ivar created_by: the chat thread owner.
    :vartype created_by: CommunicationUserIdentifier
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
            created_by = CommunicationUserIdentifierConverter.from_identifier_model(
                chat_thread.created_by_communication_identifier)

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
    :vartype sender: CommunicationUserIdentifier
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
            sender = CommunicationUserIdentifierConverter.from_identifier_model(
                read_receipt.sender_communication_identifier)

        return cls(
            sender=sender,
            chat_message_id=read_receipt.chat_message_id,
            read_on=read_receipt.read_on
        )

class CreateChatThreadResult(object):
    """Result of the create chat thread operation.

    :ivar chat_thread: Chat thread.
    :type chat_thread: ~azure.communication.chat.ChatThread
    :ivar errors: Errors encountered during the creation of the chat thread.
    :type errors: list((~azure.communication.chat.ChatThreadParticipant, ~azure.communication.chat.CommunicationError))
    """

    def __init__(
        self,
        **kwargs # type: Any
    ):
        # type: (...) -> None
        self.chat_thread = kwargs['chat_thread']
        self.errors = kwargs.get('errors', None)
