# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import asyncio
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Union, cast, TYPE_CHECKING

from ..._pyamqp import constants, error as errors
from ..._pyamqp.aio import AMQPClientAsync, SendClientAsync, ReceiveClientAsync
from ..._pyamqp.aio._authentication_async import JWTTokenAuthAsync
from ..._pyamqp.aio._connection_async import Connection as ConnectionAsync
from ..._pyamqp.endpoints import Source

from ._base_async import AmqpTransportAsync
from ..._transport._pyamqp_transport import PyamqpTransport
from ...exceptions import EventHubError, EventDataSendError, OperationTimeoutError
from ..._constants import MAX_BUFFER_LENGTH


if TYPE_CHECKING:
    from .._client_base_async import ClientBaseAsync, ConsumerProducerMixin
    from ..._pyamqp.message import Message

_LOGGER = logging.getLogger(__name__)


class PyamqpTransportAsync(PyamqpTransport, AmqpTransportAsync):
    """
    Class which defines pyamqp-based methods used by the producer and consumer.
    """

    @staticmethod
    async def create_connection_async(
        *,
        endpoint: str,
        auth: JWTTokenAuthAsync,
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
        Creates and returns the pyamqp Connection object.
        :keyword str endpoint: The endpoint, used by pyamqp.
        :keyword ~pyamqp.aio._authentication_async.JWTTokenAuthAsync auth: The auth, used by pyamqp.
        :keyword str container_id: Required.
        :keyword int max_frame_size: Required.
        :keyword int channel_max: Required.
        :keyword float idle_timeout: Required.
        :keyword dict[str, Any] or None properties: Required.
        :keyword float remote_idle_timeout_empty_frame_send_ratio: Required.
        :keyword error_policy: Required.
        :keyword bool debug: Required.
        :keyword str encoding: Required.

        :return: The created ConnectionAsync.
        :rtype: ~pyamqp.aio.Connection
        """
        network_trace = debug
        return ConnectionAsync(
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
    async def close_connection_async(connection):
        """
        Closes existing connection.
        :param ~pyamqp.aio.Connection connection: pyamqp Connection.
        """
        await connection.close()

    @staticmethod
    def create_send_client(
        *,
        config,
        target: str,
        auth: JWTTokenAuthAsync,  # type: ignore
        idle_timeout: Optional[float],
        network_trace: bool,
        retry_policy: Any,
        keep_alive_interval: int,
        client_name: str,
        link_properties: Optional[Dict[str, Any]],
        properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """
        Creates and returns the pyamqp SendClient.
        :keyword ~azure.eventhub._configuration.Configuration config: The configuration.

        :keyword str target: Required. The target.
        :keyword ~pyamqp.aio._authentication_async.JWTTokenAuthAsync auth: Required.
        :keyword int idle_timeout: Required.
        :keyword network_trace: Required.
        :keyword retry_policy: Required.
        :keyword keep_alive_interval: Required.
        :keyword str client_name: Required.
        :keyword dict link_properties: Required.
        :keyword dict[str, Any] or None properties: Required.

        :return: The created SendClientAsync.
        :rtype: ~pyamqp.aio.SendClientAsync
        """
        # TODO: extra passed in to pyamqp, but not used. should be used?
        msg_timeout = kwargs.pop("msg_timeout")  # pylint: disable=unused-variable  # TODO: not used by pyamqp?

        return SendClientAsync(
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
    async def send_messages_async(producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param producer: The producer with handler to send messages.
        :type producer: ~azure.eventhub.aio._producer_async.EventHubProducer
        :param int timeout_time: Timeout time.
        :param Exception last_exception: Exception to raise if message timed out. Only used by pyamqp transport.
        :param logging.Logger logger: Logger.
        """
        # pylint: disable=protected-access
        try:
            await producer._open()
            timeout = timeout_time - time.time() if timeout_time else 0
            await producer._handler.send_message_async(producer._unsent_events[0], timeout=timeout)
            producer._unsent_events = None
        except TimeoutError as exc:
            raise OperationTimeoutError(message=str(exc), details=exc) from exc

    @staticmethod
    def create_receive_client(
        *,
        config,
        source: Source,
        auth: JWTTokenAuthAsync,  # type: ignore
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
        :keyword ~pyamqp.aio._authentication_async.JWTTokenAuthAsync auth: Required.
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
        :keyword float timeout: Required.

        :return: The created ReceiveClientAsync.
        :rtype: ~pyamqp.aio.ReceiveClientAsync
        """
        return ReceiveClientAsync(
            config.hostname,
            source,
            receive_settle_mode=constants.ReceiverSettleMode.First,  # TODO: make more descriptive in pyamqp?
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
            keep_alive_interval=keep_alive_interval,
            desired_capabilities=desired_capabilities,
            streaming_receive=streaming_receive,
            message_received_callback=message_received_callback,
            timeout=timeout,
            use_tls=config.use_tls,
            **kwargs,
        )

    @staticmethod
    async def _callback_task(consumer, batch, max_batch_size, max_wait_time):
        # pylint: disable=protected-access
        while consumer._callback_task_run:
            async with consumer._message_buffer_lock:
                events = [
                    consumer._next_message_in_buffer()
                    for _ in range(min(max_batch_size, len(consumer._message_buffer)))
                ]
            now_time = time.time()
            if len(events) > 0:
                await consumer._on_event_received(events if batch else events[0])
                consumer._last_callback_called_time = now_time
            else:
                if max_wait_time and (now_time - consumer._last_callback_called_time) > max_wait_time:
                    # no events received, and need to callback
                    await consumer._on_event_received([] if batch else None)
                    consumer._last_callback_called_time = now_time
                # backoff a bit to avoid throttling CPU when no events are coming
                await asyncio.sleep(0.05)

    @staticmethod
    async def _receive_task(consumer, max_batch_size):
        # pylint:disable=protected-access
        max_retries = consumer._client._config.max_retries
        retried_times = 0
        running = True
        try:
            while retried_times <= max_retries and running and consumer._callback_task_run:
                try:
                    # set a default value of consumer._prefetch for buffer length
                    buff_length = MAX_BUFFER_LENGTH
                    await consumer._open()  # pylint: disable=protected-access
                    async with consumer._message_buffer_lock:
                        buff_length = len(consumer._message_buffer)
                    if buff_length <= max_batch_size:
                        running = await cast(ReceiveClientAsync, consumer._handler).do_work_async(
                            batch=consumer._prefetch
                        )
                    await asyncio.sleep(0.05)
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    raise
                except Exception as exception:  # pylint: disable=broad-except
                    # If optional dependency is not installed, do not retry.
                    if isinstance(exception, ImportError):
                        raise exception
                    if (
                        isinstance(exception, errors.AMQPLinkError)
                        and exception.condition == errors.ErrorCondition.LinkStolen  # pylint: disable=no-member
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
        finally:
            consumer._callback_task_run = False

    @staticmethod
    async def message_received_async(consumer, message: Message) -> None:
        async with consumer._message_buffer_lock:  # pylint: disable=protected-access
            consumer._message_buffer.append(message)  # pylint: disable=protected-access

    @staticmethod
    async def receive_messages_async(consumer, batch, max_batch_size, max_wait_time):
        """
        Receives messages, creates events, and returns them by calling the on received callback.
        :param ~azure.eventhub.aio._consumer_async.EventHubConsumer consumer: The EventHubConsumer.
        :param bool batch: If receive batch or single event.
        :param int max_batch_size: Max batch size.
        :param int max_wait_time: Max wait time.
        """
        # pylint:disable=protected-access
        consumer._callback_task_run = True
        consumer._last_callback_called_time = time.time()

        callback_task = asyncio.create_task(
            PyamqpTransportAsync._callback_task(consumer, batch, max_batch_size, max_wait_time)
        )
        receive_task = asyncio.create_task(PyamqpTransportAsync._receive_task(consumer, max_batch_size))

        tasks = [callback_task, receive_task]
        try:
            await asyncio.gather(*tasks)
        finally:
            consumer._callback_task_run = False
            for t in tasks:
                if not t.done():
                    await asyncio.wait([t], timeout=1)

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

        :return: The JWTTokenAuth.
        :rtype: ~pyamqp.aio._authentication_async.JWTTokenAuthAsync
        """
        # TODO: figure out why we're passing all these args to pyamqp JWTTokenAuth, which aren't being used
        if update_token:
            # update_token not actually needed by pyamqp
            # just using to detect wh
            return JWTTokenAuthAsync(auth_uri, auth_uri, get_token, token_type=token_type)
        return JWTTokenAuthAsync(
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
        :param ~pyamqp.aio._authentication_async.JWTTokenAuthAsync mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.

        :return: The created AMQPClientAsync.
        :rtype: ~pyamqp.aio.AMQPClientAsync
        """

        return AMQPClientAsync(
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
    async def get_updated_token_async(mgmt_auth):
        """
        Return updated auth token.
        :param ~pyamqp.aio._authentication_async.JWTTokenAuthAsync mgmt_auth: Auth.

        :return: The updated auth token.
        :rtype: str
        """
        return (await mgmt_auth.get_token()).token

    @staticmethod
    async def mgmt_client_request_async(
        mgmt_client: AMQPClientAsync,
        mgmt_msg: str,
        *,
        operation: bytes,
        operation_type: bytes,
        status_code_field: bytes,
        description_fields: bytes,
        **kwargs,
    ):
        """
        Send mgmt request.
        :param ~pyamqp.aio.AMQPClientAsync mgmt_client: Client to send request with.
        :param str mgmt_msg: Message.
        :keyword bytes operation: Operation.
        :keyword bytes operation_type: Op type.
        :keyword bytes status_code_field: mgmt status code.
        :keyword bytes description_fields: mgmt status desc.

        :return: The mgmt client.
        :rtype: ~pyamqp.aio.AMQPClientAsync
        """
        return await mgmt_client.mgmt_request_async(
            mgmt_msg,
            operation=operation.decode(),
            operation_type=operation_type.decode(),
            status_code_field=status_code_field,
            description_fields=description_fields,
            **kwargs,
        )

    @staticmethod
    async def _handle_exception_async(
        exception: Exception, closable: Union["ClientBaseAsync", "ConsumerProducerMixin"], *, is_consumer=False
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
            try:
                if isinstance(exception, errors.AuthenticationException):
                    await closable._close_connection_async()  # pylint:disable=protected-access
                elif isinstance(exception, errors.AMQPLinkError):
                    await cast(
                        "ConsumerProducerMixin", closable
                    )._close_handler_async()
                elif isinstance(exception, errors.AMQPConnectionError):
                    await closable._close_connection_async()  # pylint:disable=protected-access
                # TODO: add MessageHandlerError in amqp?
                # elif isinstance(exception, errors.MessageHandlerError):
                #     if hasattr(closable, "_close_handler"):
                #         closable._close_handler()
                else:  # errors.AMQPConnectionError, compat.TimeoutException
                    await closable._close_connection_async()  # pylint:disable=protected-access
                return PyamqpTransportAsync._create_eventhub_exception(exception, is_consumer=is_consumer)
            except AttributeError:
                pass
            return PyamqpTransportAsync._create_eventhub_exception(exception, is_consumer=is_consumer)
