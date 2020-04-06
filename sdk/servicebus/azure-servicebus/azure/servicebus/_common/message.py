# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import datetime
import uuid
from typing import Optional, List, Union, Generator

import uamqp
from uamqp import types

from .constants import (
    _BATCH_MESSAGE_OVERHEAD_COST,
    SETTLEMENT_ABANDON,
    SETTLEMENT_COMPLETE,
    SETTLEMENT_DEFER,
    SETTLEMENT_DEADLETTER,
    ReceiveSettleMode,
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_SEQUENCE_NUMBER,
    _X_OPT_ENQUEUE_SEQUENCE_NUMBER,
    _X_OPT_PARTITION_ID,
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_LOCKED_UNTIL,
    _X_OPT_LOCK_TOKEN,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    MGMT_RESPONSE_MESSAGE_EXPIRATION,
    MGMT_REQUEST_DEAD_LETTER_REASON,
    MGMT_REQUEST_DEAD_LETTER_DESCRIPTION,
    MESSAGE_COMPLETE,
    MESSAGE_DEAD_LETTER,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_RENEW_LOCK
)
from ..exceptions import (
    MessageAlreadySettled,
    MessageLockExpired,
    SessionLockExpired,
    MessageSettleFailed
)
from .utils import utc_from_timestamp, utc_now


class Message(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """A Service Bus Message.

    :ivar properties: Properties of the internal AMQP message object.
    :vartype properties: ~uamqp.message.MessageProperties
    :ivar header: Header of the internal AMQP message object.
    :vartype header: ~uamqp.message.MessageHeader
    :ivar message: Internal AMQP message object.
    :vartype message: ~uamqp.message.Message

    :param body: The data to send in a single message.
    :type body: str or bytes
    :keyword str encoding: The encoding for string data. Default is UTF-8.
    :keyword str session_id: An optional session ID for the message to be sent.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START send_complex_message]
            :end-before: [END send_complex_message]
            :language: python
            :dedent: 4
            :caption: Sending a message with additional properties

    """

    def __init__(self, body, **kwargs):
        subject = kwargs.pop('subject', None)
        # Although we might normally thread through **kwargs this causes
        # problems as MessageProperties won't absorb spurious args.
        self._encoding = kwargs.pop("encoding", 'UTF-8')
        self.properties = uamqp.message.MessageProperties(encoding=self._encoding, subject=subject)
        self.header = uamqp.message.MessageHeader()
        self._annotations = {}
        self._app_properties = {}

        self._expiry = None
        self._receiver = None
        self.session_id = kwargs.get("session_id", None)
        if 'message' in kwargs:
            self.message = kwargs['message']
            self._annotations = self.message.annotations
            self._app_properties = self.message.application_properties
            self.properties = self.message.properties
            self.header = self.message.header
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

    @property
    def session_id(self):
        # type: () -> str
        """The session id of the message

        :rtype: str
        """
        try:
            return self.properties.group_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self.properties.group_id

    @session_id.setter
    def session_id(self, value):
        """Set the session id on the message.

        :param value: The session id for the message.
        :type value: str
        """
        self.properties.group_id = value

    @property
    def annotations(self):
        # type: () -> dict
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
        # type: () -> dict
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
    def enqueue_sequence_number(self):
        # type: () -> Optional[int]
        """

        :rtype: int
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_ENQUEUE_SEQUENCE_NUMBER)
        return None

    @enqueue_sequence_number.setter
    def enqueue_sequence_number(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(_X_OPT_ENQUEUE_SEQUENCE_NUMBER)] = value

    @property
    def partition_key(self):
        # type: () -> Optional[str]
        """

        :rtype: str
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_PARTITION_KEY)
        return None

    @partition_key.setter
    def partition_key(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(_X_OPT_PARTITION_KEY)] = value

    @property
    def via_partition_key(self):
        # type: () -> Optional[str]
        """

        :rtype: str
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_VIA_PARTITION_KEY)
        return None

    @via_partition_key.setter
    def via_partition_key(self, value):
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(_X_OPT_VIA_PARTITION_KEY)] = value

    @property
    def time_to_live(self):
        # type: () -> Optional[datetime.timedelta]
        """

        :rtype: ~datetime.timedelta
        """
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
        # type: () -> Union[bytes, Generator[bytes]]
        """The body of the Message.

        :rtype: bytes or generator[bytes]
        """
        return self.message.get_data()

    def schedule(self, schedule_time_utc):
        # type: (datetime.datetime) -> None
        """Add a specific utc enqueue time to the message.

        :param schedule_time_utc: The scheduled utc time to enqueue the message.
        :type schedule_time_utc: ~datetime.datetime
        :rtype: None
        """
        if not self.properties.message_id:
            self.properties.message_id = str(uuid.uuid4())
        if not self.message.annotations:
            self.message.annotations = {}
        self.message.annotations[types.AMQPSymbol(_X_OPT_SCHEDULED_ENQUEUE_TIME)] = schedule_time_utc


class BatchMessage(object):
    """A batch of messages.

    Sending messages in a batch is more performant than sending individual message.
    BatchMessage helps you create the maximum allowed size batch of `Message` to improve sending performance.

    Use the `add` method to add messages until the maximum batch size limit in bytes has been reached -
    at which point a `ValueError` will be raised.

    **Please use the create_batch method of ServiceBusSender
    to create a BatchMessage object instead of instantiating a BatchMessage object directly.**

    :ivar max_size_in_bytes: The maximum size of bytes data that a BatchMessage object can hold.
    :vartype max_size_in_bytes: int
    :ivar message: Internal AMQP BatchMessage object.
    :vartype message: ~uamqp.BatchMessage

    :param int max_size_in_bytes: The maximum size of bytes data that a BatchMessage object can hold.

    """
    def __init__(self, max_size_in_bytes=None):
        # type: (Optional[int]) -> None
        self.max_size_in_bytes = max_size_in_bytes or uamqp.constants.MAX_MESSAGE_LENGTH_BYTES
        self.message = uamqp.BatchMessage(data=[], multi_messages=False, properties=None)
        self._size = self.message.gather()[0].get_message_encoded_size()
        self._count = 0
        self._messages = []  # type: List[Message]

    def __repr__(self):
        # type: () -> str
        batch_repr = "max_size_in_bytes={}, message_count={}".format(
            self.max_size_in_bytes, self._count
        )
        return "BatchMessage({})".format(batch_repr)

    def __len__(self):
        return self._count

    @property
    def size_in_bytes(self):
        # type: () -> int
        """The combined size of the events in the batch, in bytes.

        :rtype: int
        """
        return self._size

    def add(self, message):
        # type: (Message) -> None
        """Try to add a single Message to the batch.

        The total size of an added message is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `ValueError` will
        be raised.

        :param message: The Message to be added to the batch.
        :type message: ~azure.servicebus.Message
        :rtype: None
        :raises: :class:`ValueError`, when exceeding the size limit.
        """
        message_size = message.message.get_message_encoded_size()

        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        # message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = (
            self._size
            + message_size
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (message_size < 256) else 1]
        )

        if size_after_add > self.max_size_in_bytes:
            raise ValueError(
                "EventDataBatch has reached its size limit: {}".format(
                    self.max_size_in_bytes
                )
            )

        self.message._body_gen.append(message)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1
        self._messages.append(message)


class PeekMessage(Message):
    """A preview message.

    This message is still on the queue, and unlocked.
    A peeked message cannot be completed, abandoned, dead-lettered or deferred.
    It has no lock token or expiry.

    :ivar received_timestamp_utc: The utc timestamp of when the message is received.
    :vartype received_timestamp_utc: datetime.datetime

    """

    def __init__(self, message):
        super(PeekMessage, self).__init__(None, message=message)
        self.received_timestamp_utc = utc_now()

    @property
    def settled(self):
        # type: () -> bool
        """Whether the message has been settled.

        This will aways be `True` for a message received using ReceiveAndDelete mode,
        otherwise it will be `False` until the message is completed or otherwise settled.

        :rtype: bool
        """
        return self.message.settled

    @property
    def partition_id(self):
        # type: () -> Optional[str]
        """

        :rtype: int
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_PARTITION_ID)
        return None

    @property
    def enqueued_time_utc(self):
        # type: () -> Optional[datetime.datetime]
        """

        :rtype: ~datetime.datetime
        """
        if self.message.annotations:
            timestamp = self.message.annotations.get(_X_OPT_ENQUEUED_TIME)
            if timestamp:
                in_seconds = timestamp/1000.0
                return utc_from_timestamp(in_seconds)
        return None

    @property
    def scheduled_enqueue_time_utc(self):
        # type: () -> Optional[datetime.datetime]
        """

        :rtype: ~datetime.datetime
        """
        if self.message.annotations:
            timestamp = self.message.annotations.get(_X_OPT_SCHEDULED_ENQUEUE_TIME)
            if timestamp:
                in_seconds = timestamp/1000.0
                return utc_from_timestamp(in_seconds)
        return None

    @property
    def sequence_number(self):
        # type: () -> Optional[int]
        """

        :rtype: int
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_SEQUENCE_NUMBER)
        return None


class ReceivedMessage(PeekMessage):
    """
    A Service Bus Message received from service side.

    :ivar auto_renew_error: Error when AutoLockRenew is used and it fails to renew the message lock.
    :vartype auto_renew_error: ~azure.servicebus.AutoLockRenewTimeout or ~azure.servicebus.AutoLockRenewFailed

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START receive_complex_message]
            :end-before: [END receive_complex_message]
            :language: python
            :dedent: 4
            :caption: Checking the properties on a received message.
    """
    def __init__(self, message, mode=ReceiveSettleMode.PeekLock):
        super(ReceivedMessage, self).__init__(message=message)
        self._settled = (mode == ReceiveSettleMode.ReceiveAndDelete)
        self.auto_renew_error = None

    def _is_live(self, action):
        # pylint: disable=no-member
        if not self._receiver or not self._receiver._running:  # pylint: disable=protected-access
            raise MessageSettleFailed(action, "Orphan message had no open connection.")
        if self.settled:
            raise MessageAlreadySettled(action)
        try:
            if self.expired:
                raise MessageLockExpired(inner_exception=self.auto_renew_error)
        except TypeError:
            pass
        try:
            if self._receiver.session and self._receiver.session.expired:
                raise SessionLockExpired(inner_exception=self._receiver.session.auto_renew_error)
        except TypeError:
            pass

    @property
    def settled(self):
        # type: () -> bool
        """Whether the message has been settled.

        This will aways be `True` for a message received using ReceiveAndDelete mode,
        otherwise it will be `False` until the message is completed or otherwise settled.

        :rtype: bool
        """
        return self._settled

    @property
    def expired(self):
        # type: () -> bool
        """

        :rtype: bool
        """
        if self._receiver._session_id:  # pylint: disable=protected-access
            raise TypeError("Session messages do not expire. Please use the Session expiry instead.")
        if self.locked_until_utc and self.locked_until_utc <= utc_now():
            return True
        return False

    @property
    def locked_until_utc(self):
        # type: () -> Optional[datetime.datetime]
        """

        :rtype: datetime.datetime
        """
        if self._receiver._session_id or self.settled:  # pylint: disable=protected-access
            return None
        if self._expiry:
            return self._expiry
        if self.message.annotations and _X_OPT_LOCKED_UNTIL in self.message.annotations:
            expiry_in_seconds = self.message.annotations[_X_OPT_LOCKED_UNTIL]/1000
            self._expiry = utc_from_timestamp(expiry_in_seconds)
        return self._expiry

    @property
    def lock_token(self):
        # type: () -> Optional[Union[uuid.UUID, str]]
        """

        :rtype:  ~uuid.UUID or str
        """
        if self.settled:
            return None

        if self.message.delivery_tag:
            return uuid.UUID(bytes_le=self.message.delivery_tag)

        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(_X_OPT_LOCK_TOKEN)
        return None

    def complete(self):
        # type: () -> None
        """Complete the message.

        This removes the message from the queue.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live(MESSAGE_COMPLETE)
        try:
            self._receiver._settle_message(SETTLEMENT_COMPLETE, [self.lock_token])  # pylint: disable=protected-access
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_COMPLETE, e)
        self._settled = True

    def dead_letter(self, reason=None, description=None):
        # type: (Optional[str], Optional[str]) -> None
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.

        :param str reason: The reason for dead-lettering the message.
        :param str description: The detailed description for dead-lettering the message.
        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        # pylint: disable=protected-access
        self._is_live(MESSAGE_DEAD_LETTER)
        details = {
            MGMT_REQUEST_DEAD_LETTER_REASON: str(reason) if reason else "",
            MGMT_REQUEST_DEAD_LETTER_DESCRIPTION: str(description) if description else ""}
        try:
            self._receiver._settle_message(
                SETTLEMENT_DEADLETTER,
                [self.lock_token],
                dead_letter_details=details
            )
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_DEAD_LETTER, e)
        self._settled = True

    def abandon(self):
        # type: () -> None
        """Abandon the message.

        This message will be returned to the queue to be reprocessed.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live(MESSAGE_ABANDON)
        try:
            self._receiver._settle_message(SETTLEMENT_ABANDON, [self.lock_token])  # pylint: disable=protected-access
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_ABANDON, e)
        self._settled = True

    def defer(self):
        # type: () -> None
        """Defer the message.

        This message will remain in the queue but must be received
        specifically by its sequence number in order to be processed.

        :rtype: None
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.common.errors.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageSettleFailed if message settle operation fails.
        """
        self._is_live(MESSAGE_DEFER)
        try:
            self._receiver._settle_message(SETTLEMENT_DEFER, [self.lock_token])  # pylint: disable=protected-access
        except Exception as e:
            raise MessageSettleFailed(MESSAGE_DEFER, e)
        self._settled = True

    def renew_lock(self):
        # type: () -> None
        """Renew the message lock.

        This will maintain the lock on the message to ensure
        it is not returned to the queue to be reprocessed. In order to complete (or otherwise settle)
        the message, the lock must be maintained. Messages received via ReceiveAndDelete mode are not
        locked, and therefore cannot be renewed. This operation can also be performed as a threaded
        background task by registering the message with an `azure.servicebus.AutoLockRenew` instance.
        This operation is only available for non-sessionful messages.

        :rtype: None
        :raises: TypeError if the message is sessionful.
        :raises: ~azure.servicebus.common.errors.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.common.errors.MessageAlreadySettled is message has already been settled.
        """
        if self._receiver._session_id:  # pylint: disable=protected-access
            raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        self._is_live(MESSAGE_RENEW_LOCK)
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        expiry = self._receiver._renew_locks(token)  # pylint: disable=protected-access
        self._expiry = utc_from_timestamp(expiry[MGMT_RESPONSE_MESSAGE_EXPIRATION][0]/1000.0)
