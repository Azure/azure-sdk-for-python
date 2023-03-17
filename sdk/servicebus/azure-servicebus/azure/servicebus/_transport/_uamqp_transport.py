# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import logging
import functools
import datetime
from typing import Optional, Tuple, Callable, TYPE_CHECKING

from azure.core.serialization import TZ_UTC
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
        authentication,
        compat,
        Connection,
        __version__,
    )
    from uamqp.constants import ErrorCodes as AMQPErrorCodes
    from uamqp.message import (
        MessageHeader,
        MessageProperties,
    )
    from uamqp.errors import (
        AMQPConnectionError,
        AMQPError,
        AuthenticationException,
        ErrorAction,
        ErrorPolicy,
        MessageAlreadySettled,
        MessageContentTooLarge,
        MessageException,
    )
    uamqp_installed = True
except ImportError:
    uamqp_installed = False

from ._base import AmqpTransport
from ..amqp._constants import AmqpMessageBodyType
from .._common.utils import (
    utc_from_timestamp,
    utc_now,
    get_receive_links,
    receive_trace_context_manager
)
from .._common.constants import (
    UAMQP_LIBRARY,
    DATETIMEOFFSET_EPOCH,
    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    DEADLETTERNAME,
    MAX_ABSOLUTE_EXPIRY_TIME,
    MAX_DURATION_VALUE,
    MESSAGE_COMPLETE,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_DEAD_LETTER,
    SESSION_FILTER,
    SESSION_LOCKED_UNTIL,
    ERROR_CODE_SESSION_LOCK_LOST,
    ERROR_CODE_MESSAGE_LOCK_LOST,
    ERROR_CODE_MESSAGE_NOT_FOUND,
    ERROR_CODE_TIMEOUT,
    ERROR_CODE_AUTH_FAILED,
    ERROR_CODE_SESSION_CANNOT_BE_LOCKED,
    ERROR_CODE_SERVER_BUSY,
    ERROR_CODE_ARGUMENT_ERROR,
    ERROR_CODE_OUT_OF_RANGE,
    ERROR_CODE_ENTITY_DISABLED,
    ERROR_CODE_ENTITY_ALREADY_EXISTS,
    ERROR_CODE_PRECONDITION_FAILED,
    ServiceBusReceiveMode,
)

from ..exceptions import (
    MessageSizeExceededError,
    ServiceBusQuotaExceededError,
    ServiceBusAuthorizationError,
    ServiceBusError,
    ServiceBusConnectionError,
    ServiceBusCommunicationError,
    MessageAlreadySettled,
    MessageLockLostError,
    MessageNotFoundError,
    MessagingEntityDisabledError,
    MessagingEntityNotFoundError,
    MessagingEntityAlreadyExistsError,
    ServiceBusServerBusyError,
    ServiceBusAuthenticationError,
    SessionCannotBeLockedError,
    SessionLockLostError,
    OperationTimeoutError
)
if TYPE_CHECKING:
    from .._servicebus_receiver import ServiceBusReceiver
    from .._common.message import ServiceBusReceivedMessage

_LOGGER = logging.getLogger(__name__)

if uamqp_installed:
    _NO_RETRY_CONDITION_ERROR_CODES = (
        constants.ErrorCodes.DecodeError,
        constants.ErrorCodes.LinkMessageSizeExceeded,
        constants.ErrorCodes.NotFound,
        constants.ErrorCodes.NotImplemented,
        constants.ErrorCodes.LinkRedirect,
        constants.ErrorCodes.NotAllowed,
        constants.ErrorCodes.UnauthorizedAccess,
        constants.ErrorCodes.LinkStolen,
        constants.ErrorCodes.ResourceLimitExceeded,
        constants.ErrorCodes.ConnectionRedirect,
        constants.ErrorCodes.PreconditionFailed,
        constants.ErrorCodes.InvalidField,
        constants.ErrorCodes.ResourceDeleted,
        constants.ErrorCodes.IllegalState,
        constants.ErrorCodes.FrameSizeTooSmall,
        constants.ErrorCodes.ConnectionFramingError,
        constants.ErrorCodes.SessionUnattachedHandle,
        constants.ErrorCodes.SessionHandleInUse,
        constants.ErrorCodes.SessionErrantLink,
        constants.ErrorCodes.SessionWindowViolation,
        ERROR_CODE_SESSION_LOCK_LOST,
        ERROR_CODE_MESSAGE_LOCK_LOST,
        ERROR_CODE_OUT_OF_RANGE,
        ERROR_CODE_ARGUMENT_ERROR,
        ERROR_CODE_PRECONDITION_FAILED,
    )

    _ERROR_CODE_TO_ERROR_MAPPING = {
        constants.ErrorCodes.LinkMessageSizeExceeded: MessageSizeExceededError,
        constants.ErrorCodes.ResourceLimitExceeded: ServiceBusQuotaExceededError,
        constants.ErrorCodes.UnauthorizedAccess: ServiceBusAuthorizationError,
        constants.ErrorCodes.NotImplemented: ServiceBusError,
        constants.ErrorCodes.NotAllowed: ServiceBusError,
        constants.ErrorCodes.LinkDetachForced: ServiceBusConnectionError,
        ERROR_CODE_MESSAGE_LOCK_LOST: MessageLockLostError,
        ERROR_CODE_MESSAGE_NOT_FOUND: MessageNotFoundError,
        ERROR_CODE_AUTH_FAILED: ServiceBusAuthorizationError,
        ERROR_CODE_ENTITY_DISABLED: MessagingEntityDisabledError,
        ERROR_CODE_ENTITY_ALREADY_EXISTS: MessagingEntityAlreadyExistsError,
        ERROR_CODE_SERVER_BUSY: ServiceBusServerBusyError,
        ERROR_CODE_SESSION_CANNOT_BE_LOCKED: SessionCannotBeLockedError,
        ERROR_CODE_SESSION_LOCK_LOST: SessionLockLostError,
        ERROR_CODE_ARGUMENT_ERROR: ServiceBusError,
        ERROR_CODE_OUT_OF_RANGE: ServiceBusError,
        ERROR_CODE_TIMEOUT: OperationTimeoutError,
    }

    def _error_handler(error):
        """Handle connection and service errors.

        Called internally when an event has failed to send so we
        can parse the error to determine whether we should attempt
        to retry sending the event again.
        Returns the action to take according to error type.

        :param error: The error received in the send attempt.
        :type error: Exception
        :rtype: ~uamqp.errors.ErrorAction
        """
        if error.condition == b"com.microsoft:server-busy":
            return ErrorAction(retry=True, backoff=4)
        if error.condition == b"com.microsoft:timeout":
            return ErrorAction(retry=True, backoff=2)
        if error.condition == b"com.microsoft:operation-cancelled":
            return ErrorAction(retry=True)
        if error.condition == b"com.microsoft:container-close":
            return ErrorAction(retry=True, backoff=4)
        if error.condition in _NO_RETRY_CONDITION_ERROR_CODES:
            return ErrorAction(retry=False)
        return ErrorAction(retry=True)


    class _ServiceBusErrorPolicy(ErrorPolicy):
        def __init__(self, max_retries=3, is_session=False):
            self._is_session = is_session
            super(_ServiceBusErrorPolicy, self).__init__(
                max_retries=max_retries, on_error=_error_handler
            )

        def on_unrecognized_error(self, error):
            if self._is_session:
                return ErrorAction(retry=False)
            return super(_ServiceBusErrorPolicy, self).on_unrecognized_error(error)

        def on_link_error(self, error):
            if self._is_session:
                return ErrorAction(retry=False)
            return super(_ServiceBusErrorPolicy, self).on_link_error(error)

        def on_connection_error(self, error):
            if self._is_session:
                return ErrorAction(retry=False)
            return super(_ServiceBusErrorPolicy, self).on_connection_error(error)


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

        # To enable extensible string enums for the public facing parameter
        # and translate to the "real" uamqp constants.
        ServiceBusToAMQPReceiveModeMap = {
            ServiceBusReceiveMode.PEEK_LOCK: constants.ReceiverSettleMode.PeekLock,
            ServiceBusReceiveMode.RECEIVE_AND_DELETE: constants.ReceiverSettleMode.ReceiveAndDelete,
        }

        # define symbols
        PRODUCT_SYMBOL = types.AMQPSymbol("product")
        VERSION_SYMBOL = types.AMQPSymbol("version")
        FRAMEWORK_SYMBOL = types.AMQPSymbol("framework")
        PLATFORM_SYMBOL = types.AMQPSymbol("platform")
        USER_AGENT_SYMBOL = types.AMQPSymbol("user-agent")

        # amqp value types
        AMQP_LONG_VALUE = types.AMQPLong
        AMQP_ARRAY_VALUE = types.AMQPArray
        AMQP_UINT_VALUE = types.AMQPuInt

        # errors
        TIMEOUT_ERROR = compat.TimeoutException

        @staticmethod
        def build_message(**kwargs):
            """
            Creates a uamqp.Message with given arguments.
            :rtype: uamqp.Message
            """
            return Message(**kwargs)

        @staticmethod
        def build_batch_message(data):
            """
            Creates a uamqp.BatchMessage with given arguments.
            :rtype: uamqp.BatchMessage
            """
            return BatchMessage(data=data)

        @staticmethod
        def get_message_delivery_tag(message, _):  # pylint: disable=unused-argument
            """
            Gets delivery tag of a Message.
            :param message: Message to get delivery_tag from for uamqp.Message.
            :param frame: Message to get delivery_tag from for pyamqp.Message.
            :rtype: str
            """
            return message.delivery_tag

        @staticmethod
        def get_message_delivery_id(message, _):  # pylint: disable=unused-argument
            """
            Gets delivery id of a Message.
            :param message: Message to get delivery_id from for uamqp.Message.
            :param frame: Message to get delivery_id from for pyamqp.Message.
            :rtype: str
            """
            return message.delivery_no

        @staticmethod
        def to_outgoing_amqp_message(annotated_message):
            """
            Converts an AmqpAnnotatedMessage into an Amqp Message.
            :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
            :rtype: uamqp.Message
            """
            message_header = None
            ttl_set = False
            header_vals = annotated_message.header.values() if annotated_message.header else None
            # If header and non-None header values, create outgoing header.
            if annotated_message.header and header_vals.count(None) != len(header_vals):
                message_header = MessageHeader()
                message_header.delivery_count = annotated_message.header.delivery_count
                message_header.time_to_live = annotated_message.header.time_to_live
                message_header.first_acquirer = annotated_message.header.first_acquirer
                message_header.durable = annotated_message.header.durable
                message_header.priority = annotated_message.header.priority
                if annotated_message.header.time_to_live and annotated_message.header.time_to_live != MAX_DURATION_VALUE:
                    ttl_set = True
                    creation_time_from_ttl = int(time.mktime(
                        datetime.datetime.now(TZ_UTC).timetuple()) * UamqpTransport.TIMEOUT_FACTOR
                    )
                    absolute_expiry_time_from_ttl = int(min(
                        MAX_ABSOLUTE_EXPIRY_TIME,
                        creation_time_from_ttl + annotated_message.header.time_to_live
                    ))

            message_properties = None
            properties_vals = annotated_message.properties.values() if annotated_message.properties else None
            # If properties and non-None properties values, create outgoing properties.
            if annotated_message.properties and properties_vals.count(None) != len(properties_vals):
                creation_time = None
                absolute_expiry_time = None
                if ttl_set:
                    creation_time = creation_time_from_ttl
                    absolute_expiry_time = absolute_expiry_time_from_ttl
                else:
                    if annotated_message.properties.creation_time:
                        creation_time = int(annotated_message.properties.creation_time)
                    if annotated_message.properties.absolute_expiry_time:
                        absolute_expiry_time = int(annotated_message.properties.absolute_expiry_time)

                message_properties = MessageProperties(
                    message_id=annotated_message.properties.message_id,
                    user_id=annotated_message.properties.user_id,
                    to=annotated_message.properties.to,
                    subject=annotated_message.properties.subject,
                    reply_to=annotated_message.properties.reply_to,
                    correlation_id=annotated_message.properties.correlation_id,
                    content_type=annotated_message.properties.content_type,
                    content_encoding=annotated_message.properties.content_encoding,
                    creation_time=creation_time,
                    absolute_expiry_time=absolute_expiry_time,
                    group_id=annotated_message.properties.group_id,
                    group_sequence=annotated_message.properties.group_sequence,
                    reply_to_group_id=annotated_message.properties.reply_to_group_id,
                    encoding=annotated_message._encoding    # pylint: disable=protected-access
                )
            elif ttl_set:
                message_properties = MessageProperties(
                    creation_time=creation_time_from_ttl if ttl_set else None,
                    absolute_expiry_time=absolute_expiry_time_from_ttl if ttl_set else None,
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
        def encode_message(message):
            """
            Encodes the outgoing uamqp.Message of the message.
            :param ServiceBusMessage message: Message.
            :rtype: bytes
            """
            return message._message.encode_message()

        @staticmethod
        def update_message_app_properties(message, key, value):
            """
            Adds the given key/value to the application properties of the message.
            :param uamqp.Message message: Message.
            :param str key: Key to set in application properties.
            :param str Value: Value to set for key in application properties.
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
        def get_handler_link_name(handler):
            """
            Returns link name.
            :param AMQPClient handler: Client to get name of link from.
            :rtype: str
            """
            return handler.message_handler.name

        @staticmethod
        def create_retry_policy(config, *, is_session=False):
            """
            Creates the error retry policy.
            :param ~azure.eventhub._configuration.Configuration config: Configuration.
            :keyword bool is_session: Is session enabled.
            """
            # TODO: What's the retry overlap between servicebus and pyamqp?
            return _ServiceBusErrorPolicy(max_retries=config.retry_total, is_session=is_session)

        @staticmethod
        def create_link_properties(link_properties):
            """
            Creates and returns the link properties.
            :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
            :rtype: dict
            """
            return {types.AMQPSymbol(symbol): types.AMQPLong(value) for (symbol, value) in link_properties.items()}

        @staticmethod
        def create_connection(host, auth, network_trace, **kwargs):
            """
            Creates and returns the uamqp Connection object.
            :param str host: The hostname, used by uamqp.
            :param JWTTokenAuth auth: The auth, used by uamqp.
            :param bool network_trace: Required.
            """
            custom_endpoint_address = kwargs.pop("custom_endpoint_address") # pylint:disable=unused-variable
            ssl_opts = kwargs.pop("ssl_opts") # pylint:disable=unused-variable
            transport_type = kwargs.pop("transport_type") # pylint:disable=unused-variable
            http_proxy = kwargs.pop("http_proxy") # pylint:disable=unused-variable
            return Connection(
                hostname=host,
                sasl=auth,
                debug=network_trace,
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
        def create_send_client(config, **kwargs):
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

            return SendClient(
                target,
                debug=config.logging_enable,
                error_policy=retry_policy,
                keep_alive_interval=config.keep_alive,
                encoding=config.encoding,
                **kwargs
            )

        @staticmethod
        def set_msg_timeout(sender, logger, timeout, last_exception):
            # pylint: disable=protected-access
            if not timeout:
                sender._handler._msg_timeout = 0
                return
            if timeout <= 0.0:
                if last_exception:
                    error = last_exception
                else:
                    error = OperationTimeoutError(message="Send operation timed out")
                logger.info("%r send operation timed out. (%r)", sender._name, error)
                raise error
            sender._handler._msg_timeout = timeout * UamqpTransport.TIMEOUT_FACTOR # type: ignore

        @staticmethod
        def send_messages(sender, message, logger, timeout, last_exception):
            """
            Handles sending of service bus messages.
            :param ~azure.servicebus._servicebus_sender.ServiceBusSender sender: The sender with handler
             to send messages.
            :param message: ServiceBusMessage with uamqp.Message to be sent.
            :paramtype message: ~azure.servicebus.ServiceBusMessage or ~azure.servicebus.ServiceBusMessageBatch
            :param int timeout: Timeout time.
            :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
            :param logger: Logger.
            """
            # pylint: disable=protected-access
            sender._open()
            default_timeout = sender._handler._msg_timeout
            try:
                UamqpTransport.set_msg_timeout(sender, logger, timeout, last_exception)
                sender._handler.send_message(message._message)
            finally:
                UamqpTransport.set_msg_timeout(sender, logger, default_timeout, None)

        @staticmethod
        def add_batch(
            sb_message_batch, outgoing_sb_message
        ):  # pylint: disable=unused-argument
            """
            Add EventData to the data body of the BatchMessage.
            :param event_data_batch: EventDataBatch to add data to.
            :param outgoing_event_data: Transformed EventData for sending.
            :param event_data: EventData to add to internal batch events. uamqp use only.
            :rtype: None
            """
            # pylint: disable=protected-access
            sb_message_batch._message._body_gen.append(
                outgoing_sb_message._message
            )

        @staticmethod
        def create_source(source, session_filter):
            """
            Creates and returns the Source.

            :param str source: Required.
            :param int or None session_id: Required.
            """
            source = Source(source)
            source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
            return source

        @staticmethod
        def create_receive_client(receiver, **kwargs):
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
            :keyword timeout: Required.
            """
            source = kwargs.pop("source")
            retry_policy = kwargs.pop("retry_policy")
            network_trace = kwargs.pop("network_trace")
            link_credit = kwargs.pop("link_credit")
            receive_mode = kwargs.pop("receive_mode")

            return ReceiveClient(
                source,
                debug=network_trace,  # pylint:disable=protected-access
                error_policy=retry_policy,
                prefetch=link_credit,
                auto_complete=False,
                receive_settle_mode=UamqpTransport.ServiceBusToAMQPReceiveModeMap[receive_mode],
                send_settle_mode=constants.SenderSettleMode.Settled
                if receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
                else None,
                on_attach=functools.partial(
                    UamqpTransport.on_attach,
                    receiver
                ),
                **kwargs
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
            handler.open(connection=client._conn_manager.get_connection(
                client._address.hostname, auth
            ))

        @staticmethod
        def on_attach(receiver, source, target, properties, error): # pylint: disable=unused-argument
            """
            Receiver on_attach callback.
            """
            # pylint: disable=protected-access
            if receiver._session and str(source) == receiver._entity_uri:
                # This has to live on the session object so that autorenew has access to it.
                receiver._session._session_start = utc_now()
                expiry_in_seconds = properties.get(SESSION_LOCKED_UNTIL)
                if expiry_in_seconds:
                    expiry_in_seconds = (
                        expiry_in_seconds - DATETIMEOFFSET_EPOCH
                    ) / 10000000
                    receiver._session._locked_until_utc = utc_from_timestamp(expiry_in_seconds)
                session_filter = source.get_filter(name=SESSION_FILTER)
                receiver._session_id = session_filter.decode(receiver._config.encoding)
                receiver._session._session_id = receiver._session_id
        
        @staticmethod
        def iter_contextual_wrapper(receiver, max_wait_time=None):
            """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
            and per-iter argument passing that requires the former."""
            # pylint: disable=protected-access
            original_timeout = None
            while True:
                # This is not threadsafe, but gives us a way to handle if someone passes
                # different max_wait_times to different iterators and uses them in concert.
                if max_wait_time:
                    original_timeout = receiver._handler._timeout
                    receiver._handler._timeout = max_wait_time * UamqpTransport.TIMEOUT_FACTOR
                try:
                    message = receiver._inner_next()
                    links = get_receive_links(message)
                    with receive_trace_context_manager(receiver, links=links):
                        yield message
                except StopIteration:
                    break
                finally:
                    if original_timeout:
                        try:
                            receiver._handler._timeout = original_timeout
                        except AttributeError:  # Handler may be disposed already.
                            pass
        
        # wait_time used by pyamqp
        @staticmethod
        def iter_next(receiver, wait_time=None):    # pylint: disable=unused-argument
            try:
                receiver._receive_context.set()
                receiver._open()
                if not receiver._message_iter:
                    receiver._message_iter = receiver._handler.receive_messages_iter()
                uamqp_message = next(receiver._message_iter)
                message = receiver._build_received_message(uamqp_message)
                if (
                    receiver._auto_lock_renewer
                    and not receiver._session
                    and receiver._receive_mode != ServiceBusReceiveMode.RECEIVE_AND_DELETE
                ):
                    receiver._auto_lock_renewer.register(receiver, message)
                return message
            finally:
                receiver._receive_context.clear()

        @staticmethod
        def enhanced_message_received(reciever, message):
            """
            Receiver enhanced_message_received callback.
            """
            # pylint: disable=protected-access
            reciever._handler._was_message_received = True
            if reciever._receive_context.is_set():
                reciever._handler._received_messages.put(message)
            else:
                message.release()

        @staticmethod
        def build_received_message(
            receiver: "ServiceBusReceiver",
            message_type: "ServiceBusReceivedMessage",
            received: "Message"
        ):
            # pylint: disable=protected-access
            message = message_type(
                message=received, receive_mode=receiver._receive_mode, receiver=receiver
            )
            message._uamqp_message = received
            receiver._last_received_sequenced_number = message.sequence_number
            return message

        @staticmethod
        def get_receive_timeout(handler):
            """
            Gets the timeout on the ReceiveClient.
            :param ReceiveClient handler: Handler to set timeout on.
            :rtype: int
            """
            return handler._timeout    # pylint: disable=protected-access

        @staticmethod
        def set_receive_timeout(handler, max_wait_time):
            """
            Sets the timeout on the ReceiveClient and returns original timeout.
            :param ReceiveClient handler: Handler to set timeout on.
            :param int max_wait_time: Max wait time.
            :rtype: None
            """
            handler._timeout = max_wait_time    # pylint: disable=protected-access

        @staticmethod
        def get_current_time(handler):
            """
            Gets the current time.
            :param ReceiveClient handler: Handler with counter to get time.
            :rtype: int
            """
            return handler._counter.get_current_ms()    # pylint: disable=protected-access

        @staticmethod
        def reset_link_credit(handler, link_credit):
            """
            Resets the link credit on the link.
            :param ReceiveClient handler: Client with link to reset link credit.
            :param int link_credit: Link credit needed.
            :rtype: None
            """
            handler.message_handler.reset_link_credit(link_credit)

        # Executes message settlement, implementation is in _settle_message_via_receiver_link
        # May be able to remove and just call methods in private method.
        @staticmethod
        def settle_message_via_receiver_link(
            handler: ReceiveClient,
            message: "ServiceBusReceivedMessage",
            settle_operation: str,
            dead_letter_reason: Optional[str] = None,
            dead_letter_error_description: Optional[str] = None,
        ) -> None:  # pylint: disable=unused-argument
            UamqpTransport.settle_message_via_receiver_link_impl(
                handler,
                message,
                settle_operation,
                dead_letter_reason,
                dead_letter_error_description
            )()

        @staticmethod
        def settle_message_via_receiver_link_impl(
            _: ReceiveClient,
            message: "ServiceBusReceivedMessage",
            settle_operation: str,
            dead_letter_reason: Optional[str] = None,
            dead_letter_error_description: Optional[str] = None,
        ) -> Callable:  # pylint: disable=unused-argument
            # pylint: disable=protected-access
            if settle_operation == MESSAGE_COMPLETE:
                return functools.partial(message._message.accept)
            if settle_operation == MESSAGE_ABANDON:
                return functools.partial(message._message.modify, True, False)
            if settle_operation == MESSAGE_DEAD_LETTER:
                return functools.partial(
                    message._message.reject,
                    condition=DEADLETTERNAME,
                    description=dead_letter_error_description,
                    info={
                        RECEIVER_LINK_DEAD_LETTER_REASON: dead_letter_reason,
                        RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION: dead_letter_error_description,
                    },
                )
            if settle_operation == MESSAGE_DEFER:
                return functools.partial(message._message.modify, True, True)
            raise ValueError(
                f"Unsupported settle operation type: {settle_operation}"
            )

        @staticmethod
        def parse_received_message(message, message_type, **kwargs):
            """
            Parses peek/deferred op messages into ServiceBusReceivedMessage.
            :param Message message: Message to parse.
            :param ServiceBusReceivedMessage message_type: Message type to pass parsed message to.
            :keyword ServiceBusReceiver receiver: Required.
            :keyword bool is_peeked_message: Optional. For peeked messages.
            :keyword bool is_deferred_message: Optional. For deferred messages.
            :keyword ServiceBusReceiveMode receive_mode: Optional.
            """
            parsed = []
            for m in message.get_data()[b"messages"]:
                wrapped = Message.decode_from_bytes(bytearray(m[b"message"]))
                parsed.append(
                    message_type(
                        wrapped, **kwargs
                    )
                )
            return parsed

        @staticmethod
        def get_message_value(message):
            return message.get_data()

        #@staticmethod
        #def check_link_stolen(consumer, exception):
        #    """
        #    Checks if link stolen and handles exception.
        #    :param consumer: The EventHubConsumer.
        #    :param exception: Exception to check.
        #    """
        #    if (
        #        isinstance(exception, LinkDetach)
        #        and exception.condition == constants.ErrorCodes.LinkStolen  # pylint: disable=no-member
        #    ):
        #        raise consumer._handle_exception(exception)  # pylint: disable=protected-access

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
            refresh_window = 0 if update_token else 300

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

        #@staticmethod
        #def create_mgmt_client(address, mgmt_auth, config):
        #    """
        #    Creates and returns the mgmt AMQP client.
        #    :param _Address address: Required. The Address.
        #    :param JWTTokenAuth mgmt_auth: Auth for client.
        #    :param ~azure.eventhub._configuration.Configuration config: The configuration.
        #    """

        #    mgmt_target = f"amqps://{address.hostname}{address.path}"
        #    return AMQPClient(
        #        mgmt_target,
        #        auth=mgmt_auth,
        #        debug=config.network_tracing
        #    )

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
        def create_mgmt_msg(
            message,
            application_properties,
            config, # pylint:disable=unused-argument
            reply_to,
            **kwargs
        ):
            """
            :param message: The message to send in the management request.
            :paramtype message: Any
            :param Dict[bytes, str] application_properties: App props.
            :param ~azure.servicebus._common._configuration.Configuration config: Configuration.
            :param str reply_to: Reply to.
            :rtype: uamqp.Message
            """
            return Message( # type: ignore # TODO: fix mypy error
                body=message,
                properties=MessageProperties(
                    reply_to=reply_to,
                    encoding=config.encoding,
                    **kwargs
                ),
                application_properties=application_properties,
            )

        @staticmethod
        def mgmt_client_request(
            mgmt_client,
            mgmt_msg,
            *,
            operation,
            operation_type,
            node,
            timeout,
            callback
        ):
            """
            Send mgmt request.
            :param AMQPClient mgmt_client: Client to send request with.
            :param Message mgmt_msg: Message.
            :keyword bytes operation: Operation.
            :keyword bytes operation_type: Op type.
            :keyword bytes node: Mgmt target.
            :keyword int timeout: Timeout.
            :keyword Callable callback: Callback to process request response.
            """
            return mgmt_client.mgmt_request(
                mgmt_msg,
                operation,
                op_type=operation_type,
                node=node,
                timeout=timeout * UamqpTransport.TIMEOUT_FACTOR if timeout else None,
                callback=functools.partial(callback, amqp_transport=UamqpTransport)
            )

        #@staticmethod
        #def get_error(status_code, description):
        #    """
        #    Gets error corresponding to status code.
        #    :param status_code: Status code.
        #    :param str description: Description of error.
        #    """
        #    if status_code in [401]:
        #        return AuthenticationException(
        #            f"Management authentication failed. Status code: {status_code}, Description: {description!r}"
        #        )
        #    if status_code in [404]:
        #        return ConnectError(
        #            f"Management connection failed. Status code: {status_code}, Description: {description!r}"
        #        )
        #    return AMQPConnectionError(
        #        f"Management request error. Status code: {status_code}, Description: {description!r}"
        #    )

        #@staticmethod
        #def check_timeout_exception(base, exception):
        #    """
        #    Checks if timeout exception.
        #    :param base: ClientBase.
        #    :param exception: Exception to check.
        #    """
        #    if not base.running and isinstance(
        #        exception, compat.TimeoutException
        #    ):
        #        exception = AuthenticationException(
        #            "Authorization timeout."
        #        )
        #    return exception

        @staticmethod
        def _handle_amqp_exception_with_condition(
            logger, condition, description, exception=None, status_code=None
        ):
            # handling AMQP Errors that have the condition field or the mgmt handler
            logger.info(
                "AMQP error occurred: (%r), condition: (%r), description: (%r).",
                exception,
                condition,
                description,
            )
            if condition == AMQPErrorCodes.NotFound:
                # handle NotFound error code
                error_cls = (
                    ServiceBusCommunicationError
                    if isinstance(exception, AMQPConnectionError)
                    else MessagingEntityNotFoundError
                )
            elif condition == AMQPErrorCodes.ClientError and "timed out" in str(exception):
                # handle send timeout
                error_cls = OperationTimeoutError
            elif condition == AMQPErrorCodes.UnknownError and isinstance(exception, AMQPConnectionError):
                error_cls = ServiceBusConnectionError
            else:
                # handle other error codes
                error_cls = _ERROR_CODE_TO_ERROR_MAPPING.get(condition, ServiceBusError)

            error = error_cls(
                message=description,
                error=exception,
                condition=condition,
                status_code=status_code,
            )
            if condition in _NO_RETRY_CONDITION_ERROR_CODES:
                error._retryable = False  # pylint: disable=protected-access
            else:
                error._retryable = True # pylint: disable=protected-access

            return error

        @staticmethod
        def _handle_amqp_exception_without_condition(logger, exception):
            error_cls = ServiceBusError
            if isinstance(exception, AMQPConnectionError):
                logger.info("AMQP Connection error occurred: (%r).", exception)
                error_cls = ServiceBusConnectionError
            elif isinstance(exception, AuthenticationException):
                logger.info("AMQP Connection authentication error occurred: (%r).", exception)
                error_cls = ServiceBusAuthenticationError
            elif isinstance(exception, MessageException):
                logger.info("AMQP Message error occurred: (%r).", exception)
                if isinstance(exception, MessageAlreadySettled):
                    error_cls = MessageAlreadySettled
                elif isinstance(exception, MessageContentTooLarge):
                    error_cls = MessageSizeExceededError
            else:
                logger.info(
                    "Unexpected AMQP error occurred (%r). Handler shutting down.", exception
                )

            error = error_cls(message=str(exception), error=exception)
            return error

        @staticmethod
        def _handle_amqp_mgmt_error(
            logger, error_description, condition=None, description=None, status_code=None
        ):
            if description:
                error_description += f" {description}."

            raise UamqpTransport._handle_amqp_exception_with_condition(
                logger,
                condition,
                description=error_description,
                exception=None,
                status_code=status_code,
            )

        @staticmethod
        def create_servicebus_exception(logger, exception):
            if isinstance(exception, AMQPError):
                try:
                    # handling AMQP Errors that have the condition field
                    condition = exception.condition
                    description = exception.description
                    exception = UamqpTransport._handle_amqp_exception_with_condition(
                        logger, condition, description, exception=exception
                    )
                except AttributeError:
                    # handling AMQP Errors that don't have the condition field
                    exception = UamqpTransport._handle_amqp_exception_without_condition(logger, exception)
            elif not isinstance(exception, ServiceBusError):
                logger.exception(
                    "Unexpected error occurred (%r). Handler shutting down.", exception
                )
                exception = ServiceBusError(
                    message=f"Handler failed: {exception}.", error=exception
                )

            return exception
