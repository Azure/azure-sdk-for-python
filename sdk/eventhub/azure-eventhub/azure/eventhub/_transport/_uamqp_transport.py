# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
from typing import TYPE_CHECKING, Optional

from uamqp import (
    BatchMessage,
    constants,
    MessageBodyType,
    Message,
    types,
    SendClient,
)
from uamqp.message import (
    MessageHeader,
    MessageProperties,
)
from uamqp.errors import ErrorPolicy, ErrorAction

from ._base import AmqpTransport, TransportMessageBase
from ..amqp._constants import AmqpMessageBodyType
from ..amqp._constants import AmqpMessageBodyType
from .._constants import (
    NO_RETRY_ERRORS, 
    PROP_PARTITION_KEY_AMQP_SYMBOL,
)
from ..exceptions import OperationTimeoutError

if TYPE_CHECKING:
    import logging

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
    if error.condition == b"com.microsoft:server-busy":
        return ErrorAction(retry=True, backoff=4)
    if error.condition == b"com.microsoft:timeout":
        return ErrorAction(retry=True, backoff=2)
    if error.condition == b"com.microsoft:operation-cancelled":
        return ErrorAction(retry=True)
    if error.condition == b"com.microsoft:container-close":
        return ErrorAction(retry=True, backoff=4)
    if error.condition in NO_RETRY_ERRORS:
        return ErrorAction(retry=False)
    return ErrorAction(retry=True)

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
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """
    # define constants
    BATCH_MESSAGE = BatchMessage
    MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES
    AMQP_MESSAGE_BODY_TYPE_MAP = {
        MessageBodyType.Data.value: AmqpMessageBodyType.DATA,
        MessageBodyType.Sequence.value: AmqpMessageBodyType.SEQUENCE,
        MessageBodyType.Value.value: AmqpMessageBodyType.VALUE,
    }
    TRANSPORT_MESSAGE = UamqpTransportMessage
    IDLE_TIMEOUT_FACTOR = 1000 # pyamqp = 1

    # define symbols
    PRODUCT_SYMBOL = types.AMQPSymbol("product")
    VERSION_SYMBOL = types.AMQPSymbol("version")
    FRAMEWORK_SYMBOL = types.AMQPSymbol("framework")
    PLATFORM_SYMBOL = types.AMQPSymbol("platform")
    USER_AGENT_SYMBOL = types.AMQPSymbol("user-agent")

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

    def create_retry_policy(self, retry_total):
        """
        Creates the error retry policy.
        :param retry_total: Max number of retries.
        """
        return ErrorPolicy(max_retries=retry_total, on_error=_error_handler)

    def create_link_properties(self, timeout_symbol, timeout):
        """
        Creates and returns the link properties.
        :param bytes timeout_symbol: The timeout symbol.
        :param int timeout: The timeout to set as value.
        """
        return {
            types.AMQPSymbol(timeout_symbol): types.AMQPLong(timeout)
        }

    def create_send_client(self, *, config, **kwargs): # pylint:disable=unused-argument
        """
        Creates and returns the uamqp SendClient.
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
        """
        target = kwargs.pop("target")
        retry_policy = kwargs.pop("retry_policy")
        network_trace = kwargs.pop("network_trace")

        return SendClient(
            target,
            debug=network_trace,  # pylint:disable=protected-access
            error_policy=retry_policy,
            **kwargs
        )

    def _set_msg_timeout(self, timeout_time, last_exception, logger):
        # type: (Optional[float], Optional[Exception], logging.Logger) -> None
        if not timeout_time:
            return
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                error = last_exception
            else:
                error = OperationTimeoutError("Send operation timed out")
            logger.info("%r send operation timed out. (%r)", self._name, error)
            raise error
        self._handler._msg_timeout = remaining_time * 1000  # type: ignore  # pylint: disable=protected-access

    def send_messages(self, producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        """
        # pylint: disable=protected-access
        producer._unsent_events[0].on_send_complete = producer._on_outcome
        self._set_msg_timeout(timeout_time, last_exception, logger)
        producer._handler.queue_message(*producer._unsent_events)  # type: ignore
        producer._handler.wait()  # type: ignore
        producer._unsent_events = producer._handler.pending_messages  # type: ignore
        if producer._outcome != constants.MessageSendResult.Ok:
            if producer._outcome == constants.MessageSendResult.Timeout:
                producer._condition = OperationTimeoutError("Send operation timed out")
            if producer._condition:
                raise producer._condition

    def get_batch_message_data(self, batch_message):
        """
        Gets the data body of the BatchMessage.
        :param batch_message: BatchMessage to retrieve data body from.
        """
        return batch_message._body_gen  # pylint:disable=protected-access

    def set_message_partition_key(self, message, partition_key, **kwargs):  # pylint:disable=unused-argument
        # type: (Message, Optional[Union[bytes, str]], Any) -> None
        """Set the partition key as an annotation on a uamqp message.

        :param ~uamqp.Message message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: None
        """
        if partition_key:
            annotations = message.annotations
            if annotations is None:
                annotations = {}
            annotations[
                PROP_PARTITION_KEY_AMQP_SYMBOL
            ] = partition_key
            header = MessageHeader()
            header.durable = True
            message.annotations = annotations
            message.header = header
