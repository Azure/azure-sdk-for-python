# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import functools
from typing import TYPE_CHECKING, Optional, Any, Callable, Union, AsyncIterator, cast
import time

from ..._pyamqp import constants
from ..._pyamqp.message import BatchMessage
from ..._pyamqp.utils import amqp_string_value
from ..._pyamqp.aio import SendClientAsync, ReceiveClientAsync
from ..._pyamqp.aio._authentication_async import JWTTokenAuthAsync
from ..._pyamqp.aio._connection_async import Connection as ConnectionAsync
from ..._pyamqp.error import (
    AMQPConnectionError,
    AMQPError,
    MessageException,
)

from ._base_async import AmqpTransportAsync
from ..._common.utils import utc_from_timestamp, utc_now
from ..._common.tracing import get_receive_links, receive_trace_context_manager
from ..._common.constants import (
    DATETIMEOFFSET_EPOCH,
    SESSION_LOCKED_UNTIL,
    SESSION_FILTER,
    RECEIVER_LINK_DEAD_LETTER_ERROR_DESCRIPTION,
    RECEIVER_LINK_DEAD_LETTER_REASON,
    DEADLETTERNAME,
    MESSAGE_COMPLETE,
    MESSAGE_ABANDON,
    MESSAGE_DEFER,
    MESSAGE_DEAD_LETTER,
    ServiceBusReceiveMode,
)
from ..._transport._pyamqp_transport import PyamqpTransport
from ...exceptions import (
    OperationTimeoutError
)

if TYPE_CHECKING:
    from logging import Logger
    from ..._common.message import ServiceBusReceivedMessage, ServiceBusMessage, ServiceBusMessageBatch
    from ..._common._configuration import Configuration
    from .._servicebus_receiver_async import ServiceBusReceiver
    from .._servicebus_sender_async import ServiceBusSender
    from ..._pyamqp.performatives import AttachFrame
    from ..._pyamqp.message import Message
    from ..._pyamqp.aio._client_async import AMQPClientAsync

class PyamqpTransportAsync(PyamqpTransport, AmqpTransportAsync):
    """
    Class which defines pyamqp-based methods used by the sender and receiver.
    """

    @staticmethod
    async def create_connection_async(
        host: str, auth: "JWTTokenAuthAsync", network_trace: bool, **kwargs: Any
    ) -> "ConnectionAsync":
        """
        Creates and returns the pyamqp Connection object.
        :param str host: The hostname used by pyamqp.
        :param JWTTokenAuth auth: The auth used by pyamqp.
        :param bool network_trace: Debug setting.
        :return: An instance of an asynchronous pyamqp Connection.
        :rtype: ~pyamqp.aio.ConnectionAsync
        """
        return ConnectionAsync(
            endpoint=host,
            sasl_credential=auth.sasl,
            network_trace=network_trace,
            **kwargs
        )

    @staticmethod
    async def close_connection_async(connection: "ConnectionAsync") -> None:
        """
        Closes existing connection.
        :param ~pyamqp.aio.ConnectionAsync connection: pyamqp Connection.
        """
        await connection.close()

    @staticmethod
    def create_send_client_async(
        config: "Configuration", **kwargs: Any
    ) -> "SendClientAsync":
        """
        Creates and returns the pyamqp SendClient.
        :param Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword JWTTokenAuth auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword properties: Required.
        :return: An instance of an asynchronous pyamqp SendClient.
        :rtype: ~pyamqp.aio.SendClientAsync
        """
        target = kwargs.pop("target")
        return SendClientAsync(
            config.hostname,
            target,
            network_trace=config.logging_enable,
            keep_alive_interval=config.keep_alive,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            socket_timeout=config.socket_timeout,
            **kwargs,
        )

    @staticmethod
    async def send_messages_async(
        sender: "ServiceBusSender",
        message: Union["ServiceBusMessage", "ServiceBusMessageBatch"],
        logger: "Logger",
        timeout: int,
        last_exception: Optional[Exception]
    ) -> None:  # pylint: disable=unused-argument
        """
        Handles sending of service bus messages.
        :param ~azure.servicebus.ServiceBusSender sender: The sender with handler to send messages.
        :param ~pyamqp.message.Message message: The message to send.
        :param int timeout: Timeout time.
        :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logging.Logger logger: Logger.
        """
        # pylint: disable=protected-access
        await sender._open()
        try:
            if isinstance(message._message, list):
                await sender._handler.send_message_async(BatchMessage(*message._message), timeout=timeout)
            else:
                await sender._handler.send_message_async(
                    message._message,
                    timeout=timeout
                )

        except TimeoutError as exc:
            raise OperationTimeoutError(message="Send operation timed out") from exc
        except MessageException as e:
            raise PyamqpTransportAsync.create_servicebus_exception(logger, e)

    @staticmethod
    def create_receive_client_async(
        receiver: "ServiceBusReceiver", **kwargs: Any
    ) -> "ReceiveClientAsync":  # pylint:disable=unused-argument
        """
        Creates and returns the receive client.
        :param ~azure.servicebus.aio.ServiceBusReceiver receiver: The receiver.

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

        :returns: A ReceiveClientAsync.
        :rtype: ~pyamqp.aio.ReceiveClientAsync
        """
        config = receiver._config   # pylint: disable=protected-access
        source = kwargs.pop("source")
        receive_mode = kwargs.pop("receive_mode")

        return ReceiveClientAsync(
            config.hostname,
            source,
            http_proxy=config.http_proxy,
            transport_type=config.transport_type,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
            receive_settle_mode=PyamqpTransportAsync.ServiceBusToAMQPReceiveModeMap[receive_mode],
            send_settle_mode=constants.SenderSettleMode.Settled
            if receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
            else constants.SenderSettleMode.Unsettled,
            on_attach=functools.partial(
                PyamqpTransportAsync.on_attach_async,
                receiver
            ),
            socket_timeout=config.socket_timeout,
            **kwargs,
        )

    @staticmethod
    async def iter_contextual_wrapper_async(
        receiver: "ServiceBusReceiver", max_wait_time: Optional[int] = None
    ) -> AsyncIterator["ServiceBusReceivedMessage"]:
        while True:
            # pylint: disable=protected-access
            try:
                message = await receiver._inner_anext(wait_time=max_wait_time)
                links = get_receive_links(message)
                with receive_trace_context_manager(receiver, links=links):
                    yield message
            except StopAsyncIteration:
                break

    @staticmethod
    async def iter_next_async(
        receiver: "ServiceBusReceiver", wait_time: Optional[int] = None
    ) -> "ServiceBusReceivedMessage":
        # pylint: disable=protected-access
        try:
            receiver._receive_context.set()
            await receiver._open()
            if not receiver._message_iter or wait_time:
                receiver._message_iter = await receiver._handler.receive_messages_iter_async(timeout=wait_time)
            pyamqp_message = await cast(AsyncIterator["Message"], receiver._message_iter).__anext__()
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
    async def enhanced_message_received_async(
        receiver: "ServiceBusReceiver",
        frame: "AttachFrame",
        message: "Message"
    ) -> None:
        """Callback run on receipt of every message.

        Releases messages from the internal buffer when there is no active receive call. In PEEKLOCK mode,
        this helps avoid messages from expiring in the buffer and incrementing the delivery count of a message.

        Should not be used with RECEIVE_AND_DELETE mode, since those messages are settled right away and removed
        from the Service Bus entity.

        :param ~azure.servicebus.aio.ServiceBusReceiver receiver: The receiver object.
        :param ~pyamqp.performatives.AttachFrame frame: The attach frame.
        :param ~pyamqp.message.Message message: The received message.
        """
        # pylint: disable=protected-access
        receiver._handler._last_activity_timestamp = time.time()
        if receiver._receive_context.is_set():
            receiver._handler._received_messages.put((frame, message))
        else:
            await receiver._handler.settle_messages_async(frame[1], 'released')

    @staticmethod
    def set_handler_message_received_async(receiver: "ServiceBusReceiver") -> None:
        # reassigning default _message_received method in ReceiveClient
        # pylint: disable=protected-access
        receiver._handler._message_received_async = functools.partial(  # type: ignore[assignment]
            PyamqpTransportAsync.enhanced_message_received_async,
            receiver
        )

    @staticmethod
    async def reset_link_credit_async(
        handler: "ReceiveClientAsync", link_credit: int
    ) -> None:
        """
        Resets the link credit on the link.
        :param ReceiveClientAsync handler: Client with link to reset link credit.
        :param int link_credit: Link credit needed.
        :rtype: None
        """
        await handler._link.flow(link_credit=link_credit)   # pylint: disable=protected-access

    @staticmethod
    async def settle_message_via_receiver_link_async(
        handler: "ReceiveClientAsync",
        message: "ServiceBusReceivedMessage",
        settle_operation: str,
        dead_letter_reason: Optional[str] = None,
        dead_letter_error_description: Optional[str] = None,
    ) -> None:
        # pylint: disable=protected-access
        try:
            if settle_operation == MESSAGE_COMPLETE:
                return await handler.settle_messages_async(message._delivery_id, 'accepted')
            if settle_operation == MESSAGE_ABANDON:
                return await handler.settle_messages_async(
                    message._delivery_id,
                    'modified',
                    delivery_failed=True,
                    undeliverable_here=False
                )
            if settle_operation == MESSAGE_DEAD_LETTER:
                return await handler.settle_messages_async(
                    message._delivery_id,
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
                return await handler.settle_messages_async(
                    message._delivery_id,
                    'modified',
                    delivery_failed=True,
                    undeliverable_here=True
                )
        except AttributeError as ae:
            raise RuntimeError("handler is not initialized and cannot complete the message") from ae

        except AMQPConnectionError as e:
            raise RuntimeError("Connection lost during settle operation.") from e

        raise ValueError(
            f"Unsupported settle operation type: {settle_operation}"
        )

    @staticmethod
    async def on_attach_async(
        receiver: "ServiceBusReceiver", attach_frame: "AttachFrame"
    ) -> None:
        # pylint: disable=protected-access, unused-argument
        if receiver._session and attach_frame.source.address.decode() == receiver._entity_uri:
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
    async def create_token_auth_async(
        auth_uri: str,
        get_token: Callable,
        token_type: bytes,
        config: "Configuration",
        **kwargs: Any
    ) -> "JWTTokenAuthAsync":
        """
        Creates the JWTTokenAuth.
        :param str auth_uri: The auth uri to pass to JWTTokenAuth.
        :param callable get_token: The callback function used for getting and refreshing
        tokens. It should return a valid jwt token each time it is called.
        :param bytes token_type: Token type.
        :param Configuration config: EH config.

        :keyword bool update_token: Required. Whether to update token. If not updating token,
        then pass 300 to refresh_window.
        :return: An instance of JWTTokenAuth.
        :rtype: ~pyamqp.aio._authentication_async.JWTTokenAuthAsync
        """
        # TODO: figure out why we're passing all these args to pyamqp JWTTokenAuth, which aren't being used
        update_token = kwargs.pop("update_token")  # pylint: disable=unused-variable
        if update_token:
            # update_token not actually needed by pyamqp
            # just using to detect which args to pass
            return JWTTokenAuthAsync(auth_uri, auth_uri, get_token)
        return JWTTokenAuthAsync(
            auth_uri,
            auth_uri,
            get_token,
            token_type=token_type,
            timeout=config.auth_timeout,
            custom_endpoint_hostname=config.custom_endpoint_hostname,
            port=config.connection_port,
            verify=config.connection_verify,
        )

    @staticmethod
    async def mgmt_client_request_async(
        mgmt_client: "AMQPClientAsync",
        mgmt_msg: "Message",
        *,
        operation: bytes,
        operation_type: bytes,
        node: bytes,
        timeout: int,
        callback: Callable
    ) -> "ServiceBusReceivedMessage":
        """
        Send mgmt request.
        :param ~pyamqp.aio.AMQPClientAsync mgmt_client: Client to send request with.
        :param ~pyamqp.message.Message mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes node: Mgmt target.
        :keyword int timeout: Timeout.
        :keyword callable callback: Callback to process request response.
        :return: The result returned by the mgmt request.
        :rtype: ~azure.servicebus.ServiceBusReceivedMessage
        """
        status, description, response = await mgmt_client.mgmt_request_async(
            mgmt_msg,
            operation=amqp_string_value(operation.decode("UTF-8")),
            operation_type=amqp_string_value(operation_type),
            node=node,
            timeout=timeout,  # TODO: check if this should be seconds * 1000 if timeout else None,
        )
        return callback(status, response, description, amqp_transport=PyamqpTransportAsync)
