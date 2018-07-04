# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
import time

from uamqp import Message, BatchMessage
from uamqp import types
from uamqp.message import MessageHeader, MessageProperties


class EventData(object):
    """
    The EventData class is a holder of event content.
    Acts as a wrapper to an ~uamqp.message.Message object.
    """

    PROP_SEQ_NUMBER = b"x-opt-sequence-number"
    PROP_OFFSET = b"x-opt-offset"
    PROP_PARTITION_KEY = b"x-opt-partition-key"
    PROP_TIMESTAMP = b"x-opt-enqueued-time"
    PROP_DEVICE_ID = b"iothub-connection-device-id"

    def __init__(self, body=None, batch=None, to_device=None, message=None):
        """
        Initialize EventData.

        :param body: The data to send in a single message.
        :type body: str, bytes or list
        :param batch: A data generator to send batched messages.
        :type batch: Generator
        :param message: The received message.
        :type message: ~uamqp.message.Message
        """
        self._partition_key = types.AMQPSymbol(EventData.PROP_PARTITION_KEY)
        self._annotations = {}
        self._properties = {}
        self._msg_properties = MessageProperties()
        if to_device:
            self._msg_properties.to = '/devices/{}/messages/devicebound'.format(to_device)
        if batch:
            self.message = BatchMessage(data=batch, multi_messages=True, properties=self._msg_properties)
        elif message:
            self.message = message
            self._annotations = message.annotations
            self._properties = message.application_properties
        else:
            if isinstance(body, list) and body:
                self.message = Message(body[0], properties=self._msg_properties)
                for more in body[1:]:
                    self.message._body.append(more)  # pylint: disable=protected-access
            elif body is None:
                raise ValueError("EventData cannot be None.")
            else:
                self.message = Message(body, properties=self._msg_properties)


    @property
    def sequence_number(self):
        """
        The sequence number of the event data object.

        :rtype: int
        """
        return self._annotations.get(EventData.PROP_SEQ_NUMBER, None)

    @property
    def offset(self):
        """
        The offset of the event data object.

        :rtype: int
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
            return datetime.datetime.fromtimestamp(float(timestamp)/1000)
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

    @partition_key.setter
    def partition_key(self, value):
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

    @property
    def properties(self):
        """
        Application defined properties on the message.

        :rtype: dict
        """
        return self._properties

    @properties.setter
    def properties(self, value):
        """
        Application defined properties on the message.

        :param value: The application properties for the EventData.
        :type value: dict
        """
        self._properties = value
        properties = dict(self._properties)
        self.message.application_properties = properties

    @property
    def body(self):
        """
        The body of the event data object.

        :rtype: bytes or generator[bytes]
        """
        return self.message.get_data()


class Offset(object):
    """
    The offset (position or timestamp) where a receiver starts. Examples:
    Beginning of the event stream:
      >>> offset = Offset("-1")
    End of the event stream:
      >>> offset = Offset("@latest")
    Events after the specified offset:
      >>> offset = Offset("12345")
    Events from the specified offset:
      >>> offset = Offset("12345", True)
    Events after a datetime:
      >>> offset = Offset(datetime.datetime.utcnow())
    Events after a specific sequence number:
      >>> offset = Offset(1506968696002)
    """

    def __init__(self, value, inclusive=False):
        """
        Initialize Offset.

        :param value: The offset value.
        :type value: ~datetime.datetime or int or str
        :param inclusive: Whether to include the supplied value as the start point.
        :type inclusive: bool
        """
        self.value = value
        self.inclusive = inclusive

    def selector(self):
        """
        Creates a selector expression of the offset.

        :rtype: bytes
        """
        operator = ">=" if self.inclusive else ">"
        if isinstance(self.value, datetime.datetime):
            timestamp = (time.mktime(self.value.timetuple()) * 1000) + (self.value.microsecond/1000)
            return ("amqp.annotation.x-opt-enqueued-time {} '{}'".format(operator, int(timestamp))).encode('utf-8')
        elif isinstance(self.value, int):
            return ("amqp.annotation.x-opt-sequence-number {} '{}'".format(operator, self.value)).encode('utf-8')
        return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, self.value)).encode('utf-8')


class EventHubError(Exception):
    """
    Represents an error happened in the client.
    """
    pass
