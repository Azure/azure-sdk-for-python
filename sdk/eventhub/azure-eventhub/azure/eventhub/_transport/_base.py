# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from abc import ABC, abstractmethod

class AmqpTransport(ABC):
    """
    Abstract class that defines a set of common methods needed by producer and consumer.
    """
    # define constants
    BATCH_MESSAGE = None
    MAX_FRAME_SIZE_BYTES = None
    IDLE_TIMEOUT_FACTOR = None

    PRODUCT_SYMBOL = None
    VERSION_SYMBOL = None
    FRAMEWORK_SYMBOL = None
    PLATFORM_SYMBOL = None
    USER_AGENT_SYMBOL = None

    # errors
    AMQP_LINK_ERROR = None
    LINK_STOLEN_CONDITION = None
    MGMT_AUTH_EXCEPTION = None
    CONNECTION_ERROR = None
    AMQP_CONNECTION_ERROR = None

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
    def create_link_properties(self, link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
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
        """

    @abstractmethod
    def send_messages(self, producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
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

    @abstractmethod
    def create_source(self, source, offset, filter):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes filter: Required.
        """

    @abstractmethod
    def create_receive_client(self, *, config, **kwargs):
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
    @abstractmethod
    def open_receive_client(self, *, handler, client, auth):
        """
        Opens the receive client.
        :param ReceiveClient handler: The receive client.
        :param ~azure.eventhub.EventHubConsumerClient client: The consumer client.
        """

    @abstractmethod
    def create_token_auth(self, auth_uri, get_token, token_type, config, **kwargs):
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

    @abstractmethod
    def create_mgmt_client(self, address, mgmt_auth, config):
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

    @abstractmethod
    def get_updated_token(self, mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """

    @abstractmethod
    def mgmt_client_request(self, mgmt_client, mgmt_msg, **kwargs):
        """
        Send mgmt request.
        :param AMQP Client mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword operation_type: Op type.
        :keyword status_code_field: mgmt status code.
        :keyword description_fields: mgmt status desc.
        """

    @abstractmethod
    def get_error(self, error, message, *, condition=None):
        """
        Gets error and passes in error message, and, if applicable, condition.
        :param error: The error to raise.
        :param str message: Error message.
        :param condition: Optional error condition. Will not be used by uamqp.
        """

    @abstractmethod
    def get_link_max_message_size(self, handler):
        """
        Returns max peer message size.
        :param AMQPClient handler: Client to get remote max message size on link from.
        """
