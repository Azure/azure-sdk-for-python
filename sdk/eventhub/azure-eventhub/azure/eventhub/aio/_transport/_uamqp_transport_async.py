# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import asyncio
import time
import logging
from typing import Callable, Dict, Union, cast, TYPE_CHECKING, List, Optional, Any

try:
    from uamqp import (
        constants,
        types,
        SendClientAsync,
        ReceiveClientAsync,
        utils,
        authentication,
        AMQPClientAsync,
        Source,
        errors,
    )
    from uamqp.async_ops import ConnectionAsync
    from ..._transport._uamqp_transport import UamqpTransport

    uamqp_installed = True
except ImportError:
    uamqp_installed = False

from ._base_async import AmqpTransportAsync
from ...exceptions import (
    OperationTimeoutError,
    EventHubError,
    EventDataError,
    EventDataSendError,
)

if TYPE_CHECKING:
    from .._client_base_async import ClientBaseAsync, ConsumerProducerMixin
    from ..._consumer_async import EventHubConsumer
    from ..._common import EventData

    try:
        from uamqp import Message
    except ImportError:
        Message = None

_LOGGER = logging.getLogger(__name__)

if uamqp_installed:

    class UamqpTransportAsync(UamqpTransport, AmqpTransportAsync):
        """
        Class which defines uamqp-based methods used by the producer and consumer.
        """

        @staticmethod
        async def create_connection_async(
            *,
            endpoint: str,
            auth: authentication.JWTTokenAuth,
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
        ) -> ConnectionAsync:
            """
            Creates and returns the uamqp async Connection object.
            :keyword str endpoint: The endpoint, used by pyamqp.
            :keyword ~uamqp.authentication.JWTTokenAsync auth: The auth, used by uamqp.
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
            :rtype: ~uamqp.async_ops.ConnectionAsync
            """
            return ConnectionAsync(
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
        async def close_connection_async(connection):
            """
            Closes existing connection.
            :param ~uamqp.async_ops.ConnectionAsync connection: uamqp Connection.
            """
            await connection.destroy_async()

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
            :keyword ~uamqp.authentication.JWTTokenAsync auth: Required.
            :keyword int idle_timeout: Required.
            :keyword network_trace: Required.
            :keyword retry_policy: Required.
            :keyword keep_alive_interval: Required.
            :keyword str client_name: Required.
            :keyword dict link_properties: Required.
            :keyword dict[str, Any] or None properties: Required.

            :return: The send client.
            :rtype: ~uamqp.SendClientAsync
            """
            return SendClientAsync(
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
        async def send_messages_async(producer, timeout_time, last_exception, logger):
            """
            Handles sending of event data messages.
            :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
            :param int timeout_time: Timeout time.
            :param Exception last_exception: Exception to raise if message timed out. Only used by uamqp transport.
            :param logging.Logger logger: Logger.
            """
            # pylint: disable=protected-access
            await producer._open()
            producer._unsent_events[0].on_send_complete = producer._on_outcome
            UamqpTransportAsync._set_msg_timeout(producer, timeout_time, last_exception, logger)
            producer._handler.queue_message(*producer._unsent_events)  # type: ignore
            await producer._handler.wait_async()  # type: ignore
            producer._unsent_events = producer._handler.pending_messages  # type: ignore
            if producer._outcome != constants.MessageSendResult.Ok:
                if producer._outcome == constants.MessageSendResult.Timeout:
                    producer._condition = OperationTimeoutError("Send operation timed out")
                if producer._condition:
                    raise producer._condition

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

            :return: The receive client.
            :rtype: ~uamqp.ReceiveClientAsync
            """
            symbol_array = desired_capabilities
            desired_capabilities = None
            if symbol_array:
                symbol_array = [types.AMQPSymbol(symbol) for symbol in symbol_array]
                desired_capabilities = utils.data_factory(types.AMQPArray(symbol_array))

            client = ReceiveClientAsync(
                source,
                debug=network_trace,
                error_policy=retry_policy,
                desired_capabilities=desired_capabilities,
                prefetch=link_credit,
                receive_settle_mode=constants.ReceiverSettleMode.ReceiveAndDelete,
                auto_complete=False,
                client_name=client_name,
                properties=properties,
                link_properties=link_properties,
                idle_timeout=idle_timeout,
                auth=auth,
                keep_alive_interval=keep_alive_interval,
                timeout=timeout,
                **kwargs,
            )
            # pylint:disable=protected-access
            client._streaming_receive = streaming_receive
            client._message_received_callback = message_received_callback
            return client

        @staticmethod
        def message_received_async(consumer, message: "Message") -> None:
            consumer._message_buffer.append(message)  # pylint: disable=protected-access

        @staticmethod
        async def receive_messages_async(
            consumer: "EventHubConsumer", batch: bool, max_batch_size: int, max_wait_time: Optional[int] = None
        ):
            """
            Receives messages, creates events, and returns them by calling the on received callback.
            :param ~azure.eventhub.aio.EventHubConsumer consumer: The EventHubConsumer.
            :param bool batch: If receive batch or single event.
            :param int max_batch_size: Max batch size.
            :param int or None max_wait_time: Max wait time.
            """
            # pylint:disable=protected-access
            max_retries = consumer._client._config.max_retries  # pylint:disable=protected-access
            has_not_fetched_once = True  # ensure one trip when max_wait_time is very small
            deadline = time.time() + (max_wait_time or 0)  # max_wait_time can be None
            while len(consumer._message_buffer) < max_batch_size and (time.time() < deadline or has_not_fetched_once):
                retried_times = 0
                has_not_fetched_once = False
                while retried_times <= max_retries:
                    try:
                        await consumer._open()
                        await cast(
                            ReceiveClientAsync, consumer._handler
                        ).do_work_async()  # uamqp sleeps 0.05 if none received
                        break
                    except asyncio.CancelledError:  # pylint: disable=try-except-raise
                        raise
                    except Exception as exception:  # pylint: disable=broad-except
                        if (
                            isinstance(exception, errors.LinkDetach)
                            and exception.condition == constants.ErrorCodes.LinkStolen  # pylint: disable=no-member
                        ):
                            raise await consumer._handle_exception(exception)
                        if not consumer.running:  # exit by close
                            return
                        if consumer._last_received_event:
                            consumer._offset = consumer._last_received_event.offset
                        last_exception = await consumer._handle_exception(exception)
                        retried_times += 1
                        if retried_times > max_retries:
                            _LOGGER.info(
                                "%r operation has exhausted retry. Last exception: %r.",
                                consumer._name,
                                last_exception,
                            )
                            raise last_exception from None

            if consumer._message_buffer:
                while consumer._message_buffer:
                    if batch:
                        events_for_callback: List[EventData] = []
                        for _ in range(min(max_batch_size, len(consumer._message_buffer))):
                            events_for_callback.append(consumer._next_message_in_buffer())
                        await consumer._on_event_received(events_for_callback)
                    else:
                        await consumer._on_event_received(consumer._next_message_in_buffer())
            elif max_wait_time:
                if batch:
                    await consumer._on_event_received([])
                else:
                    await consumer._on_event_received(None)

        @staticmethod
        async def create_token_auth_async(
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

            :return: A JWTTokenAsync instance.
            :rtype: ~uamqp.authentication.JWTTokenAsync
            """
            refresh_window = 300
            if update_token:
                refresh_window = 0

            token_auth = authentication.JWTTokenAsync(
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
                await token_auth.update_token()
            return token_auth

        @staticmethod
        def create_mgmt_client(address, mgmt_auth, config):
            """
            Creates and returns the mgmt AMQP client.
            :param _Address address: Required. The Address.
            :param ~uamqp.authentication.JWTTokenAsync mgmt_auth: Auth for client.
            :param ~azure.eventhub._configuration.Configuration config: The configuration.

            :return: The mgmt AMQP client.
            :rtype: ~uamqp.AMQPClientAsync
            """

            mgmt_target = f"amqps://{address.hostname}{address.path}"
            return AMQPClientAsync(mgmt_target, auth=mgmt_auth, debug=config.network_tracing)

        @staticmethod
        async def get_updated_token_async(mgmt_auth):
            """
            Return updated auth token.
            :param ~uamqp.authentication.JWTTokenAuth mgmt_auth: Auth.
            :return: Updated token.
            :rtype: str
            """
            return mgmt_auth.token

        @staticmethod
        async def open_mgmt_client_async(mgmt_client, conn):
            """
            Opens the mgmt AMQP client.
            :param ~uamqp.AMQPClientAsync mgmt_client: uamqp AMQPClient.
            :param ~uamqp.async_ops.ConnectionAsync conn: Connection.
            """
            await mgmt_client.open_async(connection=conn)

        @staticmethod
        async def mgmt_client_request_async(
            mgmt_client: AMQPClientAsync,
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
            :param ~uamqp.AMQPClient mgmt_client: Client to send request with.
            :param str mgmt_msg: Message.
            :keyword bytes operation: Operation.
            :keyword bytes operation_type: Op type.
            :keyword bytes status_code_field: mgmt status code.
            :keyword bytes description_fields: mgmt status desc.

            :return: Status code, description, response.
            :rtype: tuple
            """
            response = await mgmt_client.mgmt_request_async(
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
        async def _handle_exception_async(
            exception: Exception,
            closable: Union["ClientBaseAsync", "ConsumerProducerMixin"],
            *,
            is_consumer=False,  # pylint:disable=unused-argument
        ) -> Exception:
            # pylint: disable=protected-access
            if isinstance(exception, asyncio.CancelledError):
                raise exception
            error = exception
            try:
                name = cast("ConsumerProducerMixin", closable)._name
            except AttributeError:
                name = cast("ClientBaseAsync", closable)._container_id
            if isinstance(exception, KeyboardInterrupt):  # pylint:disable=no-else-raise
                _LOGGER.info("%r stops due to keyboard interrupt", name)
                await cast("ConsumerProducerMixin", closable)._close_connection_async()
                raise error
            elif isinstance(exception, EventHubError):
                await cast("ConsumerProducerMixin", closable)._close_handler_async()
                raise error
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
                try:
                    if isinstance(exception, errors.AuthenticationException):
                        await closable._close_connection_async()
                    elif isinstance(exception, errors.LinkDetach):
                        await cast("ConsumerProducerMixin", closable)._close_handler_async()
                    elif isinstance(exception, errors.ConnectionClose):
                        await closable._close_connection_async()
                    elif isinstance(exception, errors.MessageHandlerError):
                        await cast("ConsumerProducerMixin", closable)._close_handler_async()
                    else:  # errors.AMQPConnectionError, compat.TimeoutException, and any other errors
                        await closable._close_connection_async()
                except AttributeError:
                    pass
                return UamqpTransport._create_eventhub_exception(exception)
