# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._shared.models import CommunicationUser
from ._generated.models import ChatThreadMember as ChatThreadMemberAutorest


class ChatThreadMember(object):
    """A member of the chat thread.

    All required parameters must be populated in order to send to Azure.

    :param user: Required. The CommunicationUser.
    :type user: CommunicationUser
    :param display_name: Display name for the chat thread member.
    :type display_name: str
    :param share_history_time: Time from which the chat history is shared with the member. The
     timestamp is in ISO8601 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type share_history_time: ~datetime.datetime
    """

    def __init__(
        self,
        **kwargs
    ):
        self.user = kwargs['user']
        self.display_name = kwargs.get('display_name', None)
        self.share_history_time = kwargs.get('share_history_time', None)

    @classmethod
    def _from_generated(cls, chat_thread_member):
        return cls(
            user=CommunicationUser(chat_thread_member.id),
            display_name=chat_thread_member.display_name,
            share_history_time=chat_thread_member.share_history_time
        )

    def _to_generated(self):
        return ChatThreadMemberAutorest(
            id=self.user.identifier,
            display_name=self.display_name,
            share_history_time=self.share_history_time
        )


class ChatMessage(object):
    """ChatMessage.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The id of the chat message. This id is server generated.
    :vartype id: str
    :param type: Type of the chat message. Possible values include: "Text",
     "ThreadActivity/TopicUpdate", "ThreadActivity/AddMember", "ThreadActivity/DeleteMember".
    :type type: str
    :param priority: The chat message priority. Possible values include: "Normal", "High".
    :type priority: str or ~azure.communication.chat.models.ChatMessagePriority
    :ivar version: Version of the chat message.
    :vartype version: str
    :param content: Content of the chat message.
    :type content: str
    :param sender_display_name: The display name of the chat message sender. This property is used
     to populate sender name for push notifications.
    :type sender_display_name: str
    :ivar created_on: The timestamp when the chat message arrived at the server. The timestamp is
     in ISO8601 format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :vartype created_on: ~datetime.datetime
    :ivar sender: The chat message sender.
    :vartype sender: CommunicationUser
    :param deleted_on: The timestamp when the chat message was deleted. The timestamp is in ISO8601
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type deleted_on: ~datetime.datetime
    :param edited_on: The timestamp when the chat message was edited. The timestamp is in ISO8601
     format: ``yyyy-MM-ddTHH:mm:ssZ``.
    :type edited_on: ~datetime.datetime
    """

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.type = kwargs.get('type', None)
        self.priority = kwargs.get('priority', None)
        self.version = kwargs['version']
        self.content = kwargs.get('content', None)
        self.sender_display_name = kwargs.get('sender_display_name', None)
        self.created_on = kwargs['created_on']
        self.sender = kwargs['sender']
        self.deleted_on = kwargs.get('deleted_on', None)
        self.edited_on = kwargs.get('edited_on', None)

    @classmethod
    def _from_generated(cls, chat_message):
        return cls(
            id=chat_message.id,
            type=chat_message.type,
            priority=chat_message.priority,
            version=chat_message.version,
            content=chat_message.content,
            sender_display_name=chat_message.sender_display_name,
            created_on=chat_message.created_on,
            sender=CommunicationUser(chat_message.sender_id),
            deleted_on=chat_message.deleted_on,
            edited_on=chat_message.edited_on
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
    :vartype created_by: CommunicationUser
    :param members: Chat thread members.
    :type members: list[~azure.communication.chat.ChatThreadMember]
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.topic = kwargs.get('topic', None)
        self.created_on = kwargs['created_on']
        self.created_by = kwargs['created_by']
        self.members = kwargs.get('members', None)

    @classmethod
    def _from_generated(cls, chat_thread):
        return cls(
            id=chat_thread.id,
            topic=chat_thread.topic,
            created_on=chat_thread.created_on,
            created_by=CommunicationUser(chat_thread.created_by),
            members=[ChatThreadMember._from_generated(x) for x in chat_thread.members]
        )


class ReadReceipt(object):
    """A read receipt indicates the time a chat message was read by a recipient.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar sender: Read receipt sender.
    :vartype sender_id: CommunicationUser
    :ivar chat_message_id: Id for the chat message that has been read. This id is generated by the
     server.
    :vartype chat_message_id: str
    :ivar read_on: Read receipt timestamp. The timestamp is in ISO8601 format: ``yyyy-MM-
     ddTHH:mm:ssZ``.
    :vartype read_on: ~datetime.datetime
    """

    def __init__(
        self,
        **kwargs
    ):
        self.sender = kwargs['sender']
        self.chat_message_id = kwargs['chat_message_id']
        self.read_on = kwargs['read_on']

    @classmethod
    def _from_generated(cls, read_receipt):
        return cls(
            sender=CommunicationUser(read_receipt.sender_id),
            chat_message_id=read_receipt.chat_message_id,
            read_on=read_receipt.read_on
        )
