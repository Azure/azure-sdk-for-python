# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Union, TYPE_CHECKING, Any, Dict, Callable
from typing_extensions import Literal

if TYPE_CHECKING:
    try:
        from uamqp import types as uamqp_types
    except ImportError:
        uamqp_types = None

class AmqpTransportAsync(ABC):  # pylint: disable=too-many-public-methods
    """
    Abstract class that defines a set of common methods needed by sender and receiver.
    """
    KIND: str

    # define constants
    MAX_FRAME_SIZE_BYTES: int
    MAX_MESSAGE_LENGTH_BYTES: int
    TIMEOUT_FACTOR: int
    CONNECTION_CLOSING_STATES: Tuple

    ServiceBusToAMQPReceiveModeMap: Dict[str, Any]

    # define symbols
    PRODUCT_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal["product"]]
    VERSION_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal["version"]]
    FRAMEWORK_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal["framework"]]
    PLATFORM_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal["platform"]]
    USER_AGENT_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal["user-agent"]]
    PROP_PARTITION_KEY_AMQP_SYMBOL: Union[uamqp_types.AMQPSymbol, Literal[b'x-opt-partition-key']]
    AMQP_LONG_VALUE: Callable
    AMQP_ARRAY_VALUE: Callable
    AMQP_UINT_VALUE: Callable

    @staticmethod
    @abstractmethod
    def build_message(**kwargs):
        """
        Creates a uamqp.Message or pyamqp.Message with given arguments.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def build_batch_message(data):
        """
        Creates a uamqp.BatchMessage or pyamqp.BatchMessage with given arguments.
        :param list[~uamqp.Message or ~pyamqp.Message] data: A list of uamqp.Message or pyamqp.Message.
        :rtype: uamqp.BatchMessage or pyamqp.BatchMessage
        """

    @staticmethod
    @abstractmethod
    def to_outgoing_amqp_message(annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def update_message_app_properties(message, key, value):
        """
        Adds the given key/value to the application properties of the message.
        :param uamqp.Message or pyamqp.Message message: Message.
        :param str key: Key to set in application properties.
        :param str value: Value to set for key in application properties.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def get_batch_message_encoded_size(message):
        """
        Gets the batch message encoded size given an underlying Message.
        :param uamqp.BatchMessage message: Message to get encoded size of.
        :rtype: int
        """

    @staticmethod
    @abstractmethod
    def get_remote_max_message_size(handler):
        """
        Returns max peer message size.
        :param AMQPClient handler: Client to get remote max message size on link from.
        :rtype: int
        """

    @staticmethod
    @abstractmethod
    def create_retry_policy(config):
        """
        Creates the error retry policy.
        :param Configuration config: Configuration.
        """

    @staticmethod
    @abstractmethod
    async def create_connection_async(host, auth, network_trace, **kwargs):
        """
        Creates and returns the pyamqp Connection object.
        :param str host: The hostname used by pyamqp.
        :param JWTTokenAuth auth: The auth used by pyamqp.
        :param bool network_trace: Debug setting.
        """

    @staticmethod
    @abstractmethod
    async def close_connection_async(connection):
        """
        Closes existing connection.
        :param ~uamqp.ConnectionAsync connection: uamqp or pyamqp Connection.
        """

    @staticmethod
    @abstractmethod
    def create_send_client_async(config, **kwargs):
        """
        Creates and returns the send client.
        :param Configuration config: The configuration.

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

    @staticmethod
    @abstractmethod
    async def send_messages_async(sender, message, logger, timeout, last_exception):
        """
        Handles sending of service bus messages.
        :param ~uamqp.SendClientAsync or ~pyamqp.aio.SendCientAsync sender: The sender with handler to send messages.
        :param Message message: The message to send.
        :param int timeout: Timeout time.
        :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logging.Logger logger: Logger.
        """

    @staticmethod
    @abstractmethod
    def create_source(source, session_filter):
        """
        Creates and returns the Source.

        :param Source source: Required.
        :param str or None session_filter: Required.
        """

    @staticmethod
    @abstractmethod
    def create_receive_client_async(receiver, **kwargs):
        """
        Creates and returns the receive client.
        :param ~uamqp.ReceiveClientAsync or ~pyamqp.aio.ReceiveClientAsync receiver: The receiver.

        :keyword Source source: Required. The source.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword properties: Required.
        :keyword link_credit: Required. The prefetch.
        :keyword keep_alive_interval: Required. Missing in pyamqp.
        :keyword desired_capabilities: Required.
        :keyword streaming_receive: Required.
        :keyword message_received_callback: Required.
        :keyword timeout: Required.
        """

    @staticmethod
    @abstractmethod
    async def iter_contextual_wrapper_async(
        receiver, max_wait_time=None
    ):
        """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
        and per-iter argument passing that requires the former.
        :param ~uamqp.ReceiveClientAsync or ~pyamqp.aio.ReceiveClientAsync
         receiver: Client with handler to iterate through messages.
        :param int or None max_wait_time: Max wait time.
        """

    @staticmethod
    @abstractmethod
    async def iter_next_async(
        receiver, wait_time=None
    ):
        """
        Used to iterate through received messages.
        :param ~uamqp.ReceiveClientAsync or ~pyamqp.aio.ReceiveClientAsync
         receiver: Client with handler to iterate through messages.
        :param int or None wait_time: Wait time.
        """

    @staticmethod
    @abstractmethod
    def build_received_message(receiver, message_type, received):
        """
        Build ServiceBusReceivedMessage.
        :param ~uamqp.ReceiveClientAsync or ~pyamqp.aio.ReceiveClientAsync
         receiver: Client with handler to build message from.
        :param str message_type: Message type.
        :param Message received: Received message.
        """

    @staticmethod
    @abstractmethod
    def set_handler_message_received_async(receiver):
        """
        Sets _message_received on async handler.
        :param ~uamqp.ReceiveClientAsync or ~pyamqp.aio.ReceiveClientAsync
         receiver: Client with handler to set _message_received on.
        """

    @staticmethod
    @abstractmethod
    def get_current_time(handler):
        """
        Gets the current time.
        :param ~uamqp.ReceiveClientAsync
         or ~pyamqp.aio.ReceiveClientAsync handler: Client with link to get current time from.
        """

    @staticmethod
    @abstractmethod
    async def reset_link_credit_async(
        handler, link_credit
    ):
        """
        Resets the link credit on the link.
        :param ~uamqp.ReceiveClientAsync
         or ~pyamqp.aio.ReceiveClientAsync handler: Client with link to reset link credit.
        :param int link_credit: Link credit needed.
        :rtype: None
        """

    @staticmethod
    @abstractmethod
    async def settle_message_via_receiver_link_async(
        handler,
        message,
        settle_operation,
        dead_letter_reason=None,
        dead_letter_error_description=None,
    ) -> None:
        """
        Settles message.
        :param ~uamqp.ReceiveClientAsync or
         ~pyamqp.aio.ReceiveClientAsync handler: Client with link to settle message on.
        :param ~uamqp.Message or ~pyamqp.message.Message message: The received message to settle.
        :param str settle_operation: The settle operation.
        :param str or None dead_letter_reason: Optional. The dead letter reason.
        :param str or None dead_letter_error_description: Optional. The dead letter error description.
        """

    @staticmethod
    @abstractmethod
    def parse_received_message(message, message_type, **kwargs):
        """
        Parses peek/deferred op messages into ServiceBusReceivedMessage.
        :param ~uamqp.Message or ~pyamqp.message.Message message: Message to parse.
        :param ~azure.servicebus.ServiceBusReceivedMessage message_type: Parse messages to return.
        :keyword ~azure.servicebus.aio.ServiceBusReceiver receiver: Required.
        :keyword bool is_peeked_message: Optional. For peeked messages.
        :keyword bool is_deferred_message: Optional. For deferred messages.
        :keyword ~azure.servicebus.ServiceBusReceiveMode receive_mode: Optional.
        """

    @staticmethod
    @abstractmethod
    async def create_token_auth_async(auth_uri, get_token, token_type, config, **kwargs):
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param callable get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param Configuration config: EH config.

        :keyword bool update_token: Whether to update token. If not updating token,
         then pass 300 to refresh_window. Only used by uamqp.
        :returns: JWTTokenAuth.
        :rtype: ~pyamqp.aio._authentication_async.JWTTokenAuth or ~uamqp.authentication.JWTTokenAuth
        """

    @staticmethod
    @abstractmethod
    async def mgmt_client_request_async(
        mgmt_client,
        mgmt_msg,
        *,
        operation,
        operation_type,
        node,
        timeout,
        callback
    ):
        """
        Send mgmt request.
        :param AMQPClient mgmt_client: Client to send request with.
        :param Message mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes node: Mgmt target.
        :keyword int timeout: Timeout.
        :keyword Callable callback: Callback to process request response.
        """
