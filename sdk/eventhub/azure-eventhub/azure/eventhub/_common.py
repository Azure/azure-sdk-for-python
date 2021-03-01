# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import json
import logging
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

from uamqp import BatchMessage, Message, constants, types

from ._utils import set_message_partition_key, trace_message, utc_from_timestamp
from ._constants import (
    PROP_SEQ_NUMBER,
    PROP_OFFSET,
    PROP_PARTITION_KEY,
    PROP_PARTITION_KEY_AMQP_SYMBOL,
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
    PRODUCER_SEQUENCE_NUMBER_SYMBOL,
    PRODUCER_ID_SYMBOL,
    PRODUCER_EPOCH_SYMBOL,
    MAX_SHORT,
    MAX_INT,
    MAX_LONG
)

if TYPE_CHECKING:
    import datetime

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

    def __init__(self, body=None):
        # type: (Union[str, bytes, List[AnyStr]]) -> None
        self._last_enqueued_event_properties = {}  # type: Dict[str, Any]
        self._sys_properties = None  # type: Optional[Dict[bytes, Any]]
        if body and isinstance(body, list):
            self.message = Message(body[0])
            for more in body[1:]:
                self.message._body.append(more)  # pylint: disable=protected-access
        elif body is None:
            raise ValueError("EventData cannot be None.")
        else:
            self.message = Message(body)
        self.message.annotations = {}
        self.message.application_properties = {}
        self._published_sequence_number = None
        self._pending_published_sequence_number = None

    def __repr__(self):
        # type: () -> str
        # pylint: disable=bare-except
        try:
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
    def _from_message(cls, message):
        # type: (Message) -> EventData
        """Internal use only.

        Creates an EventData object from a raw uamqp message.

        :param ~uamqp.Message message: A received uamqp message.
        :rtype: ~azure.eventhub.EventData
        """
        event_data = cls(body="")
        event_data.message = message
        return event_data

    def _encode_message(self):
        # type: () -> bytes
        return self.message.encode_message()

    @property
    def sequence_number(self):
        # type: () -> Optional[int]
        """The sequence number of the event.

        :rtype: int
        """
        return self.message.annotations.get(PROP_SEQ_NUMBER, None)

    @property
    def published_sequence_number(self):
        # type: () -> Optional[int]
        """
        The publishing sequence number assigned to the event at the time it was successfully published.
        If the producer was not configured to apply sequence numbering or if the event has not yet been successfully
        published, the value will be None.

        :rtype: int
        """
        return self._published_sequence_number

    @property
    def offset(self):
        # type: () -> Optional[str]
        """The offset of the event.

        :rtype: str
        """
        try:
            return self.message.annotations[PROP_OFFSET].decode("UTF-8")
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self):
        # type: () -> Optional[datetime.datetime]
        """The enqueued timestamp of the event.

        :rtype: datetime.datetime
        """
        timestamp = self.message.annotations.get(PROP_TIMESTAMP, None)
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
            return self.message.annotations[PROP_PARTITION_KEY_AMQP_SYMBOL]
        except KeyError:
            return self.message.annotations.get(PROP_PARTITION_KEY, None)

    @property
    def properties(self):
        # type: () -> Dict[Union[str, bytes], Any]
        """Application-defined properties on the event.

        :rtype: dict
        """
        return self.message.application_properties

    @properties.setter
    def properties(self, value):
        # type: (Dict[Union[str, bytes], Any]) -> None
        """Application-defined properties on the event.

        :param dict value: The application properties for the EventData.
        """
        properties = None if value is None else dict(value)
        self.message.application_properties = properties

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
            if self.message.properties:
                for key, prop_name in _SYS_PROP_KEYS_TO_MSG_PROPERTIES:
                    value = getattr(self.message.properties, prop_name, None)
                    if value:
                        self._sys_properties[key] = value
            self._sys_properties.update(self.message.annotations)
        return self._sys_properties

    @property
    def body(self):
        # type: () -> Union[bytes, Iterable[bytes]]
        """The content of the event.

        :rtype: bytes or Generator[bytes]
        """
        try:
            return self.message.get_data()
        except TypeError:
            raise ValueError("Event content empty.")

    def body_as_str(self, encoding="UTF-8"):
        # type: (str) -> str
        """The content of the event as a string, if the data is of a compatible type.

        :param encoding: The encoding to use for decoding event data.
         Default is 'UTF-8'
        :rtype: str
        """
        data = self.body
        try:
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
        :rtype: dict
        """
        data_str = self.body_as_str(encoding=encoding)
        try:
            return json.loads(data_str)
        except Exception as e:
            raise TypeError("Event data is not compatible with JSON type: {}".format(e))


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

    def __init__(self, max_size_in_bytes=None, partition_id=None, partition_key=None, **kwargs):
        # type: (Optional[int], Optional[str], Optional[Union[str, bytes]], Any) -> None
        self.max_size_in_bytes = max_size_in_bytes or constants.MAX_MESSAGE_LENGTH_BYTES
        self.message = BatchMessage(data=[], multi_messages=False, properties=None)
        self._partition_id = partition_id
        self._partition_key = partition_key
        self._is_idempotent_batch = kwargs.pop("is_idempotent_batch", False)

        set_message_partition_key(self.message, self._partition_key)
        self._size = self.message.gather()[0].get_message_encoded_size()
        self._count = 0
        self._starting_published_sequence_number = None

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
        batch_data_instance = cls(partition_key=partition_key)
        batch_data_instance.message._body_gen = (  # pylint:disable=protected-access
            batch_data
        )
        return batch_data_instance

    def _load_events(self, events):
        for event_data in events:
            try:
                self.add(event_data)
            except ValueError:
                raise ValueError("The combined size of EventData collection exceeds the Event Hub frame size limit. "
                                 "Please send a smaller collection of EventData, or use EventDataBatch, "
                                 "which is guaranteed to be under the frame size limit")

    @property
    def size_in_bytes(self):
        # type: () -> int
        """The combined size of the events in the batch, in bytes.

        :rtype: int
        """
        return self._size

    @property
    def starting_published_sequence_number(self):
        # type() -> Optional[int]
        """
        The publishing sequence number assigned to the first event in the batch at the time
        the batch was successfully published. If the producer was not configured to apply
        sequence numbering or if the batch has not yet been successfully published, the value
        will be None.

        :rtype: int
        """
        return self._starting_published_sequence_number

    def add(self, event_data):
        # type: (EventData) -> None
        """Try to add an EventData to the batch.

        The total size of an added event is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `ValueError` will
        be raised.

        :param event_data: The EventData to add to the batch.
        :type event_data: ~azure.eventhub.EventData
        :rtype: None
        :raise: :class:`ValueError`, when exceeding the size limit.
        """
        if self._partition_key:
            if (
                event_data.partition_key
                and event_data.partition_key != self._partition_key
            ):
                raise ValueError(
                    "The partition key of event_data does not match the partition key of this batch."
                )
            if not event_data.partition_key:
                set_message_partition_key(event_data.message, self._partition_key)

        if self._is_idempotent_batch and event_data.published_sequence_number is not None:
            raise ValueError("EventData object that has already been published by "
                             "idempotent producer cannot be published again.")

        trace_message(event_data)
        if self._is_idempotent_batch:
            # Reserve space for producer-owned fields that correspond to the idempotent publishing, if enabled.
            event_data.message.annotations[PRODUCER_EPOCH_SYMBOL] = types.AMQPShort(int(MAX_SHORT))
            event_data.message.annotations[PRODUCER_ID_SYMBOL] = types.AMQPLong(int(MAX_LONG))
            event_data.message.annotations[PRODUCER_SEQUENCE_NUMBER_SYMBOL] = types.AMQPInt(int(MAX_INT))

        event_data_size = event_data.message.get_message_encoded_size()

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

        self.message._body_gen.append(event_data)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1


class DictMixin(object):
    def __setitem__(self, key, item):
        # type: (Any, Any) -> None
        self.__dict__[key] = item

    def __getitem__(self, key):
        # type: (Any) -> Any
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        # type: () -> str
        return str(self)

    def __len__(self):
        # type: () -> int
        return len(self.keys())

    def __delitem__(self, key):
        # type: (Any) -> None
        self.__dict__[key] = None

    def __eq__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        # type: (Any) -> bool
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        # type: () -> str
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k):
        # type: (Any) -> bool
        return k in self.__dict__

    def update(self, *args, **kwargs):
        # type: (Any, Any) -> None
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        # type: () -> list
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        # type: () -> list
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        # type: () -> list
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        # type: (Any, Optional[Any]) -> Any
        if key in self.__dict__:
            return self.__dict__[key]
        return default
