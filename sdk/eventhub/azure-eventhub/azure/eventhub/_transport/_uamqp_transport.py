# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from uamqp import (
    BatchMessage,
    constants,
    MessageBodyType,
    Message,
)
from uamqp.message import (
    MessageHeader,
    MessageProperties,
)

from ._base import AmqpTransport, TransportMessageBase
from ..amqp._constants import AmqpMessageBodyType
from ..amqp._constants import AmqpMessageBodyType


class UamqpTransportMessage(TransportMessageBase, Message):

    @property
    def body_type(self):
        # type: () -> AmqpMessageBodyType
        """The body type of the underlying AMQP message.

        :rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """
        return UamqpTransport.AMQP_MESSAGE_BODY_TYPE_MAP.get(
            self._body.type, AmqpMessageBodyType.VALUE  # pylint: disable=protected-access
        )

    @property
    def body(self):
        """The body of the Message. The format may vary depending on the body type:
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.DATA<azure.eventhub.amqp.AmqpMessageBodyType.DATA>`,
        the body could be bytes or Iterable[bytes].
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.SEQUENCE<azure.eventhub.amqp.AmqpMessageBodyType.SEQUENCE>`,
        the body could be List or Iterable[List].
        For :class:`azure.eventhub.amqp.AmqpMessageBodyType.VALUE<azure.eventhub.amqp.AmqpMessageBodyType.VALUE>`,
        the body could be any type.

        :rtype: Any
        """
        return self.get_data()

class UamqpTransport(AmqpTransport):

    # define constants
    BATCH_MESSAGE = BatchMessage
    MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES

    AMQP_MESSAGE_BODY_TYPE_MAP = {
        MessageBodyType.Data.value: AmqpMessageBodyType.DATA,
        MessageBodyType.Sequence.value: AmqpMessageBodyType.SEQUENCE,
        MessageBodyType.Value.value: AmqpMessageBodyType.VALUE,
    }
    TRANSPORT_MESSAGE = UamqpTransportMessage

    def to_outgoing_amqp_message(self, annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Transport Message.
        """
        message_header = None
        if annotated_message.header:
            message_header = MessageHeader()
            message_header.delivery_count = annotated_message.header.delivery_count
            message_header.time_to_live = annotated_message.header.time_to_live
            message_header.first_acquirer = annotated_message.header.first_acquirer
            message_header.durable = annotated_message.header.durable
            message_header.priority = annotated_message.header.priority

        message_properties = None
        if annotated_message.properties:
            message_properties = MessageProperties(
                message_id=annotated_message.properties.message_id,
                user_id=annotated_message.properties.user_id,
                to=annotated_message.properties.to,
                subject=annotated_message.properties.subject,
                reply_to=annotated_message.properties.reply_to,
                correlation_id=annotated_message.properties.correlation_id,
                content_type=annotated_message.properties.content_type,
                content_encoding=annotated_message.properties.content_encoding,
                creation_time=int(annotated_message.properties.creation_time)
                    if annotated_message.properties.creation_time else None,
                absolute_expiry_time=int(annotated_message.properties.absolute_expiry_time)
                if annotated_message.properties.absolute_expiry_time else None,
                group_id=annotated_message.properties.group_id,
                group_sequence=annotated_message.properties.group_sequence,
                reply_to_group_id=annotated_message.properties.reply_to_group_id,
                encoding=annotated_message._encoding    # pylint: disable=protected-access
            )

        amqp_body_type = annotated_message.body_type  # pylint: disable=protected-access
        amqp_body = annotated_message.body
        if amqp_body_type == AmqpMessageBodyType.DATA:
            amqp_body_type = MessageBodyType.Data
            amqp_body = list(amqp_body)
        elif amqp_body_type == AmqpMessageBodyType.SEQUENCE:
            amqp_body_type = MessageBodyType.Sequence
            amqp_body = list(amqp_body)
        else:
            # amqp_body_type is type of AmqpMessageBodyType.VALUE
            amqp_body_type = MessageBodyType.Value

        return UamqpTransportMessage(
            body=amqp_body,
            body_type=amqp_body_type,
            header=message_header,
            properties=message_properties,
            application_properties=annotated_message.application_properties,
            annotations=annotated_message.annotations,
            delivery_annotations=annotated_message.delivery_annotations,
            footer=annotated_message.footer
        )
