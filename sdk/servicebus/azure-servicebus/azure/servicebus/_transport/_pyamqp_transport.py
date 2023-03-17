# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import functools
import time
import datetime
from typing import Optional, Tuple, cast, List, TYPE_CHECKING

from azure.core.serialization import TZ_UTC
from .._pyamqp import (
    utils,
    SendClient,
    constants,
    ReceiveClient,
    __version__,
)
from .._pyamqp.error import (
    ErrorCondition,
    AMQPException,
    AMQPError,
    RetryPolicy,
    AMQPConnectionError,
    AuthenticationException,
    MessageException,
)
from .._pyamqp.utils import amqp_long_value, amqp_array_value, amqp_string_value, amqp_uint_value
from .._pyamqp._encode import encode_payload
from .._pyamqp._decode import decode_payload
from .._pyamqp.message import Message, BatchMessage, Header, Properties
from .._pyamqp.authentication import JWTTokenAuth
from .._pyamqp.endpoints import Source
from .._pyamqp._connection import Connection, _CLOSING_STATES

from ._base import AmqpTransport
from .._common.utils import (
    utc_from_timestamp,
    utc_now,
    get_receive_links,
    receive_trace_context_manager
)
from .._common.constants import (
#    NO_RETRY_ERRORS,
#    CUSTOM_CONDITION_BACKOFF,
    PYAMQP_LIBRARY,
    DATETIMEOFFSET_EPOCH,
    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    DEADLETTERNAME,
    MAX_ABSOLUTE_EXPIRY_TIME,
    MAX_DURATION_VALUE,
    MAX_MESSAGE_LENGTH_BYTES,
    MESSAGE_COMPLETE,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_DEAD_LETTER,
    SESSION_FILTER,
    SESSION_LOCKED_UNTIL,
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_LOCKED_UNTIL,
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
    ServiceBusAuthenticationError,
    ServiceBusCommunicationError,
    MessageLockLostError,
    MessageNotFoundError,
    MessagingEntityDisabledError,
    MessagingEntityNotFoundError,
    MessagingEntityAlreadyExistsError,
    ServiceBusServerBusyError,
    SessionCannotBeLockedError,
    SessionLockLostError,
    OperationTimeoutError
)

if TYPE_CHECKING:
    from .._servicebus_receiver import ServiceBusReceiver
    from .._common.message import ServiceBusReceivedMessage

_LOGGER = logging.getLogger(__name__)

class _ServiceBusErrorPolicy(RetryPolicy):

    no_retry = RetryPolicy.no_retry + cast(List[ErrorCondition], [
                ERROR_CODE_SESSION_LOCK_LOST,
                ERROR_CODE_MESSAGE_LOCK_LOST,
                ERROR_CODE_OUT_OF_RANGE,
                ERROR_CODE_ARGUMENT_ERROR,
                ERROR_CODE_PRECONDITION_FAILED,
            ])

    def __init__(self, is_session=False, **kwargs):
        self._is_session = is_session
        custom_condition_backoff = {
            b"com.microsoft:server-busy": 4,
            b"com.microsoft:timeout": 2,
            b"com.microsoft:container-close": 4
        }
        super(_ServiceBusErrorPolicy, self).__init__(
            custom_condition_backoff=custom_condition_backoff,
            **kwargs
        )

    def is_retryable(self, error):
        if self._is_session:
            return False
        return super().is_retryable(error)

_LONG_ANNOTATIONS = (
    _X_OPT_ENQUEUED_TIME,
    _X_OPT_LOCKED_UNTIL
)

_ERROR_CODE_TO_ERROR_MAPPING = {
    ErrorCondition.LinkMessageSizeExceeded: MessageSizeExceededError,
    ErrorCondition.ResourceLimitExceeded: ServiceBusQuotaExceededError,
    ErrorCondition.UnauthorizedAccess: ServiceBusAuthorizationError,
    ErrorCondition.NotImplemented: ServiceBusError,
    ErrorCondition.NotAllowed: ServiceBusError,
    ErrorCondition.LinkDetachForced: ServiceBusConnectionError,
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

class PyamqpTransport(AmqpTransport):   # pylint: disable=too-many-public-methods
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """

    # define constants
    MAX_FRAME_SIZE_BYTES = constants.MAX_FRAME_SIZE_BYTES
    MAX_MESSAGE_LENGTH_BYTES = MAX_MESSAGE_LENGTH_BYTES
    TIMEOUT_FACTOR = 1
    CONNECTION_CLOSING_STATES: Tuple = _CLOSING_STATES
    TRANSPORT_IDENTIFIER = f"{PYAMQP_LIBRARY}/{__version__}"

    # To enable extensible string enums for the public facing parameter, and translate to the "real" uamqp constants.
    ServiceBusToAMQPReceiveModeMap = {
        ServiceBusReceiveMode.PEEK_LOCK: constants.ReceiverSettleMode.Second,
        ServiceBusReceiveMode.RECEIVE_AND_DELETE: constants.ReceiverSettleMode.First,
    }

    # define symbols
    PRODUCT_SYMBOL = "product"
    VERSION_SYMBOL = "version"
    FRAMEWORK_SYMBOL = "framework"
    PLATFORM_SYMBOL = "platform"
    USER_AGENT_SYMBOL = "user-agent"
    #ERROR_CONDITIONS = [condition.value for condition in ErrorCondition]

    # amqp value types
    AMQP_LONG_VALUE = amqp_long_value
    AMQP_ARRAY_VALUE = amqp_array_value
    AMQP_UINT_VALUE = amqp_uint_value

    # errors
    TIMEOUT_ERROR = TimeoutError

    @staticmethod
    def build_message(**kwargs):
        """
        Creates a pyamqp.Message with given arguments.
        :rtype: pyamqp.Message
        """
        return Message(**kwargs)

    @staticmethod
    def build_batch_message(data):
        """
        Creates a pyamqp.BatchMessage with given arguments.
        :rtype: pyamqp.BatchMessage
        """
        message = cast(List, [None] * 9)
        message[5] = data
        return message

    @staticmethod
    def get_message_delivery_tag(_, frame):  # pylint: disable=unused-argument
        """
        Gets delivery tag of a Message.
        :param message: Message to get delivery_tag from for uamqp.Message.
        :param frame: Message to get delivery_tag from for pyamqp.Message.
        :rtype: str
        """
        return frame[2] if frame else None

    @staticmethod
    def get_message_delivery_id(_, frame):  # pylint: disable=unused-argument
        """
        Gets delivery id of a Message.
        :param message: Message to get delivery_id from for uamqp.Message.
        :param frame: Message to get delivery_id from for pyamqp.Message.
        :rtype: str
        """
        return frame[1] if frame else None

    @staticmethod
    def to_outgoing_amqp_message(annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Message.
        :param AmqpAnnotatedMessage annotated_message: AmqpAnnotatedMessage to convert.
        :rtype: pyamqp.Message
        """
        message_header = None
        ttl_set = False
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
            if annotated_message.header.time_to_live and annotated_message.header.time_to_live != MAX_DURATION_VALUE:
                ttl_set = True
                creation_time_from_ttl = int(
                    time.mktime(datetime.datetime.now(TZ_UTC).timetuple()) * 1000   # TODO: should this be * 1?
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

            message_properties = Properties(
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
            )
        elif ttl_set:
            message_properties = Properties(
                creation_time=creation_time_from_ttl if ttl_set else None,
                absolute_expiry_time=absolute_expiry_time_from_ttl if ttl_set else None,
            )
        annotations = None
        if annotated_message.annotations:
            # TODO: Investigate how we originally encoded annotations.
            annotations = dict(annotated_message.annotations)
            for key in _LONG_ANNOTATIONS:
                if key in annotated_message.annotations:
                    annotations[key] = amqp_long_value(annotated_message.annotations[key])
        message_dict = {
            "header": message_header,
            "properties": message_properties,
            "application_properties": annotated_message.application_properties,
            "message_annotations": annotations,
            "delivery_annotations": annotated_message.delivery_annotations,
            "data": annotated_message._data_body,  # pylint: disable=protected-access
            "sequence": annotated_message._sequence_body,  # pylint: disable=protected-access
            "value": annotated_message._value_body,  # pylint: disable=protected-access
            "footer": annotated_message.footer,
        }

        return Message(**message_dict)

    @staticmethod
    def encode_message(message):
        """
        Encodes the outgoing pyamqp.Message of the message.
        :param ServiceBusMessage message: Message.
        :rtype: bytes
        """
        output = bytearray()
        return encode_payload(output, message._message)  # pylint: disable=protected-access

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
        :param List message: Message to get encoded size of.
        :rtype: int
        """
        return utils.get_message_encoded_size(BatchMessage(*message))

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
    def get_handler_link_name(handler):
        """
        Returns link name.
        :param AMQPClient handler: Client to get name of link from.
        :rtype: str
        """
        return handler._link.name

    @staticmethod
    def create_retry_policy(config, *, is_session=False):
        """
        Creates the error retry policy.
        :param ~azure.eventhub._configuration.Configuration config: Configuration.
        :keyword bool is_session: Is session enabled.
        """
        # TODO: What's the retry overlap between servicebus and pyamqp?
        return _ServiceBusErrorPolicy(
            is_session=is_session,
            retry_total=config.retry_total,
            retry_backoff_factor=config.retry_backoff_factor,
            retry_backoff_max=config.retry_backoff_max,
            retry_mode=config.retry_mode,
            #no_retry_condition=NO_RETRY_ERRORS,
            #custom_condition_backoff=CUSTOM_CONDITION_BACKOFF,
        )

    @staticmethod
    def create_link_properties(link_properties):
        """
        Creates and returns the link properties.
        :param dict[bytes, int] link_properties: The dict of symbols and corresponding values.
        :rtype: dict
        """
        return {
            symbol: amqp_long_value(value)
            for (symbol, value) in link_properties.items()
        }

    @staticmethod
    def create_connection(host, auth, network_trace, **kwargs):
        """
        Creates and returns the pyamqp Connection object.
        :param str host: The hostname used by pyamqp.
        :param JWTTokenAuth auth: The auth used by pyamqp.
        :param bool network_trace: Debug setting.
        """
        return Connection(
            endpoint=host,
            sasl_credential=auth.sasl,
            network_trace=network_trace,
            **kwargs
        )

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
    def create_send_client(config, **kwargs):
        """
        Creates and returns the pyamqp SendClient.
        :keyword ~azure.servicebus._configuration.Configuration config: The configuration. Required.

        :keyword str target: Required. The target.
        :keyword JWTTokenAuth auth: Required.
        :keyword retry_policy: Required.
        :keyword str client_name: Required.
        :keyword properties: Required.
        """

        target = kwargs.pop("target")
        return SendClient(
            config.hostname,
            target,
            network_trace=config.logging_enable,
            keep_alive_interval=config.keep_alive,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            **kwargs,
        )

    @staticmethod
    def send_messages(sender, message, logger, timeout, last_exception):    # pylint: disable=unused-argument
        """
        Handles sending of service bus messages.
        :param ~azure.servicebus._servicebus_sender.ServiceBusSender sender: The sender with handler
         to send messages.
        :param int timeout: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
        """
        # pylint: disable=protected-access
        sender._open()
        try:
            if isinstance(message._message, list):    # BatchMessage
                sender._handler.send_message(BatchMessage(*message._message), timeout=timeout) # pylint:disable=protected-access
            else:   # Message
                sender._handler.send_message(message._message, timeout=timeout) # pylint:disable=protected-access
        except TimeoutError:
            raise OperationTimeoutError(message="Send operation timed out")
        except MessageException as e:
            raise PyamqpTransport.create_servicebus_exception(logger, e)

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
        utils.add_batch(
            sb_message_batch._message, outgoing_sb_message._message
        )

    @staticmethod
    def create_source(source, session_filter):
        """
        Creates and returns the Source.

        :param str source: Required.
        :param int or None session_id: Required.
        """
        filter_map = {SESSION_FILTER: session_filter}
        source = Source(address=source, filters=filter_map)
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
        :keyword streaming_receive: Required.
        :keyword timeout: Required.
        """
        config = receiver._config   # pylint: disable=protected-access
        source = kwargs.pop("source")
        receive_mode = kwargs.pop("receive_mode")
        return ReceiveClient(
            config.hostname,
            source,
            http_proxy=config.http_proxy,
            transport_type=config.transport_type,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            receive_settle_mode=PyamqpTransport.ServiceBusToAMQPReceiveModeMap[receive_mode],
            send_settle_mode=constants.SenderSettleMode.Settled
            if receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
            else constants.SenderSettleMode.Unsettled,
            on_attach=functools.partial(
                PyamqpTransport.on_attach,
                receiver
            ),
            **kwargs
        )

    @staticmethod
    def open_receive_client(*, handler, client, auth):
        """
        Opens the receive client and returns ready status.
        :param ReceiveClient handler: The receive client.
        :param ~azure.eventhub.ServiceBusConsumerClient client: The consumer client.
        :param auth: Auth.
        :rtype: bool
        """
        # pylint:disable=protected-access
        handler.open(
            connection=client._conn_manager.get_connection(
                client._address.hostname, auth
            )
        )

    # TODO: ask why this is a callable.
    @staticmethod
    def on_attach(receiver, attach_frame):
        """
        Receiver on_attach callback.
        """
        # pylint: disable=protected-access, unused-argument
        if receiver._session and attach_frame.source.address.decode(receiver._config.encoding) == receiver._entity_uri:
            # This has to live on the session object so that autorenew has access to it.
            receiver._session._session_start = utc_now()
            expiry_in_seconds = attach_frame.properties.get(SESSION_LOCKED_UNTIL)
            if expiry_in_seconds:
                expiry_in_seconds = (
                    expiry_in_seconds - DATETIMEOFFSET_EPOCH
                ) / 10000000
                receiver._session._locked_until_utc = utc_from_timestamp(expiry_in_seconds)
            session_filter = attach_frame.source.filters[SESSION_FILTER]
            receiver._session_id = session_filter.decode(receiver._config.encoding)
            receiver._session._session_id = receiver._session_id

    @staticmethod
    def iter_contextual_wrapper(receiver, max_wait_time=None):
        """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
        and per-iter argument passing that requires the former."""
        while True:
            try:
                message = receiver._inner_next(wait_time=max_wait_time)
                links = get_receive_links(message)
                with receive_trace_context_manager(receiver, links=links):
                    yield message
            except StopIteration:
                break
    
    @staticmethod
    def iter_next(receiver, wait_time=None):
        try:
            receiver._receive_context.set()
            receiver._open()
            if not receiver._message_iter or wait_time:
                receiver._message_iter = receiver._handler.receive_messages_iter(timeout=wait_time)
            pyamqp_message = next(receiver._message_iter)
            message = receiver._build_received_message(pyamqp_message)
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
    def enhanced_message_received(receiver, frame, message):
        """
        Receiver enhanced_message_received callback.
        """
        # pylint: disable=protected-access
        receiver._handler._was_message_received = True
        if receiver._receive_context.is_set():
            receiver._handler._received_messages.put((frame, message))
        else:
            receiver._handler.settle_messages(frame[1], 'released')

    @staticmethod
    def build_received_message(
        receiver: "ServiceBusReceiver",
        message_type: "ServiceBusReceivedMessage",
        received: "Message"
    ):
        message = message_type(
            message=received[1], receive_mode=receiver._receive_mode, receiver=receiver, frame=received[0]
        )
        receiver._last_received_sequenced_number = message.sequence_number
        return message

    @staticmethod
    def get_receive_timeout(handler):
        """
        Gets the timeout on the ReceiveClient.
        :param ReceiveClient handler: Handler to set timeout on.
        :rtype: int
        """
        return handler._idle_timeout

    @staticmethod
    def set_receive_timeout(handler, max_wait_time):
        """
        Sets the timeout on the ReceiveClient and returns original timeout.
        :param ReceiveClient handler: Handler to set timeout on.
        :param int max_wait_time: Max wait time.
        :rtype: None
        """
        # _timeout to _idle_timeout
        handler._idle_timeout = max_wait_time

    @staticmethod
    def get_current_time(handler):  # pylint: disable=unused-argument
        """
        Gets the current time.
        :param ReceiveClient handler: Handler with counter to get time. Unused for pyamqp.
        :rtype: int
        """
        return time.time()

    @staticmethod
    def reset_link_credit(handler, link_credit):
        """
        Resets the link credit on the link.
        :param ReceiveClient handler: Client with link to reset link credit.
        :param int link_credit: Link credit needed.
        :rtype: None
        """
        handler._link.flow(link_credit=link_credit) # pylint: disable=protected-access

    @staticmethod
    def settle_message_via_receiver_link(
        handler: ReceiveClient,
        message: "ServiceBusReceivedMessage",
        settle_operation: str,
        dead_letter_reason: Optional[str] = None,
        dead_letter_error_description: Optional[str] = None,
    ) -> None:
        if settle_operation == MESSAGE_COMPLETE:
            return handler.settle_messages(message.delivery_id, 'accepted')
        if settle_operation == MESSAGE_ABANDON:
            return handler.settle_messages(
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=False
            )
        if settle_operation == MESSAGE_DEAD_LETTER:
            return handler.settle_messages(
                message.delivery_id,
                'rejected',
                error=AMQPError(
                    condition=DEADLETTERNAME,
                    description=dead_letter_error_description,
                    info={
                        RECEIVER_LINK_DEAD_LETTER_REASON: dead_letter_reason,
                        RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION: dead_letter_error_description,
                    }
                )
            )
        if settle_operation == MESSAGE_DEFER:
            return handler.settle_messages(
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=True
            )
        raise ValueError(
            f"Unsupported settle operation type: {settle_operation}"
        )

    @staticmethod
    def parse_received_message(message, message_type, **kwargs):
        """
        Parses peek/deferred op messages into ServiceBusReceivedMessage.
        :param Message message: Message to parse.
        :param ServiceBusReceivedMessage message_type: Parse messages to return.
        :keyword ServiceBusReceiver receiver: Required.
        :keyword bool is_peeked_message: Optional. For peeked messages.
        :keyword bool is_deferred_message: Optional. For deferred messages.
        :keyword ServiceBusReceiveMode receive_mode: Optional.
        """
        parsed = []
        for m in message.value[b"messages"]:
            wrapped = decode_payload(memoryview(m[b"message"]))
            parsed.append(
                message_type(
                    wrapped, **kwargs
                )
            )
        return parsed

    @staticmethod
    def get_message_value(message):
        return message.value

    #@staticmethod
    #def check_link_stolen(consumer, exception):
    #    """
    #    Checks if link stolen and handles exception.
    #    :param consumer: The ServiceBusConsumer.
    #    :param exception: Exception to check.
    #    """

    #    if (
    #        isinstance(exception, AMQPLinkError)
    #        and exception.condition == ErrorCondition.LinkStolen
    #    ):
    #        raise consumer._handle_exception(  # pylint: disable=protected-access
    #            exception
    #        )

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
            return JWTTokenAuth(auth_uri, auth_uri, get_token)
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

    #@staticmethod
    #def create_mgmt_client(
    #    address, mgmt_auth, config
    #):  # pylint: disable=unused-argument
    #    """
    #    Creates and returns the mgmt AMQP client.
    #    :param _Address address: Required. The Address.
    #    :param JWTTokenAuth mgmt_auth: Auth for client.
    #    :param ~azure.eventhub._configuration.Configuration config: The configuration.
    #    """

    #    return AMQPClient(
    #        config.hostname,
    #        auth=mgmt_auth,
    #        network_trace=config.network_tracing,
    #        transport_type=config.transport_type,
    #        http_proxy=config.http_proxy,
    #        custom_endpoint_address=config.custom_endpoint_address,
    #        connection_verify=config.connection_verify,
    #    )

    @staticmethod
    def get_updated_token(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """
        return mgmt_auth.get_token()

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
        :rtype: pyamqp.Message
        """
        return Message( # type: ignore # TODO: fix mypy error
            value=message,
            properties=Properties(
                reply_to=reply_to,
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
        status, description, response = mgmt_client.mgmt_request(
            mgmt_msg,
            operation=amqp_string_value(operation.decode("UTF-8")),
            operation_type=amqp_string_value(operation_type),
            node=node,
            timeout=timeout,  # TODO: check if this should be seconds * 1000 if timeout else None,
        )
        return callback(status, response, description, amqp_transport=PyamqpTransport)

    #@staticmethod
    #def get_error(status_code, description):
    #    """
    #    Gets error and passes in error message, and, if applicable, condition.
    #    :param error: The error to raise.
    #    :param str message: Error message.
    #    :param condition: Optional error condition. Will not be used by uamqp.
    #    """
    #    if status_code in [401]:
    #        return AuthenticationException(
    #            ErrorCondition.UnauthorizedAccess,
    #            description=f"""Management authentication failed. Status code: {status_code}, """
    #                """Description: {description!r}""",
    #        )
    #    if status_code in [404]:
    #        return AMQPConnectionError(
    #            ErrorCondition.NotFound,
    #            description=f"Management connection failed. Status code: {status_code}, Description: {description!r}",
    #        )
    #    return AMQPConnectionError(
    #        ErrorCondition.UnknownError,
    #        description=f"Management request error. Status code: {status_code}, Description: {description!r}",
    #    )

    #@staticmethod
    #def check_timeout_exception(base, exception):
    #    """
    #    Checks if timeout exception.
    #    :param base: ClientBase.
    #    :param exception: Exception to check.
    #    """
    #    if not base.running and isinstance(exception, TimeoutError):
    #        exception = AuthenticationException(
    #            ErrorCondition.InternalError,
    #            description="Authorization timeout.",
    #        )
    #    return exception

    @staticmethod
    def _handle_amqp_exception_with_condition(
        logger, condition, description, exception=None, status_code=None
    ):
        #
        # handling AMQP Errors that have the condition field or the mgmt handler
        logger.info(
            "AMQP error occurred: (%r), condition: (%r), description: (%r).",
            exception,
            condition,
            description,
        )
        if isinstance(exception, AuthenticationException):
            logger.info("AMQP Connection authentication error occurred: (%r).", exception)
            error_cls = ServiceBusAuthenticationError
        # elif isinstance(exception, MessageException):
        #     logger.info("AMQP Message error occurred: (%r).", exception)
        #     if isinstance(exception, MessageAlreadySettled):
        #         error_cls = MessageAlreadySettled
        #     elif isinstance(exception, MessageContentTooLarge):
        #         error_cls = MessageSizeExceededError
        elif condition == ErrorCondition.NotFound:
            # handle NotFound error code
            error_cls = (
                ServiceBusCommunicationError
                if isinstance(exception, AMQPConnectionError)
                else MessagingEntityNotFoundError
            )
        elif condition == ErrorCondition.ClientError and "timed out" in str(exception):
            # handle send timeout
            error_cls = OperationTimeoutError
        elif condition == ErrorCondition.UnknownError or isinstance(exception, AMQPConnectionError):
            error_cls = ServiceBusConnectionError
        else:
            error_cls = _ERROR_CODE_TO_ERROR_MAPPING.get(condition, ServiceBusError)

        error = error_cls(
            message=description,
            error=exception,
            condition=condition,
            status_code=status_code,
        )
        if condition in _ServiceBusErrorPolicy.no_retry:
            error._retryable = False  # pylint: disable=protected-access
        else:
            error._retryable = True # pylint: disable=protected-access

        return error

    @staticmethod
    def _handle_amqp_mgmt_error(
        logger, error_description, condition=None, description=None, status_code=None
    ):
        if description:
            error_description += f" {description}."

        raise PyamqpTransport._handle_amqp_exception_with_condition(
            logger,
            condition,
            description=error_description,
            exception=None,
            status_code=status_code,
        )

    @staticmethod
    def create_servicebus_exception(logger, exception):
        if isinstance(exception, AMQPException):
            # handling AMQP Errors that have the condition field
            condition = exception.condition
            description = exception.description
            exception = PyamqpTransport._handle_amqp_exception_with_condition(
                logger, condition, description, exception=exception
            )
        elif not isinstance(exception, ServiceBusError):
            logger.exception(
                "Unexpected error occurred (%r). Handler shutting down.", exception
            )
            exception = ServiceBusError(
                message=f"Handler failed: {exception}.", error=exception
            )

        return exception
