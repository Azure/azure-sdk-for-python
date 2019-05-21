# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import datetime
import calendar
import json

import six

from uamqp import Message, BatchMessage
from uamqp import types, constants, errors
from uamqp.message import MessageHeader, MessageProperties

_NO_RETRY_ERRORS = (
    b"com.microsoft:argument-out-of-range",
    b"com.microsoft:entity-disabled",
    b"com.microsoft:auth-failed",
    b"com.microsoft:precondition-failed",
    b"com.microsoft:argument-error"
)

def _error_handler(error):
    """
    Called internally when an event has failed to send so we
    can parse the error to determine whether we should attempt
    to retry sending the event again.
    Returns the action to take according to error type.

    :param error: The error received in the send attempt.
    :type error: Exception
    :rtype: ~uamqp.errors.ErrorAction
    """
    if error.condition == b'com.microsoft:server-busy':
        return errors.ErrorAction(retry=True, backoff=4)
    if error.condition == b'com.microsoft:timeout':
        return errors.ErrorAction(retry=True, backoff=2)
    if error.condition == b'com.microsoft:operation-cancelled':
        return errors.ErrorAction(retry=True)
    if error.condition == b"com.microsoft:container-close":
        return errors.ErrorAction(retry=True, backoff=4)
    if error.condition in _NO_RETRY_ERRORS:
        return errors.ErrorAction(retry=False)
    return errors.ErrorAction(retry=True)


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

    def __init__(self, body=None, batch=None, to_device=None, message=None):
        """
        Initialize EventData.

        :param body: The data to send in a single message.
        :type body: str, bytes or list
        :param batch: A data generator to send batched messages.
        :type batch: Generator
        :param to_device: An IoT device to route to.
        :type to_device: str
        :param message: The received message.
        :type message: ~uamqp.message.Message
        """
        self._partition_key = types.AMQPSymbol(EventData.PROP_PARTITION_KEY)
        self._annotations = {}
        self._app_properties = {}
        self.msg_properties = MessageProperties()
        if to_device:
            self.msg_properties.to = '/devices/{}/messages/devicebound'.format(to_device)
        if batch:
            self.message = BatchMessage(data=batch, multi_messages=True, properties=self.msg_properties)
        elif message:
            self.message = message
            self.msg_properties = message.properties
            self._annotations = message.annotations
            self._app_properties = message.application_properties
        else:
            if isinstance(body, list) and body:
                self.message = Message(body[0], properties=self.msg_properties)
                for more in body[1:]:
                    self.message._body.append(more)  # pylint: disable=protected-access
            elif body is None:
                raise ValueError("EventData cannot be None.")
            else:
                self.message = Message(body, properties=self.msg_properties)

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

        :rtype: ~azure.eventhub.common.Offset
        """
        try:
            return Offset(self._annotations[EventData.PROP_OFFSET].decode('UTF-8'))
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
        properties = dict(self._app_properties)
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
            timestamp = (calendar.timegm(self.value.utctimetuple()) * 1000) + (self.value.microsecond/1000)
            return ("amqp.annotation.x-opt-enqueued-time {} '{}'".format(operator, int(timestamp))).encode('utf-8')
        if isinstance(self.value, six.integer_types):
            return ("amqp.annotation.x-opt-sequence-number {} '{}'".format(operator, self.value)).encode('utf-8')
        return ("amqp.annotation.x-opt-offset {} '{}'".format(operator, self.value)).encode('utf-8')


class EventHubError(Exception):
    """
    Represents an error happened in the client.

    :ivar message: The error message.
    :vartype message: str
    :ivar error: The error condition, if available.
    :vartype error: str
    :ivar details: The error details, if included in the
     service response.
    :vartype details: dict[str, str]
    """

    def __init__(self, message, details=None):
        self.error = None
        self.message = message
        self.details = details
        if isinstance(message, constants.MessageSendResult):
            self.message = "Message send failed with result: {}".format(message)
        if details and isinstance(details, Exception):
            try:
                condition = details.condition.value.decode('UTF-8')
            except AttributeError:
                condition = details.condition.decode('UTF-8')
            _, _, self.error = condition.partition(':')
            self.message += "\nError: {}".format(self.error)
            try:
                self._parse_error(details.description)
                for detail in self.details:
                    self.message += "\n{}".format(detail)
            except:  # pylint: disable=bare-except
                self.message += "\n{}".format(details)
        super(EventHubError, self).__init__(self.message)

    def _parse_error(self, error_list):
        details = []
        self.message = error_list if isinstance(error_list, six.text_type) else error_list.decode('UTF-8')
        details_index = self.message.find(" Reference:")
        if details_index >= 0:
            details_msg = self.message[details_index + 1:]
            self.message = self.message[0:details_index]

            tracking_index = details_msg.index(", TrackingId:")
            system_index = details_msg.index(", SystemTracker:")
            timestamp_index = details_msg.index(", Timestamp:")
            details.append(details_msg[:tracking_index])
            details.append(details_msg[tracking_index + 2: system_index])
            details.append(details_msg[system_index + 2: timestamp_index])
            details.append(details_msg[timestamp_index + 2:])
            self.details = details
