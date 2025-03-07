# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, TYPE_CHECKING, Optional, Any, Dict, Callable
from typing_extensions import Literal

if TYPE_CHECKING:
    from logging import Logger
    from ..._configuration import Configuration
    from .._producer_async import EventHubProducer
    from .._consumer_async import EventHubConsumer
    from ..._common import EventData
    from .._consumer_client_async import EventHubConsumerClient
    from .._client_base_async import ClientBase
    from ..._client_base import _Address
    from ...amqp._amqp_message import AmqpAnnotatedMessage

    try:
        from uamqp.types import AMQPSymbol as uamqp_Types_AMQPSymbol
        from uamqp.constants import (
            ConnectionState as uamqp_ConnectionState,
        )
        from uamqp import (
            Message as uamqp_Message,
            BatchMessage as uamqp_BatchMessage,
            AMQPClientAsync as uamqp_AMQPClient,
            Connection as uamqp_Connection,
            Source as uamqp_Source,
            ReceiveClientAsync as uamqp_ReceiveClient,
            SendClientAsync as uamqp_SendClient,
        )
        from uamqp.authentication import JWTTokenAsync as uamqp_JWTTokenAuth

    except ImportError:
        pass

    from ..._pyamqp.aio import (
        AMQPClientAsync as pyamqp_AMQPClient,
        Connection as pyamqp_Connection,
        ReceiveClientAsync as pyamqp_ReceiveClient,
        SendClientAsync as pyamqp_SendClient,
    )
    from ..._pyamqp.message import (
        Message as pyamqp_Message,
        BatchMessage as pyamqp_BatchMessage,
    )
    from ..._pyamqp.endpoints import Source as pyamqp_Source
    from ..._pyamqp.aio._authentication_async import JWTTokenAuthAsync as pyamqp_JWTTokenAuth
    from ..._pyamqp.constants import (
        ConnectionState as pyamqp_ConnectionState,
    )


class AmqpTransportAsync(ABC):  # pylint: disable=too-many-public-methods
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
    # define symbols
    PRODUCT_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal["product"]]
    VERSION_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal["version"]]
    FRAMEWORK_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal["framework"]]
    PLATFORM_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal["platform"]]
    USER_AGENT_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal["user-agent"]]
    PROP_PARTITION_KEY_AMQP_SYMBOL: Union[uamqp_Types_AMQPSymbol, Literal[b"x-opt-partition-key"]]

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
        :param ~azure.eventhub.amqp.AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: ~uamqp.Message or ~pyamqp.message.Message
        """

    @staticmethod
    @abstractmethod
    def get_batch_message_encoded_size(message: Union["uamqp_Message", "pyamqp_Message"]) -> int:
        """
        Gets the batch message encoded size given an underlying Message.
        :param ~uamqp.BatchMessage or ~pyamqp.message.Message message: Message to get encoded size of.
        :rtype: int
        """

    @staticmethod
    @abstractmethod
    def get_remote_max_message_size(handler: Union["uamqp_AMQPClient", "pyamqp_AMQPClient"]) -> int:
        """
        Returns max peer message size.
        :param handler: Client to get remote max message size on link from.
        :type handler: ~uamqp.AMQPClientAsync or ~pyamqp.aio.AMQPClientAsync
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
    def create_link_properties(link_properties: Dict[bytes, int]) -> Dict[bytes, Any]:
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """

    @staticmethod
    @abstractmethod
    async def create_connection_async(
        *,
        endpoint: str,
        auth: Union["uamqp_JWTTokenAuth", pyamqp_JWTTokenAuth],
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
    ) -> Union[uamqp_Connection, pyamqp_Connection]:
        """
        Creates and returns the uamqp async Connection object.
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
    async def close_connection_async(connection: Union[uamqp_Connection, pyamqp_Connection]) -> None:
        """
        Closes existing connection.
        :param ~uamqp.async_ops.ConnectionAsync or ~pyamqp.aio.Connection connection: uamqp or pyamqp Connection.
        """

    @staticmethod
    @abstractmethod
    def get_connection_state(
        connection: Union[uamqp_Connection, pyamqp_Connection]
    ) -> Union["uamqp_ConnectionState", pyamqp_ConnectionState]:
        """
        Gets connection state.
        :param ~uamqp.async_ops.ConnectionAsync or ~pyamqp.aio.Connection connection: uamqp or pyamqp Connection.
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
    ) -> Union[uamqp_SendClient, pyamqp_SendClient]:
        """
        Creates and returns the send client.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword bool network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword dict[str, Any] or None properties: Required.
        """

    @staticmethod
    @abstractmethod
    async def send_messages_async(
        producer: EventHubProducer, timeout_time: Optional[float], last_exception: Optional[Exception], logger: Logger
    ) -> None:
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logging.Logger logger: Logger.
        """

    @staticmethod
    @abstractmethod
    def set_message_partition_key(
        message: Union["uamqp_Message", "pyamqp_Message"], partition_key: Optional[Union[str, bytes]], **kwargs: Any
    ) -> Union["uamqp_Message", "pyamqp_Message"]:
        """Set the partition key as an annotation on a uamqp message.

        :param ~uamqp.Message or ~pyamqp.message.Message message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: None
        """

    @staticmethod
    @abstractmethod
    def create_source(source: str, offset: int, selector: bytes) -> Union["uamqp_Source", "pyamqp_Source"]:
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
        timeout: int,
        **kwargs: Any,
    ) -> Union["uamqp_ReceiveClient", "pyamqp_ReceiveClient"]:
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
    async def receive_messages_async(
        consumer: EventHubConsumer, batch: bool, max_batch_size: int, max_wait_time: Optional[int]
    ) -> None:
        """
        Receives messages, creates events, and returns them by calling the on received callback.
        :param ~azure.eventhub.aio._consumer_async.EventHubConsumer consumer: The EventHubConsumer.
        :param bool batch: If receive batch or single event.
        :param int max_batch_size: Max batch size.
        :param int max_wait_time: Max wait time.
        """

    @staticmethod
    @abstractmethod
    async def create_token_auth_async(
        auth_uri: str,
        get_token: Callable,
        token_type: bytes,
        config: Configuration,
        *,
        update_token: bool,
    ) -> Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"]:
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
    ) -> Union["uamqp_AMQPClient", "pyamqp_AMQPClient"]:
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

    @staticmethod
    @abstractmethod
    async def get_updated_token_async(
        mgmt_auth: Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"]
    ) -> Union["uamqp_JWTTokenAuth", "pyamqp_JWTTokenAuth"]:
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        :type mgmt_auth: ~pyamqp.aio._authentication_async.JWTTokenAuthAsync
         or uamqp.authentication.JWTTokenAsync
        """

    @staticmethod
    @abstractmethod
    async def mgmt_client_request_async(
        mgmt_client: Union["uamqp_AMQPClient", "pyamqp_AMQPClient"],
        mgmt_msg: str,
        *,
        operation: bytes,
        operation_type: bytes,
        status_code_field: bytes,
        description_fields: bytes,
        **kwargs: Any,
    ) -> None:
        """
        Send mgmt request.
        :param ~uamqp.AMQPClientAsync or ~pyamqp.aio.AMQPClientAsync mgmt_client: Client to send request with.
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
