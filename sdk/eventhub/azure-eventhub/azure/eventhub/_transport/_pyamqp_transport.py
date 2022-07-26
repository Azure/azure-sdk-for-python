# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import time
from typing import TYPE_CHECKING, Optional, Union, Any

from .._pyamqp import (
    error as errors,
    utils,
    SendClient,
    constants,
    AMQPClient,
    ReceiveClient,
)
from .._pyamqp.message import Message, BatchMessage, Header, Properties
from .._pyamqp.authentication import JWTTokenAuth
from .._pyamqp.endpoints import Source, ApacheFilters

from .._constants import (
    NO_RETRY_ERRORS,
    CUSTOM_CONDITION_BACKOFF,
)

from ._base import AmqpTransport
from ..amqp._constants import AmqpMessageBodyType
from .._constants import (
    NO_RETRY_ERRORS,
    PROP_PARTITION_KEY,
)

from ..exceptions import (
    ConnectError,
    EventDataSendError,
    OperationTimeoutError,
    EventHubError,
    AuthenticationError,
    ConnectionLostError,
    EventDataSendError,
)

_LOGGER = logging.getLogger(__name__)


class PyamqpTransport(AmqpTransport):
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """

    # define constants
    BATCH_MESSAGE = BatchMessage
    IDLE_TIMEOUT_FACTOR = 1
    MESSAGE = Message
    MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES

    # define symbols
    PRODUCT_SYMBOL = "product"
    VERSION_SYMBOL = "version"
    FRAMEWORK_SYMBOL = "framework"
    PLATFORM_SYMBOL = "platform"
    USER_AGENT_SYMBOL = "user-agent"
    PROP_PARTITION_KEY_AMQP_SYMBOL = PROP_PARTITION_KEY

    # define errors and conditions
    AMQP_LINK_ERROR = errors.AMQPLinkError
    LINK_STOLEN_CONDITION = errors.ErrorCondition.LinkStolen
    AUTH_EXCEPTION = errors.AuthenticationException
    CONNECTION_ERROR = errors.AMQPConnectionError
    AMQP_CONNECTION_ERROR = errors.AMQPConnectionError
    TIMEOUT_EXCEPTION = TimeoutError

    def to_outgoing_amqp_message(self, annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: pyamqp.Message
        """
        message_header = None
        if annotated_message.header and any(annotated_message.header.values()):
            message_header = Header(
                delivery_count=annotated_message.header.delivery_count,
                ttl=annotated_message.header.time_to_live,
                first_acquirer=annotated_message.header.first_acquirer,
                durable=annotated_message.header.durable,
                priority=annotated_message.header.priority,
            )

        message_properties = None
        if annotated_message.properties and any(annotated_message.properties.values()):
            message_properties = Properties(
                message_id=annotated_message.properties.message_id,
                user_id=annotated_message.properties.user_id,
                to=annotated_message.properties.to,
                subject=annotated_message.properties.subject,
                reply_to=annotated_message.properties.reply_to,
                correlation_id=annotated_message.properties.correlation_id,
                content_type=annotated_message.properties.content_type,
                content_encoding=annotated_message.properties.content_encoding,
                creation_time=int(annotated_message.properties.creation_time)
                if annotated_message.properties.creation_time
                else None,
                absolute_expiry_time=int(
                    annotated_message.properties.absolute_expiry_time
                )
                if annotated_message.properties.absolute_expiry_time
                else None,
                group_id=annotated_message.properties.group_id,
                group_sequence=annotated_message.properties.group_sequence,
                reply_to_group_id=annotated_message.properties.reply_to_group_id,
            )

        message_dict = {
            "header": message_header,
            "properties": message_properties,
            "application_properties": annotated_message.application_properties,
            "message_annotations": annotated_message.annotations,
            "delivery_annotations": annotated_message.delivery_annotations,
            "footer": annotated_message.footer,
        }

        if annotated_message.body_type == AmqpMessageBodyType.DATA:
            message_dict["data"] = annotated_message.body
        elif annotated_message.body_type == AmqpMessageBodyType.SEQUENCE:
            message_dict["sequence"] = annotated_message.body
        else:
            message_dict["value"] = annotated_message.body

        return Message(**message_dict)

    def get_batch_message_encoded_size(self, message):
        """
        Gets the batch message encoded size given an underlying Message.
        :param pyamqp.BatchMessage message: Message to get encoded size of.
        :rtype: int
        """
        return utils.get_message_encoded_size(message)

    def get_message_encoded_size(self, message):
        """
        Gets the message encoded size given an underlying Message.
        :param pyamqp.Message: Message to get encoded size of.
        :rtype: int
        """
        return utils.get_message_encoded_size(message)

    def get_remote_max_message_size(self, handler):
        """
        Returns max peer message size.
        :param AMQPClient handler: Client to get remote max message size on link from.
        :rtype: int
        """
        return handler._link.remote_max_message_size  # pylint: disable=protected-access

    def create_retry_policy(self, config):
        """
        Creates the error retry policy.
        :param ~azure.eventhub._configuration.Configuration config: Configuration.
        """
        return errors.RetryPolicy(
            retry_total=config.max_retries,  # pylint:disable=protected-access
            retry_backoff_factor=config.backoff_factor,  # pylint:disable=protected-access
            retry_backoff_max=config.backoff_max,  # pylint:disable=protected-access
            retry_mode=config.retry_mode,  # pylint:disable=protected-access
            no_retry_condition=NO_RETRY_ERRORS,
            custom_condition_backoff=CUSTOM_CONDITION_BACKOFF,
        )

    def create_link_properties(self, link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """
        return {
            symbol: utils.amqp_long_value(value)
            for (symbol, value) in link_properties.items()
        }

    def create_send_client(self, *, config, **kwargs):  # pylint:disable=unused-argument
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
        # TODO: extra passed in to pyamqp, but not used. should be used?
        msg_timeout = kwargs.pop(   # pylint: disable=unused-variable
            "msg_timeout"
        )  # TODO: not used by pyamqp?

        return SendClient(
            config.hostname,
            target,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            **kwargs,
        )

    def send_messages(self, producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
        """
        # pylint: disable=protected-access
        producer._open()
        timeout = timeout_time - time.time() if timeout_time else 0
        producer._handler.send_message(producer._unsent_events[0], timeout=timeout)
        producer._unsent_events = None
        # TODO: figure out if we want to use below, and see if it affects error story
        #try:
        #    producer._open()
        #    producer._handler.send_message(
        #        producer._unsent_events[0], timeout=timeout_time
        #    )
        #except self.TIMEOUT_EXCEPTION as exc:
        #    raise OperationTimeoutError(message=str(exc), details=exc)
        #except Exception as exc:
        #    raise producer._handle_exception(exc)

    def set_message_partition_key(
        self, message, partition_key, **kwargs
    ):
        # type: (Message, Optional[Union[bytes, str]], Any) -> Message
        """Set the partition key as an annotation on a uamqp message.
        :param Message message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: Message
        """
        encoding = kwargs.pop("encoding", 'utf-8')
        if partition_key:
            annotations = message.message_annotations
            if annotations is None:
                annotations = {}
            try:
                partition_key = partition_key.decode(encoding)
            except AttributeError:
                pass
            annotations[
                PROP_PARTITION_KEY
            ] = partition_key  # pylint:disable=protected-access
            header = Header(durable=True)
            return message._replace(message_annotations=annotations, header=header)
        return message

    def add_batch(self, batch_message, outgoing_event_data, event_data):    # pylint: disable=unused-argument
        """
        Add EventData to the data body of the BatchMessage.
        :param batch_message: BatchMessage to add data to.
        :param outgoing_event_data: Transformed EventData for sending.
        :param event_data: EventData to add to internal batch events. uamqp use only.
        :rtype: None
        """
        utils.add_batch(batch_message.message, outgoing_event_data.message)

    def create_source(self, source, offset, selector):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes selector: Required.
        """
        source = Source(address=source, filters={})
        if offset is not None:
            filter_key = ApacheFilters.selector_filter
            source.filters[filter_key] = (
                filter_key,
                utils.amqp_string_value(selector)
            )
        return source

    def create_receive_client(self, *, config, **kwargs):
        """
        Creates and returns the receive client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.

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
        :keyword keep_alive_interval: Required. Missing in pyamqp.
        :keyword desired_capabilities: Required.
        :keyword streaming_receive: Required.
        :keyword message_received_callback: Required.
        :keyword timeout: Required.
        """

        source = kwargs.pop("source")
        return ReceiveClient(
            config.hostname,
            source,
            receive_settle_mode=constants.ReceiverSettleMode.First, # TODO: make more descriptive in pyamqp?
            http_proxy=config.http_proxy,
            transport_type=config.transport_type,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            **kwargs,
        )

    def open_receive_client(self, *, handler, client, auth):
        """
        Opens the receive client and returns ready status.
        :param ReceiveClient handler: The receive client.
        :param ~azure.eventhub.EventHubConsumerClient client: The consumer client.
        :param auth: Auth.
        :rtype: bool
        """
        # pylint:disable=protected-access
        handler.open(
            connection=client._conn_manager.get_connection(
                client._address.hostname, auth
            )
        )

    def create_token_auth(self, auth_uri, get_token, token_type, config, **kwargs):
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param get_token: The callback function used for getting and refreshing
         tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param ~azure.eventhub._configuration.Configuration config: EH config.

        :keyword bool update_token: Whether to update token. If not updating token, then pass 300 to refresh_window.
        """
        # TODO: figure out why we're passing all these args to pyamqp JWTTokenAuth, which aren't being used
        update_token = kwargs.pop("update_token") # pylint: disable=unused-variable
        if update_token:
            # update_token not actually needed by pyamqp
            # just using to detect wh
            return JWTTokenAuth(
                auth_uri,
                auth_uri,
                get_token
            )
        return JWTTokenAuth(
            auth_uri,
            auth_uri,
            get_token,
            token_type=token_type,
            timeout=config.auth_timeout,
            custom_endpoint_hostname=config.custom_endpoint_hostname,
            port=config.connection_port,
            verify=config.connection_verify,
        )
        #if update_token:
        #    token_auth.update_token()  # TODO: why don't we need to update in pyamqp?

    def create_mgmt_client(self, address, mgmt_auth, config):
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

        return AMQPClient(
            config.hostname,
            auth=mgmt_auth,
            network_trace=config.network_tracing,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify
        )

    def get_updated_token(self, mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """
        return mgmt_auth.get_token()

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
        operation_type = kwargs.pop("operation_type")
        operation = kwargs.pop("operation")
        return mgmt_client.mgmt_request(
            mgmt_msg, operation=operation.decode(), operation_type=operation_type.decode(), **kwargs
        )

    def get_error(self, error, message, *, condition=None):
        """
        Gets error and passes in error message, and, if applicable, condition.
        :param error: The error to raise.
        :param str message: Error message.
        :param condition: Optional error condition. Will not be used by uamqp.
        """
        return error(condition, message)

    def _create_eventhub_exception(self, exception):
        if isinstance(exception, errors.AuthenticationException):
            error = AuthenticationError(str(exception), exception)
        elif isinstance(exception, errors.AMQPLinkError):
            error = ConnectError(str(exception), exception)
        # TODO: do we need MessageHanlderError in amqp any more
        #  if connection/session/link error are enough?
        # elif isinstance(exception, errors.MessageHandlerError):
        #     error = ConnectionLostError(str(exception), exception)
        elif isinstance(exception, errors.AMQPConnectionError):
            error = ConnectError(str(exception), exception)
        elif isinstance(exception, TimeoutError):
            error = ConnectionLostError(str(exception), exception)
        else:
            error = EventHubError(str(exception), exception)
        return error


    def _handle_exception(
        self, exception, closable
    ):  # pylint:disable=too-many-branches, too-many-statements
        try:  # closable is a producer/consumer object
            name = closable._name  # pylint: disable=protected-access
        except AttributeError:  # closable is an client object
            name = closable._container_id  # pylint: disable=protected-access
        if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
            _LOGGER.info("%r stops due to keyboard interrupt", name)
            closable._close_connection()  # pylint:disable=protected-access
            raise exception
        elif isinstance(exception, EventHubError):
            closable._close_handler()  # pylint:disable=protected-access
            raise exception
        # TODO: The following errors seem to be useless in EH
        # elif isinstance(
        #     exception,
        #     (
        #         errors.MessageAccepted,
        #         errors.MessageAlreadySettled,
        #         errors.MessageModified,
        #         errors.MessageRejected,
        #         errors.MessageReleased,
        #         errors.MessageContentTooLarge,
        #     ),
        # ):
        #     _LOGGER.info("%r Event data error (%r)", name, exception)
        #     error = EventDataError(str(exception), exception)
        #     raise error
        elif isinstance(exception, errors.MessageException):
            _LOGGER.info("%r Event data send error (%r)", name, exception)
            error = EventDataSendError(str(exception), exception)
            raise error
        else:
            if isinstance(exception, errors.AuthenticationException):
                if hasattr(closable, "_close_connection"):
                    closable._close_connection()  # pylint:disable=protected-access
            elif isinstance(exception, errors.AMQPLinkError):
                if hasattr(closable, "_close_handler"):
                    closable._close_handler()  # pylint:disable=protected-access
            elif isinstance(exception, errors.AMQPConnectionError):
                if hasattr(closable, "_close_connection"):
                    closable._close_connection()  # pylint:disable=protected-access
            # TODO: add MessageHandlerError in amqp?
            # elif isinstance(exception, errors.MessageHandlerError):
            #     if hasattr(closable, "_close_handler"):
            #         closable._close_handler()  # pylint:disable=protected-access
            else:  # errors.AMQPConnectionError, compat.TimeoutException
                if hasattr(closable, "_close_connection"):
                    closable._close_connection()  # pylint:disable=protected-access
            return self._create_eventhub_exception(exception)
