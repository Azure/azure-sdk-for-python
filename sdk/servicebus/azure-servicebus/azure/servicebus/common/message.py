# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import uuid

import uamqp
from uamqp import types

from azure.servicebus.common.constants import (
    DEADLETTERNAME,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    RECEIVER_LINK_DEAD_LETTER_DESCRIPTION
)
from azure.servicebus.common.errors import (
    MessageAlreadySettled,
    MessageSettleFailed,
    MessageLockExpired,
    SessionLockExpired)


class Message(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """A Service Bus Message.

    :param body: The data to send in a single message. The maximum size per message is 256 kB.
    :type body: str or bytes
    :param encoding: The encoding for string data. Default is UTF-8.
    :type encoding: str

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START send_complex_message]
            :end-before: [END send_complex_message]
            :language: python
            :dedent: 4
            :caption: Sending a message with additional properties

        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START receive_complex_message]
            :end-before: [END receive_complex_message]
            :language: python
            :dedent: 4
            :caption: Checking the properties on a received message

    """

    _X_OPT_ENQUEUED_TIME = b'x-opt-enqueued-time'
    _X_OPT_SEQUENCE_NUMBER = b'x-opt-sequence-number'
    _X_OPT_ENQUEUE_SEQUENCE_NUMBER = b'x-opt-enqueue-sequence-number'
    _X_OPT_PARTITION_ID = b'x-opt-partition-id'
    _X_OPT_PARTITION_KEY = b'x-opt-partition-key'
    _X_OPT_VIA_PARTITION_KEY = b'x-opt-via-partition-key'
    _X_OPT_LOCKED_UNTIL = b'x-opt-locked-until'
    _x_OPT_LOCK_TOKEN = b'x-opt-lock-token'
    _x_OPT_SCHEDULED_ENQUEUE_TIME = b'x-opt-scheduled-enqueue-time'

    def __init__(self, body, encoding='UTF-8', **kwargs):
        subject = kwargs.pop('subject', None)
        # Although we might normally thread through **kwargs this causes problems as MessageProperties won't absorb spurious args.
        self.properties = uamqp.message.MessageProperties(encoding=encoding, subject=subject)
        self.header = uamqp.message.MessageHeader()
        self.received_timestamp = None
        self.auto_renew_error = None
        self._annotations = {}
        self._app_properties = {}
        self._encoding = encoding
        self._expiry = None
        self._receiver = None
        if 'message' in kwargs:
            self.message = kwargs['message']
            self._annotations = self.message.annotations
            self._app_properties = self.message.application_properties
            self.properties = self.message.properties
            self.header = self.message.header
            self.received_timestamp = datetime.datetime.now()
        else:
            self._build_message(body)

    def __str__(self):
        return str(self.message)

    def _build_message(self, body):
        if isinstance(body, list) and body:  # TODO: This only works for a list of bytes/strings
            self.message = uamqp.Message(body[0], properties=self.properties, header=self.header)
            for more in body[1:]:
                self.message._body.append(more)  # pylint: disable=protected-access
        elif body is None:
            raise ValueError("Message body cannot be None.")
        else:
            self.message = uamqp.Message(body, properties=self.properties, header=self.header)

    def _is_live(self, action):
        # pylint: disable=no-member
        if self.settled:
            raise MessageAlreadySettled(action)
        try:
            if self.expired:
                raise MessageLockExpired(inner_exception=self.auto_renew_error)
        except TypeError:
            pass
        if hasattr(self._receiver, 'expired') and self._receiver.expired:
            raise SessionLockExpired(inner_exception=self._receiver.auto_renew_error)

    @property
    def settled(self):
        """Whether the message has been settled.

        This will aways be `True` for a message received using ReceiveAndDelete mode,
        otherwise it will be `False` until the message is completed or otherwise settled.

        :rtype: bool
        """
        return self.message.settled

    @property
    def annotations(self):
        """The annotations of the message.

        :rtype: dict
        """
        return self.message.annotations

    @annotations.setter
    def annotations(self, value):
        """Set the annotations on the message.

        :param value: The annotations for the Message.
        :type value: dict
        """
        self.message.annotations = value

    @property
    def user_properties(self):
        """User defined properties on the message.

        :rtype: dict
        """
        return self.message.application_properties

    @user_properties.setter
    def user_properties(self, value):
        """User defined properties on the message.

        :param value: The application properties for the Message.
        :type value: dict
        """
        self.message.application_properties = value

    @property
    def enqueued_time(self):
        if self.message.annotations:
            timestamp = self.message.annotations.get(self._X_OPT_ENQUEUED_TIME)
            if timestamp:
                in_seconds = timestamp/1000.0
                return datetime.datetime.utcfromtimestamp(in_seconds)
        return None

    @property
    def scheduled_enqueue_time(self):
        if self.message.annotations:
            timestamp = self.message.annotations.get(self._x_OPT_SCHEDULED_ENQUEUE_TIME)
            if timestamp:
                in_seconds = timestamp/1000.0
                return datetime.datetime.utcfromtimestamp(in_seconds)
        return None

    @property
    def sequence_number(self):
        if self.message.annotations:
            return self.message.annotations.get(self._X_OPT_SEQUENCE_NUMBER)
        return None

    @property
    def enqueue_sequence_number(self):
        if self.message.annotations:
            return self.message.annotations.get(self._X_OPT_ENQUEUE_SEQUENCE_NUMBER)
        return None

    @enqueue_sequence_number.setter
    def enqueue_sequence_number(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(self._X_OPT_ENQUEUE_SEQUENCE_NUMBER)] = value

    @property
    def partition_id(self):
        if self.message.annotations:
            return self.message.annotations.get(self._X_OPT_PARTITION_ID)
        return None

    @property
    def partition_key(self):
        if self.message.annotations:
            return self.message.annotations.get(self._X_OPT_PARTITION_KEY)
        return None

    @partition_key.setter
    def partition_key(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(self._X_OPT_PARTITION_KEY)] = value

    @property
    def via_partition_key(self):
        if self.message.annotations:
            return self.message.annotations.get(self._X_OPT_VIA_PARTITION_KEY)
        return None

    @via_partition_key.setter
    def via_partition_key(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(self._X_OPT_VIA_PARTITION_KEY)] = value

    @property
    def locked_until(self):
        if hasattr(self._receiver, 'locked_until') or self.settled:
            return None
        if self._expiry:
            return self._expiry
        if self.message.annotations and self._X_OPT_LOCKED_UNTIL in self.message.annotations:
            expiry_in_seconds = self.message.annotations[self._X_OPT_LOCKED_UNTIL]/1000
            self._expiry = datetime.datetime.fromtimestamp(expiry_in_seconds)
        return self._expiry

    @property
    def expired(self):
        if hasattr(self._receiver, 'locked_until'):
            raise TypeError("Session messages do not expire. Please use the Session expiry instead.")
        if self.locked_until and self.locked_until <= datetime.datetime.now():
            return True
        return False

    @property
    def lock_token(self):
        if hasattr(self._receiver, 'locked_until') or self.settled:
            return None
        if hasattr(self.message, 'delivery_tag') and self.message.delivery_tag:
            return uuid.UUID(bytes_le=self.message.delivery_tag)

        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(self._x_OPT_LOCK_TOKEN)
        return None

    @property
    def session_id(self):
        try:
            return self.properties.group_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self.properties.group_id

    @session_id.setter
    def session_id(self, value):
        self.properties.group_id = value

    @property
    def time_to_live(self):
        if self.header and self.header.time_to_live:
            return datetime.timedelta(milliseconds=self.header.time_to_live)
        return None

    @time_to_live.setter
    def time_to_live(self, value):
        if not self.header:
            self.header = uamqp.message.MessageHeader()
        if isinstance(value, datetime.timedelta):
            self.header.time_to_live = value.seconds * 1000
        else:
            self.header.time_to_live = int(value) * 1000

    @property
    def body(self):
        """The body of the Message.

        :rtype: bytes or generator[bytes]
        """
        return self.message.get_data()

    def schedule(self, schedule_time):
        """Add a specific enqueue time to the message.

        :param schedule_time: The scheduled time to enqueue the message.
        :type schedule_time: ~datetime.datetime
        """
        if not self.properties.message_id:
            self.properties.message_id = str(uuid.uuid4())
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(self._x_OPT_SCHEDULED_ENQUEUE_TIME)] = schedule_time

    def renew_lock(self):
        """Renew the message lock.

        This will maintain the lock on the message to ensure
        it is not returned to the queue to be reprocessed. In order to complete (or otherwise settle)
        the message, the lock must be maintained. Messages received via ReceiveAndDelete mode are not
        locked, and therefore cannot be renewed. This operation can also be performed as a threaded
        background task by registering the message with an `azure.servicebus.AutoLockRenew` instance.
        This operation is only available for non-sessionful messages.

        :raises: TypeError if the message is sessionful.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled is message has already been settled.
        """
        if hasattr(self._receiver, 'locked_until'):
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live('renew')
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = datetime.datetime.fromtimestamp(expiry[b'expirations'][0]/1000.0)

    def complete(self):
        """Complete the message.

        This removes the message from the queue.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('complete')
        try:
            self.message.accept()
        except Exception as e:
            raise MessageSettleFailed("complete", e)

    def dead_letter(self, description=None, reason=None):
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.
        To receive dead-lettered messages, use `QueueClient.get_deadletter_receiver()` or
        `SubscriptionClient.get_deadletter_receiver()`.

        :param str description: The error description for dead-lettering the message.
        :param str reason: The reason for dead-lettering the message. If `reason` is not set while `description` is
         set, then `reason` would be set the same as `description`.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('reject')

        info = None
        if description:
            info = {
                RECEIVER_LINK_DEAD_LETTER_REASON: reason or description,
                RECEIVER_LINK_DEAD_LETTER_DESCRIPTION: description
            }
        elif reason:
            info = {
                RECEIVER_LINK_DEAD_LETTER_REASON: reason
            }

        try:
            self.message.reject(condition=DEADLETTERNAME, description=description, info=info)
        except Exception as e:
            raise MessageSettleFailed("reject", e)

    def abandon(self):
        """Abandon the message.

        This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('abandon')
        try:
            self.message.modify(True, False)
        except Exception as e:
            raise MessageSettleFailed("abandon", e)

    def defer(self):
        """Defer the message.

        This message will remain in the queue but must be received
        specifically by its sequence number in order to be processed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('defer')
        try:
            self.message.modify(True, True)
        except Exception as e:
            raise MessageSettleFailed("defer", e)


class BatchMessage(Message):
    """A batch of messages combined into a single message body.

    The body of the messages in the batch should be supplied by an iterable,
    such as a generator.
    If the contents of the iterable exceeds the maximum size of a single message (256 kB),
    the data will be broken up across multiple messages.

    :param body: The data to send in each message in the batch. The maximum size per message is 256 kB.
     If data is supplied in excess of this limit, multiple messages will be sent.
    :type body: Iterable
    :param encoding: The encoding for string data. Default is UTF-8.
    :type encoding: str

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START send_batch_message]
            :end-before: [END send_batch_message]
            :language: python
            :dedent: 4
            :caption: Send a batched message.

    """

    def _build_message(self, body):
        if body is None:
            raise ValueError("Message body cannot be None.")
        else:
            self.message = uamqp.BatchMessage(
                data=body, multi_messages=True, properties=self.properties, header=self.header)


class PeekMessage(Message):
    """A preview message.

    This message is still on the queue, and unlocked.
    A peeked message cannot be completed, abandoned, dead-lettered or deferred.
    It has no lock token or expiry.

    """

    def __init__(self, message):
        super(PeekMessage, self).__init__(None, message=message)

    @property
    def locked_until(self):
        raise TypeError("Peeked message is not locked.")

    @property
    def lock_token(self):
        raise TypeError("Peeked message is not locked.")

    def renew_lock(self):
        """A PeekMessage cannot be renewed. Raises `TypeError`."""
        raise TypeError("Peeked message is not locked.")

    def complete(self):
        """A PeekMessage cannot be completed Raises `TypeError`."""
        raise TypeError("Peeked message cannot be completed.")

    def dead_letter(self, description=None, reason=None):
        """A PeekMessage cannot be dead-lettered. Raises `TypeError`."""
        raise TypeError("Peeked message cannot be dead-lettered.")

    def abandon(self):
        """A PeekMessage cannot be abandoned. Raises `TypeError`."""
        raise TypeError("Peeked message cannot be abandoned.")

    def defer(self):
        """A PeekMessage cannot be deferred. Raises `TypeError`."""
        raise TypeError("Peeked message cannot be deferred.")


class DeferredMessage(Message):
    """A message that has been deferred.

    A deferred message can be completed,
    abandoned, or dead-lettered, however it cannot be deferred again.

    """

    def __init__(self, message, mode):
        self._settled = mode == 0
        super(DeferredMessage, self).__init__(None, message=message)

    def _is_live(self, action):
        if not self._receiver:
            raise ValueError("Orphan message had no open connection.")
        super(DeferredMessage, self)._is_live(action)

    @property
    def lock_token(self):
        if self.settled:
            return None
        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(self._x_OPT_LOCK_TOKEN)
        return None

    @property
    def settled(self):
        return self._settled

    def complete(self):
        """Complete the message.

        This removes the message from the queue.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('complete')
        self._receiver._settle_deferred('completed', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    def dead_letter(self, description=None, reason=None):
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.
        To receive dead-lettered messages, use `QueueClient.get_deadletter_receiver()` or
        `SubscriptionClient.get_deadletter_receiver()`.

        :param str description: The error description for dead-lettering the message.
        :param str reason: The reason for dead-lettering the message. If `reason` is not set while `description` is
         set, then `reason` would be set the same as `description`.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('dead-letter')
        details = {
            'deadletter-reason': str(reason) if reason else (str(description) if description else ""),
            'deadletter-description': str(description) if description else ""}
        self._receiver._settle_deferred(  # pylint: disable=protected-access
            'suspended', [self.lock_token], dead_letter_details=details)
        self._settled = True

    def abandon(self):
        """Abandon the message.

        This message will be returned to the queue to be reprocessed.

        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live('abandon')
        self._receiver._settle_deferred('abandoned', [self.lock_token])  # pylint: disable=protected-access
        self._settled = True

    def defer(self):
        """A DeferredMessage cannot be deferred. Raises `ValueError`."""
        raise ValueError("Message is already deferred.")
