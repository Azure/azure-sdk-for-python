# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._generated.models import ChatParticipant as ChatParticipantAutorest
from ._shared.models import CommunicationUserIdentifier
from ._generated.models import ChatMessageType

class ChatThreadParticipant(object):
    """A participant of the chat thread.

    All required parameters must be populated in order to send to Azure.

    :param user: Required. The CommunicationUserIdentifier.
    :type user: CommunicationUserIdentifier
    :param display_name: Display name for the chat thread participant.
    :type display_name: str
    :param share_history_time: Time from which the chat history is shared with the participant. The
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
            user=CommunicationUserIdentifier(chat_thread_participant.id),
            display_name=chat_thread_participant.display_name,
            share_history_time=chat_thread_participant.share_history_time
        )

    def _to_generated(self):
        return ChatParticipantAutorest(
            id=self.user.identifier,
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
    :ivar sender_id: The chat message sender.
    :type sender_id: CommunicationUserIdentifier
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
        self.sender_id = kwargs['sender_id']
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
        return cls(
            id=chat_message.id,
            type=cls._get_message_type(chat_message.type),
            sequence_id=chat_message.sequence_id,
            version=chat_message.version,
            content=ChatMessageContent._from_generated(chat_message.content), # pylint:disable=protected-access
            sender_display_name=chat_message.sender_display_name,
            created_on=chat_message.created_on,
            sender_id=CommunicationUserIdentifier(chat_message.sender_id),
            deleted_on=chat_message.deleted_on,
            edited_on=chat_message.edited_on
        )


class ChatMessageContent(object):
    """Content of a chat message.

    :param message: Chat message content for messages of types text or html.
    :type message: str
    :param topic: Chat message content for messages of type topicUpdated.
    :type topic: str
    :param participants: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type participants: list[~azure.communication.chat.models.ChatParticipant]
    :param initiator: Chat message content for messages of types participantAdded or
     participantRemoved.
    :type initiator: str
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
            participants = [ChatThreadParticipant._from_generated(participant) for participant in participants_list] # pylint:disable=protected-access
        else:
            participants = []
        return cls(
            message=chat_message_content.message,
            topic=chat_message_content.topic,
            participants=participants,
            initiator=chat_message_content.initiator
        )


class ChatThread(object):
    """ChatThread.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Chat thread id.
    :vartype id: str
    :param topic: Chat thread topic.
    :type topic: str
    :ivar created_on: The timestamp when the chat thread was created. The timestamp is in ISO8601
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_on: ~datetime.datetime
    :ivar created_by: the chat thread owner.
    :vartype created_by: CommunicationUserIdentifier
    :param participants: Chat thread participants.
    :type participants: list[~azure.communication.chat.ChatThreadParticipant]
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
        self.participants = kwargs.get('participants', None)

    @classmethod
    def _from_generated(cls, chat_thread):
        return cls(
            id=chat_thread.id,
            topic=chat_thread.topic,
            created_on=chat_thread.created_on,
            created_by=CommunicationUserIdentifier(chat_thread.created_by)
        )


class ChatMessageReadReceipt(object):
    """A chat message read receipt indicates the time a chat message was read by a recipient.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar sender: Read receipt sender.
    :vartype sender_id: CommunicationUserIdentifier
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
        return cls(
            sender=CommunicationUserIdentifier(read_receipt.sender_id),
            chat_message_id=read_receipt.chat_message_id,
            read_on=read_receipt.read_on
        )
