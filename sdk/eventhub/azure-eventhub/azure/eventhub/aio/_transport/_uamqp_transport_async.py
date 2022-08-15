# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import asyncio
import time
import logging
from typing import Union, cast, TYPE_CHECKING, List

from uamqp import (
    constants,
    types,
    SendClientAsync,
    ReceiveClientAsync,
    utils,
    authentication,
    AMQPClientAsync,
    errors,
)
from uamqp.async_ops import ConnectionAsync

from ._base_async import AmqpTransportAsync
from ..._transport._uamqp_transport import UamqpTransport
from ...exceptions import (
    OperationTimeoutError,
    EventHubError,
    EventDataError,
    EventDataSendError,
)

if TYPE_CHECKING:
    from .._client_base_async import ClientBaseAsync, ConsumerProducerMixin
    from ..._common import EventData

_LOGGER = logging.getLogger(__name__)

class UamqpTransportAsync(UamqpTransport, AmqpTransportAsync):
    """
    Class which defines uamqp-based methods used by the producer and consumer.
    """

    @staticmethod
    async def create_connection_async(**kwargs):
        """
        Creates and returns the uamqp async Connection object.
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
        host = kwargs.pop("host")
        auth = kwargs.pop("auth")
        return ConnectionAsync(
            host,
            auth,
            **kwargs
        )

    @staticmethod
    async def close_connection_async(connection):
        """
        Closes existing connection.
        :param connection: uamqp or pyamqp Connection.
        """
        await connection.destroy_async()

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

        return SendClientAsync(
            target,
            debug=network_trace,  # pylint:disable=protected-access
            error_policy=retry_policy,
            **kwargs
        )

    @staticmethod
    async def send_messages_async(producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
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
    def create_receive_client(*, config, **kwargs): # pylint:disable=unused-argument
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

        client = ReceiveClientAsync(
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
    async def receive_messages(consumer, batch, max_batch_size, max_wait_time):
        """
        Receives messages, creates events, and returns them by calling the on received callback.
        :param ~azure.eventhub.aio.EventHubConsumer consumer: The EventHubConsumer.
        :param bool batch: If receive batch or single event.
        :param int max_batch_size: Max batch size.
        :param int or None max_wait_time: Max wait time.
        """
        # pylint:disable=protected-access
        max_retries = (
            consumer._client._config.max_retries  # pylint:disable=protected-access
        )
        has_not_fetched_once = True  # ensure one trip when max_wait_time is very small
        deadline = time.time() + (max_wait_time or 0)  # max_wait_time can be None
        while len(consumer._message_buffer) < max_batch_size and (
            time.time() < deadline or has_not_fetched_once
        ):
            retried_times = 0
            has_not_fetched_once = False
            while retried_times <= max_retries:
                try:
                    await consumer._open()
                    await cast(
                        ReceiveClientAsync, consumer._consumer
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
                        raise last_exception

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
    async def create_token_auth_async(auth_uri, get_token, token_type, config, **kwargs):
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
            refresh_window=refresh_window
        )
        if update_token:
            await token_auth.update_token()
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
        return AMQPClientAsync(
            mgmt_target,
            auth=mgmt_auth,
            debug=config.network_tracing
        )

    @staticmethod
    async def get_updated_token_async(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """
        return mgmt_auth.token

    @staticmethod
    async def mgmt_client_request_async(mgmt_client, mgmt_msg, **kwargs):
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
        return await mgmt_client.mgmt_request_async(
            mgmt_msg,
            operation,
            op_type=operation_type,
            **kwargs
        )

    @staticmethod
    async def _handle_exception_async(  # pylint:disable=too-many-branches, too-many-statements
        exception: Exception, closable: Union["ClientBaseAsync", "ConsumerProducerMixin"]
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
