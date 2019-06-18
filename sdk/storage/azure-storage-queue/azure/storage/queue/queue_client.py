# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from ._utils import (
    create_client,
    create_configuration,
    create_pipeline,
    parse_query,
    is_credential_sastoken,
    parse_connection_str,
    process_storage_error,
    basic_error_map,
    add_metadata_headers,
    return_response_headers,
    return_headers_and_deserialized
)

from ._deserialize import (
    deserialize_queue_properties
)

from .models import SignedIdentifier, QueueMessage
from ._generated.models import StorageErrorException
from .queue_iterator import QueueIterator

from azure.core import Configuration
try:
    from urllib.parse import urlparse, quote, unquote, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib2 import quote, unquote

if TYPE_CHECKING:
    from azure.core.pipeline.policies import HTTPPolicy


class QueueClient(object):

    def __init__(
            self, queue_url,  # type: str
            queue_name=None,  # type: Optional[str]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """Creates a new QueueClient. This client represents interaction with a specific
        queue, although that queue may not yet exist.
        :param str queue_url: The full URI to the queue.
        :param ~azure.storage.queue.authentication.SharedKeyCredentials credentials: Optional shared
         key credentials. This is not necessary if the URL contains a SAS token, or if the queue is
         publicly available.
        :param configuration: A optional pipeline configuration.
         This can be retrieved with :func:`QueueClient.create_configuration()`
        """
        parsed_url = urlparse(queue_url.rstrip('/'))
        if not parsed_url.path and not queue_name:
            raise ValueError("Please specify a queue name.")
        self.queue_name = queue_name or unquote(parsed_url.path.split('/')[1])

        self.scheme = parsed_url.scheme
        self.credentials = credentials
        self.account = parsed_url.hostname.split(".queue.core.")[0]
        self.queue_url = queue_url if parsed_url.path else "{}://{}/{}".format(
            self.scheme,
            parsed_url.hostname,
            quote(self.queue_name)
        )

        self.require_encryption = kwargs.get('require_encryption', False)
        self.key_encryption_key = kwargs.get('key_encryption_key')
        self.key_resolver_function = kwargs.get('key_resolver_function')

        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(self.queue_url, self._pipeline)
        self._queue_iterator = QueueIterator()

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            queue_name=None,  # type: Optional[str]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        """
        Create QueueClient from a Connection String.
        """
        account_url, creds = parse_connection_str(conn_str)
        return cls(
            account_url, queue_name=queue_name,
            credentials=creds, configuration=configuration, **kwargs)

    def create_queue(self, metadata=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, Any]], Optional[int]) -> bool
        """
        Creates a queue under the given account.
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
         :class:`StorageErrorException<queue.models.StorageErrorException>`
        """
        if self.require_encryption or (self.key_encryption_key is not None):
            raise ValueError('The require_encryption flag is set, but encryption is not supported for this method.')
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.queue.create(
                metadata=metadata,
                timeout=timeout,
                error_map=basic_error_map(),
                headers=headers,
                cls=return_response_headers,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
    
    def delete_queue(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> bool
        """
        Deletes the specified queue and any messages it contains.
        When a queue is successfully deleted, it is immediately marked for deletion 
        and is no longer accessible to clients. The queue is later removed from 
        the Queue service during garbage collection.
        Note that deleting a queue is likely to take at least 40 seconds to complete. 
        If an operation is attempted against the queue while it was being deleted, 
        an :class:`AzureConflictHttpError` will be thrown.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A boolean indicating whether the queue was deleted. If fail_not_exist 
            was set to True, this will throw instead of returning false.
        :rtype: bool
        """
        try:
            self._client.queue.delete(
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def get_queue_metadata(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """
        Retrieves user-defined metadata and queue properties on the specified
        queue. Metadata is associated with the queue as name-value pairs.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A dictionary representing the queue metadata with an 
            approximate_message_count int property on the dict estimating the 
            number of messages in the queue.
        :rtype: dict(str, str)
        """
        try:
            queue_props = self._client.queue.get_properties(
                timeout=timeout,
                error_map=basic_error_map(),
                cls=deserialize_queue_properties,
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
        queue_props.name = self.queue_name
        return queue_props

    def set_queue_metadata(self, metadata=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, Any]], Optional[int]) -> None
        """
        Sets user-defined metadata on the specified queue. Metadata is
        associated with the queue as name-value pairs.
        :param dict metadata:
            A dict containing name-value pairs to associate with the
            queue as metadata.
        :param int timeout:
            The server timeout, expressed in seconds.
        """
        try:
            return self._client.queue.set_metadata(
                metadata=metadata,
                timeout=timeout,
                error_map=basic_error_map(),
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_queue_acl(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, Any]
        """
        Returns details about any stored access policies specified on the
        queue that may be used with Shared Access Signatures.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return: A dictionary of access policies associated with the queue.
        :rtype: dict(str, :class:`~azure.storage.common.models.AccessPolicy`)
        """
        try:
            response, identifiers = self._client.queue.get_access_policy(
                timeout=timeout,
                error_map=basic_error_map(),
                cls=return_headers_and_deserialized,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return {
            'response': response,
            'signed_identifiers': identifiers or []
        }

    def set_queue_acl(self, signed_identifiers=None, timeout=None, **kwargs):
        # type: (Optional[List[SignedIdentifier]], Optional[int]) -> None
        """
        Sets stored access policies for the queue that may be used with Shared 
        Access Signatures. 
        
        When you set permissions for a queue, the existing permissions are replaced. 
        To update the queue's permissions, call :func:`~get_queue_acl` to fetch 
        all access policies associated with the queue, modify the access policy 
        that you wish to change, and then call this function with the complete 
        set of data to perform the update.
        When you establish a stored access policy on a queue, it may take up to 
        30 seconds to take effect. During this interval, a shared access signature 
        that is associated with the stored access policy will throw an 
        :class:`AzureHttpError` until the access policy becomes active.
        :param signed_identifiers:
            A list of SignedIdentifier access policies to associate with the queue. The 
            list may contain up to 5 elements. An empty list 
            will clear the access policies set on the service. 
        :type signed_identifiers: dict(str, :class:`queue.models.SignedIdentifier`)
        :param int timeout:
            The server timeout, expressed in seconds.
        """
        if signed_identifiers and len(signed_identifiers) > 15:
            raise ValueError("Too many access policies")
        try:
            self._client.queue.set_access_policy(
                queue_acl=signed_identifiers,
                timeout=timeout,
                error_map=basic_error_map(),
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def enqueue_message(self, content, visibility_timeout=None, time_to_live=None, timeout=None, **kwargs):
        # type: (Any, Optional[int], Optional[int], Optional[int]) -> QueueMessage
        """
        Adds a new message to the back of the message queue. 
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
        :rtype: :class:`~azure.storage.queue.models.QueueMessage`
        """
        queue_message = QueueMessage(content=content)

        try:
            self._queue_iterator.put(queue_message)
            self._client.messages.enqueue(
                queue_message=queue_message,
                visibilitytimeout=visibility_timeout,
                message_time_to_live=time_to_live,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
            return queue_message
        except StorageErrorException as error:
            process_storage_error(error)

    def dequeue_messages(self, visibility_timeout=None, timeout=None, **kwargs):
        # type: (Optional[int], Optional[int]) -> QueueMessage
        """
        Removes one or more messages from top of the queue.
        Returns message iterator of dict-like Message objects
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
            A :class:`~azure.storage.queue.models.QueueMessage` object.
            This object is also populated with the content although it is not
            returned from the service.
        :rtype: :class:`~azure.storage.queue.models.QueueMessage`
        """
        try:
            message = self._client.messages.dequeue(
                visibilitytimeout=visibility_timeout,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
            next(self._queue_iterator)
            return message
        except StorageErrorException as error:
            process_storage_error(error)

    def update_message(self, message, visibility_timeout=None, pop_receipt=None,
                       content=None, timeout=None, **kwargs):
        # type: (Any, int, Optional[str], Optional[Any], Optional[int], Any) -> List[QueueMessage]
        """
        Updates the visibility timeout of a message. You can also use this
        operation to update the contents of a message.
        This operation can be used to continually extend the invisibility of a 
        queue message. This functionality can be useful if you want a worker role 
        to "lease" a queue message. For example, if a worker role calls get_messages 
        and recognizes that it needs more time to process a message, it can 
        continually extend the message's invisibility until it is processed. If 
        the worker role were to fail during processing, eventually the message 
        would become visible again and another worker role could process it.
        If the key-encryption-key field is set on the local service object, this method will
        encrypt the content before uploading.
        :param str queue_name:
            The name of the queue containing the message to update.
        :param str message:
            The message object or message id identifying the message to update.
        :param str pop_receipt:
            A valid pop receipt value returned from an earlier call
            to the :func:`~get_messages` or :func:`~update_message` operation.
        :param int visibility_timeout:
            Specifies the new visibility timeout value, in seconds,
            relative to server time. The new value must be larger than or equal
            to 0, and cannot be larger than 7 days. The visibility timeout of a
            message cannot be set to a value later than the expiry time. A
            message can be updated until it has been deleted or has expired.
        :param obj content:
            Message content. Allowed type is determined by the encode_function 
            set on the service. Default is str.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return: 
            A list of :class:`~azure.storage.queue.models.QueueMessage` objects. For convenience,
            this object is also populated with the content, although it is not returned by the service.
        :rtype: list(:class:`~azure.storage.queue.models.QueueMessage`)
        """
        pop_receipt = pop_receipt or message.pop_receipt
        if pop_receipt is None:
            raise ValueError("pop_receipt must be present")
        try:
            self._client.message_id.update(
                queue_message=message,
                visibilitytimeout=visibility_timeout,
                timeout=timeout,
                pop_receipt=pop_receipt,
                error_map=basic_error_map(),
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def peek_messages(self, max_messages=None, timeout=None, **kwargs):
        # type: (Optional[int], Optional[int]) -> List[QueueMessage]
        """
        Retrieves one or more messages from the front of the queue, but does
        not alter the visibility of the message.
        Only messages that are visible may be retrieved. When a message is retrieved 
        for the first time with a call to get_messages, its dequeue_count property 
        is set to 1. If it is not deleted and is subsequently retrieved again, the 
        dequeue_count property is incremented. The client may use this value to 
        determine how many times a message has been retrieved. Note that a call 
        to peek_messages does not increment the value of DequeueCount, but returns 
        this value for the client to read.
        If the key-encryption-key or resolver field is set on the local service object, the messages will be
        decrypted before being returned.
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
        """
        if max_messages and not 1 <= max_messages <= 32:
            raise ValueError("Number of messages to peek should be between 1 and 32")
        try:
            return self._client.messages.peek(
                number_of_messages=max_messages,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def clear_messages(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> None
        """
        Deletes all messages from the specified queue.
        :param int timeout:
            The server timeout, expressed in seconds.
        """
        try:
            self._client.messages.clear(
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)

    def delete_message(self, message=None, pop_receipt=None, timeout=None, **kwargs):
        # type: (Any, Optional[str], Optional[str], Optional[int]) -> None
        """
        Deletes the specified message.
        Normally after a client retrieves a message with the get_messages operation, 
        the client is expected to process and delete the message. To delete the 
        message, you must have two items of data: id and pop_receipt. The 
        id is returned from the previous get_messages operation. The 
        pop_receipt is returned from the most recent :func:`~get_messages` or 
        :func:`~update_message` operation. In order for the delete_message operation 
        to succeed, the pop_receipt specified on the request must match the 
        pop_receipt returned from the :func:`~get_messages` or :func:`~update_message` 
        operation.
        
        :param str message:
            The message object identifying the message to delete.
        :param str pop_receipt:
            A valid pop receipt value returned from an earlier call
            to the :func:`~get_messages` or :func:`~update_message`.
        :param int timeout:
            The server timeout, expressed in seconds.
        """
        if not message and not pop_receipt:
            raise ValueError("Either a message object or a pop receipt must be given")
        pop_receipt = pop_receipt or message.pop_receipt
        if not pop_receipt:
            raise ValueError("pop_receipt is required.")
        try:
            self._client.message_id.delete(
                pop_receipt=pop_receipt,
                timeout=timeout,
                error_map=basic_error_map(),
                **kwargs
            )
        except StorageErrorException as error:
            process_storage_error(error)
