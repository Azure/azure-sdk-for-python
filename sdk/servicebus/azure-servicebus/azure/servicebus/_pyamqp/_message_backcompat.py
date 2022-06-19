# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=too-many-lines
from enum import Enum

from ._encode import encode_payload
from .utils import get_message_encoded_size
from .message import Message, Header, Properties, BatchMessage
#from uamqp import constants, errors


class MessageState(Enum):
    WaitingToBeSent = 0
    WaitingForSendAck = 1
    SendComplete = 2
    SendFailed = 3
    ReceivedUnsettled = 4
    ReceivedSettled = 5

    def __eq__(self, __o: object) -> bool:
        try:
            return self.value == __o.value
        except AttributeError:
            return super().__eq__(__o)


class MessageAlreadySettled(Exception):
    pass


DONE_STATES = (MessageState.SendComplete, MessageState.SendFailed)
RECEIVE_STATES = (MessageState.ReceivedSettled, MessageState.ReceivedUnsettled)
PENDING_STATES = (MessageState.WaitingForSendAck, MessageState.WaitingToBeSent)


class LegacyMessage(object):
    def __init__(self, message, **kwargs):
        self._message = message
        self.state = MessageState.SendComplete
        self.idle_time = 0
        self.retries = 0
        self._settler = kwargs.get('settler')
        self._encoding = kwargs.get('encoding')
        self.delivery_no = kwargs.get('delivery_no')
        self.delivery_tag = kwargs.get('delivery_tag') or None
        self.on_send_complete = None
        self.properties = LegacyMessageProperties(self._message.properties)
        self.application_properties = self._message.application_properties
        self.annotations = self._message.annotations
        self.header = LegacyMessageHeader(self._message.header)
        self.footer = self._message.footer
        self.delivery_annotations = self._message.delivery_annotations
        if self._settler:
            self.state = MessageState.ReceivedUnsettled
        elif self.delivery_no:
            self.state = MessageState.ReceivedSettled

    def __str__(self):
        return str(self._message)

    def _can_settle_message(self):
        if self.state not in RECEIVE_STATES:
            raise TypeError("Only received messages can be settled.")
        if self.settled:
            return False
        return True

    @property
    def settled(self):
        if self.state == MessageState.ReceivedUnsettled:
            return False
        return True

    def get_message_encoded_size(self):
        return get_message_encoded_size(self._message._to_outgoing_amqp_message())

    def encode_message(self):
        output = bytearray()
        encode_payload(output, self._message._to_outgoing_amqp_message())
        return bytes(output)

    def get_data(self):
        return self._message.body

    def gather(self):
        if self.state in RECEIVE_STATES:
            raise TypeError("Only new messages can be gathered.")
        if not self._message:
            raise ValueError("Message data already consumed.")
        if self.state in DONE_STATES:
            raise MessageAlreadySettled()
        return [self]

    def get_message(self):
        return self._message._to_outgoing_amqp_message()

    def accept(self):
        if self._can_settle_message():
            # TODO
            # self._response = errors.MessageAccepted()
            # self._settler(self._response)
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def reject(self, condition=None, description=None, info=None):
        if self._can_settle_message():
            # TODO
            # self._response = errors.MessageRejected(
            #     condition=condition,
            #     description=description,
            #     info=info,
            #     encoding=self._encoding,
            # )
            # self._settler(self._response)
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def release(self):
        if self._can_settle_message():
            # TODO
            #self._response = errors.MessageReleased()
            #self._settler(self._response)
            self.state = MessageState.ReceivedSettled
            return True
        return False

    def modify(self, failed, deliverable, annotations=None):
        if self._can_settle_message():
            # TODO
            # self._response = errors.MessageModified(
            #     failed, deliverable, annotations=annotations, encoding=self._encoding
            # )
            # self._settler(self._response)
            self.state = MessageState.ReceivedSettled
            return True
        return False


class LegacyBatchMessage(LegacyMessage):
    batch_format = 0x80013700
    max_message_length = 1024 * 1024
    size_offset = 0


class LegacyMessageProperties(object):

    def __init__(self, properties):
        self.message_id = self._encode_property(properties.message_id)
        self.user_id = self._encode_property(properties.user_id)
        self.to = self._encode_property(properties.to)
        self.subject = self._encode_property(properties.subject)
        self.reply_to = self._encode_property(properties.reply_to)
        self.correlation_id = self._encode_property(properties.correlation_id)
        self.content_type = self._encode_property(properties.content_type)
        self.content_encoding = self._encode_property(properties.content_encoding)
        self.absolute_expiry_time = properties.absolute_expiry_time
        self.creation_time = properties.creation_time
        self.group_id = self._encode_property(properties.group_id)
        self.group_sequence = properties.group_sequence
        self.reply_to_group_id = self._encode_property(properties.reply_to_group_id)

    def __str__(self):
        return str(
            {
                "message_id": self.message_id,
                "user_id": self.user_id,
                "to": self.to,
                "subject": self.subject,
                "reply_to": self.reply_to,
                "correlation_id": self.correlation_id,
                "content_type": self.content_type,
                "content_encoding": self.content_encoding,
                "absolute_expiry_time": self.absolute_expiry_time,
                "creation_time": self.creation_time,
                "group_id": self.group_id,
                "group_sequence": self.group_sequence,
                "reply_to_group_id": self.reply_to_group_id,
            }
        )

    def _encode_property(self, value):
        try:
            return value.encode("UTF-8")
        except AttributeError:
            return value

    def get_properties_obj(self):
        return Properties(
            self.message_id,
            self.user_id,
            self.to,
            self.subject,
            self.reply_to,
            self.correlation_id,
            self.content_type,
            self.content_encoding,
            self.absolute_expiry_time,
            self.creation_time,
            self.group_id,
            self.group_sequence,
            self.reply_to_group_id
        )


class LegacyMessageHeader(object):

    def __init__(self, header):
        self.delivery_count = header.delivery_count  # or 0
        self.time_to_live = header.time_to_live
        self.first_acquirer = header.first_acquirer
        self.durable = header.durable
        self.priority = header.priority

    def __str__(self):
        return str(
            {
                "delivery_count": self.delivery_count,
                "time_to_live": self.time_to_live,
                "first_acquirer": self.first_acquirer,
                "durable": self.durable,
                "priority": self.priority,
            }
        )

    def get_header_obj(self):
        return Header(
            self.durable,
            self.priority,
            self.time_to_live,
            self.first_acquirer,
            self.delivery_count
        )
