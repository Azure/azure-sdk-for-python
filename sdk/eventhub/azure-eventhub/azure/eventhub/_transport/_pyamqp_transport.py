# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import time
from typing import Callable, Dict, List, Optional, Union, Any, Tuple, cast

from .._pyamqp import (
    error as errors,
    utils,
    SendClient,
    constants,
    AMQPClient,
    ReceiveClient,
    __version__,
)
from .._pyamqp.message import Message, BatchMessage, Header, Properties
from .._pyamqp.authentication import JWTTokenAuth
from .._pyamqp.endpoints import Source, ApacheFilters
from .._pyamqp._connection import Connection, ConnectionState, _CLOSING_STATES

from ._base import AmqpTransport
from .._constants import (
    NO_RETRY_ERRORS,
    PROP_PARTITION_KEY,
    CUSTOM_CONDITION_BACKOFF,
    PYAMQP_LIBRARY,
)

from ..exceptions import (
    ConnectError,
    EventHubError,
    AuthenticationError,
    ConnectionLostError,
    EventDataSendError,
    OperationTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


class PyamqpTransport(AmqpTransport):  # pylint: disable=too-many-public-methods
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """

    KIND = "pyamqp"

    # define constants
    MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
    MAX_MESSAGE_LENGTH_BYTES = constants.MAX_FRAME_SIZE_BYTES  # TODO: define actual value in pyamqp
    TIMEOUT_FACTOR = 1
    CONNECTION_CLOSING_STATES: Tuple[
        ConnectionState, ConnectionState, ConnectionState, ConnectionState, Optional[ConnectionState]
    ] = _CLOSING_STATES
    TRANSPORT_IDENTIFIER = f"{PYAMQP_LIBRARY}/{__version__}"

    # define symbols
    PRODUCT_SYMBOL = "product"
    VERSION_SYMBOL = "version"
    FRAMEWORK_SYMBOL = "framework"
    PLATFORM_SYMBOL = "platform"
    USER_AGENT_SYMBOL = "user-agent"
    PROP_PARTITION_KEY_AMQP_SYMBOL = PROP_PARTITION_KEY

    ERROR_CONDITIONS = [condition.value for condition in errors.ErrorCondition]

    @staticmethod
    def build_message(**kwargs):
        """
        Creates a Message with given arguments.
        :return: Message with given arguments.
        :rtype: ~pyamqp.message.Message

        """
        return Message(**kwargs)

    @staticmethod
    def build_batch_message(**kwargs):
        """
        Creates a BatchMessage with given arguments.
        :return: BatchMessage with given arguments.
        :rtype: ~pyamqp.message.BatchMessage

        """
        return BatchMessage(**kwargs)

    @staticmethod
    def to_outgoing_amqp_message(annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param ~azure.eventhub.amqp.AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :return: Amqp Message.
        :rtype: ~pyamqp.message.Message
        """
        message_header = None
        header_vals = annotated_message.header.values() if annotated_message.header else None
        # If header and non-None header values, create outgoing header.
        if annotated_message.header and header_vals.count(None) != len(header_vals):
            message_header = Header(
                delivery_count=annotated_message.header.delivery_count,
                ttl=annotated_message.header.time_to_live,
                first_acquirer=annotated_message.header.first_acquirer,
                durable=annotated_message.header.durable,
                priority=annotated_message.header.priority,
            )

        message_properties = None
        properties_vals = annotated_message.properties.values() if annotated_message.properties else None
        # If properties and non-None properties values, create outgoing properties.
        if annotated_message.properties and properties_vals.count(None) != len(properties_vals):
            message_properties = Properties(
                message_id=annotated_message.properties.message_id,
                user_id=annotated_message.properties.user_id,
                to=annotated_message.properties.to,
                subject=annotated_message.properties.subject,
                reply_to=annotated_message.properties.reply_to,
                correlation_id=annotated_message.properties.correlation_id,
                content_type=annotated_message.properties.content_type,
                content_encoding=annotated_message.properties.content_encoding,
                creation_time=(
                    int(annotated_message.properties.creation_time)
                    if annotated_message.properties.creation_time
                    else None
                ),
                absolute_expiry_time=(
                    int(annotated_message.properties.absolute_expiry_time)
                    if annotated_message.properties.absolute_expiry_time
                    else None
                ),
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
            "data": annotated_message._data_body,  # pylint: disable=protected-access
            "sequence": annotated_message._sequence_body,  # pylint: disable=protected-access
            "value": annotated_message._value_body,  # pylint: disable=protected-access
            "footer": annotated_message.footer,
        }

        return Message(**message_dict)

    @staticmethod
    def update_message_app_properties(message, key, value):
        """
        Adds the given key/value to the application properties of the message.
        :param ~pyamqp.message.Message message: Message.
        :param str key: Key to set in application properties.
        :param str value: Value to set for key in application properties.
        :return: Message with updated application properties.
        :rtype: ~pyamqp.message.Message

        """
        if not message.application_properties:
            message = message._replace(application_properties={})
        message.application_properties.setdefault(key, value)
        return message

    @staticmethod
    def get_batch_message_encoded_size(message):
        """
        Gets the batch message encoded size given an underlying Message.
        :param ~pyamqp.message.BatchMessage message: Message to get encoded size of.
        :return: The encoded size of the batch message.
        :rtype: int
        """
        return utils.get_message_encoded_size(message)

    @staticmethod
    def get_message_encoded_size(message):
        """
        Gets the message encoded size given an underlying Message.
        :param message: Message to get encoded size of.
        :type message: ~pyamqp.message.Message
        :return: The encoded size of the message.
        :rtype: int

        """
        return utils.get_message_encoded_size(message)

    @staticmethod
    def get_remote_max_message_size(handler):
        """
        Returns max peer message size.
        :param ~pyamqp.AMQPClient handler: Client to get remote max message size on link from.
        :return: The max peer message size.
        :rtype: int

        """
        return handler._link.remote_max_message_size  # pylint: disable=protected-access

    @staticmethod
    def create_retry_policy(config):
        """
        Creates the error retry policy.
        :param ~azure.eventhub._configuration.Configuration config: Configuration.
        :return: The retry policy.
        :rtype: ~pyamqp.error.RetryPolicy

        """
        return errors.RetryPolicy(
            # hardcoding to 0 to avoid double retries and
            # 8 seconds of wait time when retrying compared to uamqp
            retry_total=0,
            retry_backoff_factor=config.backoff_factor,
            retry_backoff_max=config.backoff_max,
            retry_mode=config.retry_mode,
            no_retry_condition=NO_RETRY_ERRORS,
            custom_condition_backoff=CUSTOM_CONDITION_BACKOFF,
        )

    @staticmethod
    def create_link_properties(link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :return: The link properties.
        :rtype: dict

        """
        return {symbol: utils.amqp_long_value(value) for (symbol, value) in link_properties.items()}

    @staticmethod
    def create_connection(
        *,
        endpoint: str,
        auth: JWTTokenAuth,
        container_id: Optional[str] = None,
        max_frame_size: int,
        channel_max: int,
        idle_timeout: Optional[float],
        properties: Optional[Dict[str, Any]] = None,
        remote_idle_timeout_empty_frame_send_ratio: float,
        error_policy: Any,
        debug: bool,
        encoding: str,
        **kwargs: Any,
    ) -> Connection:
        """
        Creates and returns the uamqp Connection object.
        :keyword str endpoint: The endpoint, used by pyamqp.
        :keyword ~pyamqp.authentication.JWTTokenAuth auth: The auth, used by uamqp.
        :keyword str container_id: Required.
        :keyword int max_frame_size: Required.
        :keyword int channel_max: Required.
        :keyword float idle_timeout: Required.
        :keyword dict[str, Any] or None properties: Required.
        :keyword float remote_idle_timeout_empty_frame_send_ratio: Required.
        :keyword error_policy: Required.
        :keyword bool debug: Required.
        :keyword str encoding: Required.

        :return: The connection object.
        :rtype: ~pyamqp.Connection
        """
        network_trace = debug
        return Connection(
            endpoint,
            container_id=container_id,
            max_frame_size=max_frame_size,
            channel_max=channel_max,
            idle_timeout=idle_timeout,
            properties=properties,
            idle_timeout_empty_frame_send_ratio=remote_idle_timeout_empty_frame_send_ratio,
            network_trace=network_trace,
            **kwargs,
        )

    @staticmethod
    def close_connection(connection):
        """
        Closes existing connection.
        :param connection: pyamqp Connection.
        :type connection: ~pyamqp.Connection
        """
        connection.close()

    @staticmethod
    def get_connection_state(connection):
        """
        Gets connection state.
        :param connection: pyamqp Connection.
        :type connection: ~pyamqp.Connection
        :return: Connection state.
        :rtype: ~pyamqp.constants.ConnectionState
        """
        return connection.state

    @staticmethod
    def create_send_client(
        *,
        config,
        target: str,
        auth: JWTTokenAuth,
        idle_timeout: Optional[float],
        network_trace: bool,
        retry_policy: Any,
        keep_alive_interval: int,
        client_name: str,
        link_properties: Optional[Dict[str, Any]] = None,
        properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """
        Creates and returns the pyamqp SendClient.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword ~pyamqp.authentication.JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict[str, Any] or None link_properties: Required.
        :keyword properties: Required.

        :return: The SendClient.
        :rtype: ~pyamqp.SendClient
        """
        msg_timeout = kwargs.pop("msg_timeout")  # pylint: disable=unused-variable

        return SendClient(
            config.hostname,
            target,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            ssl_context=config.ssl_context,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            socket_timeout=config.socket_timeout,
            auth=auth,
            idle_timeout=idle_timeout,
            network_trace=network_trace,
            retry_policy=retry_policy,
            keep_alive_interval=keep_alive_interval,
            link_properties=link_properties,
            properties=properties,
            client_name=client_name,
            use_tls=config.use_tls,
            **kwargs,
        )

    @staticmethod
    def send_messages(producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logging.Logger logger: Logger.
        """
        # pylint: disable=protected-access
        try:
            producer._open()
            timeout = timeout_time - time.time() if timeout_time else 0
            producer._handler.send_message(producer._unsent_events[0], timeout=timeout)
            # TODO: The unsent_events list will always be <= 1. Even for a batch,
            # it gets the underlying singular BatchMessage.
            # May want to refactor in the future so that this isn't a list.
            producer._unsent_events = None
        except TimeoutError as exc:
            raise OperationTimeoutError(message=str(exc), details=exc) from exc

    @staticmethod
    def set_message_partition_key(
        message: Message, partition_key: Optional[Union[str, bytes]], **kwargs: Any
    ) -> Message:
        """Set the partition key as an annotation on a uamqp message.
        :param ~pyamqp.message.Message message: The message to update.
        :param str or bytes or None partition_key: The partition key value.
        :return: The message with the partition key annotation.
        :rtype: ~pyamqp.message.Message
        """
        encoding = kwargs.pop("encoding", "utf-8")
        if partition_key:
            annotations = message.message_annotations
            if annotations is None:
                annotations = {}
            try:
                partition_key = cast(bytes, partition_key).decode(encoding)
            except AttributeError:
                pass
            annotations[PROP_PARTITION_KEY] = partition_key
            header = Header(durable=True)  # type: ignore
            return message._replace(message_annotations=annotations, header=header)
        return message

    @staticmethod
    def add_batch(event_data_batch, outgoing_event_data, event_data):
        """
        Add EventData to the data body of the BatchMessage.
        :param ~azure.eventhub.EventDataBatch event_data_batch: EventDataBatch to add data to.
        :param ~azure.eventhub.EventData outgoing_event_data: EventData with outgoing Messages set for sending.
        :param ~azure.eventhub.EventData event_data: EventData to add to internal batch events. uamqp use only.
        :rtype: None
        """
        event_data_batch._internal_events.append(event_data)  # pylint: disable=protected-access
        # pylint: disable=protected-access
        utils.add_batch(event_data_batch._message, outgoing_event_data._message)

    @staticmethod
    def create_source(source, offset, selector):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes selector: Required.

        :return: The created Source.
        :rtype: ~pyamqp.endpoints.Source
        """
        source = Source(address=source, filters={})
        if offset is not None:
            filter_key = ApacheFilters.selector_filter
            source.filters[filter_key] = (filter_key, utils.amqp_string_value(selector))
        return source

    @staticmethod
    def create_receive_client(
        *,
        config,
        source: Source,
        auth: JWTTokenAuth,
        idle_timeout: Optional[float],
        network_trace: bool,
        retry_policy: Any,
        client_name: str,
        link_properties: Dict[bytes, Any],
        properties: Optional[Dict[str, Any]] = None,
        link_credit: int,
        keep_alive_interval: int,
        desired_capabilities: Optional[List[bytes]] = None,
        streaming_receive: bool,
        message_received_callback: Callable,
        timeout: float,
        **kwargs,
    ):
        """
        Creates and returns the receive client.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword Source source: Required. The source.
        :keyword ~pyamqp.authentication.JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword properties: Required.
        :keyword link_credit: Required. The prefetch.
        :keyword keep_alive_interval: Required. Missing in pyamqp.
        :keyword list[bytes] or None desired_capabilities: Required.
        :keyword streaming_receive: Required.
        :keyword message_received_callback: Required.
        :keyword float timeout: Required.

        :return: The receive client.
        :rtype: ~pyamqp.ReceiveClient
        """

        return ReceiveClient(
            config.hostname,
            source,
            receive_settle_mode=constants.ReceiverSettleMode.First,
            http_proxy=config.http_proxy,
            transport_type=config.transport_type,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            ssl_context=config.ssl_context,
            socket_timeout=config.socket_timeout,
            auth=auth,
            idle_timeout=idle_timeout,
            network_trace=network_trace,
            retry_policy=retry_policy,
            client_name=client_name,
            link_properties=link_properties,
            properties=properties,
            link_credit=link_credit,
            desired_capabilities=desired_capabilities,
            message_received_callback=message_received_callback,
            keep_alive_interval=keep_alive_interval,
            streaming_receive=streaming_receive,
            timeout=timeout,
            use_tls=config.use_tls,
            **kwargs,
        )

    @staticmethod
    def open_receive_client(*, handler, client, auth):
        """
        Opens the receive client and returns ready status.
        :keyword ~pyamqp.ReceiveClient handler: The receive client.
        :keyword ~azure.eventhub.EventHubConsumerClient client: The consumer client.
        :keyword auth: Auth.
        :paramtype auth: ~pyamqp.authentication.JWTTokenAuth
        """
        # pylint:disable=protected-access
        handler.open(connection=client._conn_manager.get_connection(client._address.hostname, auth))

    @staticmethod
    def check_link_stolen(consumer, exception):
        """
        Checks if link stolen and handles exception.
        :param ~azure.eventhub._consumer.EventHubConsumer consumer: The EventHubConsumer.
        :param Exception exception: Exception to check.
        """

        if isinstance(exception, errors.AMQPLinkError) and exception.condition == errors.ErrorCondition.LinkStolen:
            raise consumer._handle_exception(exception)  # pylint: disable=protected-access

    @staticmethod
    def create_token_auth(
        auth_uri: str,
        get_token: Callable,
        token_type: bytes,
        config,
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

        :keyword bool update_token: Whether to update token. If not updating token, then pass 300 to refresh_window.

        :return: The JWTTokenAuth.
        :rtype: ~pyamqp.authentication.JWTTokenAuth
        """
        # TODO: figure out why we're passing all these args to pyamqp JWTTokenAuth, which aren't being used
        if update_token:
            # update_token not actually needed by pyamqp
            # just using to detect wh
            return JWTTokenAuth(auth_uri, auth_uri, get_token, token_type=token_type)
        return JWTTokenAuth(
            auth_uri,
            auth_uri,
            get_token,
            token_type=token_type,
            timeout=config.auth_timeout,
            custom_endpoint_hostname=config.custom_endpoint_hostname,
            port=config.connection_port,
        )
        # if update_token:
        #    token_auth.update_token()  # TODO: why don't we need to update in pyamqp?

    @staticmethod
    def create_mgmt_client(address, mgmt_auth, config):
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param ~pyamqp.authentication.JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.

        :return: The mgmt AMQP client.
        :rtype: ~pyamqp.AMQPClient
        """

        return AMQPClient(
            config.hostname,
            auth=mgmt_auth,
            network_trace=config.network_tracing,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            ssl_context=config.ssl_context,
            use_tls=config.use_tls,
        )

    @staticmethod
    def get_updated_token(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        :type mgmt_auth: ~pyamqp.authentication.JWTTokenAuth
        :return: The mgmt AMQP client.
        :rtype: str
        """
        return mgmt_auth.get_token().token

    @staticmethod
    def mgmt_client_request(
        mgmt_client: AMQPClient,
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
        :param ~pyamqp.AMQPClient mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes status_code_field: mgmt status code.
        :keyword bytes description_fields: mgmt status desc.

        :return: Message.
        :rtype: ~pyamqp.message.Message

        """
        return mgmt_client.mgmt_request(
            mgmt_msg,
            operation=operation.decode(),
            operation_type=operation_type.decode(),
            status_code_field=status_code_field,
            description_fields=description_fields,
            **kwargs,
        )

    @staticmethod
    def get_error(status_code, description):
        """
        Gets error and passes in error message, and, if applicable, condition.
        :param int status_code: The status code.
        :param str description: Error description message.
        :return: Error.
        :rtype: ~pyamqp.error.AMQPException

        """
        if status_code in [401]:
            return errors.AuthenticationException(
                errors.ErrorCondition.UnauthorizedAccess,
                description=f"""Management authentication failed. Status code: {status_code}, """
                f"""Description: {description!r}""",
            )
        if status_code in [404]:
            return errors.AMQPConnectionError(
                errors.ErrorCondition.NotFound,
                description=f"Management connection failed. Status code: {status_code}, Description: {description!r}",
            )
        return errors.AMQPConnectionError(
            errors.ErrorCondition.UnknownError,
            description=f"Management request error. Status code: {status_code}, Description: {description!r}",
        )

    @staticmethod
    def check_timeout_exception(base, exception):
        """
        Checks if timeout exception.
        :param ~azure.eventhub._client_base.ClientBase base: ClientBase.
        :param Exception exception: Exception to check.
        :return: Exception.
        :rtype: Exception

        """
        if not base.running and isinstance(exception, TimeoutError):
            exception = errors.AuthenticationException(
                errors.ErrorCondition.InternalError,
                description="Authorization timeout.",
            )
        return exception

    @staticmethod
    def _create_eventhub_exception(exception, *, is_consumer=False):
        if isinstance(exception, errors.AuthenticationException):
            error = AuthenticationError(str(exception), exception)
        elif isinstance(exception, errors.AMQPLinkError):
            # For uamqp exception parity, raising ConnectionLostError for LinkDetaches.
            # Else, vendor error condition that starts with "com.", so raise ConnectError.
            if exception.condition in PyamqpTransport.ERROR_CONDITIONS:
                error = ConnectionLostError(str(exception), exception)
            else:
                error = ConnectError(str(exception), exception)
        # TODO: do we need MessageHandlerError in amqp any more
        #  if connection/session/link error are enough?
        # elif isinstance(exception, errors.MessageHandlerError):
        #     error = ConnectionLostError(str(exception), exception)
        elif isinstance(exception, errors.AMQPConnectionError):
            error = ConnectError(str(exception), exception)
        elif isinstance(exception, TimeoutError):
            error = ConnectionLostError(str(exception), exception)
        else:
            if (
                isinstance(exception, FileNotFoundError)
                and is_consumer
                and exception.filename
                and "ca_certs" in exception.filename
            ):

                error = exception
            else:
                error = EventHubError(str(exception), exception)
        return error

    @staticmethod
    def _handle_exception(
        exception, closable, *, is_consumer=False
    ):
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
            # TODO: issue #34266
            error = EventDataSendError(str(exception), exception)  # type: ignore[arg-type]
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
            #         closable._close_handler()
            else:  # errors.AMQPConnectionError, compat.TimeoutException
                if hasattr(closable, "_close_connection"):
                    closable._close_connection()  # pylint:disable=protected-access
            return PyamqpTransport._create_eventhub_exception(exception, is_consumer=is_consumer)
