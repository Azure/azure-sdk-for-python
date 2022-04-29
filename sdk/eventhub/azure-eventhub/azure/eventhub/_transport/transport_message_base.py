# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from abc import abstractmethod

class TransportMessageBase:
    """
    Abstract class that acts as a wrapper for the transport Message class.
    """
    @property
    @abstractmethod
    def body_type(self):
        """The body type of the underlying AMQP message.

        :rtype: ~azure.eventhub.amqp.AmqpMessageBodyType
        """

    @property
    @abstractmethod
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
