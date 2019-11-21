# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import datetime
import calendar
import json
import logging
import six

from uamqp import BatchMessage, Message, constants  # type: ignore

from ._utils import set_message_partition_key, trace_message, utc_from_timestamp
from ._constants import (
    PROP_SEQ_NUMBER,
    PROP_OFFSET,
    PROP_PARTITION_KEY,
    PROP_PARTITION_KEY_AMQP_SYMBOL,
    PROP_TIMESTAMP,
    PROP_LAST_ENQUEUED_SEQUENCE_NUMBER,
    PROP_LAST_ENQUEUED_OFFSET,
    PROP_LAST_ENQUEUED_TIME_UTC,
    PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC,
)

_LOGGER = logging.getLogger(__name__)

# event_data.encoded_size < 255, batch encode overhead is 5, >=256, overhead is 8 each
_BATCH_MESSAGE_OVERHEAD_COST = [5, 8]


class EventData(object):
    """
    The EventData class is a holder of event content.

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
        self._last_enqueued_event_properties = {}
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

    def __str__(self):
        try:
            body = self.body_as_str()
        except:  # pylint: disable=bare-except
            body = "<read-error>"
        message_as_dict = {
            'body': body,
            'application_properties': str(self.properties)
        }
        try:
            if self.sequence_number:
                message_as_dict['sequence_number'] = str(self.sequence_number)
            if self.offset:
                message_as_dict['offset'] = str(self.offset)
            if self.enqueued_time:
                message_as_dict['enqueued_time'] = str(self.enqueued_time)
            if self.partition_key:
                message_as_dict['partition_key'] = str(self.partition_key)
        except:  # pylint: disable=bare-except
            pass
        return str(message_as_dict)

    @classmethod
    def _from_message(cls, message):
        """Internal use only.

        Creates an EventData object from a raw uamqp message.

        :param ~uamqp.Message message: A received uamqp message.
        :rtype: ~azure.eventhub.EventData
        """
        event_data = cls(body='')
        event_data.message = message
        return event_data

    def _get_last_enqueued_event_properties(self):
        """Extracts the last enqueued event in from the received event delivery annotations.

        :rtype: Dict[str, Any]
        """
        if self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties

        if self.message.delivery_annotations:
            sequence_number = self.message.delivery_annotations.get(PROP_LAST_ENQUEUED_SEQUENCE_NUMBER, None)
            enqueued_time_stamp = self.message.delivery_annotations.get(PROP_LAST_ENQUEUED_TIME_UTC, None)
            if enqueued_time_stamp:
                enqueued_time_stamp = utc_from_timestamp(float(enqueued_time_stamp)/1000)
            retrieval_time_stamp = self.message.delivery_annotations.get(PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC, None)
            if retrieval_time_stamp:
                retrieval_time_stamp = utc_from_timestamp(float(retrieval_time_stamp)/1000)
            offset_bytes = self.message.delivery_annotations.get(PROP_LAST_ENQUEUED_OFFSET, None)
            offset = offset_bytes.decode('UTF-8') if offset_bytes else None
            self._last_enqueued_event_properties = {
                "sequence_number": sequence_number,
                "offset": offset,
                "enqueued_time": enqueued_time_stamp,
                "retrieval_time": retrieval_time_stamp
            }
            return self._last_enqueued_event_properties

        return None

    @property
    def sequence_number(self):
        """
        The sequence number of the event data object.

        :rtype: int or long
        """
        return self.message.annotations.get(PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        """
        The offset of the event data object.

        :rtype: str
        """
        try:
            return self.message.annotations[PROP_OFFSET].decode('UTF-8')
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self):
        """
        The enqueued timestamp of the event data object.

        :rtype: datetime.datetime
        """
        timestamp = self.message.annotations.get(PROP_TIMESTAMP, None)
        if timestamp:
            return utc_from_timestamp(float(timestamp)/1000)
        return None

    @property
    def partition_key(self):
        """
        The partition key of the event data object.

        :rtype: bytes
        """
        try:
            return self.message.annotations[PROP_PARTITION_KEY_AMQP_SYMBOL]
        except KeyError:
            return self.message.annotations.get(PROP_PARTITION_KEY, None)

    @property
    def properties(self):
        """
        Application defined properties on the message.

        :rtype: dict
        """
        return self.message.application_properties

    @properties.setter
    def properties(self, value):
        """
        Application defined properties on the message.

        :param dict value: The application properties for the EventData.
        """
        properties = None if value is None else dict(value)
        self.message.application_properties = properties

    @property
    def system_properties(self):
        """
        Metadata set by the Event Hubs Service associated with the EventData

        :rtype: dict
        """
        return self.message.annotations

    @property
    def body(self):
        """
        The body of the event data object.

        :rtype: bytes or Generator[bytes]
        """
        try:
            return self.message.get_data()
        except TypeError:
            raise ValueError("Message data empty.")

    @property
    def last_enqueued_event_properties(self):
        """
        The latest enqueued event information. This property will be updated each time an event is received when
        the receiver is created with `track_last_enqueued_event_properties` being `True`.
        The dict includes following information of the partition:

            - `sequence_number`
            - `offset`
            - `enqueued_time`
            - `retrieval_time`

        :rtype: dict or None
        """
        return self._get_last_enqueued_event_properties()

    def body_as_str(self, encoding='UTF-8'):
        """
        The body of the event data as a string if the data is of a
        compatible type.

        :param encoding: The encoding to use for decoding message data.
         Default is 'UTF-8'
        :rtype: str
        """
        data = self.body
        try:
            return "".join(b.decode(encoding) for b in data)
        except TypeError:
            return six.text_type(data)
        except:  # pylint: disable=bare-except
            pass
        try:
            return data.decode(encoding)
        except Exception as e:
            raise TypeError("Message data is not compatible with string type: {}".format(e))

    def body_as_json(self, encoding='UTF-8'):
        """
        The body of the event loaded as a JSON object is the data is compatible.

        :param encoding: The encoding to use for decoding message data.
         Default is 'UTF-8'
        :rtype: dict
        """
        data_str = self.body_as_str(encoding=encoding)
        try:
            return json.loads(data_str)
        except Exception as e:
            raise TypeError("Event data is not compatible with JSON type: {}".format(e))

    def encode_message(self):
        return self.message.encode_message()


class EventDataBatch(object):
    """
    Sending events in batch get better performance than sending individual events.
    EventDataBatch helps you create the maximum allowed size batch of `EventData` to improve sending performance.

    Use `try_add` method to add events until the maximum batch size limit in bytes has been reached -
    a `ValueError` will be raised.
    Use `send` method of :class:`EventHubProducerClient<azure.eventhub.EventHubProducerClient>`
    or the async :class:`EventHubProducerClient<azure.eventhub.aio.EventHubProducerClient>`
    for sending. The `send` method accepts partition_key as a parameter for sending a particular partition.

    **Please use the create_batch method of EventHubProducerClient
    to create an EventDataBatch object instead of instantiating an EventDataBatch object directly.**

    :param int max_size: The maximum size of bytes data that an EventDataBatch object can hold.
    :param str partition_key: With the given partition_key, event data will land to a particular partition of the
     Event Hub decided by the service.
    """

    def __init__(self, max_size=None, partition_key=None):
        self.max_size = max_size or constants.MAX_MESSAGE_LENGTH_BYTES
        self._partition_key = partition_key
        self.message = BatchMessage(data=[], multi_messages=False, properties=None)

        set_message_partition_key(self.message, self._partition_key)
        self._size = self.message.gather()[0].get_message_encoded_size()
        self._count = 0

    def __len__(self):
        return self._count

    @staticmethod
    def _from_batch(batch_data, partition_key=None):
        batch_data_instance = EventDataBatch(partition_key=partition_key)
        batch_data_instance.message._body_gen = batch_data  # pylint:disable=protected-access
        return batch_data_instance

    @property
    def size(self):
        """The size of EventDataBatch object in bytes

        :rtype: int
        """
        return self._size

    def try_add(self, event_data):
        """
        Try to add an EventData object, the size of EventData is a sum up of body, application_properties, etc.

        :param event_data: The EventData object which is attempted to be added.
        :type event_data: ~azure.eventhub.EventData
        :rtype: None
        :raise: :class:`ValueError`, when exceeding the size limit.
        """
        if self._partition_key:
            if event_data.partition_key and event_data.partition_key != self._partition_key:
                raise ValueError('The partition key of event_data does not match the partition key of this batch.')
            if not event_data.partition_key:
                set_message_partition_key(event_data.message, self._partition_key)

        trace_message(event_data)
        event_data_size = event_data.message.get_message_encoded_size()

        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        # message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = self._size + event_data_size \
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (event_data_size < 256) else 1]

        if size_after_add > self.max_size:
            raise ValueError("EventDataBatch has reached its size limit: {}".format(self.max_size))

        self.message._body_gen.append(event_data)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1


class EventPosition(object):
    """
    The position(offset, sequence or timestamp) where a consumer starts.

    :param value: The event position value. The value can be type of datetime.datetime or int or str.
    :type value: int, str or datetime.datetime
    :param bool inclusive: Whether to include the supplied value as the start point.

    Examples:

    Beginning of the event stream:
      >>> event_pos = EventPosition("-1")
    End of the event stream:
      >>> event_pos = EventPosition("@latest")
    Events after the specified offset:
      >>> event_pos = EventPosition("12345")
    Events from the specified offset:
      >>> event_pos = EventPosition("12345", True)
    Events after a datetime:
      >>> event_pos = EventPosition(datetime.datetime.utcnow())
    Events after a specific sequence number:
      >>> event_pos = EventPosition(1506968696002)
    """

    def __init__(self, value, inclusive=False):
        self.value = value if value is not None else "-1"
        self.inclusive = inclusive

    def __str__(self):
        return str(self.value)

    def _selector(self):
        """
        Creates a selector expression of the offset.

        :rtype: bytes
        """
        operator = ">=" if self.inclusive else ">"
        if isinstance(self.value, datetime.datetime):  # pylint:disable=no-else-return
            timestamp = (calendar.timegm(self.value.utctimetuple()) * 1000) + (self.value.microsecond/1000)
            return ("amqp.annotation.x-opt-enqueued-time {} '{}'".format(operator, int(timestamp))).encode('utf-8')
        elif isinstance(self.value, six.integer_types):
            return ("amqp.annotation.x-opt-sequence-number {} '{}'".format(operator, self.value)).encode('utf-8')
        return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, self.value)).encode('utf-8')
