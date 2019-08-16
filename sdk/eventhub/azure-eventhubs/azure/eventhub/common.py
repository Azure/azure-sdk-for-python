# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import datetime
import calendar
import json
import six
import logging

from azure.eventhub.error import EventDataError
from uamqp import BatchMessage, Message, types, constants
from uamqp.message import MessageHeader, MessageProperties

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
    Acts as a wrapper to an uamqp.message.Message object.

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
    PROP_TIMESTAMP = b"x-opt-enqueued-time"
    PROP_DEVICE_ID = b"iothub-connection-device-id"

    def __init__(self, body=None, to_device=None):
        """
        Initialize EventData.

        :param body: The data to send in a single message.
        :type body: str, bytes or list
        :param to_device: An IoT device to route to.
        :type to_device: str
        """

        self._partition_key = types.AMQPSymbol(EventData.PROP_PARTITION_KEY)
        self._annotations = {}
        self._app_properties = {}
        self.msg_properties = MessageProperties()
        if to_device:
            self.msg_properties.to = '/devices/{}/messages/devicebound'.format(to_device)
        if body and isinstance(body, list):
            self.message = Message(body[0], properties=self.msg_properties)
            for more in body[1:]:
                self.message._body.append(more)  # pylint: disable=protected-access
        elif body is None:
            raise ValueError("EventData cannot be None.")
        else:
            self.message = Message(body, properties=self.msg_properties)

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
        if self.device_id:
            dic['device_id'] = str(self.device_id)
        if self.partition_key:
            dic['partition_key'] = str(self.partition_key)
        return str(dic)

    def _set_partition_key(self, value):
        """
        Set the partition key of the event data object.

        :param value: The partition key to set.
        :type value: str or bytes
        """
        annotations = dict(self._annotations)
        annotations[self._partition_key] = value
        header = MessageHeader()
        header.durable = True
        self.message.annotations = annotations
        self.message.header = header
        self._annotations = annotations

    @staticmethod
    def _from_message(message):
        event_data = EventData(body='')
        event_data.message = message
        event_data.msg_properties = message.properties
        event_data._annotations = message.annotations
        event_data._app_properties = message.application_properties
        return event_data

    @property
    def sequence_number(self):
        """
        The sequence number of the event data object.

        :rtype: int or long
        """
        return self._annotations.get(EventData.PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        """
        The offset of the event data object.

        :rtype: str
        """
        try:
            return self._annotations[EventData.PROP_OFFSET].decode('UTF-8')
        except (KeyError, AttributeError):
            return None

    @property
    def enqueued_time(self):
        """
        The enqueued timestamp of the event data object.

        :rtype: datetime.datetime
        """
        timestamp = self._annotations.get(EventData.PROP_TIMESTAMP, None)
        if timestamp:
            return datetime.datetime.utcfromtimestamp(float(timestamp)/1000)
        return None

    @property
    def device_id(self):
        """
        The device ID of the event data object. This is only used for
        IoT Hub implementations.

        :rtype: bytes
        """
        return self._annotations.get(EventData.PROP_DEVICE_ID, None)

    @property
    def partition_key(self):
        """
        The partition key of the event data object.

        :rtype: bytes
        """
        try:
            return self._annotations[self._partition_key]
        except KeyError:
            return self._annotations.get(EventData.PROP_PARTITION_KEY, None)

    @property
    def application_properties(self):
        """
        Application defined properties on the message.

        :rtype: dict
        """
        return self._app_properties

    @application_properties.setter
    def application_properties(self, value):
        """
        Application defined properties on the message.

        :param value: The application properties for the EventData.
        :type value: dict
        """
        self._app_properties = value
        properties = None if value is None else dict(self._app_properties)
        self.message.application_properties = properties

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
    The EventDataBatch class is a holder of a batch of event data within max size bytes.
    Use ~azure.eventhub.Producer.create_batch method to create an EventDataBatch object.
    Do not instantiate an EventDataBatch object directly.
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
        batch_data_instance.message._body_gen = batch_data
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
        :param event_data:
        :return:
        """
        if event_data is None:
            log.warning("event_data is None when calling EventDataBatch.try_add. Ignored")
            return
        if not isinstance(event_data, EventData):
            raise TypeError('event_data should be type of EventData')

        if self._partition_key:
            if event_data.partition_key and not (event_data.partition_key == self._partition_key):
                raise EventDataError('The partition_key of event_data does not match the one of the EventDataBatch')
            if not event_data.partition_key:
                event_data._set_partition_key(self._partition_key)

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
        if isinstance(self.value, datetime.datetime):
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
        if callable(self.token):
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
