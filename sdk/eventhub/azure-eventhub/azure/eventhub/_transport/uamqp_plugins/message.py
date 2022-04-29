# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from uamqp import Message as UamqpMessage
from .constants import AMQP_MESSAGE_BODY_TYPE_MAP, AmqpMessageBodyType
from ..transport_message_base import TransportMessageBase

class TransportMessage(TransportMessageBase, UamqpMessage):

    @property
    def body_type(self):
        # type: () -> AmqpMessageBodyType
        """The body type of the underlying AMQP message.

        :rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """
        return AMQP_MESSAGE_BODY_TYPE_MAP.get(
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
