# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from typing import Union, TYPE_CHECKING, Dict, Any, Callable
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    try:
        from uamqp import types as uamqp_types
    except ImportError:
        pass

class AmqpTransport(ABC):   # pylint: disable=too-many-public-methods
    """
    Abstract class that defines a set of common methods needed by sender and receiver.
    """
    KIND: str

    # define constants
    MAX_FRAME_SIZE_BYTES: int
    MAX_MESSAGE_LENGTH_BYTES: int
    TIMEOUT_FACTOR: int
    TRANSPORT_IDENTIFIER: str

    ServiceBusToAMQPReceiveModeMap: Dict[str, Any]

    # define symbols
    PRODUCT_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
    VERSION_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
    FRAMEWORK_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
    PLATFORM_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
    USER_AGENT_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
    PROP_PARTITION_KEY_AMQP_SYMBOL: Union[uamqp_types.AMQPSymbol, str, bytes]
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
    def encode_message(message):
        """
        Encodes the outgoing uamqp/pyamqp.Message of the message.
        :param ServiceBusMessage message: Message.
        :rtype: bytes
        """

    @staticmethod
    @abstractmethod
    def update_message_app_properties(message, key, value):
        """
        Adds the given key/value to the application properties of the message.
        :param uamqp.Message or pyamqp.Message message: Message.
        :param str key: Key to set in application properties.
        :param str Value: Value to set for key in application properties.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def get_message_encoded_size(message):
        """
        Gets the message encoded size given an underlying Message.
        :param uamqp.Message or pyamqp.Message message: Message to get encoded size of.
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
    def get_handler_link_name(handler):
        """
        Returns link name.
        :param AMQPClient handler: Client to get name of link from.
        :rtype: str
        """

    @staticmethod
    @abstractmethod
    def create_retry_policy(config, *, is_session=False):
        """
        Creates the error retry policy.
        :param ~azure.servicebus._configuration.Configuration config: Configuration.
        :keyword bool is_session: Is session enabled.
        """

    @staticmethod
    @abstractmethod
    def create_connection(host, auth, network_trace, **kwargs):
        """
        Creates and returns the uamqp/pyamqp Connection object.
        :param str host: The hostname used by uamqp/pyamqp.
        :param JWTTokenAuth auth: The auth used by uamqp/pyamqp.
        :param bool network_trace: Debug setting.
        """

    @staticmethod
    @abstractmethod
    def close_connection(connection):
        """
        Closes existing connection.
        :param connection: uamqp or pyamqp Connection.
        """

    @staticmethod
    @abstractmethod
    def create_send_client(config, **kwargs):
        """
        Creates and returns the uamqp SendClient.
        :param ~azure.servicebus._common._configuration.Configuration config:
            The configuration.
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
    def send_messages(
        sender, message, logger, timeout, last_exception
    ):
        """
        Handles sending of service bus messages.
        :param ~azure.servicebus.ServiceBusSender sender: The sender with handler
            to send messages.
        :param message: ServiceBusMessage with uamqp.Message to be sent.
        :paramtype message: ~azure.servicebus.ServiceBusMessage or ~azure.servicebus.ServiceBusMessageBatch
        :param int timeout: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
        """

    @staticmethod
    @abstractmethod
    def add_batch(sb_message_batch, outgoing_sb_message):
        """
        Add ServiceBusMessage to the data body of the BatchMessage.
        :param sb_message_batch: ServiceBusMessageBatch to add data to.
        :param outgoing_sb_message: Transformed ServiceBusMessage for sending.
        :rtype: None
        """

    @staticmethod
    @abstractmethod
    def create_source(source, session_filter):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int or None session_id: Required.
        """

    @staticmethod
    @abstractmethod
    def create_receive_client(receiver, **kwargs):
        """
        Creates and returns the receive client.
        :param ~azure.servicebus._common._configuration.Configuration config:
            The configuration.

        :keyword str source: Required. The source.
        :keyword str offset: Required.
        :keyword str offset_inclusive: Required.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword properties: Required.
        :keyword link_credit: Required. The prefetch.
        :keyword keep_alive_interval: Required.
        :keyword desired_capabilities: Required.
        :keyword timeout: Required.
        """

    @staticmethod
    @abstractmethod
    def iter_contextual_wrapper(
        receiver, max_wait_time=None
    ):
        """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
        and per-iter argument passing that requires the former."""

    @staticmethod
    @abstractmethod
    def iter_next(
        receiver, wait_time=None
    ):
        """
        Used to iterate through received messages.
        """

    @staticmethod
    @abstractmethod
    def build_received_message(receiver, message_type, received):
        """
        Build ServiceBusReceivedMessage.
        """

    @staticmethod
    @abstractmethod
    def get_current_time(handler):
        """
        Gets the current time.
        """

    @staticmethod
    @abstractmethod
    def reset_link_credit(
        handler, link_credit
    ):
        """
        Resets the link credit on the link.
        """

    @staticmethod
    @abstractmethod
    def settle_message_via_receiver_link(
        handler,
        message,
        settle_operation,
        dead_letter_reason=None,
        dead_letter_error_description=None,
    ) -> None:
        """
        Settles message.
        """

    @staticmethod
    @abstractmethod
    def parse_received_message(message, message_type, **kwargs):
        """
        Parses peek/deferred op messages into ServiceBusReceivedMessage.
        :param Message message: Message to parse.
        :param ServiceBusReceivedMessage message_type: Parse messages to return.
        :keyword ServiceBusReceiver receiver: Required.
        :keyword bool is_peeked_message: Optional. For peeked messages.
        :keyword bool is_deferred_message: Optional. For deferred messages.
        :keyword ServiceBusReceiveMode receive_mode: Optional.
        """

    @staticmethod
    @abstractmethod
    def get_message_value(message):
        """Get body of type value from message."""

    @staticmethod
    @abstractmethod
    def create_token_auth(
        auth_uri, get_token, token_type, config, **kwargs
    ):
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param ~azure.servicebus._configuration.Configuration config: EH config.

        :keyword bool update_token: Whether to update token. If not updating token,
         then pass 300 to refresh_window. Only used by uamqp.
        """

    @staticmethod
    @abstractmethod
    def create_mgmt_msg(
        message, application_properties, config, reply_to, **kwargs
    ):
        """
        :param message: The message to send in the management request.
        :paramtype message: Any
        :param Dict[bytes, str] application_properties: App props.
        :param ~azure.servicebus._common._configuration.Configuration config: Configuration.
        :param str reply_to: Reply to.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def mgmt_client_request(
        mgmt_client, mgmt_msg, *, operation, operation_type, node, timeout, callback
    ):
        """
        Send mgmt request and return result of callback.
        :param AMQPClient mgmt_client: Client to send request with.
        :param Message mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes node: Mgmt target.
        :keyword int timeout: Timeout.
        :keyword Callable callback: Callback to process request response.
        """
