# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
import time
import functools
import datetime
from datetime import timezone
from typing import (
    Optional,
    List,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Union,
    Iterator,
    Type,
    cast,
    Iterable,
)

try:
    from uamqp import (
        BatchMessage,
        constants,
        MessageBodyType,
        Message,
        types,
        SendClient,
        ReceiveClient,
        Source,
        compat,
        Connection,
        __version__,
    )
    from uamqp.authentication import JWTTokenAuth
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
    from ._base import AmqpTransport
    from ..amqp._constants import AmqpMessageBodyType
    from .._common.utils import (
        utc_from_timestamp,
        utc_now,
        get_receive_links,
        receive_trace_context_manager,
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
        OperationTimeoutError,
    )

    if TYPE_CHECKING:
        from uamqp import AMQPClient, Target
        from logging import Logger
        from ..amqp import (
            AmqpAnnotatedMessage,
            AmqpMessageHeader,
            AmqpMessageProperties,
        )
        from .._servicebus_receiver import ServiceBusReceiver
        from .._servicebus_sender import ServiceBusSender
        from ..aio._servicebus_sender_async import (
            ServiceBusSender as ServiceBusSenderAsync,
        )
        from .._common.message import (
            ServiceBusReceivedMessage,
            ServiceBusMessage,
            ServiceBusMessageBatch,
        )
        from .._common._configuration import Configuration

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

        Called internally when a message has failed to send so we
        can parse the error to determine whether we should attempt
        to retry sending the message again.
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

    class UamqpTransport(AmqpTransport):  # pylint: disable=too-many-public-methods
        """
        Class which defines uamqp-based methods used by the sender and receiver.
        """

        KIND = "uamqp"

        # define constants
        MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
        MAX_MESSAGE_LENGTH_BYTES = constants.MAX_MESSAGE_LENGTH_BYTES
        TIMEOUT_FACTOR = 1000
        # CONNECTION_CLOSING_STATES: Tuple = (  # pylint:disable=protected-access
        #        c_uamqp.ConnectionState.CLOSE_RCVD,  # pylint:disable=c-extension-no-member
        #        c_uamqp.ConnectionState.CLOSE_SENT,  # pylint:disable=c-extension-no-member
        #        c_uamqp.ConnectionState.DISCARDING,  # pylint:disable=c-extension-no-member
        #        c_uamqp.ConnectionState.END,  # pylint:disable=c-extension-no-member
        #    )
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
        AMQP_LONG_VALUE: Callable = types.AMQPLong
        AMQP_ARRAY_VALUE: Callable = types.AMQPArray
        AMQP_UINT_VALUE: Callable = types.AMQPuInt

        # errors
        TIMEOUT_ERROR = compat.TimeoutException

        @staticmethod
        def build_message(**kwargs: Any) -> "Message":
            """
            Creates a uamqp.Message with given arguments.
            :rtype: uamqp.Message
            """
            return Message(**kwargs)

        @staticmethod
        def build_batch_message(data: List) -> "BatchMessage":
            """
            Creates a uamqp.BatchMessage with given arguments.
            :rtype: uamqp.BatchMessage
            """
            return BatchMessage(data=data)

        @staticmethod
        def get_message_delivery_tag(
            message: "Message", _
        ) -> str:  # pylint: disable=unused-argument
            """
            Gets delivery tag of a Message.
            :param message: Message to get delivery_tag from for uamqp.Message.
            :param frame: Message to get delivery_tag from for pyamqp.Message.
            :rtype: str
            """
            return message.delivery_tag

        @staticmethod
        def get_message_delivery_id(
            message: "Message", _
        ) -> str:  # pylint: disable=unused-argument
            """
            Gets delivery id of a Message.
            :param message: Message to get delivery_id from for uamqp.Message.
            :param frame: Message to get delivery_id from for pyamqp.Message.
            :rtype: str
            """
            return message.delivery_no

        @staticmethod
        def to_outgoing_amqp_message(
            annotated_message: "AmqpAnnotatedMessage",
        ) -> "Message":
            """
            Converts an AmqpAnnotatedMessage into an Amqp Message.
            :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
            :rtype: uamqp.Message
            """
            message_header = None
            ttl_set = False
            header_vals = (
                annotated_message.header.values() if annotated_message.header else None
            )
            # If header and non-None header values, create outgoing header.
            if header_vals and header_vals.count(None) != len(header_vals):
                annotated_message.header = cast(
                    "AmqpMessageHeader", annotated_message.header
                )
                message_header = MessageHeader()
                message_header.delivery_count = annotated_message.header.delivery_count
                message_header.time_to_live = annotated_message.header.time_to_live
                message_header.first_acquirer = annotated_message.header.first_acquirer
                message_header.durable = annotated_message.header.durable
                message_header.priority = annotated_message.header.priority
                if (
                    annotated_message.header.time_to_live
                    and annotated_message.header.time_to_live != MAX_DURATION_VALUE
                ):
                    ttl_set = True
                    creation_time_from_ttl = int(
                        time.mktime(datetime.datetime.now(timezone.utc).timetuple())
                        * UamqpTransport.TIMEOUT_FACTOR
                    )
                    absolute_expiry_time_from_ttl = int(
                        min(
                            MAX_ABSOLUTE_EXPIRY_TIME,
                            creation_time_from_ttl
                            + annotated_message.header.time_to_live,
                        )
                    )

            message_properties = None
            properties_vals = (
                annotated_message.properties.values()
                if annotated_message.properties
                else None
            )
            # If properties and non-None properties values, create outgoing properties.
            if properties_vals and properties_vals.count(None) != len(properties_vals):
                annotated_message.properties = cast(
                    "AmqpMessageProperties", annotated_message.properties
                )
                creation_time = None
                absolute_expiry_time = None
                if ttl_set:
                    creation_time = creation_time_from_ttl
                    absolute_expiry_time = absolute_expiry_time_from_ttl
                else:
                    if annotated_message.properties.creation_time:
                        creation_time = int(annotated_message.properties.creation_time)
                    if annotated_message.properties.absolute_expiry_time:
                        absolute_expiry_time = int(
                            annotated_message.properties.absolute_expiry_time
                        )

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
                    encoding=annotated_message._encoding,  # pylint: disable=protected-access
                )
            elif ttl_set:
                message_properties = MessageProperties(
                    creation_time=creation_time_from_ttl if ttl_set else None,
                    absolute_expiry_time=absolute_expiry_time_from_ttl
                    if ttl_set
                    else None,
                )

            # pylint: disable=protected-access
            amqp_body_type = annotated_message.body_type
            if amqp_body_type == AmqpMessageBodyType.DATA:
                amqp_body_type = MessageBodyType.Data
                amqp_body = list(cast(Iterable, annotated_message._data_body))
            elif amqp_body_type == AmqpMessageBodyType.SEQUENCE:
                amqp_body_type = MessageBodyType.Sequence
                amqp_body = list(cast(Iterable, annotated_message._sequence_body))
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
        def encode_message(message: "ServiceBusMessage") -> bytes:
            """
            Encodes the outgoing uamqp.Message of the message.
            :param ServiceBusMessage message: Message.
            :rtype: bytes
            """
            return cast("Message", message._message).encode_message()

        @staticmethod
        def update_message_app_properties(
            message: "Message", key: str, value: str
        ) -> "Message":
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
        def get_batch_message_encoded_size(message: "BatchMessage") -> int:
            """
            Gets the batch message encoded size given an underlying Message.
            :param uamqp.BatchMessage message: Message to get encoded size of.
            :rtype: int
            """
            return message.gather()[0].get_message_encoded_size()

        @staticmethod
        def get_message_encoded_size(message: "Message") -> int:
            """
            Gets the message encoded size given an underlying Message.
            :param uamqp.Message message: Message to get encoded size of.
            :rtype: int
            """
            return message.get_message_encoded_size()

        @staticmethod
        def get_remote_max_message_size(handler: "AMQPClient") -> int:
            """
            Returns max peer message size.
            :param AMQPClient handler: Client to get remote max message size on link from.
            :rtype: int
            """
            return (
                handler.message_handler._link.peer_max_message_size
            )  # pylint:disable=protected-access

        @staticmethod
        def get_handler_link_name(handler: "AMQPClient") -> str:
            """
            Returns link name.
            :param AMQPClient handler: Client to get name of link from.
            :rtype: str
            """
            return handler.message_handler.name

        @staticmethod
        def create_retry_policy(
            config: "Configuration", *, is_session: bool = False
        ) -> "_ServiceBusErrorPolicy":
            """
            Creates the error retry policy.
            :param ~azure.servicebus._common._configuration.Configuration config:
             Configuration.
            :keyword bool is_session: Is session enabled.
            """
            # TODO: What's the retry overlap between servicebus and pyamqp?
            return _ServiceBusErrorPolicy(
                max_retries=config.retry_total, is_session=is_session
            )

        @staticmethod
        def create_connection(
            host: str, auth: "JWTTokenAuth", network_trace: bool, **kwargs: Any
        ) -> "Connection":
            """
            Creates and returns the uamqp Connection object.
            :param str host: The hostname, used by uamqp.
            :param JWTTokenAuth auth: The auth, used by uamqp.
            :param bool network_trace: Required.
            """
            custom_endpoint_address = kwargs.pop(  # pylint:disable=unused-variable
                "custom_endpoint_address"
            )
            ssl_opts = kwargs.pop("ssl_opts")  # pylint:disable=unused-variable
            transport_type = kwargs.pop(  # pylint:disable=unused-variable
                "transport_type"
            )
            http_proxy = kwargs.pop("http_proxy")  # pylint:disable=unused-variable
            return Connection(
                hostname=host,
                sasl=auth,
                debug=network_trace,
            )

        @staticmethod
        def close_connection(connection: "Connection") -> None:
            """
            Closes existing connection.
            :param connection: uamqp or pyamqp Connection.
            """
            connection.destroy()

        @staticmethod
        def create_send_client(config: "Configuration", **kwargs: Any) -> "SendClient":
            """
            Creates and returns the uamqp SendClient.
            :param ~azure.servicebus._common._configuration.Configuration config:
             The configuration.
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
                **kwargs,
            )

        @staticmethod
        def set_msg_timeout(
            sender: Union["ServiceBusSender", "ServiceBusSenderAsync"],
            logger: "Logger",
            timeout: int,
            last_exception: Optional[Exception],
        ) -> None:
            # pylint: disable=protected-access
            if not timeout:
                cast("SendClient", sender._handler)._msg_timeout = 0
                return
            if timeout <= 0.0:
                if last_exception:
                    error = last_exception
                else:
                    error = OperationTimeoutError(message="Send operation timed out")
                logger.info("%r send operation timed out. (%r)", sender._name, error)
                raise error
            cast("SendClient", sender._handler)._msg_timeout = (
                timeout * UamqpTransport.TIMEOUT_FACTOR  # type: ignore
            )

        @staticmethod
        def send_messages(
            sender: "ServiceBusSender",
            message: Union["ServiceBusMessage", "ServiceBusMessageBatch"],
            logger: "Logger",
            timeout: int,
            last_exception: Optional[Exception],
        ) -> None:  # pylint: disable=unused-argument
            """
            Handles sending of service bus messages.
            :param ~azure.servicebus.ServiceBusSender sender: The sender with handler
             to send messages.
            :param message: ServiceBusMessage with uamqp.Message to be sent.
            :paramtype message: ~azure.servicebus.ServiceBusMessage or ~azure.servicebus.ServiceBusMessageBatch
            :param int timeout: Timeout time.
            :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
            :param logger: Logger.
            """
            # pylint: disable=protected-access
            sender._open()
            default_timeout = cast("SendClient", sender._handler)._msg_timeout
            try:
                UamqpTransport.set_msg_timeout(sender, logger, timeout, last_exception)
                sender._handler.send_message(message._message)
            finally:
                UamqpTransport.set_msg_timeout(sender, logger, default_timeout, None)

        @staticmethod
        def add_batch(
            sb_message_batch: "ServiceBusMessageBatch",
            outgoing_sb_message: "ServiceBusMessage",
        ) -> None:  # pylint: disable=unused-argument
            """
            Add ServiceBusMessage to the data body of the BatchMessage.
            :param sb_message_batch: ServiceBusMessageBatch to add data to.
            :param outgoing_sb_message: Transformed ServiceBusMessage for sending.
            :rtype: None
            """
            # pylint: disable=protected-access
            sb_message_batch._message._body_gen.append(outgoing_sb_message._message)

        @staticmethod
        def create_source(source: "Source", session_filter: Optional[str]) -> "Source":
            """
            Creates and returns the Source.

            :param str source: Required.
            :param int or None session_id: Required.
            """
            source = Source(source)
            source.set_filter(session_filter, name=SESSION_FILTER, descriptor=None)
            return source

        @staticmethod
        def create_receive_client(
            receiver: "ServiceBusReceiver", **kwargs: Any
        ) -> "ReceiveClient":
            """
            Creates and returns the receive client.
            :param ~azure.servicebus._common._configuration.Configuration config:
             The configuration.

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
                receive_settle_mode=UamqpTransport.ServiceBusToAMQPReceiveModeMap[
                    receive_mode
                ],
                send_settle_mode=constants.SenderSettleMode.Settled
                if receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
                else None,
                on_attach=functools.partial(UamqpTransport.on_attach, receiver),
                **kwargs,
            )

        @staticmethod
        def on_attach(  # pylint: disable=unused-argument
            receiver: "ServiceBusReceiver",
            source: "Source",
            target: "Target",
            properties: Dict[str, Any],
            error: Exception,
        ) -> None:
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
                    receiver._session._locked_until_utc = utc_from_timestamp(
                        expiry_in_seconds
                    )
                session_filter = source.get_filter(name=SESSION_FILTER)
                receiver._session_id = session_filter.decode(receiver._config.encoding)
                receiver._session._session_id = receiver._session_id

        @staticmethod
        def iter_contextual_wrapper(
            receiver: "ServiceBusReceiver", max_wait_time: Optional[int] = None
        ) -> Iterator["ServiceBusReceivedMessage"]:
            """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
            and per-iter argument passing that requires the former."""
            # pylint: disable=protected-access
            original_timeout = None
            while True:
                # This is not threadsafe, but gives us a way to handle if someone passes
                # different max_wait_times to different iterators and uses them in concert.
                if max_wait_time:
                    original_timeout = receiver._handler._timeout
                    receiver._handler._timeout = (
                        max_wait_time * UamqpTransport.TIMEOUT_FACTOR
                    )
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
        def iter_next(
            receiver: "ServiceBusReceiver", wait_time: Optional[int] = None
        ) -> "ServiceBusReceivedMessage":  # pylint: disable=unused-argument
            # pylint: disable=protected-access
            try:
                receiver._receive_context.set()
                receiver._open()
                if not receiver._message_iter:
                    receiver._message_iter = receiver._handler.receive_messages_iter()
                uamqp_message = next(
                    cast(Iterator["ServiceBusReceivedMessage"], receiver._message_iter)
                )
                message = receiver._build_received_message(uamqp_message)
                if (
                    receiver._auto_lock_renewer
                    and not receiver._session
                    and receiver._receive_mode
                    != ServiceBusReceiveMode.RECEIVE_AND_DELETE
                ):
                    receiver._auto_lock_renewer.register(receiver, message)
                return message
            finally:
                receiver._receive_context.clear()

        @staticmethod
        def enhanced_message_received(
            receiver: "ServiceBusReceiver", message: "Message"
        ) -> None:
            """
            Receiver enhanced_message_received callback.
            """
            # pylint: disable=protected-access
            cast("ReceiveClient", receiver._handler)._was_message_received = True
            if receiver._receive_context.is_set():
                receiver._handler._received_messages.put(message)
            else:
                message.release()

        @staticmethod
        def build_received_message(
            receiver: "ServiceBusReceiver",
            message_type: Type["ServiceBusReceivedMessage"],
            received: "Message",
        ) -> "ServiceBusReceivedMessage":
            # pylint: disable=protected-access
            message = message_type(
                message=received, receive_mode=receiver._receive_mode, receiver=receiver
            )
            message._uamqp_message = received
            receiver._last_received_sequenced_number = message.sequence_number
            return message

        @staticmethod
        def get_current_time(handler: "ReceiveClient") -> float:
            """
            Gets the current time.
            :param ReceiveClient handler: Handler with counter to get time.
            :rtype: int
            """
            return handler._counter.get_current_ms()  # pylint: disable=protected-access

        @staticmethod
        def reset_link_credit(handler: "ReceiveClient", link_credit: int) -> None:
            """
            Resets the link credit on the link.
            :param ReceiveClient handler: Client with link to reset link credit.
            :param int link_credit: Link credit needed.
            :rtype: None
            """
            handler.message_handler.reset_link_credit(link_credit)

        # Executes message settlement, implementation is in settle_message_via_receiver_link_impl
        # May be able to remove and just call methods in private method.
        @staticmethod
        def settle_message_via_receiver_link(
            handler: "ReceiveClient",
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
                dead_letter_error_description,
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
            message._message = cast(Message, message._message)
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
            raise ValueError(f"Unsupported settle operation type: {settle_operation}")

        @staticmethod
        def parse_received_message(
            message: "Message",
            message_type: Type["ServiceBusReceivedMessage"],
            **kwargs: Any,
        ) -> List["ServiceBusReceivedMessage"]:
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
                parsed.append(message_type(wrapped, **kwargs))
            return parsed

        @staticmethod
        def get_message_value(message: "Message") -> Any:
            return message.get_data()

        @staticmethod
        def create_token_auth(
            auth_uri: str,
            get_token: Callable,
            token_type: bytes,
            config: "Configuration",
            **kwargs: Any,
        ) -> "JWTTokenAuth":
            """
            Creates the JWTTokenAuth.
            :param str auth_uri: The auth uri to pass to JWTTokenAuth.
            :param get_token: The callback function used for getting and refreshing
            tokens. It should return a valid jwt token each time it is called.
            :param bytes token_type: Token type.
            :param ~azure.servicebus._configuration.Configuration config: EH config.

            :keyword bool update_token: Required. Whether to update token. If not updating token,
            then pass 300 to refresh_window.
            """
            update_token = kwargs.pop("update_token")
            refresh_window = 0 if update_token else 300

            token_auth = JWTTokenAuth(
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
        def create_mgmt_msg(
            message: "Message",
            application_properties: Dict[str, Any],
            config: "Configuration",  # pylint:disable=unused-argument
            reply_to: str,
            **kwargs: Any,
        ) -> "Message":
            """
            :param message: The message to send in the management request.
            :paramtype message: Any
            :param Dict[bytes, str] application_properties: App props.
            :param ~azure.servicebus._common._configuration.Configuration config: Configuration.
            :param str reply_to: Reply to.
            :rtype: uamqp.Message
            """
            return Message(  # type: ignore # TODO: fix mypy error
                body=message,
                properties=MessageProperties(
                    reply_to=reply_to, encoding=config.encoding, **kwargs
                ),
                application_properties=application_properties,
            )

        @staticmethod
        def mgmt_client_request(
            mgmt_client: "AMQPClient",
            mgmt_msg: "Message",
            *,
            operation: bytes,
            operation_type: bytes,
            node: bytes,
            timeout: int,
            callback: Callable,
        ) -> "ServiceBusReceivedMessage":
            """
            Send mgmt request and return result of callback.
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
                callback=functools.partial(callback, amqp_transport=UamqpTransport),
            )

        @staticmethod
        def _handle_amqp_exception_with_condition(
            logger: "Logger",
            condition: Optional["AMQPErrorCodes"],
            description: str,
            exception: Optional["AMQPError"] = None,
            status_code: Optional[str] = None,
        ) -> "ServiceBusError":
            # handling AMQP Errors that have the condition field or the mgmt handler
            logger.info(
                "AMQP error occurred: (%r), condition: (%r), description: (%r).",
                exception,
                condition,
                description,
            )
            error_cls: Type["ServiceBusError"]
            if condition == AMQPErrorCodes.NotFound:
                # handle NotFound error code
                error_cls = (
                    ServiceBusCommunicationError
                    if isinstance(exception, AMQPConnectionError)
                    else MessagingEntityNotFoundError
                )
            elif condition == AMQPErrorCodes.ClientError and "timed out" in str(
                exception
            ):
                # handle send timeout
                error_cls = OperationTimeoutError
            elif condition == AMQPErrorCodes.UnknownError and isinstance(
                exception, AMQPConnectionError
            ):
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
                error._retryable = True  # pylint: disable=protected-access

            return error

        @staticmethod
        def _handle_amqp_exception_without_condition(
            logger: "Logger", exception: "AMQPError"
        ) -> "ServiceBusError":
            error_cls: Type[ServiceBusError] = ServiceBusError
            if isinstance(exception, AMQPConnectionError):
                logger.info("AMQP Connection error occurred: (%r).", exception)
                error_cls = ServiceBusConnectionError
            elif isinstance(exception, AuthenticationException):
                logger.info(
                    "AMQP Connection authentication error occurred: (%r).", exception
                )
                error_cls = ServiceBusAuthenticationError
            elif isinstance(exception, MessageException):
                logger.info("AMQP Message error occurred: (%r).", exception)
                if isinstance(exception, MessageAlreadySettled):
                    error_cls = MessageAlreadySettled
                elif isinstance(exception, MessageContentTooLarge):
                    error_cls = MessageSizeExceededError
            else:
                logger.info(
                    "Unexpected AMQP error occurred (%r). Handler shutting down.",
                    exception,
                )

            error = error_cls(message=str(exception), error=exception)
            return error

        @staticmethod
        def handle_amqp_mgmt_error(
            logger: "Logger",
            error_description: "str",
            condition: Optional["AMQPErrorCodes"] = None,
            description: Optional[str] = None,
            status_code: Optional[str] = None,
        ) -> "ServiceBusError":
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
        def create_servicebus_exception(
            logger: "Logger", exception: Exception
        ) -> "ServiceBusError":
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
                    exception = UamqpTransport._handle_amqp_exception_without_condition(
                        logger, exception
                    )
            elif not isinstance(exception, ServiceBusError):
                logger.exception(
                    "Unexpected error occurred (%r). Handler shutting down.", exception
                )
                exception = ServiceBusError(
                    message=f"Handler failed: {exception}.", error=exception
                )

            return exception

except ImportError:
    pass
