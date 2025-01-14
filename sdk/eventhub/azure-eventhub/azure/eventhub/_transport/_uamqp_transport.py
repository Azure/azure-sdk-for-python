# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import logging
from typing import Callable, Dict, List, Optional, Union, Any, Tuple, TYPE_CHECKING

try:
    from uamqp import (
        c_uamqp,
        BatchMessage,
        constants,
        MessageBodyType,
        Message,
        types,
        SendClient,
        ReceiveClient,
        Source,
        utils,
        authentication,
        AMQPClient,
        compat,
        errors,
        Connection,
        __version__,
    )
    from uamqp.message import (
        MessageHeader,
        MessageProperties,
    )

    uamqp_installed = True
except ImportError:
    uamqp_installed = False

from ._base import AmqpTransport
from ..amqp._constants import AmqpMessageBodyType
from .._constants import (
    NO_RETRY_ERRORS,
    PROP_PARTITION_KEY,
    UAMQP_LIBRARY,
)

from ..exceptions import (
    ConnectError,
    OperationTimeoutError,
    EventHubError,
    AuthenticationError,
    ConnectionLostError,
    EventDataError,
    EventDataSendError,
)

if TYPE_CHECKING:
    try:
        from uamqp.constants import ConnectionState as uamqp_ConnectionState
    except ImportError:
        pass

    from .._pyamqp.constants import ConnectionState as pyamqp_ConnectionState

_LOGGER = logging.getLogger(__name__)

if uamqp_installed:

    def _error_handler(error):
        """
        Called internally when an event has failed to send so we
        can parse the error to determine whether we should attempt
        to retry sending the event again.
        Returns the action to take according to error type.

        :param error: The error received in the send attempt.
        :type error: Exception
        :return: The action to be taken according to error type.
        :rtype: uamqp.errors.ErrorAction

        """
        if error.condition == b"com.microsoft:server-busy":
            return errors.ErrorAction(retry=True, backoff=4)
        if error.condition == b"com.microsoft:timeout":
            return errors.ErrorAction(retry=True, backoff=2)
        if error.condition == b"com.microsoft:operation-cancelled":
            return errors.ErrorAction(retry=True)
        if error.condition == b"com.microsoft:container-close":
            return errors.ErrorAction(retry=True, backoff=4)
        if error.condition in NO_RETRY_ERRORS:
            return errors.ErrorAction(retry=False)
        return errors.ErrorAction(retry=True)

    class UamqpTransport(AmqpTransport):  # pylint: disable=too-many-public-methods
        """
        Class which defines uamqp-based methods used by the producer and consumer.
        """

        KIND = "uamqp"

        # define constants
        MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
        MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES
        TIMEOUT_FACTOR = 1000
        CONNECTION_CLOSING_STATES: Tuple[
            Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
            Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
            Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
            Union["uamqp_ConnectionState", "pyamqp_ConnectionState"],
            Optional[Union["uamqp_ConnectionState", "pyamqp_ConnectionState"]],
        ] = (
            c_uamqp.ConnectionState.CLOSE_RCVD,
            c_uamqp.ConnectionState.CLOSE_SENT,
            c_uamqp.ConnectionState.DISCARDING,
            c_uamqp.ConnectionState.END,
            None,
        )
        TRANSPORT_IDENTIFIER = f"{UAMQP_LIBRARY}/{__version__}"

        # define symbols
        PRODUCT_SYMBOL = types.AMQPSymbol("product")
        VERSION_SYMBOL = types.AMQPSymbol("version")
        FRAMEWORK_SYMBOL = types.AMQPSymbol("framework")
        PLATFORM_SYMBOL = types.AMQPSymbol("platform")
        USER_AGENT_SYMBOL = types.AMQPSymbol("user-agent")
        PROP_PARTITION_KEY_AMQP_SYMBOL = types.AMQPSymbol(PROP_PARTITION_KEY)

        @staticmethod
        def build_message(**kwargs):
            """
            Creates a uamqp.Message with given arguments.
            :return: An instance of uamqp.Message.
            :rtype: uamqp.Message

            """
            return Message(**kwargs)

        @staticmethod
        def build_batch_message(**kwargs):
            """
            Creates a uamqp.BatchMessage with given arguments.
            :return: An instance of uamqp.BatchMessage.
            :rtype: uamqp.BatchMessage

            """
            return BatchMessage(**kwargs)

        @staticmethod
        def to_outgoing_amqp_message(annotated_message):
            """
            Converts an AmqpAnnotatedMessage into an Amqp Message.
            :param ~azure.eventhub.amqp.AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
            :return: An instance of uamqp.Message.
            :rtype: uamqp.Message

            """
            message_header = None
            header_vals = annotated_message.header.values() if annotated_message.header else None
            # If header and non-None header values, create outgoing header.
            if annotated_message.header and header_vals.count(None) != len(header_vals):
                message_header = MessageHeader()
                message_header.delivery_count = annotated_message.header.delivery_count
                message_header.time_to_live = annotated_message.header.time_to_live
                message_header.first_acquirer = annotated_message.header.first_acquirer
                message_header.durable = annotated_message.header.durable
                message_header.priority = annotated_message.header.priority

            message_properties = None
            properties_vals = annotated_message.properties.values() if annotated_message.properties else None
            # If properties and non-None properties values, create outgoing properties.
            if annotated_message.properties and properties_vals.count(None) != len(properties_vals):
                message_properties = MessageProperties(
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
                    encoding=annotated_message._encoding,  # pylint: disable=protected-access
                )

            # pylint: disable=protected-access
            amqp_body_type = annotated_message.body_type
            if amqp_body_type == AmqpMessageBodyType.DATA:
                amqp_body_type = MessageBodyType.Data
                amqp_body = list(annotated_message._data_body)
            elif amqp_body_type == AmqpMessageBodyType.SEQUENCE:
                amqp_body_type = MessageBodyType.Sequence
                amqp_body = list(annotated_message._sequence_body)
            else:
                amqp_body_type = MessageBodyType.Value
                amqp_body = annotated_message._value_body

            return Message(
                body=amqp_body,
                body_type=amqp_body_type,
                header=message_header,
                properties=message_properties,
                application_properties=annotated_message.application_properties,
                annotations=annotated_message.annotations,
                delivery_annotations=annotated_message.delivery_annotations,
                footer=annotated_message.footer,
            )

        @staticmethod
        def update_message_app_properties(message, key, value):
            """
            Adds the given key/value to the application properties of the message.
            :param uamqp.Message message: Message.
            :param str key: Key to set in application properties.
            :param str value: Value to set for key in application properties.
            :return: Message with updated application properties.
            :rtype: uamqp.Message

            """
            if not message.application_properties:
                message.application_properties = {}
            message.application_properties.setdefault(key, value)
            return message

        @staticmethod
        def get_batch_message_encoded_size(message):
            """
            Gets the batch message encoded size given an underlying Message.
            :param uamqp.BatchMessage message: Message to get encoded size of.
            :return: Size in bytes of the encoded batch message.
            :rtype: int

            """
            return message.gather()[0].get_message_encoded_size()

        @staticmethod
        def get_message_encoded_size(message):
            """
            Gets the message encoded size given an underlying Message.
            :param uamqp.Message message: Message to get encoded size of.
            :return: Size in bytes of the encoded message.
            :rtype: int

            """
            return message.get_message_encoded_size()

        @staticmethod
        def get_remote_max_message_size(handler):
            """
            Returns max peer message size.
            :param uamqp.AMQPClient handler: Client to get remote max message size on link from.
            :return: Max peer message size.
            :rtype: int

            """
            return handler.message_handler._link.peer_max_message_size  # pylint:disable=protected-access

        @staticmethod
        def create_retry_policy(config):
            """
            Creates the error retry policy.
            :param ~azure.eventhub._configuration.Configuration config: Configuration.
            :return: ErrorPolicy configured.
            :rtype: uamqp.errors.ErrorPolicy

            """
            return errors.ErrorPolicy(max_retries=config.max_retries, on_error=_error_handler)

        @staticmethod
        def create_link_properties(link_properties):
            """
            Creates and returns the link properties.
            :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
            :return: The link properties.
            :rtype: dict

            """
            return {types.AMQPSymbol(symbol): types.AMQPLong(value) for (symbol, value) in link_properties.items()}

        @staticmethod
        def create_connection(
            *,
            endpoint: str,
            auth: authentication.JWTTokenAuth,
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
        ) -> Connection:
            """
            Creates and returns the uamqp Connection object.
            :keyword str endpoint: The endpoint, used by pyamqp.
            :keyword ~uamqp.authentication.JWTTokenAuth auth: The auth, used by uamqp.
            :keyword str container_id: Required.
            :keyword int max_frame_size: Required.
            :keyword int channel_max: Required.
            :keyword float idle_timeout: Required.
            :keyword dict[str, Any] or None properties: Required.
            :keyword float remote_idle_timeout_empty_frame_send_ratio: Required.
            :keyword error_policy: Required.
            :keyword bool debug: Required.
            :keyword str encoding: Required.

            :return: The connection.
            :rtype: uamqp.Connection

            """
            return Connection(
                endpoint,
                auth,
                container_id=container_id,
                max_frame_size=max_frame_size,
                channel_max=channel_max,
                idle_timeout=idle_timeout,
                properties=properties,
                remote_idle_timeout_empty_frame_send_ratio=remote_idle_timeout_empty_frame_send_ratio,
                encoding=encoding,
                debug=debug,
                **kwargs,
            )

        @staticmethod
        def close_connection(connection):
            """
            Closes existing connection.
            :param connection: uamqp Connection to destroy.
            :type connection: uamqp.Connection
            """
            connection.destroy()

        @staticmethod
        def get_connection_state(connection):
            """
            Gets connection state.
            :param connection: uamqp Connection.
            :type connection: uamqp.Connection

            :return: The connection state.
            :rtype: uamqp.constants.ConnectionState
            """
            return connection._state  # pylint:disable=protected-access

        @staticmethod
        def create_send_client(
            *,
            config,
            target: str,
            auth: authentication.JWTTokenAuth,
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
            Creates and returns the uamqp SendClient.
            :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

            :keyword str target: Required. The target.
            :keyword ~uamqp.authentication.JWTTokenAuth auth: Required.
            :keyword int idle_timeout: Required.
            :keyword network_trace: Required.
            :keyword retry_policy: Required.
            :keyword keep_alive_interval: Required.
            :keyword str client_name: Required.
            :keyword dict link_properties: Required.
            :keyword dict[str, Any] or None properties: Required.

            :return: The send client.
            :rtype: uamqp.SendClient
            """
            return SendClient(
                target,
                debug=network_trace,
                error_policy=retry_policy,
                keep_alive_interval=keep_alive_interval,
                client_name=client_name,
                properties=properties,
                link_properties=link_properties,
                idle_timeout=idle_timeout,
                auth=auth,
                **kwargs,
            )

        @staticmethod
        def _set_msg_timeout(producer, timeout_time, last_exception, logger):
            # pylint: disable=protected-access
            if not timeout_time:
                return
            remaining_time = timeout_time - time.time()
            if remaining_time <= 0.0:
                if last_exception:
                    error = last_exception
                else:
                    error = OperationTimeoutError("Send operation timed out")
                logger.info("%r send operation timed out. (%r)", producer._name, error)
                raise error
            producer._handler._msg_timeout = remaining_time * 1000  # type: ignore

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
            producer._open()
            producer._unsent_events[0].on_send_complete = producer._on_outcome
            UamqpTransport._set_msg_timeout(producer, timeout_time, last_exception, logger)
            producer._handler.queue_message(*producer._unsent_events)  # type: ignore
            producer._handler.wait()  # type: ignore
            producer._unsent_events = producer._handler.pending_messages  # type: ignore
            if producer._outcome != constants.MessageSendResult.Ok:
                if producer._outcome == constants.MessageSendResult.Timeout:
                    producer._condition = OperationTimeoutError("Send operation timed out")
                if producer._condition:
                    raise producer._condition

        @staticmethod
        def set_message_partition_key(
            message: Message, partition_key: Optional[Union[bytes, str]] = None, **kwargs: Any
        ) -> Message:
            """Set the partition key as an annotation on a uamqp message.

            :param uamqp.Message message: The message to update.
            :param str or bytes or None partition_key: The partition key value.
            :returns: Message with partition key annotation set.
            :rtype: uamqp.Message
            """
            if partition_key:
                annotations = message.annotations
                if annotations is None:
                    annotations = {}
                annotations[
                    UamqpTransport.PROP_PARTITION_KEY_AMQP_SYMBOL  # TODO: see if setting non-amqp symbol is valid
                ] = partition_key
                header = MessageHeader()
                header.durable = True
                message.annotations = annotations
                message.header = header
            return message

        @staticmethod
        def add_batch(event_data_batch, outgoing_event_data, event_data):
            """
            Add EventData to the data body of the BatchMessage.
            :param uamqp.BatchMessage event_data_batch: BatchMessage to add data to.
            :param ~azure.eventhub.EventData outgoing_event_data: EventData with outgoing Messages set for sending.
            :param ~azure.eventhub.EventData event_data: EventData to add to internal batch events. uamqp use only.
            :rtype: None
            """
            # pylint: disable=protected-access
            event_data_batch._internal_events.append(event_data)
            event_data_batch._message._body_gen.append(outgoing_event_data._message)

        @staticmethod
        def create_source(source, offset, selector):
            """
            Creates and returns the Source.

            :param str source: Required.
            :param int offset: Required.
            :param bytes selector: Required.
            :returns: Source.
            :rtype: uamqp.Source
            """
            source = Source(source)
            if offset is not None:
                source.set_filter(selector)
            return source

        @staticmethod
        def create_receive_client(
            *,
            config,
            source: Source,
            auth: authentication.JWTTokenAuth,
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
            :keyword ~uamqp.authentication.JWTTokenAuth auth: Required.
            :keyword int idle_timeout: Required.
            :keyword network_trace: Required.
            :keyword retry_policy: Required.
            :keyword str client_name: Required.
            :keyword dict link_properties: Required.
            :keyword dict[str, Any] or None properties: Required.
            :keyword link_credit: Required. The prefetch.
            :keyword keep_alive_interval: Required.
            :keyword list[bytes] or None desired_capabilities: Required.
            :keyword streaming_receive: Required.
            :keyword message_received_callback: Required.
            :keyword timeout: Required.

            :returns: The receive client.
            :rtype: uamqp.ReceiveClient
            """
            symbol_array = desired_capabilities
            desired_capabilities = None
            if symbol_array:
                symbol_array = [types.AMQPSymbol(symbol) for symbol in symbol_array]
                desired_capabilities = utils.data_factory(types.AMQPArray(symbol_array))

            client = ReceiveClient(
                source,
                debug=network_trace,
                error_policy=retry_policy,
                desired_capabilities=desired_capabilities,
                prefetch=link_credit,
                receive_settle_mode=constants.ReceiverSettleMode.ReceiveAndDelete,
                auto_complete=False,
                keep_alive_interval=keep_alive_interval,
                client_name=client_name,
                properties=properties,
                link_properties=link_properties,
                idle_timeout=idle_timeout,
                auth=auth,
                timeout=timeout,
                **kwargs,
            )
            # pylint:disable=protected-access
            client._streaming_receive = streaming_receive
            client._message_received_callback = message_received_callback
            return client

        @staticmethod
        def open_receive_client(*, handler, client, auth):
            """
            Opens the receive client and returns ready status.
            :keyword uamqp.ReceiveClient handler: The receive client.
            :keyword ~azure.eventhub.EventHubConsumerClient client: The consumer client.
            :keyword ~uamqp.authentication.JWTTokenAuth auth: Auth.
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
            if (
                isinstance(exception, errors.LinkDetach)
                and exception.condition == constants.ErrorCodes.LinkStolen
            ):
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

            :keyword bool update_token: Required. Whether to update token. If not updating token,
            then pass 300 to refresh_window.

            :returns: The JWTTokenAuth.
            :rtype: ~uamqp.authentication.JWTTokenAuth

            """
            refresh_window = 300
            if update_token:
                refresh_window = 0

            token_auth = authentication.JWTTokenAuth(
                auth_uri,
                auth_uri,
                get_token,
                token_type=token_type,
                timeout=config.auth_timeout,
                http_proxy=config.http_proxy,
                transport_type=config.transport_type,
                custom_endpoint_hostname=config.custom_endpoint_hostname,
                port=config.connection_port,
                verify=config.connection_verify,
                refresh_window=refresh_window,
            )
            if update_token:
                token_auth.update_token()
            return token_auth

        @staticmethod
        def create_mgmt_client(address, mgmt_auth, config):
            """
            Creates and returns the mgmt AMQP client.
            :param _Address address: Required. The Address.
            :param ~uamqp.authentication.JWTTokenAuth mgmt_auth: Auth for client.
            :param ~azure.eventhub._configuration.Configuration config: The configuration.
            :returns: The mgmt AMQP client.
            :rtype: uamqp.AMQPClient

            """

            mgmt_target = f"amqps://{address.hostname}{address.path}"
            return AMQPClient(mgmt_target, auth=mgmt_auth, debug=config.network_tracing)

        @staticmethod
        def open_mgmt_client(mgmt_client, conn):
            """
            Opens the mgmt AMQP client.
            :param uamqp.AMQPClient mgmt_client: uamqp AMQPClient.
            :param conn: Connection.
            :type conn: uamqp.Connection
            """
            mgmt_client.open(connection=conn)

        @staticmethod
        def get_updated_token(mgmt_auth):
            """
            Return updated auth token.
            :param mgmt_auth: Auth.
            :type mgmt_auth: ~uamqp.authentication.JWTTokenAuth
            :return: Updated auth token.
            :rtype: str
            """
            return mgmt_auth.token

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
            :param uamqp.AMQPClient mgmt_client: Client to send request with.
            :param str mgmt_msg: Message.
            :keyword bytes operation: Operation.
            :keyword bytes operation_type: Op type.
            :keyword bytes status_code_field: mgmt status code.
            :keyword bytes description_fields: mgmt status desc.
            :return: Status code, description, and response.
            :rtype: tuple[str, str, uamqp.Message]
            """
            response = mgmt_client.mgmt_request(
                mgmt_msg,
                operation,
                op_type=operation_type,
                status_code_field=status_code_field,
                description_fields=description_fields,
                **kwargs,
            )
            status_code = response.application_properties[status_code_field]
            description: Optional[Union[str, bytes]] = response.application_properties.get(description_fields)
            return status_code, description, response

        @staticmethod
        def get_error(status_code, description):
            """
            Gets error corresponding to status code.
            :param int status_code: Status code.
            :param str description: Description of error.
            :return: Error corresponding to status code.
            :rtype: uamqp.errors.AMQPConnectionError or
             uamqp.errors.AuthenticationException or ~azure.eventhub.exceptions.ConnectError
            """
            if status_code in [401]:
                return errors.AuthenticationException(
                    f"Management authentication failed. Status code: {status_code}, Description: {description!r}"
                )
            if status_code in [404]:
                return ConnectError(
                    f"Management connection failed. Status code: {status_code}, Description: {description!r}"
                )
            return errors.AMQPConnectionError(
                f"Management request error. Status code: {status_code}, Description: {description!r}"
            )

        @staticmethod
        def check_timeout_exception(base, exception):
            """
            Checks if timeout exception.
            :param ~azure.eventhub._client_base.ClientBase base: ClientBase.
            :param Exception exception: Exception to check.
            :return: Timeout exception.
            :rtype: Exception
            """
            if not base.running and isinstance(exception, compat.TimeoutException):
                exception = errors.AuthenticationException("Authorization timeout.")
            return exception

        @staticmethod
        def _create_eventhub_exception(exception):
            if isinstance(exception, errors.AuthenticationException):
                error = AuthenticationError(str(exception), exception)
            elif isinstance(exception, errors.VendorLinkDetach):
                error = ConnectError(str(exception), exception)
            elif isinstance(exception, errors.LinkDetach):
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.ConnectionClose):
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.MessageHandlerError):
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.AMQPConnectionError):
                error_type = (
                    AuthenticationError
                    if str(exception).startswith("Unable to open authentication session")
                    else ConnectError
                )
                error = error_type(str(exception), exception)
            elif isinstance(exception, compat.TimeoutException):
                error = ConnectionLostError(str(exception), exception)
            else:
                error = EventHubError(str(exception), exception)
            return error

        @staticmethod
        def _handle_exception(
            exception, closable, *, is_consumer=False  # pylint:disable=unused-argument
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
            elif isinstance(
                exception,
                (
                    errors.MessageAccepted,
                    errors.MessageAlreadySettled,
                    errors.MessageModified,
                    errors.MessageRejected,
                    errors.MessageReleased,
                    errors.MessageContentTooLarge,
                ),
            ):
                _LOGGER.info("%r Event data error (%r)", name, exception)
                error = EventDataError(str(exception), exception)
                raise error
            elif isinstance(exception, errors.MessageException):
                _LOGGER.info("%r Event data send error (%r)", name, exception)
                error = EventDataSendError(str(exception), exception)
                raise error
            else:
                if isinstance(exception, errors.AuthenticationException):
                    if hasattr(closable, "_close_connection"):
                        closable._close_connection()  # pylint:disable=protected-access
                elif isinstance(exception, errors.LinkDetach):
                    if hasattr(closable, "_close_handler"):
                        closable._close_handler()  # pylint:disable=protected-access
                elif isinstance(exception, errors.ConnectionClose):
                    if hasattr(closable, "_close_connection"):
                        closable._close_connection()  # pylint:disable=protected-access
                elif isinstance(exception, errors.MessageHandlerError):
                    if hasattr(closable, "_close_handler"):
                        closable._close_handler()  # pylint:disable=protected-access
                else:  # errors.AMQPConnectionError, compat.TimeoutException
                    if hasattr(closable, "_close_connection"):
                        closable._close_connection()  # pylint:disable=protected-access
                return UamqpTransport._create_eventhub_exception(exception)
