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

from uamqp import BatchMessage, Message, types, constants  # type: ignore
from uamqp.message import MessageHeader  # type: ignore

from azure.core.settings import settings # type: ignore

from azure.eventhub.error import EventDataError

log = logging.getLogger(__name__)

# event_data.encoded_size < 255, batch encode overhead is 5, >=256, overhead is 8 each
_BATCH_MESSAGE_OVERHEAD_COST = [5, 8]


def parse_sas_token(sas_token):
    """Parse a SAS token into its components.

    :param sas_token: The SAS token.
    :type sas_token: str
    :rtype: dict[str, str]
    """
    sas_data = {}
    token = sas_token.partition(' ')[2]
    fields = token.split('&')
    for field in fields:
        key, value = field.split('=', 1)
        sas_data[key.lower()] = value
    return sas_data


class EventData(object):
    """
    The EventData class is a holder of event content.

    Example:
        .. literalinclude:: ../examples/test_examples_eventhub.py
            :start-after: [START create_event_data]
            :end-before: [END create_event_data]
            :language: python
            :dedent: 4
            :caption: Create instances of EventData

    """

    PROP_SEQ_NUMBER = b"x-opt-sequence-number"
    PROP_OFFSET = b"x-opt-offset"
    PROP_PARTITION_KEY = b"x-opt-partition-key"
    PROP_PARTITION_KEY_AMQP_SYMBOL = types.AMQPSymbol(PROP_PARTITION_KEY)
    PROP_TIMESTAMP = b"x-opt-enqueued-time"
    PROP_LAST_ENQUEUED_SEQUENCE_NUMBER = b"last_enqueued_sequence_number"
    PROP_LAST_ENQUEUED_OFFSET = b"last_enqueued_offset"
    PROP_LAST_ENQUEUED_TIME_UTC = b"last_enqueued_time_utc"
    PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC = b"runtime_info_retrieval_time_utc"

    def __init__(self, body=None):
        """
        Initialize EventData.

        :param body: The data to send in a single message.
        :type body: str, bytes or list
        """

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

    def __str__(self):
        dic = {
            'body': self.body_as_str(),
            'application_properties': str(self.application_properties)
        }

        if self.sequence_number:
            dic['sequence_number'] = str(self.sequence_number)
        if self.offset:
            dic['offset'] = str(self.offset)
        if self.enqueued_time:
            dic['enqueued_time'] = str(self.enqueued_time)
        if self.partition_key:
            dic['partition_key'] = str(self.partition_key)
        return str(dic)

    def _set_partition_key(self, value):
        """
        Set the partition key of the event data object.

        :param value: The partition key to set.
        :type value: str or bytes
        """
        annotations = dict(self.message.annotations)
        annotations[EventData.PROP_PARTITION_KEY_AMQP_SYMBOL] = value
        header = MessageHeader()
        header.durable = True
        self.message.annotations = annotations
        self.message.header = header

    def _trace_message(self, parent_span=None):
        """Add tracing information to this message.

        Will open and close a "Azure.EventHubs.message" span, and
        add the "DiagnosticId" as app properties of the message.
        """
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is not None:
            current_span = parent_span or span_impl_type(span_impl_type.get_current_span())
            message_span = current_span.span(name="Azure.EventHubs.message")
            message_span.start()
            app_prop = dict(self.application_properties) if self.application_properties else dict()
            app_prop.setdefault(b"Diagnostic-Id", message_span.get_trace_parent().encode('ascii'))
            self.application_properties = app_prop
            message_span.finish()

    def _trace_link_message(self, parent_span=None):
        """Link the current message to current span.

        Will extract DiagnosticId if available.
        """
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is not None:
            current_span = parent_span or span_impl_type(span_impl_type.get_current_span())
            if current_span and self.application_properties:
                traceparent = self.application_properties.get(b"Diagnostic-Id", "").decode('ascii')
                if traceparent:
                    current_span.link(traceparent)

    def _get_last_enqueued_event_properties(self):
        if self._last_enqueued_event_properties:
            return self._last_enqueued_event_properties

        if self.message.delivery_annotations:
            enqueued_time_stamp = \
                self.message.delivery_annotations.get(EventData.PROP_LAST_ENQUEUED_TIME_UTC, None)
            retrieval_time_stamp = \
                self.message.delivery_annotations.get(EventData.PROP_RUNTIME_INFO_RETRIEVAL_TIME_UTC, None)

            self._last_enqueued_event_properties = {
                "sequence_number":
                    self.message.delivery_annotations.get(EventData.PROP_LAST_ENQUEUED_SEQUENCE_NUMBER, None),
                "offset":
                    self.message.delivery_annotations.get(EventData.PROP_LAST_ENQUEUED_OFFSET, None),
                "enqueued_time":
                    datetime.datetime.utcfromtimestamp(
                        float(enqueued_time_stamp)/1000) if enqueued_time_stamp else None,
                "retrieval_time":
                    datetime.datetime.utcfromtimestamp(
                        float(retrieval_time_stamp)/1000) if retrieval_time_stamp else None
            }
            return self._last_enqueued_event_properties

        return None

    @classmethod
    def _from_message(cls, message):
        # pylint:disable=protected-access
        event_data = cls(body='')
        event_data.message = message
        return event_data

    @property
    def sequence_number(self):
        """
        The sequence number of the event data object.

        :rtype: int or long
        """
        return self.message.annotations.get(EventData.PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        """
        The offset of the event data object.

        :rtype: str
        """
        try:
            return self.message.annotations[EventData.PROP_OFFSET].decode('UTF-8')
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self):
        """
        The enqueued timestamp of the event data object.

        :rtype: datetime.datetime
        """
        timestamp = self.message.annotations.get(EventData.PROP_TIMESTAMP, None)
        if timestamp:
            return datetime.datetime.utcfromtimestamp(float(timestamp)/1000)
        return None

    @property
    def partition_key(self):
        """
        The partition key of the event data object.

        :rtype: bytes
        """
        try:
            return self.message.annotations[EventData.PROP_PARTITION_KEY_AMQP_SYMBOL]
        except KeyError:
            return self.message.annotations.get(EventData.PROP_PARTITION_KEY, None)

    @property
    def application_properties(self):
        """
        Application defined properties on the message.

        :rtype: dict
        """
        return self.message.application_properties

    @application_properties.setter
    def application_properties(self, value):
        """
        Application defined properties on the message.

        :param value: The application properties for the EventData.
        :type value: dict
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

    def body_as_str(self, encoding='UTF-8'):
        """
        The body of the event data as a string if the data is of a
        compatible type.

        :param encoding: The encoding to use for decoding message data.
         Default is 'UTF-8'
        :rtype: str or unicode
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
    Use `send` method of ~azure.eventhub.EventHubProducer or ~azure.eventhub.aio.EventHubProducer for sending.

    Please use the `create_batch` method of `EventHubProducer`
    to create an `EventDataBatch` object instead of instantiating an `EventDataBatch` object directly.
    """

    def __init__(self, max_size=None, partition_key=None):
        self.max_size = max_size or constants.MAX_MESSAGE_LENGTH_BYTES
        self._partition_key = partition_key
        self.message = BatchMessage(data=[], multi_messages=False, properties=None)

        self._set_partition_key(partition_key)
        self._size = self.message.gather()[0].get_message_encoded_size()
        self._count = 0

    def __len__(self):
        return self._count

    @property
    def size(self):
        """The size in bytes

        :return: int
        """
        return self._size

    @staticmethod
    def _from_batch(batch_data, partition_key=None):
        batch_data_instance = EventDataBatch(partition_key=partition_key)
        batch_data_instance.message._body_gen = batch_data  # pylint:disable=protected-access
        return batch_data_instance

    def _set_partition_key(self, value):
        if value:
            annotations = self.message.annotations
            if annotations is None:
                annotations = dict()
            annotations[types.AMQPSymbol(EventData.PROP_PARTITION_KEY)] = value
            header = MessageHeader()
            header.durable = True
            self.message.annotations = annotations
            self.message.header = header

    def try_add(self, event_data):
        """
        The message size is a sum up of body, properties, header, etc.
        :param event_data: ~azure.eventhub.EventData
        :return: None
        :raise: ValueError, when exceeding the size limit.
        """
        if event_data is None:
            log.warning("event_data is None when calling EventDataBatch.try_add. Ignored")
            return
        if not isinstance(event_data, EventData):
            raise TypeError('event_data should be type of EventData')

        if self._partition_key:
            if event_data.partition_key and event_data.partition_key != self._partition_key:
                raise EventDataError('The partition_key of event_data does not match the one of the EventDataBatch')
            if not event_data.partition_key:
                event_data._set_partition_key(self._partition_key)  # pylint:disable=protected-access

        event_data._trace_message()  # pylint:disable=protected-access

        event_data_size = event_data.message.get_message_encoded_size()

        # For a BatchMessage, if the encoded_message_size of event_data is < 256, then the overhead cost to encode that
        #  message into the BatchMessage would be 5 bytes, if >= 256, it would be 8 bytes.
        size_after_add = self._size + event_data_size\
            + _BATCH_MESSAGE_OVERHEAD_COST[0 if (event_data_size < 256) else 1]

        if size_after_add > self.max_size:
            raise ValueError("EventDataBatch has reached its size limit {}".format(self.max_size))

        self.message._body_gen.append(event_data)  # pylint: disable=protected-access
        self._size = size_after_add
        self._count += 1


class EventPosition(object):
    """
    The position(offset, sequence or timestamp) where a consumer starts. Examples:

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
        """
        Initialize EventPosition.

        :param value: The event position value.
        :type value: ~datetime.datetime or int or str
        :param inclusive: Whether to include the supplied value as the start point.
        :type inclusive: bool
        """
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


# TODO: move some behaviors to these two classes.
class EventHubSASTokenCredential(object):
    """
    SAS token used for authentication.
    """
    def __init__(self, token):
        """
        :param token: A SAS token or function that returns a SAS token. If a function is supplied,
         it will be used to retrieve subsequent tokens in the case of token expiry. The function should
         take no arguments.
        :type token: str or callable
        """
        self.token = token

    def get_sas_token(self):
        if callable(self.token):  # pylint:disable=no-else-return
            return self.token()
        else:
            return self.token


class EventHubSharedKeyCredential(object):
    """
    The shared access key credential used for authentication.
    """
    def __init__(self, policy, key):
        """
        :param policy: The name of the shared access policy.
        :type policy: str
        :param key: The shared access key.
        :type key: str
        """

        self.policy = policy
        self.key = key


class _Address(object):
    def __init__(self, hostname=None, path=None):
        self.hostname = hostname
        self.path = path
