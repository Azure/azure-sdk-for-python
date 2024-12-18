# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from typing import List, Tuple, Union, TYPE_CHECKING, Optional, Any, Dict, Callable
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from logging import Logger
    from .._configuration import Configuration
    from .._producer import EventHubProducer
    from .._consumer import EventHubConsumer
    from .._common import EventData
    from .._consumer_client import EventHubConsumerClient
    from .._client_base import _Address, ClientBase
    from ..amqp._amqp_message import AmqpAnnotatedMessage

    try:
        from uamqp.types import AMQPSymbol as uamqp_Types_AMQPSymbol
        from uamqp.constants import ConnectionState as uamqp_ConnectionState
        from uamqp import (
            Message as uamqp_Message,
            BatchMessage as uamqp_BatchMessage,
            AMQPClient as uamqp_AMQPClient,
            Connection as uamqp_Connection,
            Source as uamqp_Source,
            ReceiveClient as uamqp_ReceiveClient,
        )
        from uamqp.authentication import JWTTokenAuth as uamqp_JWTTokenAuth

    except ImportError:
        pass

    from .._pyamqp import (
        AMQPClient as pyamqp_AMQPClient,
        Connection as pyamqp_Connection,
        ReceiveClient as pyamqp_ReceiveClient,
    )
    from .._pyamqp.message import (
        Message as pyamqp_Message,
        BatchMessage as pyamqp_BatchMessage,
    )
    from .._pyamqp.endpoints import Source as pyamqp_Source
    from .._pyamqp.authentication import JWTTokenAuth as pyamqp_JWTTokenAuth
    from .._pyamqp.constants import ConnectionState as pyamqp_ConnectionState


class AmqpTransport(ABC):  # pylint: disable=too-many-public-methods
    """
    Abstract class that defines a set of common methods needed by producer and consumer.
    """

    KIND: str

    # define constants
    MAX_FRAME_SIZE_BYTES: int
    MAX_MESSAGE_LENGTH_BYTES: int
    TIMEOUT_FACTOR: int
    CONNECTION_CLOSING_STATES: Tuple[
        Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
        Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
        Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
        Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
        Optional[Union["uamqp_ConnectionState", "pyamqp_ConnectionState"]],
    ]
    TRANSPORT_IDENTIFIER: str

    # define symbols
    PRODUCT_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]
    VERSION_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]
    FRAMEWORK_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]
    PLATFORM_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]
    USER_AGENT_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]
    PROP_PARTITION_KEY_AMQP_SYMBOL: Union[uamqp_Types_AMQPSymbol, str, bytes]

    @staticmethod
    @abstractmethod
    def build_message(**kwargs: Any) -> Union["uamqp_Message", "pyamqp_Message"]:
        """
        Creates a uamqp.Message or pyamqp.Message with given arguments.
        :rtype: ~uamqp.Message or ~pyamqp.message.Message
        """

    @staticmethod
    @abstractmethod
    def build_batch_message(**kwargs: Any) -> Union["uamqp_BatchMessage", "pyamqp_BatchMessage"]:
        """
        Creates a uamqp.BatchMessage or pyamqp.BatchMessage with given arguments.
        :rtype: ~uamqp.BatchMessage or ~pyamqp.message.BatchMessage
        """

    @staticmethod
    @abstractmethod
    def to_outgoing_amqp_message(annotated_message: AmqpAnnotatedMessage) -> Union["uamqp_Message", "pyamqp_Message"]:
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: ~uamqp.Message or ~pyamqp.message.Message
        """

    @staticmethod
    @abstractmethod
    def update_message_app_properties(
        message: Union["uamqp_Message", "pyamqp_Message"], key: Union[str, bytes], value: str
    ) -> Union["uamqp_Message", "pyamqp_Message"]:
        """
        Adds the given key/value to the application properties of the message.
        :param ~uamqp.Message or ~pyamqp.message.Message message: Message.
        :param str key: Key to set in application properties.
        :param str value: Value to set for key in application properties.
        :rtype: ~uamqp.Message or ~pyamqp.message.Message
        """

    @staticmethod
    @abstractmethod
    def get_message_encoded_size(message: Union["uamqp_Message", "pyamqp_Message"]) -> int:
        """
        Gets the message encoded size given an underlying Message.
        :param ~uamqp.Message or ~pyamqp.message.Message message: Message to get encoded size of.
        :rtype: int
        """

    @staticmethod
    @abstractmethod
    def get_remote_max_message_size(handler: Union["uamqp_AMQPClient", "pyamqp_AMQPClient"]) -> int:
        """
        Returns max peer message size.
        :param ~pyamqp.AMQPClient or ~uamqp.AMQPClient handler: Client to get remote max message size on link from.
        :rtype: int
        """

    @staticmethod
    @abstractmethod
    def create_retry_policy(config: Configuration) -> None:
        """
        Creates the error retry policy.
        :param ~azure.eventhub._configuration.Configuration config: Configuration.
        """

    @staticmethod
    @abstractmethod
    def create_link_properties(link_properties: Dict[bytes, int]) -> Dict[bytes, int]:
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """

    @staticmethod
    @abstractmethod
    def create_connection(
        *,
        endpoint: str,
        auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"],
        container_id: Optional[str] = None,
        max_frame_size: int,
        channel_max: int,
        idle_timeout: Optional[float],
        properties: Optional[Dict[str, Any]],
        remote_idle_timeout_empty_frame_send_ratio: float,
        error_policy: Any,
        debug: bool,
        encoding: str,
        **kwargs: Any,
    ) -> Union["uamqp_Connection", "pyamqp_Connection"]:
        """
        Creates and returns the uamqp Connection object.
        :keyword str endpoint: The endpoint, used by pyamqp.
        :keyword JWTTokenAuth auth: The auth, used by uamqp.
        :keyword str container_id: Required.
        :keyword int max_frame_size: Required.
        :keyword int channel_max: Required.
        :keyword float idle_timeout: Required.
        :keyword dict[str, Any] or None properties: Required.
        :keyword float remote_idle_timeout_empty_frame_send_ratio: Required.
        :keyword error_policy: Required.
        :keyword bool debug: Required.
        :keyword str encoding: Required.
        """

    @staticmethod
    @abstractmethod
    def close_connection(connection: Union["uamqp_Connection", "pyamqp_Connection"]):
        """
        Closes existing connection.
        :param connection: uamqp or pyamqp Connection.
        :type connection: ~uamqp.Connection or ~pyamqp.Connection
        """

    @staticmethod
    @abstractmethod
    def get_connection_state(
        connection: Union["uamqp_Connection", "pyamqp_Connection"]
    ) -> Union["uamqp_ConnectionState", "pyamqp_ConnectionState"]:
        """
        Gets connection state.
        :param connection: uamqp or pyamqp Connection.
        :type connection: ~uamqp.Connection or ~pyamqp.Connection
        """

    @staticmethod
    @abstractmethod
    def create_send_client(
        *,
        config: Configuration,
        target: str,
        auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"],
        idle_timeout: Optional[float],
        network_trace: bool,
        retry_policy: Any,
        keep_alive_interval: int,
        client_name: str,
        link_properties: Optional[Dict[str, Any]],
        properties: Optional[Dict[str, Any]],
        **kwargs: Any,
    ):
        """
        Creates and returns the send client.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict[str, Any] or None link_properties: Required.
        :keyword properties: Required.
        """

    @staticmethod
    @abstractmethod
    def send_messages(
        producer: EventHubProducer, timeout_time: Optional[float], last_exception: Optional[Exception], logger: Logger
    ):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param float or none timeout_time: Timeout time.
        :param Exception or none last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logging.Logger logger: Logger.
        """

    @staticmethod
    @abstractmethod
    def set_message_partition_key(
        message: Union["uamqp_Message", "pyamqp_Message"], partition_key: Optional[Union[str, bytes]], **kwargs: Any
    ):
        """Set the partition key as an annotation on a uamqp message.

        :param ~uamqp.Message or ~pyamqp.message.Message message: The message to update.
        :param str partition_key: The partition key value.
        """

    @staticmethod
    @abstractmethod
    def add_batch(
        event_data_batch: Union["uamqp_BatchMessage", "pyamqp_BatchMessage"],
        outgoing_event_data: EventData,
        event_data: EventData,
    ):
        """
        Add EventData to the data body of the BatchMessage.
        :param ~pyamqp.message.BatchMessage or ~uamqp.BatchMessage event_data_batch: BatchMessage to add data to.
        :param ~azure.eventhub.EventData outgoing_event_data: EventData with outgoing Messages set for sending.
        :param EventData event_data: EventData to add to internal batch events. uamqp use only.
        """

    @staticmethod
    @abstractmethod
    def create_source(source: Union["uamqp_Source", "pyamqp_Source"], offset: int, selector: bytes):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes selector: Required.
        """

    @staticmethod
    @abstractmethod
    def create_receive_client(
        *,
        config: Configuration,
        source: Union["uamqp_Source", "pyamqp_Source"],
        auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"],
        idle_timeout: Optional[float],
        network_trace: bool,
        retry_policy: Any,
        client_name: str,
        link_properties: Dict[bytes, Any],
        properties: Optional[Dict[str, Any]],
        link_credit: int,
        keep_alive_interval: int,
        desired_capabilities: Optional[List[bytes]],
        streaming_receive: bool,
        message_received_callback: Callable,
        timeout: float,
        **kwargs: Any,
    ):
        """
        Creates and returns the receive client.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword ~uamqp.Source or ~pyamqp.endpoints.Source source: Required. The source.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword dict[str, Any] or None properties: Required.
        :keyword link_credit: Required. The prefetch.
        :keyword keep_alive_interval: Required. Missing in pyamqp.
        :keyword list[bytes] or None desired_capabilities: Required.
        :keyword streaming_receive: Required.
        :keyword message_received_callback: Required.
        :keyword timeout: Required.
        """

    @staticmethod
    @abstractmethod
    def open_receive_client(
        *,
        handler: Union["uamqp_ReceiveClient", "pyamqp_ReceiveClient"],
        client: EventHubConsumerClient,
        auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"],
    ):
        """
        Opens the receive client.
        :keyword ~uamqp.ReceiveClient or ~pyamqp.ReceiveClient handler: The receive client.
        :keyword ~azure.eventhub.EventHubConsumerClient client: The consumer client.
        :keyword ~pyamqp.authentication.JWTTokenAuth or uamqp.authentication.JWTTokenAuth auth: The auth.
        """

    @staticmethod
    @abstractmethod
    def check_link_stolen(consumer: EventHubConsumer, exception: Exception):
        """
        Checks if link stolen and handles exception.
        :param ~azure.eventhub._consumer.EventHubConsumer consumer: The EventHubConsumer.
        :param Exception exception: Exception to check.
        """

    @staticmethod
    @abstractmethod
    def create_token_auth(
        auth_uri: str,
        get_token: Callable,
        token_type: bytes,
        config: Configuration,
        *,
        update_token: bool,
    ):
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param callable get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param ~azure.eventhub._configuration.Configuration config: EH config.

        :keyword bool update_token: Whether to update token. If not updating token,
         then pass 300 to refresh_window. Only used by uamqp.
        """

    @staticmethod
    @abstractmethod
    def create_mgmt_client(
        address: _Address, mgmt_auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"], config: Configuration
    ):
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param ~pyamqp.authentication.JWTTokenAuth or uamqp.authentication.JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

    @staticmethod
    @abstractmethod
    def get_updated_token(mgmt_auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"]):
        """
        Return updated auth token.
        :param ~pyamqp.authentication.JWTTokenAuth or uamqp.authentication.JWTTokenAuth mgmt_auth: Auth.
        """

    @staticmethod
    @abstractmethod
    def mgmt_client_request(
        mgmt_client: Union["uamqp_AMQPClient", "pyamqp_AMQPClient"],
        mgmt_msg: str,
        *,
        operation: bytes,
        operation_type: bytes,
        status_code_field: bytes,
        description_fields: bytes,
        **kwargs: Any,
    ):
        """
        Send mgmt request.
        :param ~uamqp.AMQPClient or ~pyamqp.AMQPClient mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes status_code_field: mgmt status code.
        :keyword bytes description_fields: mgmt status desc.
        """

    @staticmethod
    @abstractmethod
    def get_error(status_code: int, description: str):
        """
        Gets error corresponding to status code.
        :param int status_code: Status code.
        :param str description: Description of error.
        """

    @staticmethod
    @abstractmethod
    def check_timeout_exception(base: ClientBase, exception: Exception):
        """
        Checks if timeout exception.
        :param ~azure.eventhub._client_base.ClientBase base: ClientBase.
        :param Exception exception: Exception to check.
        """
