# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# pylint: disable=too-many-lines

import datetime
import uuid
import functools
import logging
import copy
from typing import Optional, List, Union, Iterable, TYPE_CHECKING, Callable, Any

import uamqp.message
from uamqp.constants import MessageState

from .constants import (
    _BATCH_MESSAGE_OVERHEAD_COST,
    SETTLEMENT_ABANDON,
    SETTLEMENT_COMPLETE,
    SETTLEMENT_DEFER,
    SETTLEMENT_DEADLETTER,
    ReceiveMode,
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_SEQUENCE_NUMBER,
    _X_OPT_ENQUEUE_SEQUENCE_NUMBER,
    _X_OPT_PARTITION_KEY,
    _X_OPT_VIA_PARTITION_KEY,
    _X_OPT_LOCKED_UNTIL,
    _X_OPT_LOCK_TOKEN,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    _X_OPT_DEAD_LETTER_SOURCE,
    MGMT_RESPONSE_MESSAGE_EXPIRATION,
    MGMT_REQUEST_DEAD_LETTER_REASON,
    MGMT_REQUEST_DEAD_LETTER_ERROR_DESCRIPTION,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION,
    MESSAGE_COMPLETE,
    MESSAGE_DEAD_LETTER,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_RENEW_LOCK,
    DEADLETTERNAME,
    PROPERTIES_DEAD_LETTER_REASON,
    PROPERTIES_DEAD_LETTER_ERROR_DESCRIPTION,
    ANNOTATION_SYMBOL_PARTITION_KEY,
    ANNOTATION_SYMBOL_VIA_PARTITION_KEY,
    ANNOTATION_SYMBOL_SCHEDULED_ENQUEUE_TIME,
    ANNOTATION_SYMBOL_KEY_MAP
)
from ..exceptions import (
    MessageAlreadySettled,
    MessageLockExpired,
    SessionLockExpired,
    MessageSettleFailed,
    MessageContentTooLarge,
    ServiceBusError)
from .utils import utc_from_timestamp, utc_now, transform_messages_to_sendable_if_needed
if TYPE_CHECKING:
    from .._servicebus_receiver import ServiceBusReceiver
    from .._servicebus_session_receiver import ServiceBusSessionReceiver

_LOGGER = logging.getLogger(__name__)


class Message(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """A Service Bus Message.

    :param body: The data to send in a single message.
    :type body: Union[str, bytes]

    :keyword dict properties: The user defined properties on the message.
    :keyword str session_id: The session identifier of the message for a sessionful entity.
    :keyword str message_id: The id to identify the message.
    :keyword datetime.datetime scheduled_enqueue_time_utc: The utc scheduled enqueue time to the message.
    :keyword datetime.timedelta time_to_live: The life duration of a message.
    :keyword str content_type: The content type descriptor.
    :keyword str correlation_id: The correlation identifier.
    :keyword str label: The application specific label.
    :keyword str partition_key: The partition key for sending a message to a partitioned entity.
    :keyword str via_partition_key: The partition key for sending a message into an entity via a partitioned
     transfer queue.
    :keyword str to: The `to` address used for auto_forward chaining scenarios.
    :keyword str reply_to: The address of an entity to send replies to.
    :keyword str reply_to_session_id: The session identifier augmenting the `reply_to` address.
    :keyword str encoding: The encoding for string data. Default is UTF-8.

    :ivar AMQPMessage amqp_message: Advanced use only.  The internal AMQP message payload that is sent or received.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START send_complex_message]
            :end-before: [END send_complex_message]
            :language: python
            :dedent: 4
            :caption: Sending a message with additional properties

    """

    def __init__(self, body, **kwargs):
        # type: (Union[str, bytes], Any) -> None
        # Although we might normally thread through **kwargs this causes
        # problems as MessageProperties won't absorb spurious args.
        self._encoding = kwargs.pop("encoding", 'UTF-8')
        self._amqp_properties = uamqp.message.MessageProperties(encoding=self._encoding)
        self._amqp_header = uamqp.message.MessageHeader()

        if 'message' in kwargs:
            # Note: This cannot be renamed until UAMQP no longer relies on this specific name.
            self.message = kwargs['message']
            self._amqp_properties = self.message.properties
            self._amqp_header = self.message.header
        else:
            self._build_message(body)
            self.properties = kwargs.pop("properties", None)
            self.session_id = kwargs.pop("session_id", None)
            self.message_id = kwargs.get("message_id", None)
            self.content_type = kwargs.pop("content_type", None)
            self.correlation_id = kwargs.pop("correlation_id", None)
            self.to = kwargs.pop("to", None)
            self.reply_to = kwargs.pop("reply_to", None)
            self.reply_to_session_id = kwargs.pop("reply_to_session_id", None)
            self.label = kwargs.pop("label", None)
            self.scheduled_enqueue_time_utc = kwargs.pop("scheduled_enqueue_time_utc", None)
            self.time_to_live = kwargs.pop("time_to_live", None)
            self.partition_key = kwargs.pop("partition_key", None)
            self.via_partition_key = kwargs.pop("via_partition_key", None)
        # If message is the full message, amqp_message is the "public facing interface" for what we expose.
        self.amqp_message = AMQPMessage(self.message) # type: AMQPMessage

    def __str__(self):
        return str(self.message)

    def _build_message(self, body):
        if isinstance(body, list) and body:  # TODO: This only works for a list of bytes/strings
            self.message = uamqp.Message(body[0], properties=self._amqp_properties, header=self._amqp_header)
            for more in body[1:]:
                self.message._body.append(more)  # pylint: disable=protected-access
        elif body is None:
            raise ValueError("Message body cannot be None.")
        else:
            self.message = uamqp.Message(body, properties=self._amqp_properties, header=self._amqp_header)

    def _set_message_annotations(self, key, value):
        if not self.message.annotations:
            self.message.annotations = {}

        if isinstance(self, ReceivedMessage):
            try:
                del self.message.annotations[key]
            except KeyError:
                pass

        if value is None:
            try:
                del self.message.annotations[ANNOTATION_SYMBOL_KEY_MAP[key]]
            except KeyError:
                pass
        else:
            self.message.annotations[ANNOTATION_SYMBOL_KEY_MAP[key]] = value

    def _to_outgoing_message(self):
        # type: () -> Message
        self.message.state = MessageState.WaitingToBeSent
        self.message._response = None # pylint: disable=protected-access
        return self

    @property
    def session_id(self):
        # type: () -> str
        """The session identifier of the message for a sessionful entity.

        For sessionful entities, this application-defined value specifies the session affiliation of the message.
        Messages with the same session identifier are subject to summary locking and enable exact in-order
        processing and demultiplexing. For non-sessionful entities, this value is ignored.

        See Message Sessions in `https://docs.microsoft.com/azure/service-bus-messaging/message-sessions`.

        :rtype: str
        """
        try:
            return self._amqp_properties.group_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.group_id

    @session_id.setter
    def session_id(self, value):
        # type: (str) -> None
        self._amqp_properties.group_id = value

    @property
    def properties(self):
        # type: () -> dict
        """The user defined properties on the message.

        :rtype: dict
        """
        return self.message.application_properties

    @properties.setter
    def properties(self, value):
        # type: (dict) -> None
        self.message.application_properties = value

    @property
    def partition_key(self):
        # type: () -> Optional[str]
        """ The partition key for sending a message to a partitioned entity.

        Setting this value enables assigning related messages to the same internal partition, so that submission
        sequence order is correctly recorded.
        The partition is chosen by a hash function over this value and cannot be chosen directly.

        See Partitioned queues and topics in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-partitioning`.

        :rtype: str
        """
        p_key = None
        try:
            p_key = self.message.annotations.get(_X_OPT_PARTITION_KEY) or \
                self.message.annotations.get(ANNOTATION_SYMBOL_PARTITION_KEY)
            return p_key.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return p_key

    @partition_key.setter
    def partition_key(self, value):
        # type: (str) -> None
        self._set_message_annotations(_X_OPT_PARTITION_KEY, value)

    @property
    def via_partition_key(self):
        # type: () -> Optional[str]
        """ The partition key for sending a message into an entity via a partitioned transfer queue.

        If a message is sent via a transfer queue in the scope of a transaction, this value selects the transfer
        queue partition: This is functionally equivalent to `partition_key` and ensures that messages are kept
        together and in order as they are transferred.

        See Transfers and Send Via in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-transactions#transfers-and-send-via`.

        :rtype: str
        """
        via_p_key = None
        try:
            via_p_key = self.message.annotations.get(_X_OPT_VIA_PARTITION_KEY) or \
                self.message.annotations.get(ANNOTATION_SYMBOL_VIA_PARTITION_KEY)
            return via_p_key.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return via_p_key

    @via_partition_key.setter
    def via_partition_key(self, value):
        # type: (str) -> None
        self._set_message_annotations(_X_OPT_VIA_PARTITION_KEY, value)

    @property
    def time_to_live(self):
        # type: () -> Optional[datetime.timedelta]
        """The life duration of a message.

        This value is the relative duration after which the message expires, starting from the instant the message
        has been accepted and stored by the broker, as captured in `enqueued_time_utc`.
        When not set explicitly, the assumed value is the DefaultTimeToLive for the respective queue or topic.
        A message-level time-to-live value cannot be longer than the entity's time-to-live setting and it is silently
        adjusted if it does.

        See Expiration in `https://docs.microsoft.com/azure/service-bus-messaging/message-expiration`

        :rtype: ~datetime.timedelta
        """
        if self._amqp_header and self._amqp_header.time_to_live:
            return datetime.timedelta(milliseconds=self._amqp_header.time_to_live)
        return None

    @time_to_live.setter
    def time_to_live(self, value):
        # type: (datetime.timedelta) -> None
        if not self._amqp_header:
            self._amqp_header = uamqp.message.MessageHeader()
        if value is None:
            self._amqp_header.time_to_live = value
        elif isinstance(value, datetime.timedelta):
            self._amqp_header.time_to_live = value.seconds * 1000
        else:
            self._amqp_header.time_to_live = int(value) * 1000

    @property
    def scheduled_enqueue_time_utc(self):
        # type: () -> Optional[datetime.datetime]
        """The utc scheduled enqueue time to the message.

        This property can be used for scheduling when sending a message through `ServiceBusSender.send` method.
        If cancelling scheduled messages is required, you should use the `ServiceBusSender.schedule` method,
        which returns sequence numbers that can be used for future cancellation.
        `scheduled_enqueue_time_utc` is None if not set.

        :rtype: ~datetime.datetime
        """
        if self.message.annotations:
            timestamp = self.message.annotations.get(_X_OPT_SCHEDULED_ENQUEUE_TIME) or \
                self.message.annotations.get(ANNOTATION_SYMBOL_SCHEDULED_ENQUEUE_TIME)
            if timestamp:
                try:
                    in_seconds = timestamp/1000.0
                    return utc_from_timestamp(in_seconds)
                except TypeError:
                    return timestamp
        return None

    @scheduled_enqueue_time_utc.setter
    def scheduled_enqueue_time_utc(self, value):
        # type: (datetime.datetime) -> None
        if not self._amqp_properties.message_id:
            self._amqp_properties.message_id = str(uuid.uuid4())
        self._set_message_annotations(_X_OPT_SCHEDULED_ENQUEUE_TIME, value)

    @property
    def body(self):
        # type: () -> Union[bytes, Iterable[bytes]]
        """The body of the Message.

        :rtype: bytes or Iterable[bytes]
        """
        return self.message.get_data()

    @property
    def content_type(self):
        # type: () -> str
        """The content type descriptor.

        Optionally describes the payload of the message, with a descriptor following the format of RFC2045, Section 5,
        for example "application/json".

        :rtype: str
        """
        try:
            return self._amqp_properties.content_type.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.content_type

    @content_type.setter
    def content_type(self, val):
        # type: (str) -> None
        self._amqp_properties.content_type = val

    @property
    def correlation_id(self):
        # type: () -> str
        # pylint: disable=line-too-long
        """The correlation identifier.

        Allows an application to specify a context for the message for the purposes of correlation, for example
        reflecting the MessageId of a message that is being replied to.

        See Message Routing and Correlation in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messages-payloads?#message-routing-and-correlation`.

        :rtype: str
        """
        try:
            return self._amqp_properties.correlation_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.correlation_id

    @correlation_id.setter
    def correlation_id(self, val):
        # type: (str) -> None
        self._amqp_properties.correlation_id = val

    @property
    def label(self):
        # type: () -> str
        """The application specific label.

        This property enables the application to indicate the purpose of the message to the receiver in a standardized
        fashion, similar to an email subject line.

        :rtype: str
        """
        try:
            return self._amqp_properties.subject.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.subject

    @label.setter
    def label(self, val):
        # type: (str) -> None
        self._amqp_properties.subject = val

    @property
    def message_id(self):
        # type: () -> str
        """The id to identify the message.

        The message identifier is an application-defined value that uniquely identifies the message and its payload.
        The identifier is a free-form string and can reflect a GUID or an identifier derived from the
        application context.  If enabled, the duplicate detection (see
        `https://docs.microsoft.com/azure/service-bus-messaging/duplicate-detection`)
         feature identifies and removes second and further submissions of messages with the same message id.

        :rtype: str
        """
        try:
            return self._amqp_properties.message_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.message_id

    @message_id.setter
    def message_id(self, val):
        # type: (str) -> None
        self._amqp_properties.message_id = val

    @property
    def reply_to(self):
        # type: () -> str
        # pylint: disable=line-too-long
        """The address of an entity to send replies to.

        This optional and application-defined value is a standard way to express a reply path to the receiver of
        the message. When a sender expects a reply, it sets the value to the absolute or relative path of the queue
        or topic it expects the reply to be sent to.

        See Message Routing and Correlation in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messages-payloads?#message-routing-and-correlation`.

        :rtype: str
        """
        try:
            return self._amqp_properties.reply_to.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.reply_to

    @reply_to.setter
    def reply_to(self, val):
        # type: (str) -> None
        self._amqp_properties.reply_to = val

    @property
    def reply_to_session_id(self):
        # type: () -> str
        # pylint: disable=line-too-long
        """The session identifier augmenting the `reply_to` address.

        This value augments the `reply_to` information and specifies which session id should be set for the reply
        when sent to the reply entity.

        See Message Routing and Correlation in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messages-payloads?#message-routing-and-correlation`.

        :rtype: str
        """
        try:
            return self._amqp_properties.reply_to_group_id.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.reply_to_group_id

    @reply_to_session_id.setter
    def reply_to_session_id(self, val):
        # type: (str) -> None
        self._amqp_properties.reply_to_group_id = val

    @property
    def to(self):
        # type: () -> str
        """The `to` address.

        This property is reserved for future use in routing scenarios and presently ignored by the broker itself.
        Applications can use this value in rule-driven auto-forward chaining scenarios to indicate the intended
        logical destination of the message.

        See https://docs.microsoft.com/azure/service-bus-messaging/service-bus-auto-forwarding for more details.

        :rtype: str
        """
        try:
            return self._amqp_properties.to.decode('UTF-8')
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.to

    @to.setter
    def to(self, val):
        # type: (str) -> None
        self._amqp_properties.to = val


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

    def _from_list(self, messages):
        for each in messages:
            if not isinstance(each, Message):
                raise TypeError("Only Message or an iterable object containing Message objects are accepted."
                                 "Received instead: {}".format(each.__class__.__name__))
            self.add(each)

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
        :raises: :class: ~azure.servicebus.exceptions.MessageContentTooLarge, when exceeding the size limit.
        """
        message = transform_messages_to_sendable_if_needed(message)
        message_size = message.message.get_message_encoded_size()

        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        # message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = (
            self._size
            + message_size
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (message_size < 256) else 1]
        )

        if size_after_add > self.max_size_in_bytes:
            raise MessageContentTooLarge(
                "BatchMessage has reached its size limit: {}".format(
                    self.max_size_in_bytes
                )
            )

        self.message._body_gen.append(message)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1
        self._messages.append(message)


class PeekedMessage(Message):
    """A preview message.

    This message is still on the queue, and unlocked.
    A peeked message cannot be completed, abandoned, dead-lettered or deferred.
    It has no lock token or expiry.
    """

    def __init__(self, message):
        # type: (uamqp.message.Message) -> None
        super(PeekedMessage, self).__init__(None, message=message) # type: ignore

    def _to_outgoing_message(self):
        # type: () -> Message
        amqp_message = self.message
        amqp_body = amqp_message._body  # pylint: disable=protected-access

        if isinstance(amqp_body, uamqp.message.DataBody):
            body = b''.join(amqp_body.data)
        else:
            # amqp_body is type of uamqp.message.ValueBody
            body = amqp_body.data

        return Message(
            body=body,
            content_type=self.content_type,
            correlation_id=self.correlation_id,
            label=self.label,
            message_id=self.message_id,
            partition_key=self.partition_key,
            properties=self.properties,
            reply_to=self.reply_to,
            reply_to_session_id=self.reply_to_session_id,
            session_id=self.session_id,
            scheduled_enqueue_time_utc=self.scheduled_enqueue_time_utc,
            time_to_live=self.time_to_live,
            to=self.to,
            via_partition_key=self.via_partition_key
        )

    @property
    def dead_letter_error_description(self):
        # type: () -> Optional[str]
        """
        Dead letter error description, when the message is received from a deadletter subqueue of an entity.

        :rtype: str
        """
        if self.message.application_properties:
            try:
                return self.message.application_properties.get(PROPERTIES_DEAD_LETTER_ERROR_DESCRIPTION).decode('UTF-8')
            except AttributeError:
                pass
        return None

    @property
    def dead_letter_reason(self):
        # type: () -> Optional[str]
        """
        Dead letter reason, when the message is received from a deadletter subqueue of an entity.

        :rtype: str
        """
        if self.message.application_properties:
            try:
                return self.message.application_properties.get(PROPERTIES_DEAD_LETTER_REASON).decode('UTF-8')
            except AttributeError:
                pass
        return None

    @property
    def dead_letter_source(self):
        # type: () -> Optional[str]
        """
        The name of the queue or subscription that this message was enqueued on, before it was deadlettered.
        This property is only set in messages that have been dead-lettered and subsequently auto-forwarded
        from the dead-letter queue to another entity. Indicates the entity in which the message was dead-lettered.

        :rtype: str
        """
        if self.message.annotations:
            try:
                return self.message.annotations.get(_X_OPT_DEAD_LETTER_SOURCE).decode('UTF-8')
            except AttributeError:
                pass
        return None

    @property
    def delivery_count(self):
        # type: () -> Optional[int]
        """
        Number of deliveries that have been attempted for this message. The count is incremented
        when a message lock expires or the message is explicitly abandoned by the receiver.

        :rtype: int
        """
        if self._amqp_header:
            return self._amqp_header.delivery_count
        return None

    @property
    def enqueued_sequence_number(self):
        # type: () -> Optional[int]
        """
        For messages that have been auto-forwarded, this property reflects the sequence number that had
        first been assigned to the message at its original point of submission.

        :rtype: int
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_ENQUEUE_SEQUENCE_NUMBER)
        return None

    @property
    def enqueued_time_utc(self):
        # type: () -> Optional[datetime.datetime]
        """
        The UTC datetime at which the message has been accepted and stored in the entity.

        :rtype: ~datetime.datetime
        """
        if self.message.annotations:
            timestamp = self.message.annotations.get(_X_OPT_ENQUEUED_TIME)
            if timestamp:
                in_seconds = timestamp/1000.0
                return utc_from_timestamp(in_seconds)
        return None

    @property
    def expires_at_utc(self):
        # type: () -> Optional[datetime.datetime]
        """
        The UTC datetime at which the message is marked for removal and no longer available for retrieval
        from the entity due to expiration. Expiry is controlled by the `Message.time_to_live` property.
        This property is computed from `Message.enqueued_time_utc` + `Message.time_to_live`.

        :rtype: ~datetime.datetime
        """
        if self.enqueued_time_utc and self.time_to_live:
            return self.enqueued_time_utc + self.time_to_live
        return None

    @property
    def sequence_number(self):
        # type: () -> Optional[int]
        """
        The unique number assigned to a message by Service Bus. The sequence number is a unique 64-bit integer
        assigned to a message as it is accepted and stored by the broker and functions as its true identifier.
        For partitioned entities, the topmost 16 bits reflect the partition identifier.
        Sequence numbers monotonically increase. They roll over to 0 when the 48-64 bit range is exhausted.

        :rtype: int
        """
        if self.message.annotations:
            return self.message.annotations.get(_X_OPT_SEQUENCE_NUMBER)
        return None


class ReceivedMessageBase(PeekedMessage):
    """
    A Service Bus Message received from service side.

    :ivar auto_renew_error: Error when AutoLockRenewer is used and it fails to renew the message lock.
    :vartype auto_renew_error: ~azure.servicebus.AutoLockRenewTimeout or ~azure.servicebus.AutoLockRenewFailed

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START receive_complex_message]
            :end-before: [END receive_complex_message]
            :language: python
            :dedent: 4
            :caption: Checking the properties on a received message.
    """

    def __init__(self, message, receive_mode=ReceiveMode.PeekLock, **kwargs):
        # type: (uamqp.message.Message, ReceiveMode, Any) -> None
        super(ReceivedMessageBase, self).__init__(message=message)
        self._settled = (receive_mode == ReceiveMode.ReceiveAndDelete)
        self._received_timestamp_utc = utc_now()
        self._is_deferred_message = kwargs.get("is_deferred_message", False)
        self.auto_renew_error = None # type: Optional[Exception]
        try:
            self._receiver = kwargs.pop("receiver")  # type: Union[ServiceBusReceiver, ServiceBusSessionReceiver]
        except KeyError:
            raise TypeError("ReceivedMessage requires a receiver to be initialized.  This class should never be" + \
            "initialized by a user; the Message class should be utilized instead.")
        self._expiry = None # type: Optional[datetime.datetime]

    def _check_live(self, action):
        # pylint: disable=no-member
        if not self._receiver or not self._receiver._running:  # pylint: disable=protected-access
            raise MessageSettleFailed(action, "Orphan message had no open connection.")
        if self._settled:
            raise MessageAlreadySettled(action)
        try:
            if self._lock_expired:
                raise MessageLockExpired(inner_exception=self.auto_renew_error)
        except TypeError:
            pass
        try:
            if self._receiver.session._lock_expired:  # pylint: disable=protected-access
                raise SessionLockExpired(inner_exception=self._receiver.session.auto_renew_error)
        except AttributeError:
            pass

    def _settle_via_mgmt_link(self, settle_operation, dead_letter_reason=None, dead_letter_error_description=None):
        # type: (str, Optional[str], Optional[str]) -> Callable
        # pylint: disable=protected-access

        if settle_operation == MESSAGE_COMPLETE:
            return functools.partial(
                self._receiver._settle_message,
                SETTLEMENT_COMPLETE,
                [self.lock_token],
            )
        if settle_operation == MESSAGE_ABANDON:
            return functools.partial(
                self._receiver._settle_message,
                SETTLEMENT_ABANDON,
                [self.lock_token],
            )
        if settle_operation == MESSAGE_DEAD_LETTER:
            return functools.partial(
                self._receiver._settle_message,
                SETTLEMENT_DEADLETTER,
                [self.lock_token],
                dead_letter_details={
                    MGMT_REQUEST_DEAD_LETTER_REASON: dead_letter_reason or "",
                    MGMT_REQUEST_DEAD_LETTER_ERROR_DESCRIPTION: dead_letter_error_description or ""
                }
            )
        if settle_operation == MESSAGE_DEFER:
            return functools.partial(
                self._receiver._settle_message,
                SETTLEMENT_DEFER,
                [self.lock_token],
            )
        raise ValueError("Unsupported settle operation type: {}".format(settle_operation))

    def _settle_via_receiver_link(self, settle_operation, dead_letter_reason=None, dead_letter_error_description=None):
        # type: (str, Optional[str], Optional[str]) -> Callable
        if settle_operation == MESSAGE_COMPLETE:
            return functools.partial(self.message.accept)
        if settle_operation == MESSAGE_ABANDON:
            return functools.partial(self.message.modify, True, False)
        if settle_operation == MESSAGE_DEAD_LETTER:
            return functools.partial(
                self.message.reject,
                condition=DEADLETTERNAME,
                description=dead_letter_error_description,
                info={
                    RECEIVER_LINK_DEAD_LETTER_REASON: dead_letter_reason,
                    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION: dead_letter_error_description
                }
            )
        if settle_operation == MESSAGE_DEFER:
            return functools.partial(self.message.modify, True, True)
        raise ValueError("Unsupported settle operation type: {}".format(settle_operation))

    @property
    def _lock_expired(self):
        # type: () -> bool
        # pylint: disable=protected-access
        """
        Whether the lock on the message has expired.

        :rtype: bool
        """
        try:
            if self._receiver.session:  # type: ignore
                raise TypeError("Session messages do not expire. Please use the Session expiry instead.")
        except AttributeError: # Is not a session receiver
            pass
        if self.locked_until_utc and self.locked_until_utc <= utc_now():
            return True
        return False

    @property
    def lock_token(self):
        # type: () -> Optional[Union[uuid.UUID, str]]
        """
        The lock token for the current message serving as a reference to the lock that
        is being held by the broker in PeekLock mode.

        :rtype:  ~uuid.UUID or str
        """
        if self._settled:
            return None

        if self.message.delivery_tag:
            return uuid.UUID(bytes_le=self.message.delivery_tag)

        delivery_annotations = self.message.delivery_annotations
        if delivery_annotations:
            return delivery_annotations.get(_X_OPT_LOCK_TOKEN)
        return None

    @property
    def locked_until_utc(self):
        # type: () -> Optional[datetime.datetime]
        # pylint: disable=protected-access
        """
        The UTC datetime until which the message will be locked in the queue/subscription.
        When the lock expires, delivery count of hte message is incremented and the message
        is again available for retrieval.

        :rtype: datetime.datetime
        """
        try:
            if self._settled or self._receiver.session:  # type: ignore
                return None
        except AttributeError:  # not settled, and isn't session receiver.
            pass
        if self._expiry:
            return self._expiry
        if self.message.annotations and _X_OPT_LOCKED_UNTIL in self.message.annotations:
            expiry_in_seconds = self.message.annotations[_X_OPT_LOCKED_UNTIL]/1000
            self._expiry = utc_from_timestamp(expiry_in_seconds)
        return self._expiry


class ReceivedMessage(ReceivedMessageBase):
    def _settle_message(
            self,
            settle_operation,
            dead_letter_reason=None,
            dead_letter_error_description=None,
    ):
        # type: (str, Optional[str], Optional[str]) -> None
        try:
            if not self._is_deferred_message:
                try:
                    self._settle_via_receiver_link(settle_operation,
                                                   dead_letter_reason=dead_letter_reason,
                                                   dead_letter_error_description=dead_letter_error_description)()
                    return
                except RuntimeError as exception:
                    _LOGGER.info(
                        "Message settling: %r has encountered an exception (%r)."
                        "Trying to settle through management link",
                        settle_operation,
                        exception
                    )
            self._settle_via_mgmt_link(settle_operation,
                                       dead_letter_reason=dead_letter_reason,
                                       dead_letter_error_description=dead_letter_error_description)()
        except Exception as e:
            raise MessageSettleFailed(settle_operation, e)

    def complete(self):
        # type: () -> None
        """Complete the message.

        This removes the message from the queue.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.


        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_sync]
                :end-before: [END receive_sync]
                :language: python
                :dedent: 4
                :caption: Completing a received message to remove it from the queue.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_COMPLETE)
        self._settle_message(MESSAGE_COMPLETE)
        self._settled = True

    def dead_letter(self, reason=None, error_description=None):
        # type: (Optional[str], Optional[str]) -> None
        """Move the message to the Dead Letter queue.

        The Dead Letter queue is a sub-queue that can be
        used to store messages that failed to process correctly, or otherwise require further inspection
        or processing. The queue can also be configured to send expired messages to the Dead Letter queue.

        :param str reason: The reason for dead-lettering the message.
        :param str error_description: The detailed error description for dead-lettering the message.
        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_deadletter_sync]
                :end-before: [END receive_deadletter_sync]
                :language: python
                :dedent: 4
                :caption: Dead letter a message to remove it from the queue by sending it to the dead letter subqueue,
                    and receiving it from there.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_DEAD_LETTER)
        self._settle_message(MESSAGE_DEAD_LETTER,
                             dead_letter_reason=reason,
                             dead_letter_error_description=error_description)
        self._settled = True

    def abandon(self):
        # type: () -> None
        """Abandon the message.

        This message will be returned to the queue and made available to be received again.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.


        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START abandon_message]
                :end-before: [END abandon_message]
                :language: python
                :dedent: 4
                :caption: Abandoning a received message to return it immediately to the queue.
        """
        # pylint: disable=protected-access
        self._check_live(MESSAGE_ABANDON)
        self._settle_message(MESSAGE_ABANDON)
        self._settled = True

    def defer(self):
        # type: () -> None
        """Defer the message.

        This message will remain in the queue but must be requested
        specifically by its sequence number in order to be received.

        :rtype: None
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled if the message has been settled.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired if message lock has already expired.
        :raises: ~azure.servicebus.exceptions.SessionLockExpired if session lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageSettleFailed if message settle operation fails.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
                :start-after: [START receive_defer_sync]
                :end-before: [END receive_defer_sync]
                :language: python
                :dedent: 4
                :caption: Deferring a received message sets it aside such that it can only be received
                    by calling receive_deffered_messages with its sequence number
        """
        self._check_live(MESSAGE_DEFER)
        self._settle_message(MESSAGE_DEFER)
        self._settled = True

    def renew_lock(self, **kwargs):
        # type: (Any) -> datetime.datetime
        # pylint: disable=protected-access,no-member
        """Renew the message lock.

        This will maintain the lock on the message to ensure it is not returned to the queue
        to be reprocessed.

        In order to complete (or otherwise settle) the message, the lock must be maintained,
        and cannot already have expired; an expired lock cannot be renewed.

        Messages received via ReceiveAndDelete mode are not locked, and therefore cannot be renewed.
        This operation is only available for non-sessionful messages as well.

        Lock renewal can be performed as a background task by registering the message with an
        `azure.servicebus.AutoLockRenewer` instance.

        :keyword float timeout: The total operation timeout in seconds including all the retries. The value must be
         greater than 0 if specified. The default value is None, meaning no timeout.
        :returns: The utc datetime the lock is set to expire at.
        :rtype: datetime.datetime
        :raises: TypeError if the message is sessionful.
        :raises: ~azure.servicebus.exceptions.MessageLockExpired is message lock has already expired.
        :raises: ~azure.servicebus.exceptions.MessageAlreadySettled is message has already been settled.
        """
        try:
            if self._receiver.session:  # type: ignore
                raise TypeError("Session messages cannot be renewed. Please renew the Session lock instead.")
        except AttributeError:
            pass
        self._check_live(MESSAGE_RENEW_LOCK)
        token = self.lock_token
        if not token:
            raise ValueError("Unable to renew lock - no lock token found.")

        timeout = kwargs.pop("timeout", None)
        if timeout is not None and timeout <= 0:
            raise ValueError("The timeout must be greater than 0.")

        expiry = self._receiver._renew_locks(token, timeout=timeout)  # type: ignore
        self._expiry = utc_from_timestamp(expiry[MGMT_RESPONSE_MESSAGE_EXPIRATION][0]/1000.0)  # type: datetime.datetime

        return self._expiry


class AMQPMessage(object):
    """
    The internal AMQP message that this ServiceBusMessage represents.  Is read-only.
    """
    def __init__(self, message):
        # type: (uamqp.Message) -> None
        self._message = message

    @property
    def properties(self):
        # type: () -> uamqp.message.MessageProperties
        """
        Properties to add to the message.

        :rtype: ~uamqp.message.MessageProperties
        """
        return uamqp.message.MessageProperties(message_id=self._message.properties.message_id,
                                               user_id=self._message.properties.user_id,
                                               to=self._message.properties.to,
                                               subject=self._message.properties.subject,
                                               reply_to=self._message.properties.reply_to,
                                               correlation_id=self._message.properties.correlation_id,
                                               content_type=self._message.properties.content_type,
                                               content_encoding=self._message.properties.content_encoding
                                               )

    # NOTE: These are disabled pending arch. design and cross-sdk consensus on
    # how we will expose sendability of amqp focused messages. To undo, uncomment and remove deepcopies/workarounds.
    #
    #@properties.setter
    #def properties(self, value):
    #    self._message.properties = value

    @property
    def application_properties(self):
        # type: () -> dict
        """
        Service specific application properties.

        :rtype: dict
        """
        return copy.deepcopy(self._message.application_properties)

    #@application_properties.setter
    #def application_properties(self, value):
    #    self._message.application_properties = value

    @property
    def annotations(self):
        # type: () -> dict
        """
        Service specific message annotations. Keys in the dictionary
        must be `uamqp.types.AMQPSymbol` or `uamqp.types.AMQPuLong`.

        :rtype: dict
        """
        return copy.deepcopy(self._message.annotations)

    #@annotations.setter
    #def annotations(self, value):
    #    self._message.annotations = value

    @property
    def delivery_annotations(self):
        # type: () -> dict
        """
        Delivery-specific non-standard properties at the head of the message.
        Delivery annotations convey information from the sending peer to the receiving peer.
        Keys in the dictionary must be `uamqp.types.AMQPSymbol` or `uamqp.types.AMQPuLong`.

        :rtype: dict
        """
        return copy.deepcopy(self._message.delivery_annotations)

    #@delivery_annotations.setter
    #def delivery_annotations(self, value):
    #    self._message.delivery_annotations = value

    @property
    def header(self):
        # type: () -> uamqp.message.MessageHeader
        """
        The message header.

        :rtype: ~uamqp.message.MessageHeader
        """
        return uamqp.message.MessageHeader(header=self._message.header)

    #@header.setter
    #def header(self, value):
    #    self._message.header = value

    @property
    def footer(self):
        # type: () -> dict
        """
        The message footer.

        :rtype: dict
        """
        return copy.deepcopy(self._message.footer)

    #@footer.setter
    #def footer(self, value):
    #    self._message.footer = value
