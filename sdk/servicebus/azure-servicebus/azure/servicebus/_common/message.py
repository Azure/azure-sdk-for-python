# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# pylint: disable=too-many-lines

import datetime
import uuid
import logging
import copy
from typing import Optional, List, Union, Iterable, TYPE_CHECKING, Any, Mapping, cast

import six

import uamqp.errors
import uamqp.message
from uamqp.constants import MessageState

from .constants import (
    _BATCH_MESSAGE_OVERHEAD_COST,
    ServiceBusReceiveMode,
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_SEQUENCE_NUMBER,
    _X_OPT_ENQUEUE_SEQUENCE_NUMBER,
    _X_OPT_PARTITION_KEY,
    _X_OPT_LOCKED_UNTIL,
    _X_OPT_LOCK_TOKEN,
    _X_OPT_SCHEDULED_ENQUEUE_TIME,
    _X_OPT_DEAD_LETTER_SOURCE,
    PROPERTIES_DEAD_LETTER_REASON,
    PROPERTIES_DEAD_LETTER_ERROR_DESCRIPTION,
    ANNOTATION_SYMBOL_PARTITION_KEY,
    ANNOTATION_SYMBOL_SCHEDULED_ENQUEUE_TIME,
    ANNOTATION_SYMBOL_KEY_MAP,
    MESSAGE_PROPERTY_MAX_LENGTH,
)

from ..exceptions import MessageSizeExceededError
from .utils import (
    utc_from_timestamp,
    utc_now,
    transform_messages_to_sendable_if_needed,
    trace_message,
    create_messages_from_dicts_if_needed
)

if TYPE_CHECKING:
    from ..aio._servicebus_receiver_async import (
        ServiceBusReceiver as AsyncServiceBusReceiver,
    )
    from .._servicebus_receiver import ServiceBusReceiver
    from azure.core.tracing import AbstractSpan

_LOGGER = logging.getLogger(__name__)


class ServiceBusMessage(
    object
):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    """A Service Bus Message.

    :param body: The data to send in a single message.
    :type body: Optional[Union[str, bytes]]

    :keyword Optional[dict] application_properties: The user defined properties on the message.
    :keyword Optional[str] session_id: The session identifier of the message for a sessionful entity.
    :keyword Optional[str] message_id: The id to identify the message.
    :keyword Optional[datetime.datetime] scheduled_enqueue_time_utc: The utc scheduled enqueue time to the message.
    :keyword Optional[datetime.timedelta] time_to_live: The life duration of a message.
    :keyword Optional[str] content_type: The content type descriptor.
    :keyword Optional[str] correlation_id: The correlation identifier.
    :keyword Optional[str] subject: The application specific subject, sometimes referred to as label.
    :keyword Optional[str] partition_key: The partition key for sending a message to a partitioned entity.
    :keyword Optional[str] to: The `to` address used for auto_forward chaining scenarios.
    :keyword Optional[str] reply_to: The address of an entity to send replies to.
    :keyword Optional[str] reply_to_session_id: The session identifier augmenting the `reply_to` address.

    :ivar AMQPAnnotatedMessage raw_amqp_message: Advanced use only.
        The internal AMQP message payload that is sent or received.

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_servicebus.py
            :start-after: [START send_complex_message]
            :end-before: [END send_complex_message]
            :language: python
            :dedent: 4
            :caption: Sending a message with additional properties

    """

    def __init__(self, body, **kwargs):
        # type: (Optional[Union[str, bytes]], Any) -> None
        # Although we might normally thread through **kwargs this causes
        # problems as MessageProperties won't absorb spurious args.
        self._encoding = kwargs.pop("encoding", "UTF-8")
        self._amqp_properties = uamqp.message.MessageProperties(encoding=self._encoding)
        self._amqp_header = uamqp.message.MessageHeader()

        if "message" in kwargs:
            # Note: This cannot be renamed until UAMQP no longer relies on this specific name.
            self.message = kwargs["message"]
            self._amqp_properties = self.message.properties
            self._amqp_header = self.message.header
        else:
            self._build_message(body)
            self.application_properties = kwargs.pop("application_properties", None)
            self.session_id = kwargs.pop("session_id", None)
            self.message_id = kwargs.get("message_id", None)
            self.content_type = kwargs.pop("content_type", None)
            self.correlation_id = kwargs.pop("correlation_id", None)
            self.to = kwargs.pop("to", None)
            self.reply_to = kwargs.pop("reply_to", None)
            self.reply_to_session_id = kwargs.pop("reply_to_session_id", None)
            self.subject = kwargs.pop("subject", None)
            self.scheduled_enqueue_time_utc = kwargs.pop(
                "scheduled_enqueue_time_utc", None
            )
            self.time_to_live = kwargs.pop("time_to_live", None)
            self.partition_key = kwargs.pop("partition_key", None)

        # If message is the full message, raw_amqp_message is the "public facing interface" for what we expose.
        self.raw_amqp_message = AMQPAnnotatedMessage(
            self.message
        )  # type: AMQPAnnotatedMessage

    def __str__(self):
        return str(self.message)

    def _build_message(self, body):
        if not (
            isinstance(body, (six.string_types, six.binary_type)) or (body is None)
        ):
            raise TypeError(
                "ServiceBusMessage body must be a string, bytes, or None.  Got instead: {}".format(
                    type(body)
                )
            )

        self.message = uamqp.Message(
            body, properties=self._amqp_properties, header=self._amqp_header
        )

    def _set_message_annotations(self, key, value):
        if not self.message.annotations:
            self.message.annotations = {}

        if isinstance(self, ServiceBusReceivedMessage):
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
        # type: () -> ServiceBusMessage
        self.message.state = MessageState.WaitingToBeSent
        self.message._response = None  # pylint: disable=protected-access
        return self

    @property
    def session_id(self):
        # type: () -> Optional[str]
        """The session identifier of the message for a sessionful entity.

        For sessionful entities, this application-defined value specifies the session affiliation of the message.
        Messages with the same session identifier are subject to summary locking and enable exact in-order
        processing and demultiplexing. For non-sessionful entities, this value is ignored.

        See Message Sessions in `https://docs.microsoft.com/azure/service-bus-messaging/message-sessions`.

        :rtype: str
        """
        try:
            return self._amqp_properties.group_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.group_id

    @session_id.setter
    def session_id(self, value):
        # type: (str) -> None
        if value and len(value) > MESSAGE_PROPERTY_MAX_LENGTH:
            raise ValueError(
                "session_id cannot be longer than {} characters.".format(
                    MESSAGE_PROPERTY_MAX_LENGTH
                )
            )

        self._amqp_properties.group_id = value

    @property
    def application_properties(self):
        # type: () -> Optional[dict]
        """The user defined properties on the message.

        :rtype: dict
        """
        return self.message.application_properties

    @application_properties.setter
    def application_properties(self, value):
        # type: (dict) -> None
        self.message.application_properties = value

    @property
    def partition_key(self):
        # type: () -> Optional[str]
        """The partition key for sending a message to a partitioned entity.

        Setting this value enables assigning related messages to the same internal partition, so that submission
        sequence order is correctly recorded.
        The partition is chosen by a hash function over this value and cannot be chosen directly.

        See Partitioned queues and topics in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-partitioning`.

        :rtype: str
        """
        p_key = None
        try:
            p_key = self.message.annotations.get(
                _X_OPT_PARTITION_KEY
            ) or self.message.annotations.get(ANNOTATION_SYMBOL_PARTITION_KEY)
            return p_key.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return p_key

    @partition_key.setter
    def partition_key(self, value):
        # type: (str) -> None
        if value and len(value) > MESSAGE_PROPERTY_MAX_LENGTH:
            raise ValueError(
                "partition_key cannot be longer than {} characters.".format(
                    MESSAGE_PROPERTY_MAX_LENGTH
                )
            )

        if value and value != self.session_id:
            raise ValueError(
                "partition_key:{} cannot be set to a different value than session_id:{}".format(
                    value, self.session_id
                )
            )
        self._set_message_annotations(_X_OPT_PARTITION_KEY, value)

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
            timestamp = self.message.annotations.get(
                _X_OPT_SCHEDULED_ENQUEUE_TIME
            ) or self.message.annotations.get(ANNOTATION_SYMBOL_SCHEDULED_ENQUEUE_TIME)
            if timestamp:
                try:
                    in_seconds = timestamp / 1000.0
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
        # type: () -> Optional[Union[bytes, Iterable[bytes]]]
        """The body of the Message.

        :rtype: bytes or Iterable[bytes]
        """
        return self.message.get_data()

    @property
    def content_type(self):
        # type: () -> Optional[str]
        """The content type descriptor.

        Optionally describes the payload of the message, with a descriptor following the format of RFC2045, Section 5,
        for example "application/json".

        :rtype: str
        """
        try:
            return self._amqp_properties.content_type.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.content_type

    @content_type.setter
    def content_type(self, value):
        # type: (str) -> None
        self._amqp_properties.content_type = value

    @property
    def correlation_id(self):
        # type: () -> Optional[str]
        # pylint: disable=line-too-long
        """The correlation identifier.

        Allows an application to specify a context for the message for the purposes of correlation, for example
        reflecting the MessageId of a message that is being replied to.

        See Message Routing and Correlation in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messages-payloads?#message-routing-and-correlation`.

        :rtype: str
        """
        try:
            return self._amqp_properties.correlation_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.correlation_id

    @correlation_id.setter
    def correlation_id(self, value):
        # type: (str) -> None
        self._amqp_properties.correlation_id = value

    @property
    def subject(self):
        # type: () -> Optional[str]
        """The application specific subject, sometimes referred to as a label.

        This property enables the application to indicate the purpose of the message to the receiver in a standardized
        fashion, similar to an email subject line.

        :rtype: str
        """
        try:
            return self._amqp_properties.subject.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.subject

    @subject.setter
    def subject(self, value):
        # type: (str) -> None
        self._amqp_properties.subject = value

    @property
    def message_id(self):
        # type: () -> Optional[str]
        """The id to identify the message.

        The message identifier is an application-defined value that uniquely identifies the message and its payload.
        The identifier is a free-form string and can reflect a GUID or an identifier derived from the
        application context.  If enabled, the duplicate detection (see
        `https://docs.microsoft.com/azure/service-bus-messaging/duplicate-detection`)
        feature identifies and removes second and further submissions of messages with the same message id.

        :rtype: str
        """
        try:
            return self._amqp_properties.message_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.message_id

    @message_id.setter
    def message_id(self, value):
        # type: (str) -> None
        if value and len(str(value)) > MESSAGE_PROPERTY_MAX_LENGTH:
            raise ValueError(
                "message_id cannot be longer than {} characters.".format(
                    MESSAGE_PROPERTY_MAX_LENGTH
                )
            )

        self._amqp_properties.message_id = value

    @property
    def reply_to(self):
        # type: () -> Optional[str]
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
            return self._amqp_properties.reply_to.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.reply_to

    @reply_to.setter
    def reply_to(self, value):
        # type: (str) -> None
        self._amqp_properties.reply_to = value

    @property
    def reply_to_session_id(self):
        # type: () -> Optional[str]
        # pylint: disable=line-too-long
        """The session identifier augmenting the `reply_to` address.

        This value augments the `reply_to` information and specifies which session id should be set for the reply
        when sent to the reply entity.

        See Message Routing and Correlation in
        `https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messages-payloads?#message-routing-and-correlation`.

        :rtype: str
        """
        try:
            return self._amqp_properties.reply_to_group_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.reply_to_group_id

    @reply_to_session_id.setter
    def reply_to_session_id(self, value):
        # type: (str) -> None
        if value and len(value) > MESSAGE_PROPERTY_MAX_LENGTH:
            raise ValueError(
                "reply_to_session_id cannot be longer than {} characters.".format(
                    MESSAGE_PROPERTY_MAX_LENGTH
                )
            )

        self._amqp_properties.reply_to_group_id = value

    @property
    def to(self):
        # type: () -> Optional[str]
        """The `to` address.

        This property is reserved for future use in routing scenarios and presently ignored by the broker itself.
        Applications can use this value in rule-driven auto-forward chaining scenarios to indicate the intended
        logical destination of the message.

        See https://docs.microsoft.com/azure/service-bus-messaging/service-bus-auto-forwarding for more details.

        :rtype: str
        """
        try:
            return self._amqp_properties.to.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._amqp_properties.to

    @to.setter
    def to(self, value):
        # type: (str) -> None
        self._amqp_properties.to = value


class ServiceBusMessageBatch(object):
    """A batch of messages.

    Sending messages in a batch is more performant than sending individual message.
    ServiceBusMessageBatch helps you create the maximum allowed size batch of `Message` to improve sending performance.

    Use the `add` method to add messages until the maximum batch size limit in bytes has been reached -
    at which point a `MessageSizeExceededError` will be raised.

    **Please use the create_message_batch method of ServiceBusSender
    to create a ServiceBusMessageBatch object instead of instantiating a ServiceBusMessageBatch object directly.**

    :param Optional[int] max_size_in_bytes: The maximum size of bytes data that a ServiceBusMessageBatch object
     can hold.
    """

    def __init__(self, max_size_in_bytes=None):
        # type: (Optional[int]) -> None
        self.message = uamqp.BatchMessage(
            data=[], multi_messages=False, properties=None
        )
        self._max_size_in_bytes = (
            max_size_in_bytes or uamqp.constants.MAX_MESSAGE_LENGTH_BYTES
        )
        self._size = self.message.gather()[0].get_message_encoded_size()
        self._count = 0
        self._messages = []  # type: List[ServiceBusMessage]

    def __repr__(self):
        # type: () -> str
        batch_repr = "max_size_in_bytes={}, message_count={}".format(
            self.max_size_in_bytes, self._count
        )
        return "ServiceBusMessageBatch({})".format(batch_repr)

    def __len__(self):
        # type: () -> int
        return self._count

    def _from_list(self, messages, parent_span=None):
        # type: (Iterable[ServiceBusMessage], AbstractSpan) -> None
        for message in messages:
            self._add(message, parent_span)

    @property
    def max_size_in_bytes(self):
        # type: () -> int
        """The maximum size of bytes data that a ServiceBusMessageBatch object can hold.

        :rtype: int
        """
        return self._max_size_in_bytes

    @property
    def size_in_bytes(self):
        # type: () -> int
        """The combined size of the messages in the batch, in bytes.

        :rtype: int
        """
        return self._size

    def add_message(self, message):
        # type: (Union[ServiceBusMessage, Mapping[str, Any]]) -> None
        """Try to add a single Message to the batch.

        The total size of an added message is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `MessageSizeExceededError` will
        be raised.

        :param message: The Message to be added to the batch.
        :type message: ~azure.servicebus.ServiceBusMessage
        :rtype: None
        :raises: :class: ~azure.servicebus.exceptions.MessageSizeExceededError, when exceeding the size limit.
        """

        return self._add(message)

    def _add(self, add_message, parent_span=None):
        # type: (Union[ServiceBusMessage, Mapping[str, Any]], AbstractSpan) -> None
        """Actual add implementation.  The shim exists to hide the internal parameters such as parent_span."""
        message = create_messages_from_dicts_if_needed(add_message, ServiceBusMessage)
        message = transform_messages_to_sendable_if_needed(message)
        message = cast(ServiceBusMessage, message)
        trace_message(
            message, parent_span
        )  # parent_span is e.g. if built as part of a send operation.
        message_size = message.message.get_message_encoded_size()

        # For a ServiceBusMessageBatch, if the encoded_message_size of event_data is < 256, then the overhead cost to
        # encode that message into the ServiceBusMessageBatch would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = (
            self._size
            + message_size
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (message_size < 256) else 1]
        )

        if size_after_add > self.max_size_in_bytes:
            raise MessageSizeExceededError(
                message="ServiceBusMessageBatch has reached its size limit: {}".format(
                    self.max_size_in_bytes
                )
            )

        self.message._body_gen.append(message)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1
        self._messages.append(message)


class ServiceBusReceivedMessage(ServiceBusMessage):
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

    def __init__(self, message, receive_mode=ServiceBusReceiveMode.PEEK_LOCK, **kwargs):
        # type: (uamqp.message.Message, Union[ServiceBusReceiveMode, str], Any) -> None
        super(ServiceBusReceivedMessage, self).__init__(None, message=message)  # type: ignore
        self._settled = receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
        self._received_timestamp_utc = utc_now()
        self._is_deferred_message = kwargs.get("is_deferred_message", False)
        self._is_peeked_message = kwargs.get("is_peeked_message", False)
        self.auto_renew_error = None  # type: Optional[Exception]
        try:
            self._receiver = kwargs.pop(
                "receiver"
            )  # type: Union[ServiceBusReceiver, AsyncServiceBusReceiver]
        except KeyError:
            raise TypeError(
                "ServiceBusReceivedMessage requires a receiver to be initialized. "
                + "This class should never be initialized by a user; "
                + "for outgoing messages, the ServiceBusMessage class should be utilized instead."
            )
        self._expiry = None  # type: Optional[datetime.datetime]

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
                raise TypeError(
                    "Session messages do not expire. Please use the Session expiry instead."
                )
        except AttributeError:  # Is not a session receiver
            pass
        if self.locked_until_utc and self.locked_until_utc <= utc_now():
            return True
        return False

    def _to_outgoing_message(self):
        # type: () -> ServiceBusMessage
        amqp_message = self.message
        amqp_body = amqp_message._body  # pylint: disable=protected-access

        if isinstance(amqp_body, uamqp.message.DataBody):
            body = b"".join(amqp_body.data)
        else:
            # amqp_body is type of uamqp.message.ValueBody
            body = amqp_body.data

        return ServiceBusMessage(
            body=body,
            content_type=self.content_type,
            correlation_id=self.correlation_id,
            subject=self.subject,
            message_id=self.message_id,
            partition_key=self.partition_key,
            application_properties=self.application_properties,
            reply_to=self.reply_to,
            reply_to_session_id=self.reply_to_session_id,
            session_id=self.session_id,
            scheduled_enqueue_time_utc=self.scheduled_enqueue_time_utc,
            time_to_live=self.time_to_live,
            to=self.to,
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
                return self.message.application_properties.get(
                    PROPERTIES_DEAD_LETTER_ERROR_DESCRIPTION
                ).decode("UTF-8")
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
                return self.message.application_properties.get(
                    PROPERTIES_DEAD_LETTER_REASON
                ).decode("UTF-8")
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
                return self.message.annotations.get(_X_OPT_DEAD_LETTER_SOURCE).decode(
                    "UTF-8"
                )
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
                in_seconds = timestamp / 1000.0
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

    @property
    def lock_token(self):
        # type: () -> Optional[Union[uuid.UUID, str]]
        """
        The lock token for the current message serving as a reference to the lock that
        is being held by the broker in PEEK_LOCK mode.

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
            expiry_in_seconds = self.message.annotations[_X_OPT_LOCKED_UNTIL] / 1000
            self._expiry = utc_from_timestamp(expiry_in_seconds)
        return self._expiry


class AMQPAnnotatedMessage(object):
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
        return uamqp.message.MessageProperties(
            message_id=self._message.properties.message_id,
            user_id=self._message.properties.user_id,
            to=self._message.properties.to,
            subject=self._message.properties.subject,
            reply_to=self._message.properties.reply_to,
            correlation_id=self._message.properties.correlation_id,
            content_type=self._message.properties.content_type,
            content_encoding=self._message.properties.content_encoding,
        )

    # NOTE: These are disabled pending arch. design and cross-sdk consensus on
    # how we will expose sendability of amqp focused messages. To undo, uncomment and remove deepcopies/workarounds.
    #
    # @properties.setter
    # def properties(self, value):
    #    self._message.properties = value

    @property
    def application_properties(self):
        # type: () -> Optional[dict]
        """
        Service specific application properties.

        :rtype: dict
        """
        return copy.deepcopy(self._message.application_properties)

    # @application_properties.setter
    # def application_properties(self, value):
    #    self._message.application_properties = value

    @property
    def annotations(self):
        # type: () -> Optional[dict]
        """
        Service specific message annotations. Keys in the dictionary
        must be `uamqp.types.AMQPSymbol` or `uamqp.types.AMQPuLong`.

        :rtype: dict
        """
        return copy.deepcopy(self._message.annotations)

    # @annotations.setter
    # def annotations(self, value):
    #    self._message.annotations = value

    @property
    def delivery_annotations(self):
        # type: () -> Optional[dict]
        """
        Delivery-specific non-standard properties at the head of the message.
        Delivery annotations convey information from the sending peer to the receiving peer.
        Keys in the dictionary must be `uamqp.types.AMQPSymbol` or `uamqp.types.AMQPuLong`.

        :rtype: dict
        """
        return copy.deepcopy(self._message.delivery_annotations)

    # @delivery_annotations.setter
    # def delivery_annotations(self, value):
    #    self._message.delivery_annotations = value

    @property
    def header(self):
        # type: () -> uamqp.message.MessageHeader
        """
        The message header.

        :rtype: ~uamqp.message.MessageHeader
        """
        return uamqp.message.MessageHeader(header=self._message.header)

    # @header.setter
    # def header(self, value):
    #    self._message.header = value

    @property
    def footer(self):
        # type: () -> Optional[dict]
        """
        The message footer.

        :rtype: dict
        """
        return copy.deepcopy(self._message.footer)

    # @footer.setter
    # def footer(self, value):
    #    self._message.footer = value
