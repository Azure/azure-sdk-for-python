# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    IO,
    Iterable,
    AnyStr,
    Dict,
    List,
    Tuple,
    TYPE_CHECKING,
)

try:
    from urllib.parse import urlparse, quote, unquote  # pylint: disable=unused-import
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import quote, unquote  # type: ignore

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.core.async_paging import AsyncItemPaged

from azure.storage.queue._shared.base_client_async import AsyncStorageAccountHostsMixin
from azure.storage.queue._shared.request_handlers import add_metadata_headers, serialize_iso
from azure.storage.queue._shared.response_handlers import (
    return_response_headers,
    process_storage_error,
    return_headers_and_deserialized,
)
from azure.storage.queue._deserialize import deserialize_queue_properties, deserialize_queue_creation
from azure.storage.queue._generated.aio import AzureQueueStorage
from azure.storage.queue._generated.models import StorageErrorException, SignedIdentifier
from azure.storage.queue._generated.models import QueueMessage as GenQueueMessage

from azure.storage.queue.models import QueueMessage, AccessPolicy
from azure.storage.queue.aio.models import MessagesPaged
from .._shared.policies_async import ExponentialRetry
from ..queue_client import QueueClient as QueueClientBase


if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.storage.queue.models import QueuePermissions, QueueProperties


class QueueClient(AsyncStorageAccountHostsMixin, QueueClientBase):
    """A async client to interact with a specific Queue.

    :ivar str url:
        The full endpoint URL to the Queue, including SAS token if used. This could be
        either the primary endpoint, or the secondard endpint depending on the current `location_mode`.
    :ivar str primary_endpoint:
        The full primary endpoint URL.
    :ivar str primary_hostname:
        The hostname of the primary endpoint.
    :ivar str secondary_endpoint:
        The full secondard endpoint URL if configured. If not available
        a ValueError will be raised. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str secondary_hostname:
        The hostname of the secondary endpoint. If not available this
        will be None. To explicitly specify a secondary hostname, use the optional
        `secondary_hostname` keyword argument on instantiation.
    :ivar str location_mode:
        The location mode that the client is currently using. By default
        this will be "primary". Options include "primary" and "secondary".
    :param str queue_url: The full URI to the queue. This can also be a URL to the storage
        account, in which case the queue must also be specified.
    :param queue: The queue. If specified, this value will override
        a queue value specified in the queue URL.
    :type queue: str or ~azure.storage.queue.models.QueueProperties
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, and account
        shared access key, or an instance of a TokenCredentials class from azure.identity.

    Example:
        .. literalinclude:: ../tests/test_queue_samples_message.py
            :start-after: [START create_queue_client]
            :end-before: [END create_queue_client]
            :language: python
            :dedent: 12
            :caption: Create the queue client with url and credential.
    """

    def __init__(
        self,
        queue_url,  # type: str
        queue=None,  # type: Optional[Union[QueueProperties, str]]
        credential=None,  # type: Optional[Any]
        loop=None,  # type: Any
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        kwargs["retry_policy"] = kwargs.get("retry_policy") or ExponentialRetry(**kwargs)
        super(QueueClient, self).__init__(queue_url, queue=queue, credential=credential, loop=loop, **kwargs)
        self._client = AzureQueueStorage(self.url, pipeline=self._pipeline, loop=loop)  # type: ignore
        self._loop = loop

    @distributed_trace_async
    async def create_queue(self, metadata=None, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[Dict[str, Any]], Optional[int], Optional[Any]) -> None
        """Creates a new queue in the storage account.

        If a queue with the same name already exists, the operation fails.

        :param metadata:
            A dict containing name-value pairs to associate with the queue as
            metadata. Note that metadata names preserve the case with which they
            were created, but are case-insensitive when set or read.
        :type metadata: dict(str, str)
        :param int timeout:
            The server timeout, expressed in seconds.
        :return: None or the result of cls(response)
        :rtype: None
        :raises:
            ~azure.storage.queue._generated.models._models.StorageErrorException

        Example:
            .. literalinclude:: ../tests/test_queue_samples_hello_world.py
                :start-after: [START create_queue]
                :end-before: [END create_queue]
                :language: python
                :dedent: 8
                :caption: Create a queue.
        """
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))  # type: ignore
        try:
            return await self._client.queue.create(  # type: ignore
                metadata=metadata, timeout=timeout, headers=headers, cls=deserialize_queue_creation, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def delete_queue(self, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[int], Optional[Any]) -> None
        """Deletes the specified queue and any messages it contains.

        When a queue is successfully deleted, it is immediately marked for deletion
        and is no longer accessible to clients. The queue is later removed from
        the Queue service during garbage collection.

        Note that deleting a queue is likely to take at least 40 seconds to complete.
        If an operation is attempted against the queue while it was being deleted,
        an :class:`HttpResponseError` will be thrown.

        :param int timeout:
            The server timeout, expressed in seconds.
        :rtype: None

        Example:
            .. literalinclude:: ../tests/test_queue_samples_hello_world.py
                :start-after: [START delete_queue]
                :end-before: [END delete_queue]
                :language: python
                :dedent: 12
                :caption: Delete a queue.
        """
        try:
            await self._client.queue.delete(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_queue_properties(self, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[int], Optional[Any]) -> QueueProperties
        """Returns all user-defined metadata for the specified queue.

        The data returned does not include the queue's list of messages.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Properties for the specified container within a container object.
        :rtype: ~azure.storage.queue.models.QueueProperties

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START get_queue_properties]
                :end-before: [END get_queue_properties]
                :language: python
                :dedent: 12
                :caption: Get the properties on the queue.
        """
        try:
            response = await self._client.queue.get_properties(
                timeout=timeout, cls=deserialize_queue_properties, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
        response.name = self.queue_name
        return response  # type: ignore

    @distributed_trace_async
    async def set_queue_metadata(self, metadata=None, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[Dict[str, Any]], Optional[int], Optional[Any]) -> None
        """Sets user-defined metadata on the specified queue.

        Metadata is associated with the queue as name-value pairs.

        :param metadata:
            A dict containing name-value pairs to associate with the
            queue as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The server timeout, expressed in seconds.

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START set_queue_metadata]
                :end-before: [END set_queue_metadata]
                :language: python
                :dedent: 12
                :caption: Set metadata on the queue.
        """
        headers = kwargs.pop("headers", {})
        headers.update(add_metadata_headers(metadata))  # type: ignore
        try:
            return await self._client.queue.set_metadata(  # type: ignore
                timeout=timeout, headers=headers, cls=return_response_headers, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def get_queue_access_policy(self, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[int], Optional[Any]) -> Dict[str, Any]
        """Returns details about any stored access policies specified on the
        queue that may be used with Shared Access Signatures.

        :param int timeout:
            The server timeout, expressed in seconds.
        :return: A dictionary of access policies associated with the queue.
        :rtype: dict(str, :class:`~azure.storage.queue.models.AccessPolicy`)
        """
        try:
            _, identifiers = await self._client.queue.get_access_policy(
                timeout=timeout, cls=return_headers_and_deserialized, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace_async
    async def set_queue_access_policy(self, signed_identifiers=None, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[Dict[str, Optional[AccessPolicy]]], Optional[int], Optional[Any]) -> None
        """Sets stored access policies for the queue that may be used with Shared
        Access Signatures.

        When you set permissions for a queue, the existing permissions are replaced.
        To update the queue's permissions, call :func:`~get_queue_access_policy` to fetch
        all access policies associated with the queue, modify the access policy
        that you wish to change, and then call this function with the complete
        set of data to perform the update.

        When you establish a stored access policy on a queue, it may take up to
        30 seconds to take effect. During this interval, a shared access signature
        that is associated with the stored access policy will throw an
        :class:`HttpResponseError` until the access policy becomes active.

        :param signed_identifiers:
            A list of SignedIdentifier access policies to associate with the queue.
            The list may contain up to 5 elements. An empty list
            will clear the access policies set on the service.
        :type signed_identifiers: dict(str, :class:`~azure.storage.queue.models.AccessPolicy`)
        :param int timeout:
            The server timeout, expressed in seconds.

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START set_access_policy]
                :end-before: [END set_access_policy]
                :language: python
                :dedent: 12
                :caption: Set an access policy on the queue.
        """
        if signed_identifiers:
            if len(signed_identifiers) > 15:
                raise ValueError(
                    "Too many access policies provided. The server does not support setting "
                    "more than 15 access policies on a single resource."
                )
            identifiers = []
            for key, value in signed_identifiers.items():
                if value:
                    value.start = serialize_iso(value.start)
                    value.expiry = serialize_iso(value.expiry)
                identifiers.append(SignedIdentifier(id=key, access_policy=value))
            signed_identifiers = identifiers  # type: ignore
        try:
            await self._client.queue.set_access_policy(queue_acl=signed_identifiers or None, timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def enqueue_message(  # type: ignore
        self,
        content,  # type: Any
        visibility_timeout=None,  # type: Optional[int]
        time_to_live=None,  # type: Optional[int]
        timeout=None,  # type: Optional[int]
        **kwargs  # type: Optional[Any]
    ):
        # type: (...) -> QueueMessage
        """Adds a new message to the back of the message queue.

        The visibility timeout specifies the time that the message will be
        invisible. After the timeout expires, the message will become visible.
        If a visibility timeout is not specified, the default value of 0 is used.

        The message time-to-live specifies how long a message will remain in the
        queue. The message will be deleted from the queue when the time-to-live
        period expires.

        If the key-encryption-key field is set on the local service object, this method will
        encrypt the content before uploading.

        :param obj content:
            Message content. Allowed type is determined by the encode_function
            set on the service. Default is str. The encoded message can be up to
            64KB in size.
        :param int visibility_timeout:
            If not specified, the default value is 0. Specifies the
            new visibility timeout value, in seconds, relative to server time.
            The value must be larger than or equal to 0, and cannot be
            larger than 7 days. The visibility timeout of a message cannot be
            set to a value later than the expiry time. visibility_timeout
            should be set to a value smaller than the time-to-live value.
        :param int time_to_live:
            Specifies the time-to-live interval for the message, in
            seconds. The time-to-live may be any positive number or -1 for infinity. If this
            parameter is omitted, the default time-to-live is 7 days.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A :class:`~azure.storage.queue.models.QueueMessage` object.
            This object is also populated with the content although it is not
            returned from the service.
        :rtype: ~azure.storage.queue.models.QueueMessage

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START enqueue_messages]
                :end-before: [END enqueue_messages]
                :language: python
                :dedent: 12
                :caption: Enqueue messages.
        """
        self._config.message_encode_policy.configure(
            self.require_encryption, self.key_encryption_key, self.key_resolver_function
        )
        content = self._config.message_encode_policy(content)
        new_message = GenQueueMessage(message_text=content)

        try:
            enqueued = await self._client.messages.enqueue(
                queue_message=new_message,
                visibilitytimeout=visibility_timeout,
                message_time_to_live=time_to_live,
                timeout=timeout,
                **kwargs
            )
            queue_message = QueueMessage(content=new_message.message_text)
            queue_message.id = enqueued[0].message_id
            queue_message.insertion_time = enqueued[0].insertion_time
            queue_message.expiration_time = enqueued[0].expiration_time
            queue_message.pop_receipt = enqueued[0].pop_receipt
            queue_message.time_next_visible = enqueued[0].time_next_visible
            return queue_message
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace
    def receive_messages(self, messages_per_page=None, visibility_timeout=None, timeout=None, **kwargs): # type: ignore
        # type: (Optional[int], Optional[int], Optional[int], Optional[Any]) -> AsyncItemPaged[Message]
        """Removes one or more messages from the front of the queue.

        When a message is retrieved from the queue, the response includes the message
        content and a pop_receipt value, which is required to delete the message.
        The message is not automatically deleted from the queue, but after it has
        been retrieved, it is not visible to other clients for the time interval
        specified by the visibility_timeout parameter.

        If the key-encryption-key or resolver field is set on the local service object, the messages will be
        decrypted before being returned.

        :param int messages_per_page:
            A nonzero integer value that specifies the number of
            messages to retrieve from the queue, up to a maximum of 32. If
            fewer are visible, the visible messages are returned. By default,
            a single message is retrieved from the queue with this operation.
        :param int visibility_timeout:
            If not specified, the default value is 0. Specifies the
            new visibility timeout value, in seconds, relative to server time.
            The value must be larger than or equal to 0, and cannot be
            larger than 7 days. The visibility timeout of a message cannot be
            set to a value later than the expiry time. visibility_timeout
            should be set to a value smaller than the time-to-live value.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            Returns a message iterator of dict-like Message objects.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.storage.queue.models.Message]

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START receive_messages]
                :end-before: [END receive_messages]
                :language: python
                :dedent: 12
                :caption: Receive messages from the queue.
        """
        self._config.message_decode_policy.configure(
            self.require_encryption, self.key_encryption_key, self.key_resolver_function
        )
        try:
            command = functools.partial(
                self._client.messages.dequeue,
                visibilitytimeout=visibility_timeout,
                timeout=timeout,
                cls=self._config.message_decode_policy,
                **kwargs
            )
            return AsyncItemPaged(command, results_per_page=messages_per_page, page_iterator_class=MessagesPaged)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def update_message(
        self,
        message,
        visibility_timeout=None,
        pop_receipt=None,  # type: ignore
        content=None,
        timeout=None,
        **kwargs
    ):
        # type: (Any, int, Optional[str], Optional[Any], Optional[int], Any) -> QueueMessage
        """Updates the visibility timeout of a message. You can also use this
        operation to update the contents of a message.

        This operation can be used to continually extend the invisibility of a
        queue message. This functionality can be useful if you want a worker role
        to "lease" a queue message. For example, if a worker role calls :func:`~receive_messages()`
        and recognizes that it needs more time to process a message, it can
        continually extend the message's invisibility until it is processed. If
        the worker role were to fail during processing, eventually the message
        would become visible again and another worker role could process it.

        If the key-encryption-key field is set on the local service object, this method will
        encrypt the content before uploading.

        :param str message:
            The message object or id identifying the message to update.
        :param int visibility_timeout:
            Specifies the new visibility timeout value, in seconds,
            relative to server time. The new value must be larger than or equal
            to 0, and cannot be larger than 7 days. The visibility timeout of a
            message cannot be set to a value later than the expiry time. A
            message can be updated until it has been deleted or has expired.
            The message object or message id identifying the message to update.
        :param str pop_receipt:
            A valid pop receipt value returned from an earlier call
            to the :func:`~receive_messages` or :func:`~update_message` operation.
        :param obj content:
            Message content. Allowed type is determined by the encode_function
            set on the service. Default is str.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A :class:`~azure.storage.queue.models.QueueMessage` object. For convenience,
            this object is also populated with the content, although it is not returned by the service.
        :rtype: ~azure.storage.queue.models.QueueMessage

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START update_message]
                :end-before: [END update_message]
                :language: python
                :dedent: 12
                :caption: Update a message.
        """
        try:
            message_id = message.id
            message_text = content or message.content
            receipt = pop_receipt or message.pop_receipt
            insertion_time = message.insertion_time
            expiration_time = message.expiration_time
            dequeue_count = message.dequeue_count
        except AttributeError:
            message_id = message
            message_text = content
            receipt = pop_receipt
            insertion_time = None
            expiration_time = None
            dequeue_count = None

        if receipt is None:
            raise ValueError("pop_receipt must be present")
        if message_text is not None:
            self._config.message_encode_policy.configure(
                self.require_encryption, self.key_encryption_key, self.key_resolver_function
            )
            message_text = self._config.message_encode_policy(message_text)
            updated = GenQueueMessage(message_text=message_text)
        else:
            updated = None  # type: ignore
        try:
            response = await self._client.message_id.update(
                queue_message=updated,
                visibilitytimeout=visibility_timeout or 0,
                timeout=timeout,
                pop_receipt=receipt,
                cls=return_response_headers,
                queue_message_id=message_id,
                **kwargs
            )
            new_message = QueueMessage(content=message_text)
            new_message.id = message_id
            new_message.insertion_time = insertion_time
            new_message.expiration_time = expiration_time
            new_message.dequeue_count = dequeue_count
            new_message.pop_receipt = response["popreceipt"]
            new_message.time_next_visible = response["time_next_visible"]
            return new_message
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def peek_messages(self, max_messages=None, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[int], Optional[int], Optional[Any]) -> List[QueueMessage]
        """Retrieves one or more messages from the front of the queue, but does
        not alter the visibility of the message.

        Only messages that are visible may be retrieved. When a message is retrieved
        for the first time with a call to :func:`~receive_messages`, its dequeue_count property
        is set to 1. If it is not deleted and is subsequently retrieved again, the
        dequeue_count property is incremented. The client may use this value to
        determine how many times a message has been retrieved. Note that a call
        to peek_messages does not increment the value of DequeueCount, but returns
        this value for the client to read.

        If the key-encryption-key or resolver field is set on the local service object,
        the messages will be decrypted before being returned.

        :param int max_messages:
            A nonzero integer value that specifies the number of
            messages to peek from the queue, up to a maximum of 32. By default,
            a single message is peeked from the queue with this operation.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A list of :class:`~azure.storage.queue.models.QueueMessage` objects. Note that
            time_next_visible and pop_receipt will not be populated as peek does
            not pop the message and can only retrieve already visible messages.
        :rtype: list(:class:`~azure.storage.queue.models.QueueMessage`)

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START peek_message]
                :end-before: [END peek_message]
                :language: python
                :dedent: 12
                :caption: Peek messages.
        """
        if max_messages and not 1 <= max_messages <= 32:
            raise ValueError("Number of messages to peek should be between 1 and 32")
        self._config.message_decode_policy.configure(
            self.require_encryption, self.key_encryption_key, self.key_resolver_function
        )
        try:
            messages = await self._client.messages.peek(
                number_of_messages=max_messages, timeout=timeout, cls=self._config.message_decode_policy, **kwargs
            )
            wrapped_messages = []
            for peeked in messages:
                wrapped_messages.append(QueueMessage._from_generated(peeked))  # pylint: disable=protected-access
            return wrapped_messages
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def clear_messages(self, timeout=None, **kwargs):  # type: ignore
        # type: (Optional[int], Optional[Any]) -> None
        """Deletes all messages from the specified queue.

        :param int timeout:
            The server timeout, expressed in seconds.

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START clear_messages]
                :end-before: [END clear_messages]
                :language: python
                :dedent: 12
                :caption: Clears all messages.
        """
        try:
            await self._client.messages.clear(timeout=timeout, **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    @distributed_trace_async
    async def delete_message(self, message, pop_receipt=None, timeout=None, **kwargs):  # type: ignore
        # type: (Any, Optional[str], Optional[str], Optional[int]) -> None
        """Deletes the specified message.

        Normally after a client retrieves a message with the receive messages operation,
        the client is expected to process and delete the message. To delete the
        message, you must have the message object itself, or two items of data: id and pop_receipt.
        The id is returned from the previous receive_messages operation. The
        pop_receipt is returned from the most recent :func:`~receive_messages` or
        :func:`~update_message` operation. In order for the delete_message operation
        to succeed, the pop_receipt specified on the request must match the
        pop_receipt returned from the :func:`~receive_messages` or :func:`~update_message`
        operation.

        :param str message:
            The message object or id identifying the message to delete.
        :param str pop_receipt:
            A valid pop receipt value returned from an earlier call
            to the :func:`~receive_messages` or :func:`~update_message`.
        :param int timeout:
            The server timeout, expressed in seconds.

        Example:
            .. literalinclude:: ../tests/test_queue_samples_message.py
                :start-after: [START delete_message]
                :end-before: [END delete_message]
                :language: python
                :dedent: 12
                :caption: Delete a message.
        """
        try:
            message_id = message.id
            receipt = pop_receipt or message.pop_receipt
        except AttributeError:
            message_id = message
            receipt = pop_receipt

        if receipt is None:
            raise ValueError("pop_receipt must be present")
        try:
            await self._client.message_id.delete(
                pop_receipt=receipt, timeout=timeout, queue_message_id=message_id, **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
