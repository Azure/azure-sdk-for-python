# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from abc import ABC, abstractmethod

class TransportMessageBase:
    """
    Abstract class that acts as a wrapper for the Message class.
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

class AmqpTransport(ABC):
    """
    Abstract class that defines a set of common methods needed by producer and consumer.
    """
    # define constants
    BATCH_MESSAGE = None
    MAX_MESSAGE_LENGTH_BYTES = None
    IDLE_TIMEOUT_FACTOR = None

    PRODUCT_SYMBOL = None
    VERSION_SYMBOL = None
    FRAMEWORK_SYMBOL = None
    PLATFORM_SYMBOL = None
    USER_AGENT_SYMBOL = None

    @abstractmethod
    def to_outgoing_amqp_message(self, annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Transport Message.
        :rtype: TransportMessageBase
        """

    @abstractmethod
    def create_retry_policy(self, retry_total):
        """
        Creates and returns the error retry policy.
        :param int retry_total: Max number of retries.
        """

    @abstractmethod
    def create_link_properties(self, timeout_symbol, timeout):
        """
        Creates and returns the link properties.
        :param bytes timeout_symbol: The timeout symbol.
        :param int timeout: The timeout to set as value.
        """

    @abstractmethod
    def create_send_client(self, *, config, **kwargs):
        """
        Creates and returns the send client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword properties: Required.
        :keyword config: Optional. Client configuration.
        """

    @abstractmethod
    def send_messages(self, producer, timeout_time, last_exception):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        """

    @abstractmethod
    def get_batch_message_data(self, batch_message):
        """
        Gets the data body of the BatchMessage.
        :param batch_message: BatchMessage to retrieve data body from.
        """

    @abstractmethod
    def set_message_partition_key(self, message, partition_key, **kwargs):
        """Set the partition key as an annotation on a uamqp message.

        :param message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: None
        """
