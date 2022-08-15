# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from abc import ABC, abstractmethod

class AmqpTransportAsync(ABC):
    """
    Abstract class that defines a set of common methods needed by producer and consumer.
    """
    # define constants
    MAX_FRAME_SIZE_BYTES = None
    MAX_MESSAGE_LENGTH_BYTES = None
    IDLE_TIMEOUT_FACTOR = None

    # define symbols
    PRODUCT_SYMBOL = None
    VERSION_SYMBOL = None
    FRAMEWORK_SYMBOL = None
    PLATFORM_SYMBOL = None
    USER_AGENT_SYMBOL = None
    PROP_PARTITION_KEY_AMQP_SYMBOL = None

    @staticmethod
    @abstractmethod
    def build_message(**kwargs):
        """
        Creates a uamqp.Message or pyamqp.Message with given arguments.
        :rtype: uamqp.Message or pyamqp.Message
        """

    @staticmethod
    @abstractmethod
    def build_batch_message(**kwargs):
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
        :param ~azure.eventhub._configuration.Configuration config: Configuration.
        """

    @staticmethod
    @abstractmethod
    def create_link_properties(link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """

    @staticmethod
    @abstractmethod
    async def create_connection_async(**kwargs):
        """
        Creates and returns the uamqp async Connection object.
        :keyword str host: The hostname, used by uamqp.
        :keyword JWTTokenAuth auth: The auth, used by uamqp.
        :keyword str endpoint: The endpoint, used by pyamqp.
        :keyword str container_id: Required.
        :keyword int max_frame_size: Required.
        :keyword int channel_max: Required.
        :keyword int idle_timeout: Required.
        :keyword Dict properties: Required.
        :keyword int remote_idle_timeout_empty_frame_send_ratio: Required.
        :keyword error_policy: Required.
        :keyword bool debug: Required.
        :keyword str encoding: Required.
        """

    @staticmethod
    @abstractmethod
    async def close_connection_async(connection):
        """
        Closes existing connection.
        :param connection: uamqp or pyamqp Connection.
        """

    @staticmethod
    @abstractmethod
    def get_connection_state(connection):
        """
        Gets connection state.
        :param connection: uamqp or pyamqp Connection.
        """

    @staticmethod
    @abstractmethod
    def create_send_client(*, config, **kwargs):
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
        """

    @staticmethod
    @abstractmethod
    async def send_messages_async(producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
        """

    @staticmethod
    @abstractmethod
    def set_message_partition_key(message, partition_key, **kwargs):
        """Set the partition key as an annotation on a uamqp message.

        :param message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: None
        """

    @staticmethod
    @abstractmethod
    def create_source(source, offset, selector):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes selector: Required.
        """

    @staticmethod
    @abstractmethod
    def create_receive_client(*, config, **kwargs):
        """
        Creates and returns the receive client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.

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
    async def receive_messages(consumer, batch, max_batch_size, max_wait_time):
        """
        Receives messages, creates events, and returns them by calling the on received callback.
        :param ~azure.eventhub.aio.EventHubConsumer consumer: The EventHubConsumer.
        :param bool batch: If receive batch or single event.
        :param int max_batch_size: Max batch size.
        :param int or None max_wait_time: Max wait time.
        """

    @staticmethod
    @abstractmethod
    async def create_token_auth_async(auth_uri, get_token, token_type, config, **kwargs):
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param ~azure.eventhub._configuration.Configuration config: EH config.

        :keyword bool update_token: Whether to update token. If not updating token,
         then pass 300 to refresh_window. Only used by uamqp.
        """

    @staticmethod
    @abstractmethod
    def create_mgmt_client(address, mgmt_auth, config):
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

    @staticmethod
    @abstractmethod
    async def get_updated_token_async(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """

    @staticmethod
    @abstractmethod
    async def mgmt_client_request_async(mgmt_client, mgmt_msg, **kwargs):
        """
        Send mgmt request.
        :param AMQP Client mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword operation_type: Op type.
        :keyword status_code_field: mgmt status code.
        :keyword description_fields: mgmt status desc.
        """

    @staticmethod
    @abstractmethod
    def get_error(status_code, description):
        """
        Gets error corresponding to status code.
        :param status_code: Status code.
        :param str description: Description of error.
        """

    @staticmethod
    @abstractmethod
    def check_timeout_exception(base, exception):
        """
        Checks if timeout exception.
        :param base: ClientBase.
        :param exception: Exception to check.
        """
