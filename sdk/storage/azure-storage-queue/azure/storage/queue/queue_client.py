# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from azure.core import Configuration

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

    def create_queue(self, metadata=None, timeout=None):
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
        :return:
            A boolean indicating whether the queue was created. If fail_on_exist 
            was set to True, this will throw instead of returning false.
        :rtype: bool
        """
    
    def delete_queue(self, timeout=None):
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

    def get_queue_metadata(self, timeout=None):
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

    def set_queue_metadata(self, metadata=None, timeout=None):
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

    def get_queue_acl(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, Any]
        """
        Returns details about any stored access policies specified on the
        queue that may be used with Shared Access Signatures.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return: A dictionary of access policies associated with the queue.
        :rtype: dict(str, :class:`~azure.storage.common.models.AccessPolicy`)
        """

    def set_queue_acl(self, signed_identifiers=None, timeout=None):
        # type: (Optional[Dict[Any, Any]], Optional[int]) -> None
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
            A dictionary of access policies to associate with the queue. The 
            dictionary may contain up to 5 elements. An empty dictionary 
            will clear the access policies set on the service. 
        :type signed_identifiers: dict(str, :class:`~azure.storage.common.models.AccessPolicy`)
        :param int timeout:
            The server timeout, expressed in seconds.
        """

    def enqueue_message(self, content, visibility_timeout=None, time_to_live=None, timeout=None):
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

    def dequeue_messages(self, visibility_timeout=None, timeout=None):
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

    def update_message(self, message, visibility_timeout, pop_receipt=None,
                       content=None, timeout=None):
        # type: (Any, int, Optional[str], Optional[Any], Optional[int]) -> List[QueueMessage]
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

    def peek_messages(self, max_messages=None, timeout=None):
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

    def clear_messages(self, timeout=None):
        # type: (Optional[int]) -> None
        """
        Deletes all messages from the specified queue.
        :param int timeout:
            The server timeout, expressed in seconds.
        """

    def delete_message(self, message, pop_receipt=None, timeout=None):
        # type: (Any, int, Optional[str], Optional[int]) -> None
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
            The message object or message id identifying the message to delete.
        :param str pop_receipt:
            A valid pop receipt value returned from an earlier call
            to the :func:`~get_messages` or :func:`~update_message`.
        :param int timeout:
            The server timeout, expressed in seconds.
        """
