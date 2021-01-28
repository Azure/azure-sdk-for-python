# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from uuid import uuid4
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.tracing.decorator import distributed_trace

from ._chat_thread_client import ChatThreadClient
from ._common import CommunicationUserCredentialPolicy
from ._shared.user_credential import CommunicationUserCredential
from ._generated import AzureCommunicationChatService
from ._generated.models import CreateChatThreadRequest
from ._models import (
    ChatThread,
    ChatThreadParticipant
)
from ._utils import _to_utc_datetime, return_response # pylint: disable=unused-import
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
    from datetime import datetime
    from azure.core.paging import ItemPaged


class ChatClient(object):
    """A client to interact with the AzureCommunicationService Chat gateway.

    This client provides operations to create chat thread, delete chat thread,
    get chat thread by id, list chat threads, create chat thread client.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param CommunicationUserCredential credential:
        The credentials with which to authenticate.

    .. admonition:: Example:

        .. literalinclude:: ../samples/chat_client_sample.py
            :start-after: [START create_chat_client]
            :end-before: [END create_chat_client]
            :language: python
            :dedent: 8
            :caption: Creating the ChatClient from a URL and token.
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: CommunicationUserCredential
            **kwargs  # type: Any
    ):
        # type: (...) -> None
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

        self._endpoint = endpoint
        self._credential = credential

        self._client = AzureCommunicationChatService(
            self._endpoint,
            authentication_policy=CommunicationUserCredentialPolicy(self._credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs
        )

    @distributed_trace
    def get_chat_thread_client(
        self, thread_id, # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ChatThreadClient
        """
        Get ChatThreadClient by providing a thread_id.

        :param thread_id: Required. The thread id.
        :type thread_id: str
        :return: ChatThreadClient
        :rtype: ~azure.communication.chat.ChatThreadClient
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_client_sample.py
                :start-after: [START get_chat_thread_client]
                :end-before: [END get_chat_thread_client]
                :language: python
                :dedent: 8
                :caption: Creating the ChatThreadClient from an existing chat thread id.
        """
        if not thread_id:
            raise ValueError("thread_id cannot be None.")

        return ChatThreadClient(
            endpoint=self._endpoint,
            credential=self._credential,
            thread_id=thread_id,
            **kwargs
        )

    @distributed_trace
    def create_chat_thread(
        self, topic,  # type: str
        thread_participants,  # type: list[ChatThreadParticipant]
        repeatability_request_id=None,  # type: Optional[str]
        **kwargs  # type: Any
    ):
        # type: (...) -> ChatThreadClient
        """Creates a chat thread.

        :param topic: Required. The thread topic.
        :type topic: str
        :param thread_participants: Required. Participants to be added to the thread.
        :type thread_participants: list[~azure.communication.chat.ChatThreadParticipant]
        :param repeatability_request_id: If specified, the client directs that the request is
         repeatable; that is, that the client can make the request multiple times with the same
         Repeatability-Request-ID and get back an appropriate response without the server executing the
         request multiple times. The value of the Repeatability-Request-ID is an opaque string
         representing a client-generated, globally unique for all time, identifier for the request. If not
         specified, a new unique id would be generated.
        :type repeatability_request_id: str
        :return: ChatThreadClient
        :rtype: ~azure.communication.chat.ChatThreadClient
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_client_sample.py
                :start-after: [START create_thread]
                :end-before: [END create_thread]
                :language: python
                :dedent: 8
                :caption: Creating ChatThreadClient by creating a new chat thread.
        """
        if not topic:
            raise ValueError("topic cannot be None.")
        if not thread_participants:
            raise ValueError("List of ChatThreadParticipant cannot be None.")
        if repeatability_request_id is None:
            repeatability_request_id = str(uuid4())

        participants = [m._to_generated() for m in thread_participants]  # pylint:disable=protected-access
        create_thread_request = \
            CreateChatThreadRequest(topic=topic, participants=participants)

        create_chat_thread_result = self._client.chat.create_chat_thread(
            create_chat_thread_request=create_thread_request,
            repeatability_request_id=repeatability_request_id,
            **kwargs)
        if hasattr(create_chat_thread_result, 'errors') and \
                create_chat_thread_result.errors is not None:
            participants = \
                create_chat_thread_result.errors.invalid_participants
            errors = []
            for participant in participants:
                errors.append('participant ' + participant.target +
                ' failed to join thread due to: ' + participant.message)
            raise RuntimeError(errors)
        thread_id = create_chat_thread_result.chat_thread.id
        return ChatThreadClient(
            endpoint=self._endpoint,
            credential=self._credential,
            thread_id=thread_id,
            **kwargs
        )

    @distributed_trace
    def get_chat_thread(
        self, thread_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ChatThread
        """Gets a chat thread.

        :param thread_id: Required. Thread id to get.
        :type thread_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ChatThread, or the result of cls(response)
        :rtype: ~azure.communication.chat.ChatThread
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_client_sample.py
                :start-after: [START get_thread]
                :end-before: [END get_thread]
                :language: python
                :dedent: 8
                :caption: Getting a chat thread by thread id.
        """
        if not thread_id:
            raise ValueError("thread_id cannot be None.")

        chat_thread = self._client.chat.get_chat_thread(thread_id, **kwargs)
        return ChatThread._from_generated(chat_thread)  # pylint:disable=protected-access

    @distributed_trace
    def list_chat_threads(
        self,
        **kwargs
    ):
        # type: (...) -> ItemPaged[ChatThreadInfo]
        """Gets the list of chat threads of a user.

        :keyword int results_per_page: The maximum number of chat threads returned per page.
        :keyword ~datetime.datetime start_time: The earliest point in time to get chat threads up to.
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ItemPaged[:class:`~azure.communication.chat.ChatThreadInfo`]
        :rtype: ~azure.core.paging.ItemPaged
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_client_sample.py
                :start-after: [START list_threads]
                :end-before: [END list_threads]
                :language: python
                :dedent: 8
                :caption: listing chat threads.
        """
        results_per_page = kwargs.pop("results_per_page", None)
        start_time = kwargs.pop("start_time", None)

        return self._client.chat.list_chat_threads(
            max_page_size=results_per_page,
            start_time=start_time,
            **kwargs)

    @distributed_trace
    def delete_chat_thread(
        self,
        thread_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes a thread.

        :param thread_id: Required. Thread id to delete.
        :type thread_id: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/chat_client_sample.py
                :start-after: [START delete_thread]
                :end-before: [END delete_thread]
                :language: python
                :dedent: 8
                :caption: deleting chat thread.
        """
        if not thread_id:
            raise ValueError("thread_id cannot be None.")

        return self._client.chat.delete_chat_thread(thread_id, **kwargs)

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> ChatClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
