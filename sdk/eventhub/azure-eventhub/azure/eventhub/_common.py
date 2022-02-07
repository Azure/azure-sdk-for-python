# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import json
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
import six

from ._utils import (
    set_message_partition_key,
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

from ._pyamqp import constants, utils as pyutils
from ._pyamqp.message import BatchMessage, Message

if TYPE_CHECKING:
    import datetime

PrimitiveTypes = Optional[Union[
    int,
    float,
    bytes,
    bool,
    str,
    Dict,
    List,
    uuid.UUID,
]]

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
        self.message = (self._raw_amqp_message._message)  # pylint:disable=protected-access
        self._raw_amqp_message.header = AmqpMessageHeader()
        self._raw_amqp_message.properties = AmqpMessageProperties()
        self.message_id = None
        self.content_type = None
        self.correlation_id = None

    def __repr__(self):
        # type: () -> str
        # pylint: disable=bare-except
        try:
            # TODO: below call won't work b/c pyamqp.message.message doesn't have body_type
            body_str = self.body_as_str()
        except:
            body_str = "<read-error>"
        event_repr = "body='{}'".format(body_str)
        try:
            event_repr += ", properties={}".format(self.properties)
        except:
            event_repr += ", properties=<read-error>"
        try:
            event_repr += ", offset={}".format(self.offset)
        except:
            event_repr += ", offset=<read-error>"
        try:
            event_repr += ", sequence_number={}".format(self.sequence_number)
        except:
            event_repr += ", sequence_number=<read-error>"
        try:
            event_repr += ", partition_key={!r}".format(self.partition_key)
        except:
            event_repr += ", partition_key=<read-error>"
        try:
            event_repr += ", enqueued_time={!r}".format(self.enqueued_time)
        except:
            event_repr += ", enqueued_time=<read-error>"
        return "EventData({})".format(event_repr)

    def __str__(self):
        # type: () -> str
        try:
            body_str = self.body_as_str()
        except:  # pylint: disable=bare-except
            body_str = "<read-error>"
        event_str = "{{ body: '{}'".format(body_str)
        try:
            event_str += ", properties: {}".format(self.properties)
            if self.offset:
                event_str += ", offset: {}".format(self.offset)
            if self.sequence_number:
                event_str += ", sequence_number: {}".format(self.sequence_number)
            if self.partition_key:
                event_str += ", partition_key={!r}".format(self.partition_key)
            if self.enqueued_time:
                event_str += ", enqueued_time={!r}".format(self.enqueued_time)
        except:  # pylint: disable=bare-except
            pass
        event_str += " }"
        return event_str

    @classmethod
    def _from_message(cls, message, raw_amqp_message=None):
        # type: (Message, Optional[AmqpAnnotatedMessage]) -> EventData
        # pylint:disable=protected-access
        """Internal use only.

        Creates an EventData object from a raw uamqp message and, if provided, AmqpAnnotatedMessage.

        :param ~uamqp.Message message: A received uamqp message.
        :param ~azure.eventhub.amqp.AmqpAnnotatedMessage message: An amqp annotated message.
        :rtype: ~azure.eventhub.EventData
        """
        event_data = cls(body="")
        event_data.message = message
        # pylint: disable=protected-access
        event_data._raw_amqp_message = raw_amqp_message if raw_amqp_message else AmqpAnnotatedMessage(message=message)
        return event_data

    def _encode_message(self):
        # type: () -> bytes
        # pylint: disable=protected-access
        return self._raw_amqp_message._message.encode_message()

    def _decode_non_data_body_as_str(self, encoding="UTF-8"):
        # type: (str) -> str
        # pylint: disable=protected-access
        body = self.raw_amqp_message.body
        if self.body_type == AmqpMessageBodyType.VALUE:
            if not body:
                return ""
            return str(decode_with_recurse(body, encoding))

        seq_list = [d for seq_section in body for d in seq_section]
        return str(decode_with_recurse(seq_list, encoding))

    def _to_outgoing_message(self):
        # type: () -> EventData
        self.message = (self._raw_amqp_message._to_outgoing_amqp_message())  # pylint:disable=protected-access
        return self

    @property
    def raw_amqp_message(self):
        # type: () -> AmqpAnnotatedMessage
        """Advanced usage only. The internal AMQP message payload that is sent or received."""
        return self._raw_amqp_message

    @property
    def sequence_number(self):
        # type: () -> Optional[int]
        """The sequence number of the event.

        :rtype: int
        """
        return self._raw_amqp_message.annotations.get(PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        # type: () -> Optional[str]
        """The offset of the event.

        :rtype: str
        """
        try:
            return self._raw_amqp_message.annotations[PROP_OFFSET].decode("UTF-8")
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self):
        # type: () -> Optional[datetime.datetime]
        """The enqueued timestamp of the event.

        :rtype: datetime.datetime
        """
        timestamp = self._raw_amqp_message.annotations.get(PROP_TIMESTAMP, None)
        if timestamp:
            return utc_from_timestamp(float(timestamp) / 1000)
        return None

    @property
    def partition_key(self):
        # type: () -> Optional[bytes]
        """The partition key of the event.

        :rtype: bytes
        """
        try:
            return self._raw_amqp_message.annotations[PROP_PARTITION_KEY]
        except KeyError:
            return self._raw_amqp_message.annotations.get(PROP_PARTITION_KEY, None)

    @property
    def properties(self):
        # type: () -> Dict[Union[str, bytes], Any]
        """Application-defined properties on the event.

        :rtype: dict
        """
        return self._raw_amqp_message.application_properties

    @properties.setter
    def properties(self, value):
        # type: (Dict[Union[str, bytes], Any]) -> None
        """Application-defined properties on the event.

        :param dict value: The application properties for the EventData.
        """
        properties = None if value is None else dict(value)
        self._raw_amqp_message.application_properties = properties

    @property
    def system_properties(self):
        # type: () -> Dict[bytes, Any]
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
    def body(self):
        # type: () -> PrimitiveTypes
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
    def body_type(self):
        # type: () -> AmqpMessageBodyType
        """The body type of the underlying AMQP message.

        :rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """
        return self._raw_amqp_message.body_type

    def body_as_str(self, encoding="UTF-8"):
        # type: (str) -> str
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
            return six.text_type(data)
        except:  # pylint: disable=bare-except
            pass
        try:
            return cast(bytes, data).decode(encoding)
        except Exception as e:
            raise TypeError(
                "Message data is not compatible with string type: {}".format(e)
            )

    def body_as_json(self, encoding="UTF-8"):
        # type: (str) -> Dict[str, Any]
        """The content of the event loaded as a JSON object, if the data is compatible.

        :param encoding: The encoding to use for decoding event data.
         Default is 'UTF-8'
        :rtype: Dict[str, Any]
        """
        data_str = self.body_as_str(encoding=encoding)
        try:
            return json.loads(data_str)
        except Exception as e:
            raise TypeError("Event data is not compatible with JSON type: {}".format(e))

    @property
    def content_type(self):
        # type: () -> Optional[str]
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
    def content_type(self, value):
        # type: (str) -> None
        if not self._raw_amqp_message.properties:
            self._raw_amqp_message.properties = AmqpMessageProperties()
        self._raw_amqp_message.properties.content_type = value

    @property
    def correlation_id(self):
        # type: () -> Optional[str]
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
    def correlation_id(self, value):
        # type: (str) -> None
        if not self._raw_amqp_message.properties:
            self._raw_amqp_message.properties = AmqpMessageProperties()
        self._raw_amqp_message.properties.correlation_id = value

    @property
    def message_id(self):
        # type: () -> Optional[str]
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
    def message_id(self, value):
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

    def __init__(self, max_size_in_bytes=None, partition_id=None, partition_key=None):
        # type: (Optional[int], Optional[str], Optional[Union[str, bytes]]) -> None

        if partition_key and not isinstance(
            partition_key, (six.text_type, six.binary_type)
        ):
            _LOGGER.info(
                "WARNING: Setting partition_key of non-string value on the events to be sent is discouraged "
                "as the partition_key will be ignored by the Event Hub service and events will be assigned "
                "to all partitions using round-robin. Furthermore, there are SDKs for consuming events which expect "
                "partition_key to only be string type, they might fail to parse the non-string value."
            )

        self.max_size_in_bytes = max_size_in_bytes or constants.MAX_FRAME_SIZE_BYTES
        self.message = BatchMessage(data=[])
        self._partition_id = partition_id
        self._partition_key = partition_key
        self.message = set_message_partition_key(self.message, self._partition_key)
        self._size = pyutils.get_message_encoded_size(self.message)
        self._count = 0

    def __repr__(self):
        # type: () -> str
        batch_repr = "max_size_in_bytes={}, partition_id={}, partition_key={!r}, event_count={}".format(
            self.max_size_in_bytes, self._partition_id, self._partition_key, self._count
        )
        return "EventDataBatch({})".format(batch_repr)

    def __len__(self):
        return self._count

    @classmethod
    def _from_batch(cls, batch_data, partition_key=None):
        # type: (Iterable[EventData], Optional[AnyStr]) -> EventDataBatch
        outgoing_batch_data = [transform_outbound_single_message(m, EventData) for m in batch_data]
        batch_data_instance = cls(partition_key=partition_key)
        batch_data_instance.message._body_gen = (  # pylint:disable=protected-access
            outgoing_batch_data
        )
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
    def size_in_bytes(self):
        # type: () -> int
        """The combined size of the events in the batch, in bytes.

        :rtype: int
        """
        return self._size

    def add(self, event_data):
        # type: (Union[EventData, AmqpAnnotatedMessage]) -> None
        """Try to add an EventData to the batch.

        The total size of an added event is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `ValueError` will
        be raised.

        :param event_data: The EventData to add to the batch.
        :type event_data: Union[~azure.eventhub.EventData, ~azure.eventhub.amqp.AmqpAnnotatedMessage]
        :rtype: None
        :raise: :class:`ValueError`, when exceeding the size limit.
        """

        outgoing_event_data = transform_outbound_single_message(event_data, EventData)

        if self._partition_key:
            if (
                outgoing_event_data.partition_key
                and outgoing_event_data.partition_key != self._partition_key
            ):
                raise ValueError(
                    "The partition key of event_data does not match the partition key of this batch."
                )
            if not outgoing_event_data.partition_key:
                outgoing_event_data.message = set_message_partition_key(
                    outgoing_event_data.message, self._partition_key
                )

        trace_message(outgoing_event_data)
        event_data_size = pyutils.get_message_encoded_size(outgoing_event_data.message)
        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        # message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = (
            self._size
            + event_data_size
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (event_data_size < 256) else 1]
        )

        if size_after_add > self.max_size_in_bytes:
            raise ValueError(
                "EventDataBatch has reached its size limit: {}".format(
                    self.max_size_in_bytes
                )
            )

        pyutils.add_batch(self.message, outgoing_event_data.message)
        self._size = size_after_add
        self._count += 1
