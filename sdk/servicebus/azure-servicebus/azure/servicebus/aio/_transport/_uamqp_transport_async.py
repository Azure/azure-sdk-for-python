# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import functools
from typing import TYPE_CHECKING, Optional, Any, Callable, Union, AsyncIterator, cast

try:
    from uamqp import (
        constants,
        SendClientAsync,
        ReceiveClientAsync,
    )
    from uamqp.authentication import JWTTokenAsync as JWTTokenAuthAsync
    from uamqp.async_ops import ConnectionAsync
    from ..._transport._uamqp_transport import UamqpTransport
    from ._base_async import AmqpTransportAsync
    from .._async_utils import get_running_loop
    from ..._common.tracing import get_receive_links, receive_trace_context_manager
    from ..._common.constants import ServiceBusReceiveMode

    if TYPE_CHECKING:
        from uamqp import AMQPClientAsync, Message
        from logging import Logger
        from .._servicebus_receiver_async import ServiceBusReceiver
        from .._servicebus_sender_async import ServiceBusSender
        from ..._common.message import ServiceBusReceivedMessage, ServiceBusMessage, ServiceBusMessageBatch
        from ..._common._configuration import Configuration


    class UamqpTransportAsync(UamqpTransport, AmqpTransportAsync):
        """
        Class which defines uamqp-based methods used by the sender and receiver.
        """

        @staticmethod
        async def create_connection_async(
            host: str, auth: "JWTTokenAuthAsync", network_trace: bool, **kwargs: Any
        ) -> "ConnectionAsync":
            """
            Creates and returns the uamqp Connection object.
            :param str host: The hostname, used by uamqp.
            :param ~uamqp.authentication.JWTTokenAuth auth: The auth, used by uamqp.
            :param bool network_trace: Required.
            :return: An instance of ConnectionAsync.
            :rtype: ~uamqp.async_ops.ConnectionAsync
            """
            custom_endpoint_address = kwargs.pop("custom_endpoint_address") # pylint:disable=unused-variable
            ssl_opts = kwargs.pop("ssl_opts") # pylint:disable=unused-variable
            transport_type = kwargs.pop("transport_type") # pylint:disable=unused-variable
            http_proxy = kwargs.pop("http_proxy") # pylint:disable=unused-variable
            return ConnectionAsync(
                hostname=host,
                sasl=auth,
                debug=network_trace,
            )

        @staticmethod
        async def close_connection_async(connection: "ConnectionAsync") -> None:
            """
            Closes existing connection.
            :param ~uamqp.async_ops.ConnectionAsync connection: uamqp Connection.
            """
            await connection.destroy_async()

        @staticmethod
        def create_send_client_async(
            config: "Configuration", **kwargs: Any
        ) -> "SendClientAsync":
            """
            Creates and returns the uamqp SendClient.
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

            :return: An instance of SendClient.
            :rtype: ~uamqp.aio.SendClientAsync
            """
            target = kwargs.pop("target")
            retry_policy = kwargs.pop("retry_policy")

            return SendClientAsync(
                target,
                debug=config.logging_enable,
                error_policy=retry_policy,
                keep_alive_interval=config.keep_alive,
                encoding=config.encoding,
                **kwargs
            )

        @staticmethod
        async def send_messages_async(
            sender: "ServiceBusSender",
            message: Union["ServiceBusMessage", "ServiceBusMessageBatch"],
            logger: "Logger",
            timeout: int,
            last_exception: Optional[Exception]
        ) -> None:
            """
            Handles sending of service bus messages.
            :param ServiceBusSender sender: The sender with handler to send messages.
            :param message: ServiceBusMessage with uamqp.Message to be sent.
            :type message: ~azure.servicebus.ServiceBusMessage or ~azure.servicebus.ServiceBusMessageBatch
            :param int timeout: Timeout time.
            :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
            :param Logger logger: Logger.
            """
            # pylint: disable=protected-access
            await sender._open()
            default_timeout = cast("SendClientAsync", sender._handler)._msg_timeout
            try:
                UamqpTransportAsync.set_msg_timeout(sender, logger, timeout, last_exception)
                await cast("SendClientAsync", sender._handler).send_message_async(message._message)
            finally:  # reset the timeout of )the handler back to the default value
                UamqpTransportAsync.set_msg_timeout(sender, logger, default_timeout, None)

        @staticmethod
        def create_receive_client_async(
            receiver: "ServiceBusReceiver", **kwargs: Any
        ) -> "ReceiveClientAsync":
            """
            Creates and returns the receive client.
            :param ~auzre.servicebus.aio.ServiceBusReceiver receiver: The receiver.

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

            :return: An instance of ReceiveClientAsync.
            :rtype: ~uamqp.ReceiveClientAsync
            """
            source = kwargs.pop("source")
            retry_policy = kwargs.pop("retry_policy")
            network_trace = kwargs.pop("network_trace")
            link_credit = kwargs.pop("link_credit")
            receive_mode = kwargs.pop("receive_mode")

            return ReceiveClientAsync(
                source,
                debug=network_trace,  # pylint:disable=protected-access
                error_policy=retry_policy,
                prefetch=link_credit,
                auto_complete=False,
                receive_settle_mode=UamqpTransportAsync.ServiceBusToAMQPReceiveModeMap[receive_mode],
                send_settle_mode=constants.SenderSettleMode.Settled
                if receive_mode == ServiceBusReceiveMode.RECEIVE_AND_DELETE
                else None,
                on_attach=functools.partial(
                    UamqpTransportAsync.on_attach,
                    receiver
                ),
                **kwargs
            )

        @staticmethod
        async def iter_contextual_wrapper_async(
            receiver: "ServiceBusReceiver", max_wait_time: Optional[int] = None
        ) -> AsyncIterator["ServiceBusReceivedMessage"]:
            """The purpose of this wrapper is to allow both state restoration (for multiple concurrent iteration)
            and per-iter argument passing that requires the former.

            :param receiver: The receiver.
            :type receiver: ~azure.servicebus.aio.ServiceBusReceiver
            :param max_wait_time: The maximum amount of time to wait for messages, in seconds.
            :type max_wait_time: int or None
            :return: An iterator of messages.
            :rtype: asynciterator[~azure.servicebus.aio.ServiceBusReceivedMessage]
            """
            # pylint: disable=protected-access
            original_timeout = None
            while True:
                # This is not threadsafe, but gives us a way to handle if someone passes
                # different max_wait_times to different iterators and uses them in concert.
                if max_wait_time:
                    original_timeout = receiver._handler._timeout
                    receiver._handler._timeout = max_wait_time * UamqpTransport.TIMEOUT_FACTOR
                try:
                    message = await receiver._inner_anext()
                    links = get_receive_links(message)
                    with receive_trace_context_manager(receiver, links=links):
                        yield message
                except StopAsyncIteration:
                    break
                finally:
                    if original_timeout:
                        try:
                            receiver._handler._timeout = original_timeout
                        except AttributeError:  # Handler may be disposed already.
                            pass

        # wait_time used by pyamqp
        @staticmethod
        async def iter_next_async(
            receiver: "ServiceBusReceiver", wait_time: Optional[int] = None
        ) -> "ServiceBusReceivedMessage": # pylint: disable=unused-argument
            # pylint: disable=protected-access
            try:
                receiver._receive_context.set()
                await receiver._open()
                if not receiver._message_iter:
                    receiver._message_iter = receiver._handler.receive_messages_iter_async()
                uamqp_message = await cast(AsyncIterator["Message"], receiver._message_iter).__anext__()
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

        # called by async ServiceBusReceiver
        enhanced_message_received_async = UamqpTransport.enhanced_message_received

        @staticmethod
        def set_handler_message_received_async(receiver: "ServiceBusReceiver") -> None:
            # reassigning default _message_received method in ReceiveClient
            # pylint: disable=protected-access
            receiver._handler._message_received = functools.partial(  # type: ignore[assignment]
                UamqpTransportAsync.enhanced_message_received_async,
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
            await handler.message_handler.reset_link_credit_async(link_credit)

        @staticmethod
        async def settle_message_via_receiver_link_async(
            handler: "ReceiveClientAsync",
            message: "ServiceBusReceivedMessage",
            settle_operation: str,
            dead_letter_reason: Optional[str] = None,
            dead_letter_error_description: Optional[str] = None,
        ) -> None:  # pylint: disable=unused-argument
            await get_running_loop().run_in_executor(
                None,
                UamqpTransportAsync.settle_message_via_receiver_link_impl(
                    handler,
                    message,
                    settle_operation,
                    dead_letter_reason,
                    dead_letter_error_description
                ),
            )

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
            :rtype: ~uamqp.authentication.JWTTokenAuth
            """
            update_token = kwargs.pop("update_token")
            refresh_window = 0 if update_token else 300

            token_auth = JWTTokenAuthAsync(
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
                await token_auth.update_token()
            return token_auth

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
            :param ~uamqp.AMQPClient mgmt_client: Client to send request with.
            :param ~uamqp.Message mgmt_msg: Message.
            :keyword bytes operation: Operation.
            :keyword bytes operation_type: Op type.
            :keyword bytes node: Mgmt target.
            :keyword int timeout: Timeout.
            :keyword callable callback: Callback to process request response.
            :return: The received mgmt response.
            :rtype: ~azure.servicebus.ServiceBusReceivedMessage
            """
            return await mgmt_client.mgmt_request_async(
                mgmt_msg,
                operation,
                op_type=operation_type,
                node=node,
                timeout=timeout * UamqpTransportAsync.TIMEOUT_FACTOR if timeout else None,
                callback=functools.partial(callback, amqp_transport=UamqpTransportAsync)
            )
except ImportError:
    pass
