# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.tracing.decorator import distributed_trace

from ._shared.user_credential import CommunicationUserCredential
from ._common import CommunicationUserCredentialPolicy
from ._generated import AzureCommunicationChatService
from ._generated.models import (
    AddChatParticipantsRequest,
    SendReadReceiptRequest,
    SendChatMessageRequest,
    UpdateChatMessageRequest,
    UpdateChatThreadRequest,
    ChatMessageType
)
from ._models import (
    ChatThreadParticipant,
    ChatMessage,
    ChatMessageReadReceipt
)

from ._utils import _to_utc_datetime # pylint: disable=unused-import
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
    from datetime import datetime
    from azure.core.paging import ItemPaged


class ChatThreadClient(object):
    """A client to interact with the AzureCommunicationService Chat gateway.
    Instances of this class is normally created by ChatClient.create_chat_thread()

    This client provides operations to add participant to chat thread, remove participant from
    chat thread, send message, delete message, update message, send typing notifications,
    send and list read receipt

    :ivar thread_id: Chat thread id.
    :vartype thread_id: str

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param CommunicationUserCredential credential:
        The credentials with which to authenticate. The value contains a User
        Access Token
    :param str thread_id:
        The unique thread id.

    .. admonition:: Example:

        .. literalinclude:: ../samples/chat_thread_client_sample.py
            :start-after: [START create_chat_thread_client]
            :end-before: [END create_chat_thread_client]
            :language: python
            :dedent: 8
            :caption: Creating the ChatThreadClient.
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: CommunicationUserCredential
            thread_id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        if not thread_id:
            raise ValueError("thread_id can not be None or empty")

        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._thread_id = thread_id
        self._endpoint = endpoint
        self._credential = credential

        self._client = AzureCommunicationChatService(
            endpoint,
            authentication_policy=CommunicationUserCredentialPolicy(self._credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @property
    def thread_id(self):
        # type: () -> str
        """
        Gets the thread id from the client.

        :rtype: str
        """
        return self._thread_id

    @distributed_trace
    def update_topic(
        self,
        topic=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Updates a thread's properties.

        :param topic: Thread topic. If topic is not specified, the update will succeeded but
         chat thread properties will not be changed.
        :type topic: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START update_topic]
                :end-before: [END update_topic]
                :language: python
                :dedent: 8
                :caption: Updating chat thread.
        """

        update_topic_request = UpdateChatThreadRequest(topic=topic)
        return self._client.chat_thread.update_chat_thread(
            chat_thread_id=self._thread_id,
            update_chat_thread_request=update_topic_request,
            **kwargs)

    @distributed_trace
    def send_read_receipt(
        self,
        message_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Posts a read receipt event to a thread, on behalf of a user.

        :param message_id: Required. Id of the latest message read by current user.
        :type message_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START send_read_receipt]
                :end-before: [END send_read_receipt]
                :language: python
                :dedent: 8
                :caption: Sending read receipt of a chat message.
        """
        if not message_id:
            raise ValueError("message_id cannot be None.")

        post_read_receipt_request = SendReadReceiptRequest(chat_message_id=message_id)
        return self._client.chat_thread.send_chat_read_receipt(
            self._thread_id,
            send_read_receipt_request=post_read_receipt_request,
            **kwargs)

    @distributed_trace
    def list_read_receipts(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[ChatMessageReadReceipt]
        """Gets read receipts for a thread.

        :keyword int results_per_page: The maximum number of chat message read receipts to be returned per page.
        :keyword int skip: Skips chat message read receipts up to a specified position in response.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ItemPaged[:class:`~azure.communication.chat.ChatMessageReadReceipt`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START list_read_receipts]
                :end-before: [END list_read_receipts]
                :language: python
                :dedent: 8
                :caption: Listing read receipts.
        """
        results_per_page = kwargs.pop("results_per_page", None)
        skip = kwargs.pop("skip", None)

        return self._client.chat_thread.list_chat_read_receipts(
            self._thread_id,
            max_page_size=results_per_page,
            skip=skip,
            cls=lambda objs: [ChatMessageReadReceipt._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs)

    @distributed_trace
    def send_typing_notification(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Posts a typing event to a thread, on behalf of a user.

        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START send_typing_notification]
                :end-before: [END send_typing_notification]
                :language: python
                :dedent: 8
                :caption: Sending typing notification.
        """
        return self._client.chat_thread.send_typing_notification(self._thread_id, **kwargs)

    @distributed_trace
    def send_message(
        self,
        content,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> str
        """Sends a message to a thread.

        :param content: Required. Chat message content.
        :type content: str
        :param chat_message_type: The chat message type. Possible values include: "text", "html", "participant_added",
        "participant_removed", "topic_updated" Default: ChatMessageType.TEXT
        :type chat_message_type: str or ~azure.communication.chat.models.ChatMessageType
        :keyword str sender_display_name: The display name of the message sender. This property is used to
          populate sender name for push notifications.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: str, or the result of cls(response)
        :rtype: str
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START send_message]
                :end-before: [END send_message]
                :language: python
                :dedent: 8
                :caption: Sending a message.
        """
        if not content:
            raise ValueError("content cannot be None.")

        chat_message_type = kwargs.pop("chat_message_type", None)
        if chat_message_type is None:
            chat_message_type = ChatMessageType.TEXT
        elif not isinstance(chat_message_type, ChatMessageType):
            try:
                chat_message_type = ChatMessageType.__getattr__(chat_message_type) # pylint:disable=protected-access
            except Exception:
                raise ValueError(
                    "chat_message_type: {message_type} is not acceptable".format(message_type=chat_message_type))

        sender_display_name = kwargs.pop("sender_display_name", None)

        create_message_request = SendChatMessageRequest(
            content=content,
            type=chat_message_type,
            sender_display_name=sender_display_name
        )

        send_chat_message_result = self._client.chat_thread.send_chat_message(
            chat_thread_id=self._thread_id,
            send_chat_message_request=create_message_request,
            **kwargs)
        return send_chat_message_result.id

    @distributed_trace
    def get_message(
        self,
        message_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ChatMessage
        """Gets a message by id.

        :param message_id: Required. The message id.
        :type message_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ChatMessage, or the result of cls(response)
        :rtype: ~azure.communication.chat.ChatMessage
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START get_message]
                :end-before: [END get_message]
                :language: python
                :dedent: 8
                :caption: Getting a message by message id.
        """
        if not message_id:
            raise ValueError("message_id cannot be None.")

        chat_message = self._client.chat_thread.get_chat_message(self._thread_id, message_id, **kwargs)
        return ChatMessage._from_generated(chat_message)  # pylint:disable=protected-access

    @distributed_trace
    def list_messages(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[ChatMessage]
        """Gets a list of messages from a thread.

        :keyword int results_per_page: The maximum number of messages to be returned per page.
        :keyword ~datetime.datetime start_time: The start time where the range query.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ItemPaged[:class:`~azure.communication.chat.ChatMessage`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START list_messages]
                :end-before: [END list_messages]
                :language: python
                :dedent: 8
                :caption: Listing messages of a chat thread.
        """
        results_per_page = kwargs.pop("results_per_page", None)
        start_time = kwargs.pop("start_time", None)

        a = self._client.chat_thread.list_chat_messages(
            self._thread_id,
            max_page_size=results_per_page,
            start_time=start_time,
            cls=lambda objs: [ChatMessage._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs)
        return a

    @distributed_trace
    def update_message(
        self,
        message_id,  # type: str
        content=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Updates a message.

        :param message_id: Required. The message id.
        :type message_id: str
        :param content: Chat message content.
        :type content: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START update_message]
                :end-before: [END update_message]
                :language: python
                :dedent: 8
                :caption: Updating a sent messages.
        """
        if not message_id:
            raise ValueError("message_id cannot be None.")

        update_message_request = UpdateChatMessageRequest(content=content, priority=None)

        return self._client.chat_thread.update_chat_message(
            chat_thread_id=self._thread_id,
            chat_message_id=message_id,
            update_chat_message_request=update_message_request,
            **kwargs)

    @distributed_trace
    def delete_message(
        self,
        message_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes a message.

        :param message_id: Required. The message id.
        :type message_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START delete_message]
                :end-before: [END delete_message]
                :language: python
                :dedent: 8
                :caption: Deleting a messages.
        """
        if not message_id:
            raise ValueError("message_id cannot be None.")

        return self._client.chat_thread.delete_chat_message(
            chat_thread_id=self._thread_id,
            chat_message_id=message_id,
            **kwargs)

    @distributed_trace
    def list_participants(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[ChatThreadParticipant]
        """Gets the participants of a thread.

        :keyword int results_per_page: The maximum number of participants to be returned per page.
        :keyword int skip: Skips participants up to a specified position in response.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ItemPaged[:class:`~azure.communication.chat.ChatThreadParticipant`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START list_participants]
                :end-before: [END list_participants]
                :language: python
                :dedent: 8
                :caption: Listing participants of chat thread.
        """

        results_per_page = kwargs.pop("results_per_page", None)
        skip = kwargs.pop("skip", None)

        return self._client.chat_thread.list_chat_participants(
            self._thread_id,
            max_page_size=results_per_page,
            skip=skip,
            cls=lambda objs: [ChatThreadParticipant._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs)

    @distributed_trace
    def add_participant(
            self,
            thread_participant,  # type: ChatThreadParticipant
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Adds single thread participant to a thread. If participant already exist, no change occurs.

        :param thread_participant: Required. Single thread participant to be added to the thread.
        :type thread_participant: ~azure.communication.chat.ChatThreadParticipant
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START add_participant]
                :end-before: [END add_participant]
                :language: python
                :dedent: 8
                :caption: Adding single participant to chat thread.
        """
        if not thread_participant:
            raise ValueError("thread_participant cannot be None.")

        participants = [thread_participant._to_generated()]  # pylint:disable=protected-access
        add_thread_participants_request = AddChatParticipantsRequest(participants=participants)

        return self._client.chat_thread.add_chat_participants(
            chat_thread_id=self._thread_id,
            add_chat_participants_request=add_thread_participants_request,
            **kwargs)

    @distributed_trace
    def add_participants(
        self,
        thread_participants,  # type: list[ChatThreadParticipant]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Adds thread participants to a thread. If participants already exist, no change occurs.

        :param thread_participants: Required. Thread participants to be added to the thread.
        :type thread_participants: list[~azure.communication.chat.ChatThreadParticipant]
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START add_participants]
                :end-before: [END add_participants]
                :language: python
                :dedent: 8
                :caption: Adding participants to chat thread.
        """
        if not thread_participants:
            raise ValueError("thread_participants cannot be None.")

        participants = [m._to_generated() for m in thread_participants]  # pylint:disable=protected-access
        add_thread_participants_request = AddChatParticipantsRequest(participants=participants)

        return self._client.chat_thread.add_chat_participants(
            chat_thread_id=self._thread_id,
            add_chat_participants_request=add_thread_participants_request,
            **kwargs)

    @distributed_trace
    def remove_participant(
        self,
        user,  # type: CommunicationUser
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Remove a participant from a thread.

        :param user: Required. User identity of the thread participant to remove from the thread.
        :type user: ~azure.communication.chat.CommunicationUser
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_thread_client_sample.py
                :start-after: [START remove_participant]
                :end-before: [END remove_participant]
                :language: python
                :dedent: 8
                :caption: Removing participant from chat thread.
        """
        if not user:
            raise ValueError("user cannot be None.")

        return self._client.chat_thread.remove_chat_participant(
            chat_thread_id=self._thread_id,
            chat_participant_id=user.identifier,
            **kwargs)

    def close(self):
        # type: () -> None
        return self._client.close()

    def __enter__(self):
        # type: () -> ChatThreadClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
