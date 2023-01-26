# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import time
from typing import Optional, Union, Any, Tuple, cast

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
from .._pyamqp._connection import Connection, _CLOSING_STATES

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
    OperationTimeoutError
)

_LOGGER = logging.getLogger(__name__)


class PyamqpTransport(AmqpTransport):   # pylint: disable=too-many-public-methods
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """

    # define constants
    MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
    MAX_MESSAGE_LENGTH_BYTES = (
        constants.MAX_FRAME_SIZE_BYTES
    )  # TODO: define actual value in pyamqp
    TIMEOUT_FACTOR = 1
    CONNECTION_CLOSING_STATES: Tuple = _CLOSING_STATES
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
        Creates a pyamqp.Message with given arguments.
        :rtype: pyamqp.Message
        """
        return Message(**kwargs)

    @staticmethod
    def build_batch_message(**kwargs):
        """
        Creates a pyamqp.BatchMessage with given arguments.
        :rtype: pyamqp.BatchMessage
        """
        return BatchMessage(**kwargs)

    @staticmethod
    def to_outgoing_amqp_message(annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: pyamqp.Message
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
        :param pyamqp.Message message: Message.
        :param str key: Key to set in application properties.
        :param str Value: Value to set for key in application properties.
        :rtype: pyamqp.Message
        """
        if not message.application_properties:
            message = message._replace(application_properties={})
        message.application_properties.setdefault(key, value)
        return message

    @staticmethod
    def get_batch_message_encoded_size(message):
        """
        Gets the batch message encoded size given an underlying Message.
        :param pyamqp.BatchMessage message: Message to get encoded size of.
        :rtype: int
        """
        return utils.get_message_encoded_size(message)

    @staticmethod
    def get_message_encoded_size(message):
        """
        Gets the message encoded size given an underlying Message.
        :param pyamqp.Message: Message to get encoded size of.
        :rtype: int
        """
        return utils.get_message_encoded_size(message)

    @staticmethod
    def get_remote_max_message_size(handler):
        """
        Returns max peer message size.
        :param AMQPClient handler: Client to get remote max message size on link from.
        :rtype: int
        """
        return handler._link.remote_max_message_size  # pylint: disable=protected-access

    @staticmethod
    def create_retry_policy(config):
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

    @staticmethod
    def create_link_properties(link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """
        return {
            symbol: utils.amqp_long_value(value)
            for (symbol, value) in link_properties.items()
        }

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
        endpoint = kwargs.pop("endpoint")
        host = kwargs.pop("host")  # pylint:disable=unused-variable
        auth = kwargs.pop("auth")  # pylint:disable=unused-variable
        network_trace = kwargs.pop("debug")
        return Connection(endpoint, network_trace=network_trace, **kwargs)

    @staticmethod
    def close_connection(connection):
        """
        Closes existing connection.
        :param connection: uamqp or pyamqp Connection.
        """
        connection.close()

    @staticmethod
    def get_connection_state(connection):
        """
        Gets connection state.
        :param connection: uamqp or pyamqp Connection.
        """
        return connection.state

    @staticmethod
    def create_send_client(*, config, **kwargs):  # pylint:disable=unused-argument
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
        # TODO: not used by pyamqp?
        msg_timeout = kwargs.pop(  # pylint: disable=unused-variable
            "msg_timeout"
        )

        return SendClient(
            config.hostname,
            target,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            **kwargs,
        )

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
        try:
            producer._open()
            timeout = timeout_time - time.time() if timeout_time else 0
            producer._handler.send_message(
                producer._unsent_events[0], timeout=timeout
            )
            # TODO: The unsent_events list will always be <= 1. Even for a batch,
            # it gets the underlying singular BatchMessage.
            # May want to refactor in the future so that this isn't a list.
            producer._unsent_events = None
        except TimeoutError as exc:
            raise OperationTimeoutError(message=str(exc), details=exc)

    @staticmethod
    def set_message_partition_key(message, partition_key, **kwargs):
        # type: (Message, Optional[Union[bytes, str]], Any) -> Message
        """Set the partition key as an annotation on a uamqp message.
        :param Message message: The message to update.
        :param str partition_key: The partition key value.
        :rtype: Message
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
            annotations[
                PROP_PARTITION_KEY
            ] = partition_key  # pylint:disable=protected-access
            header = Header(durable=True)  # type: ignore
            return message._replace(message_annotations=annotations, header=header)
        return message

    @staticmethod
    def add_batch(
        event_data_batch, outgoing_event_data, event_data
    ):  # pylint: disable=unused-argument
        """
        Add EventData to the data body of the BatchMessage.
        :param event_data_batch: EventDataBatch to add data to.
        :param outgoing_event_data: Transformed EventData for sending.
        :param event_data: EventData to add to internal batch events. uamqp use only.
        :rtype: None
        """
        event_data_batch._internal_events.append(  # pylint: disable=protected-access
            event_data
        )
        # pylint: disable=protected-access
        utils.add_batch(
            event_data_batch._message, outgoing_event_data._message
        )

    @staticmethod
    def create_source(source, offset, selector):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int offset: Required.
        :param bytes selector: Required.
        """
        source = Source(address=source, filters={})
        if offset is not None:
            filter_key = ApacheFilters.selector_filter
            source.filters[filter_key] = (filter_key, utils.amqp_string_value(selector))
        return source

    @staticmethod
    def create_receive_client(*, config, **kwargs):
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
            receive_settle_mode=constants.ReceiverSettleMode.First,
            http_proxy=config.http_proxy,
            transport_type=config.transport_type,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            **kwargs,
        )

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
        handler.open(
            connection=client._conn_manager.get_connection(
                client._address.hostname, auth
            )
        )

    @staticmethod
    def check_link_stolen(consumer, exception):
        """
        Checks if link stolen and handles exception.
        :param consumer: The EventHubConsumer.
        :param exception: Exception to check.
        """

        if (
            isinstance(exception, errors.AMQPLinkError)
            and exception.condition == errors.ErrorCondition.LinkStolen
        ):
            raise consumer._handle_exception(  # pylint: disable=protected-access
                exception
            )

    @staticmethod
    def create_token_auth(auth_uri, get_token, token_type, config, **kwargs):
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
        update_token = kwargs.pop("update_token")  # pylint: disable=unused-variable
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
            verify=config.connection_verify,
        )
        # if update_token:
        #    token_auth.update_token()  # TODO: why don't we need to update in pyamqp?

    @staticmethod
    def create_mgmt_client(
        address, mgmt_auth, config
    ):  # pylint: disable=unused-argument
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
            connection_verify=config.connection_verify,
        )

    @staticmethod
    def get_updated_token(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """
        return mgmt_auth.get_token().token

    @staticmethod
    def mgmt_client_request(mgmt_client, mgmt_msg, **kwargs):
        """
        Send mgmt request.
        :param AMQPClient mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword operation_type: Op type.
        :keyword status_code_field: mgmt status code.
        :keyword description_fields: mgmt status desc.
        """
        operation_type = kwargs.pop("operation_type")
        operation = kwargs.pop("operation")
        return mgmt_client.mgmt_request(
            mgmt_msg,
            operation=operation.decode(),
            operation_type=operation_type.decode(),
            **kwargs,
        )

    @staticmethod
    def get_error(status_code, description):
        """
        Gets error and passes in error message, and, if applicable, condition.
        :param error: The error to raise.
        :param str message: Error message.
        :param condition: Optional error condition. Will not be used by uamqp.
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
        :param base: ClientBase.
        :param exception: Exception to check.
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
            return PyamqpTransport._create_eventhub_exception(exception, is_consumer=is_consumer)
