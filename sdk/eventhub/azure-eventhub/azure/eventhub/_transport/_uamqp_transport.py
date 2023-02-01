# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import logging
from typing import Optional, Union, Any, Tuple

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
        :rtype: ~uamqp.errors.ErrorAction
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


    class UamqpTransport(AmqpTransport):    # pylint: disable=too-many-public-methods
        """
        Class which defines uamqp-based methods used by the producer and consumer.
        """
        # define constants
        MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
        MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES
        TIMEOUT_FACTOR = 1000
        CONNECTION_CLOSING_STATES: Tuple = (  # pylint:disable=protected-access
                c_uamqp.ConnectionState.CLOSE_RCVD,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.CLOSE_SENT,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.DISCARDING,  # pylint:disable=c-extension-no-member
                c_uamqp.ConnectionState.END,  # pylint:disable=c-extension-no-member
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
            :rtype: uamqp.Message
            """
            return Message(**kwargs)

        @staticmethod
        def build_batch_message(**kwargs):
            """
            Creates a uamqp.BatchMessage with given arguments.
            :rtype: uamqp.BatchMessage
            """
            return BatchMessage(**kwargs)

        @staticmethod
        def to_outgoing_amqp_message(annotated_message):
            """
            Converts an AmqpAnnotatedMessage into an Amqp Message.
            :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
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
                    creation_time=int(annotated_message.properties.creation_time)
                        if annotated_message.properties.creation_time else None,
                    absolute_expiry_time=int(annotated_message.properties.absolute_expiry_time)
                    if annotated_message.properties.absolute_expiry_time else None,
                    group_id=annotated_message.properties.group_id,
                    group_sequence=annotated_message.properties.group_sequence,
                    reply_to_group_id=annotated_message.properties.reply_to_group_id,
                    encoding=annotated_message._encoding    # pylint: disable=protected-access
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
                footer=annotated_message.footer
            )

        @staticmethod
        def update_message_app_properties(message, key, value):
            """
            Adds the given key/value to the application properties of the message.
            :param pyamqp.Message message: Message.
            :param str key: Key to set in application properties.
            :param str Value: Value to set for key in application properties.
            :rtype: pyamqp.Message
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
            :rtype: int
            """
            return message.gather()[0].get_message_encoded_size()

        @staticmethod
        def get_message_encoded_size(message):
            """
            Gets the message encoded size given an underlying Message.
            :param uamqp.Message message: Message to get encoded size of.
            :rtype: int
            """
            return message.get_message_encoded_size()

        @staticmethod
        def get_remote_max_message_size(handler):
            """
            Returns max peer message size.
            :param AMQPClient handler: Client to get remote max message size on link from.
            :rtype: int
            """
            return handler.message_handler._link.peer_max_message_size  # pylint:disable=protected-access

        @staticmethod
        def create_retry_policy(config):
            """
            Creates the error retry policy.
            :param ~azure.eventhub._configuration.Configuration config: Configuration.
            """
            return errors.ErrorPolicy(max_retries=config.max_retries, on_error=_error_handler)

        @staticmethod
        def create_link_properties(link_properties):
            """
            Creates and returns the link properties.
            :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
            :rtype: dict
            """
            return {types.AMQPSymbol(symbol): types.AMQPLong(value) for (symbol, value) in link_properties.items()}

        @staticmethod
        def create_connection(**kwargs):
            """
            Creates and returns the uamqp Connection object.
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
            endpoint = kwargs.pop("endpoint") # pylint:disable=unused-variable
            custom_endpoint_address = kwargs.pop("custom_endpoint_address") # pylint:disable=unused-variable
            host = kwargs.pop("host")
            auth = kwargs.pop("auth")
            return Connection(
                host,
                auth,
                **kwargs
            )

        @staticmethod
        def close_connection(connection):
            """
            Closes existing connection.
            :param connection: uamqp or pyamqp Connection.
            """
            connection.destroy()

        @staticmethod
        def get_connection_state(connection):
            """
            Gets connection state.
            :param connection: uamqp or pyamqp Connection.
            """
            return connection._state    # pylint:disable=protected-access

        @staticmethod
        def create_send_client(*, config, **kwargs): # pylint:disable=unused-argument
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
                debug=network_trace,
                error_policy=retry_policy,
                **kwargs
            )

        @staticmethod
        def _set_msg_timeout(producer, timeout_time, last_exception, logger):
            if not timeout_time:
                return
            remaining_time = timeout_time - time.time()
            if remaining_time <= 0.0:
                if last_exception:
                    error = last_exception
                else:
                    error = OperationTimeoutError("Send operation timed out")
                logger.info("%r send operation timed out. (%r)", producer._name, error) # pylint: disable=protected-access
                raise error
            producer._handler._msg_timeout = remaining_time * 1000  # type: ignore  # pylint: disable=protected-access

        @staticmethod
        def send_messages(producer, timeout_time, last_exception, logger):
            """
            Handles sending of event data messages.
            :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
            :param int timeout_time: Timeout time.
            :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
            :param logger: Logger.
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
        def set_message_partition_key(message, partition_key, **kwargs):  # pylint:disable=unused-argument
            # type: (Message, Optional[Union[bytes, str]], Any) -> Message
            """Set the partition key as an annotation on a uamqp message.

            :param ~uamqp.Message message: The message to update.
            :param str partition_key: The partition key value.
            :rtype: Message
            """
            if partition_key:
                annotations = message.annotations
                if annotations is None:
                    annotations = {}
                annotations[
                    UamqpTransport.PROP_PARTITION_KEY_AMQP_SYMBOL   # TODO: see if setting non-amqp symbol is valid
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
            :param event_data_batch: BatchMessage to add data to.
            :param outgoing_event_data: Transformed EventData for sending.
            :param event_data: EventData to add to internal batch events. uamqp use only.
            :rtype: None
            """
            # pylint: disable=protected-access
            event_data_batch._internal_events.append(event_data)
            event_data_batch._message._body_gen.append(
                outgoing_event_data._message
            )

        @staticmethod
        def create_source(source, offset, selector):
            """
            Creates and returns the Source.

            :param str source: Required.
            :param int offset: Required.
            :param bytes selector: Required.
            """
            source = Source(source)
            if offset is not None:
                source.set_filter(selector)
            return source

        @staticmethod
        def create_receive_client(*, config, **kwargs): # pylint: disable=unused-argument
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
            :keyword keep_alive_interval: Required.
            :keyword desired_capabilities: Required.
            :keyword streaming_receive: Required.
            :keyword message_received_callback: Required.
            :keyword timeout: Required.
            """

            source = kwargs.pop("source")
            symbol_array = kwargs.pop("desired_capabilities")
            desired_capabilities = None
            if symbol_array:
                symbol_array = [types.AMQPSymbol(symbol) for symbol in symbol_array]
                desired_capabilities = utils.data_factory(types.AMQPArray(symbol_array))
            retry_policy = kwargs.pop("retry_policy")
            network_trace = kwargs.pop("network_trace")
            link_credit = kwargs.pop("link_credit")
            streaming_receive = kwargs.pop("streaming_receive")
            message_received_callback = kwargs.pop("message_received_callback")

            client = ReceiveClient(
                source,
                debug=network_trace,  # pylint:disable=protected-access
                error_policy=retry_policy,
                desired_capabilities=desired_capabilities,
                prefetch=link_credit,
                receive_settle_mode=constants.ReceiverSettleMode.ReceiveAndDelete,
                auto_complete=False,
                **kwargs
            )
            # pylint:disable=protected-access
            client._streaming_receive = streaming_receive
            client._message_received_callback = (message_received_callback)
            return client

        @staticmethod
        def open_receive_client(*, handler, client, auth):
            """
            Opens the receive client and returns ready status.
            :param ReceiveClient handler: The receive client.
            :param ~azure.eventhub.EventHubConsumerClient client: The consumer client.
            :param auth: Auth.
            :rtype: bool
            """
            # pylint:disable=protected-access
            handler.open(connection=client._conn_manager.get_connection(
                client._address.hostname, auth
            ))

        @staticmethod
        def check_link_stolen(consumer, exception):
            """
            Checks if link stolen and handles exception.
            :param consumer: The EventHubConsumer.
            :param exception: Exception to check.
            """
            if (
                isinstance(exception, errors.LinkDetach)
                and exception.condition == constants.ErrorCodes.LinkStolen  # pylint: disable=no-member
            ):
                raise consumer._handle_exception(exception)  # pylint: disable=protected-access

        @staticmethod
        def create_token_auth(auth_uri, get_token, token_type, config, **kwargs):
            """
            Creates the JWTTokenAuth.
            :param str auth_uri: The auth uri to pass to JWTTokenAuth.
            :param get_token: The callback function used for getting and refreshing
            tokens. It should return a valid jwt token each time it is called.
            :param bytes token_type: Token type.
            :param ~azure.eventhub._configuration.Configuration config: EH config.

            :keyword bool update_token: Required. Whether to update token. If not updating token,
            then pass 300 to refresh_window.
            """
            update_token = kwargs.pop("update_token")
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
                refresh_window=refresh_window
            )
            if update_token:
                token_auth.update_token()
            return token_auth

        @staticmethod
        def create_mgmt_client(address, mgmt_auth, config):
            """
            Creates and returns the mgmt AMQP client.
            :param _Address address: Required. The Address.
            :param JWTTokenAuth mgmt_auth: Auth for client.
            :param ~azure.eventhub._configuration.Configuration config: The configuration.
            """

            mgmt_target = f"amqps://{address.hostname}{address.path}"
            return AMQPClient(
                mgmt_target,
                auth=mgmt_auth,
                debug=config.network_tracing
            )

        @staticmethod
        def open_mgmt_client(mgmt_client, conn):
            """
            Opens the mgmt AMQP client.
            :param AMQPClient mgmt_client: uamqp AMQPClient.
            :param conn: Connection.
            """
            mgmt_client.open(connection=conn)

        @staticmethod
        def get_updated_token(mgmt_auth):
            """
            Return updated auth token.
            :param mgmt_auth: Auth.
            """
            return mgmt_auth.token

        @staticmethod
        def mgmt_client_request(mgmt_client, mgmt_msg, **kwargs):
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
            response = mgmt_client.mgmt_request(
                mgmt_msg,
                operation,
                op_type=operation_type,
                **kwargs
            )
            status_code = response.application_properties[kwargs.get("status_code_field")]
            description = response.application_properties.get(
                kwargs.get("description_fields")
            )  # type: Optional[Union[str, bytes]]
            return status_code, description, response

        @staticmethod
        def get_error(status_code, description):
            """
            Gets error corresponding to status code.
            :param status_code: Status code.
            :param str description: Description of error.
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
            :param base: ClientBase.
            :param exception: Exception to check.
            """
            if not base.running and isinstance(
                exception, compat.TimeoutException
            ):
                exception = errors.AuthenticationException(
                    "Authorization timeout."
                )
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
            exception, closable, *, is_consumer=False   # pylint:disable=unused-argument
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
