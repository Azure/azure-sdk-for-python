# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals, annotations

import json
import datetime
import logging
import uuid
from typing import (
    Union,
    Dict,
    Any,
    AnyStr,
    Iterable,
    Optional,
    List,
    TYPE_CHECKING,
    cast,
)
from typing_extensions import TypedDict

from ._utils import (
    trace_message,
    utc_from_timestamp,
    transform_outbound_single_message,
    decode_with_recurse,
)
from ._constants import (
    PROP_SEQ_NUMBER,
    PROP_OFFSET,
    PROP_PARTITION_KEY,
    PROP_TIMESTAMP,
    PROP_ABSOLUTE_EXPIRY_TIME,
    PROP_CONTENT_ENCODING,
    PROP_CONTENT_TYPE,
    PROP_CORRELATION_ID,
    PROP_GROUP_ID,
    PROP_GROUP_SEQUENCE,
    PROP_MESSAGE_ID,
    PROP_REPLY_TO,
    PROP_REPLY_TO_GROUP_ID,
    PROP_SUBJECT,
    PROP_TO,
    PROP_USER_ID,
    PROP_CREATION_TIME,
)
from .amqp import (
    AmqpAnnotatedMessage,
    AmqpMessageBodyType,
    AmqpMessageHeader,
    AmqpMessageProperties,
)
from ._transport._uamqp_transport import UamqpTransport
from uamqp import types

if TYPE_CHECKING:
    from uamqp import Message as uamqp_Message, BatchMessage as uamqp_BatchMessage
    from ._transport._base import AmqpTransport

MessageContent = TypedDict("MessageContent", {"content": bytes, "content_type": str})
PrimitiveTypes = Optional[
    Union[
        int,
        float,
        bytes,
        bool,
        str,
        Dict,
        List,
        uuid.UUID,
    ]
]

_LOGGER = logging.getLogger(__name__)

# event_data.encoded_size < 255, batch encode overhead is 5, >=256, overhead is 8 each
_BATCH_MESSAGE_OVERHEAD_COST = [5, 8]

_SYS_PROP_KEYS_TO_MSG_PROPERTIES = (
    (PROP_MESSAGE_ID, "message_id"),
    (PROP_USER_ID, "user_id"),
    (PROP_TO, "to"),
    (PROP_SUBJECT, "subject"),
    (PROP_REPLY_TO, "reply_to"),
    (PROP_CORRELATION_ID, "correlation_id"),
    (PROP_CONTENT_TYPE, "content_type"),
    (PROP_CONTENT_ENCODING, "content_encoding"),
    (PROP_ABSOLUTE_EXPIRY_TIME, "absolute_expiry_time"),
    (PROP_CREATION_TIME, "creation_time"),
    (PROP_GROUP_ID, "group_id"),
    (PROP_GROUP_SEQUENCE, "group_sequence"),
    (PROP_REPLY_TO_GROUP_ID, "reply_to_group_id"),
)


class EventData(object):
    """The EventData class is a container for event content.

    :param body: The data to send in a single message. body can be type of str or bytes.
    :type body: str or bytes

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_code_eventhub.py
            :start-after: [START create_event_data]
            :end-before: [END create_event_data]
            :language: python
            :dedent: 4
            :caption: Create instances of EventData

    """

    def __init__(
        self,
        body: Optional[Union[str, bytes, List[AnyStr]]] = None,
    ) -> None:
        self._last_enqueued_event_properties = {}  # type: Dict[str, Any]
        self._sys_properties = None  # type: Optional[Dict[bytes, Any]]
        if body is None:
            raise ValueError("EventData cannot be None.")

        # Internal usage only for transforming AmqpAnnotatedMessage to outgoing EventData
        self._raw_amqp_message = AmqpAnnotatedMessage(  # type: ignore
            data_body=body, annotations={}, application_properties={}
        )
        # amqp message to be reset right before sending
        self._message = UamqpTransport.to_outgoing_amqp_message(self._raw_amqp_message)
        self._raw_amqp_message.header = AmqpMessageHeader()
        self._raw_amqp_message.properties = AmqpMessageProperties()
        self.message_id = None
        self.content_type = None
        self.correlation_id = None

    def __repr__(self) -> str:
        # pylint: disable=bare-except
        try:
            body_str = self.body_as_str()
        except:
            body_str = "<read-error>"
        event_repr = f"body='{body_str}'"
        try:
            event_repr += f", properties={self.properties}"
        except:
            event_repr += ", properties=<read-error>"
        try:
            event_repr += f", offset={self.offset}"
        except:
            event_repr += ", offset=<read-error>"
        try:
            event_repr += f", sequence_number={self.sequence_number}"
        except:
            event_repr += ", sequence_number=<read-error>"
        try:
            event_repr += f", partition_key={self.partition_key!r}"
        except:
            event_repr += ", partition_key=<read-error>"
        try:
            event_repr += f", enqueued_time={self.enqueued_time!r}"
        except:
            event_repr += ", enqueued_time=<read-error>"
        return f"EventData({event_repr})"

    def __str__(self) -> str:
        try:
            body_str = self.body_as_str()
        except:  # pylint: disable=bare-except
            body_str = "<read-error>"
        event_str = f"{{ body: '{body_str}'"
        try:
            event_str += f", properties: {self.properties}"
            if self.offset:
                event_str += f", offset: {self.offset}"
            if self.sequence_number:
                event_str += f", sequence_number: {self.sequence_number}"
            if self.partition_key:
                event_str += f", partition_key={self.partition_key!r}"
            if self.enqueued_time:
                event_str += f", enqueued_time={self.enqueued_time!r}"
        except:  # pylint: disable=bare-except
            pass
        event_str += " }"
        return event_str

    def __message_content__(self) -> MessageContent:
        if self.body_type != AmqpMessageBodyType.DATA:
            raise TypeError("`body_type` must be `AmqpMessageBodyType.DATA`.")
        content = bytearray()
        for c in self.body:  # type: ignore
            content += c  # type: ignore
        content_type = cast(str, self.content_type)
        return {"content": bytes(content), "content_type": content_type}

    @classmethod
    def from_message_content(  # pylint: disable=unused-argument
        cls, content: bytes, content_type: str, **kwargs: Any
    ) -> "EventData":
        """
        Creates an EventData object given content type and a content value to be set as body.

        :param bytes content: The content value to be set as the body of the message.
        :param str content_type: The content type to be set on the message.
        :rtype: ~azure.eventhub.EventData
        """
        event_data = cls(content)
        event_data.content_type = content_type
        return event_data

    @classmethod
    def _from_message(
        cls,
        message: uamqp_Message,
        raw_amqp_message: Optional[AmqpAnnotatedMessage] = None,
    ) -> EventData:
        # pylint:disable=protected-access
        """Internal use only.

        Creates an EventData object from a raw uamqp message and, if provided, AmqpAnnotatedMessage.

        :param ~uamqp.Message message: A received uamqp message.
        :param ~azure.eventhub.amqp.AmqpAnnotatedMessage message: An amqp annotated message.
        :rtype: ~azure.eventhub.EventData
        """
        event_data = cls(body="")
        # pylint: disable=protected-access
        event_data._message = message
        event_data._raw_amqp_message = (
            raw_amqp_message
            if raw_amqp_message
            else AmqpAnnotatedMessage(message=message)
        )
        return event_data

    def _decode_non_data_body_as_str(self, encoding: str = "UTF-8") -> str:
        # pylint: disable=protected-access
        body = self.raw_amqp_message.body
        if self.body_type == AmqpMessageBodyType.VALUE:
            if not body:
                return ""
            return str(decode_with_recurse(body, encoding))

        seq_list = [d for seq_section in body for d in seq_section]
        return str(decode_with_recurse(seq_list, encoding))

    @property
    def message(self) -> uamqp_Message:
        return self._message

    @message.setter
    def message(self, value: uamqp_Message) -> None:
        self._message = value

    @property
    def raw_amqp_message(self) -> AmqpAnnotatedMessage:
        """Advanced usage only. The internal AMQP message payload that is sent or received."""
        return self._raw_amqp_message

    @property
    def sequence_number(self) -> Optional[int]:
        """The sequence number of the event.

        :rtype: int
        """
        return self._raw_amqp_message.annotations.get(PROP_SEQ_NUMBER, None)

    @property
    def offset(self) -> Optional[str]:
        """The offset of the event.

        :rtype: str
        """
        try:
            return self._raw_amqp_message.annotations[PROP_OFFSET].decode("UTF-8")
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self) -> Optional[datetime.datetime]:
        """The enqueued timestamp of the event.

        :rtype: datetime.datetime
        """
        timestamp = self._raw_amqp_message.annotations.get(PROP_TIMESTAMP, None)
        if timestamp:
            return utc_from_timestamp(float(timestamp) / 1000)
        return None

    @property
    def partition_key(self) -> Optional[bytes]:
        """The partition key of the event.

        :rtype: bytes
        """
        return self._raw_amqp_message.annotations.get(PROP_PARTITION_KEY, None)

    @property
    def properties(self) -> Dict[Union[str, bytes], Any]:
        """Application-defined properties on the event.

        :rtype: dict
        """
        return self._raw_amqp_message.application_properties

    @properties.setter
    def properties(self, value: Dict[Union[str, bytes], Any]):
        """Application-defined properties on the event.

        :param dict value: The application properties for the EventData.
        """
        properties = None if value is None else dict(value)
        self._raw_amqp_message.application_properties = properties

    @property
    def system_properties(self) -> Dict[bytes, Any]:
        """Metadata set by the Event Hubs Service associated with the event.

        An EventData could have some or all of the following meta data depending on the source
        of the event data.

            - b"x-opt-sequence-number" (int)
            - b"x-opt-offset" (bytes)
            - b"x-opt-partition-key" (bytes)
            - b"x-opt-enqueued-time" (int)
            - b"message-id" (bytes)
            - b"user-id" (bytes)
            - b"to" (bytes)
            - b"subject" (bytes)
            - b"reply-to" (bytes)
            - b"correlation-id" (bytes)
            - b"content-type" (bytes)
            - b"content-encoding" (bytes)
            - b"absolute-expiry-time" (int)
            - b"creation-time" (int)
            - b"group-id" (bytes)
            - b"group-sequence" (bytes)
            - b"reply-to-group-id" (bytes)

        :rtype: dict
        """

        if self._sys_properties is None:
            self._sys_properties = {}
            if self._raw_amqp_message.properties:
                for key, prop_name in _SYS_PROP_KEYS_TO_MSG_PROPERTIES:
                    value = getattr(self._raw_amqp_message.properties, prop_name, None)
                    if value:
                        self._sys_properties[key] = value
            self._sys_properties.update(self._raw_amqp_message.annotations)
        return self._sys_properties

    @property
    def body(self) -> PrimitiveTypes:
        """The body of the Message. The format may vary depending on the body type:
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.DATA<azure.eventhub.amqp.AmqpMessageBodyType.DATA>`,
        the body could be bytes or Iterable[bytes].
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.SEQUENCE<azure.eventhub.amqp.AmqpMessageBodyType.SEQUENCE>`,
        the body could be List or Iterable[List].
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.VALUE<azure.eventhub.amqp.AmqpMessageBodyType.VALUE>`,
        the body could be any type.

        :rtype: int or bool or float or bytes or str or dict or list or uuid.UUID
        """
        try:
            return self._raw_amqp_message.body
        except:
            raise ValueError("Event content empty.")

    @property
    def body_type(self) -> AmqpMessageBodyType:
        """The body type of the underlying AMQP message.

        :rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """
        return self._raw_amqp_message.body_type

    def body_as_str(self, encoding: str = "UTF-8") -> str:
        """The content of the event as a string, if the data is of a compatible type.

        :param encoding: The encoding to use for decoding event data.
         Default is 'UTF-8'
        :rtype: str
        """
        data = self.body
        try:
            if self.body_type != AmqpMessageBodyType.DATA:
                return self._decode_non_data_body_as_str(encoding=encoding)
            return "".join(b.decode(encoding) for b in cast(Iterable[bytes], data))
        except TypeError:
            return str(data)
        except:  # pylint: disable=bare-except
            pass
        try:
            return cast(bytes, data).decode(encoding)
        except Exception as e:
            raise TypeError(f"Message data is not compatible with string type: {e}")

    def body_as_json(self, encoding: str = "UTF-8") -> Dict[str, Any]:
        """The content of the event loaded as a JSON object, if the data is compatible.

        :param encoding: The encoding to use for decoding event data.
         Default is 'UTF-8'
        :rtype: Dict[str, Any]
        """
        data_str = self.body_as_str(encoding=encoding)
        try:
            return json.loads(data_str)
        except Exception as e:
            raise TypeError(f"Event data is not compatible with JSON type: {e}")

    @property
    def content_type(self) -> Optional[str]:
        """The content type descriptor.
        Optionally describes the payload of the message, with a descriptor following the format of RFC2045, Section 5,
        for example "application/json".
        :rtype: str
        """
        if not self._raw_amqp_message.properties:
            return None
        try:
            return self._raw_amqp_message.properties.content_type.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._raw_amqp_message.properties.content_type

    @content_type.setter
    def content_type(self, value: str) -> None:
        if not self._raw_amqp_message.properties:
            self._raw_amqp_message.properties = AmqpMessageProperties()
        self._raw_amqp_message.properties.content_type = value

    @property
    def correlation_id(self) -> Optional[str]:
        """The correlation identifier.
        Allows an application to specify a context for the message for the purposes of correlation, for example
        reflecting the MessageId of a message that is being replied to.
        :rtype: str
        """
        if not self._raw_amqp_message.properties:
            return None
        try:
            return self._raw_amqp_message.properties.correlation_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._raw_amqp_message.properties.correlation_id

    @correlation_id.setter
    def correlation_id(self, value: str) -> None:
        if not self._raw_amqp_message.properties:
            self._raw_amqp_message.properties = AmqpMessageProperties()
        self._raw_amqp_message.properties.correlation_id = value

    @property
    def message_id(self) -> Optional[str]:
        """The id to identify the message.
        The message identifier is an application-defined value that uniquely identifies the message and its payload.
        The identifier is a free-form string and can reflect a GUID or an identifier derived from the
        application context.  If enabled, the duplicate detection feature identifies and removes second and
        further submissions of messages with the same message id.
        :rtype: str
        """
        if not self._raw_amqp_message.properties:
            return None
        try:
            return self._raw_amqp_message.properties.message_id.decode("UTF-8")
        except (AttributeError, UnicodeDecodeError):
            return self._raw_amqp_message.properties.message_id

    @message_id.setter
    def message_id(self, value: str) -> None:
        if not self._raw_amqp_message.properties:
            self._raw_amqp_message.properties = AmqpMessageProperties()
        self._raw_amqp_message.properties.message_id = value


class EventDataBatch(object):
    """A batch of events.

    Sending events in a batch is more performant than sending individual events.
    EventDataBatch helps you create the maximum allowed size batch of `EventData` to improve sending performance.

    Use the `add` method to add events until the maximum batch size limit in bytes has been reached -
    at which point a `ValueError` will be raised.
    Use the `send_batch` method of :class:`EventHubProducerClient<azure.eventhub.EventHubProducerClient>`
    or the async :class:`EventHubProducerClient<azure.eventhub.aio.EventHubProducerClient>`
    for sending.

    **Please use the create_batch method of EventHubProducerClient
    to create an EventDataBatch object instead of instantiating an EventDataBatch object directly.**

    **WARNING: Updating the value of the instance variable max_size_in_bytes on an instantiated EventDataBatch object
    is HIGHLY DISCOURAGED. The updated max_size_in_bytes value may conflict with the maximum size of events allowed
    by the Event Hubs service and result in a sending failure.**

    :param int max_size_in_bytes: The maximum size of bytes data that an EventDataBatch object can hold.
    :param str partition_id: The specific partition ID to send to.
    :param str partition_key: With the given partition_key, event data will be sent to a particular partition of the
     Event Hub decided by the service.
    """

    def __init__(
        self,
        max_size_in_bytes: Optional[int] = None,
        partition_id: Optional[str] = None,
        partition_key: Optional[Union[str, bytes]] = None,
        **kwargs,
    ) -> None:
        # TODO: this changes API, check with Anna if valid -
        # Might need move out message creation to right before sending.
        # Might take more time to loop through events and add them all to batch in `send` than in `add` here
        self._amqp_transport = kwargs.pop("amqp_transport", UamqpTransport)


        if partition_key and not isinstance(
            partition_key, (str, bytes)
        ):
            _LOGGER.info(
                "WARNING: Setting partition_key of non-string value on the events to be sent is discouraged "
                "as the partition_key will be ignored by the Event Hub service and events will be assigned "
                "to all partitions using round-robin. Furthermore, there are SDKs for consuming events which expect "
                "partition_key to only be string type, they might fail to parse the non-string value."
            )

        self.max_size_in_bytes = (
            max_size_in_bytes or self._amqp_transport.MAX_FRAME_SIZE_BYTES
        )
        self._message = self._amqp_transport.build_batch_message(data=[])
        self._partition_id = partition_id
        self._partition_key = partition_key

        self._message = self._amqp_transport.set_message_partition_key(
            self._message, self._partition_key
        )
        self._size = self._amqp_transport.get_batch_message_encoded_size(self._message)
        self._count = 0
        self._internal_events: List[
            Union[EventData, AmqpAnnotatedMessage]
        ] = []

    def __repr__(self) -> str:
        batch_repr = (
            f"max_size_in_bytes={self.max_size_in_bytes}, partition_id={self._partition_id}, "
            f"partition_key={self._partition_key!r}, event_count={self._count}"
        )
        return f"EventDataBatch({batch_repr})"

    def __len__(self) -> int:
        return self._count

    @classmethod
    def _from_batch(
        cls,
        batch_data: Iterable[EventData],
        amqp_transport: AmqpTransport,
        partition_key: Optional[AnyStr] = None,
    ) -> EventDataBatch:
        outgoing_batch_data = [
            transform_outbound_single_message(
                m, EventData, amqp_transport.to_outgoing_amqp_message
            )
            for m in batch_data
        ]
        batch_data_instance = cls(
            partition_key=partition_key, amqp_transport=amqp_transport
        )

        for event_data in outgoing_batch_data:
            batch_data_instance.add(event_data)
        return batch_data_instance

    def _load_events(self, events):
        for event_data in events:
            try:
                self.add(event_data)
            except ValueError:
                raise ValueError(
                    "The combined size of EventData or AmqpAnnotatedMessage collection exceeds "
                    "the Event Hub frame size limit. Please send a smaller collection of EventData "
                    "or use EventDataBatch, which is guaranteed to be under the frame size limit"
                )

    @property
    def size_in_bytes(self) -> int:
        """The combined size of the events in the batch, in bytes.

        :rtype: int
        """
        return self._size

    @property
    def message(self) -> uamqp_BatchMessage:
        return self._message

    @message.setter
    def message(self, value: uamqp_BatchMessage) -> None:
        self._message = value

    def add(self, event_data: Union[EventData, AmqpAnnotatedMessage]) -> None:
        """Try to add an EventData to the batch.

        The total size of an added event is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `ValueError` will
        be raised.

        :param event_data: The EventData to add to the batch.
        :type event_data: Union[~azure.eventhub.EventData, ~azure.eventhub.amqp.AmqpAnnotatedMessage]
        :rtype: None
        :raise: :class:`ValueError`, when exceeding the size limit.
        """

        outgoing_event_data = transform_outbound_single_message(
            event_data, EventData, self._amqp_transport.to_outgoing_amqp_message
        )

        if self._partition_key:
            if (
                outgoing_event_data.partition_key
                and outgoing_event_data.partition_key != self._partition_key
            ):
                raise ValueError(
                    "The partition key of event_data does not match the partition key of this batch."
                )
            if not outgoing_event_data.partition_key:
                self._amqp_transport.set_message_partition_key(
                    outgoing_event_data._message,  # pylint: disable=protected-access
                    self._partition_key,
                )

        trace_message(outgoing_event_data)
        event_data_size = self._amqp_transport.get_message_encoded_size(
            outgoing_event_data._message  # pylint: disable=protected-access
        )
        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        # message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = (
            self._size
            + event_data_size
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (event_data_size < 256) else 1]
        )

        if size_after_add > self.max_size_in_bytes:
            raise ValueError(
                f"EventDataBatch has reached its size limit: {self.max_size_in_bytes}"
            )

        self._amqp_transport.add_batch(self, outgoing_event_data, event_data)
        self._size = size_after_add
        self._count += 1
