# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import asyncio
import time
import logging
from typing import Union, cast, TYPE_CHECKING, Optional

from ..._pyamqp import constants, error as AMQPErrors
from ..._pyamqp.utils import amqp_string_value
from ..._pyamqp.aio import AMQPClientAsync, SendClientAsync, ReceiveClientAsync
from ..._pyamqp.aio._authentication_async import JWTTokenAuthAsync
from ..._pyamqp.aio._connection_async import Connection as ConnectionAsync

from ._base_async import AmqpTransportAsync
from ..._common.utils import utc_from_timestamp, utc_now
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
    from ..._pyamqp.message import Message
    from .._servicebus_receiver_async import ServiceBusReceiver as ServiceBusReceiverAsync
    from ..._common.message import ServiceBusReceivedMessage

_LOGGER = logging.getLogger(__name__)


class PyamqpTransportAsync(PyamqpTransport, AmqpTransportAsync):
    """
    Class which defines pyamqp-based methods used by the producer and consumer.
    """

    @staticmethod
    async def create_connection_async(host, auth, network_trace, **kwargs):
        """
        Creates and returns the pyamqp Connection object.
        :param str host: The hostname used by pyamqp.
        :param JWTTokenAuth auth: The auth used by pyamqp.
        :param bool network_trace: Debug setting.
        """
        return ConnectionAsync(
            endpoint=host,
            sasl_credential=auth.sasl,
            network_trace=network_trace,
            **kwargs
        )

    @staticmethod
    async def close_connection_async(connection):
        """
        Closes existing connection.
        :param connection: pyamqp Connection.
        """
        await connection.close()

    @staticmethod
    def create_send_client(config, **kwargs):
        """
        Creates and returns the pyamqp SendClient.
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
        return SendClientAsync(
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
    async def send_messages_async(producer, timeout_time, last_exception, logger):
        """
        Handles sending of event data messages.
        :param ~azure.eventhub._producer.EventHubProducer producer: The producer with handler to send messages.
        :param int timeout_time: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by pyamqp transport.
        :param logger: Logger.
        """
        # pylint: disable=protected-access
        try:
            await producer._open()
            timeout = timeout_time - time.time() if timeout_time else 0
            await producer._handler.send_message_async(producer._unsent_events[0], timeout=timeout)
            producer._unsent_events = None
        except TimeoutError as exc:
            raise OperationTimeoutError(message=str(exc), details=exc)

    @staticmethod
    def create_receive_client(*, config, **kwargs):  # pylint:disable=unused-argument
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
            **kwargs,
        )

    @staticmethod
    async def settle_message_via_receiver_link_async(
        handler: "ServiceBusReceiverAsync",
        message: "ServiceBusReceivedMessage",
        settle_operation: str,
        dead_letter_reason: Optional[str] = None,
        dead_letter_error_description: Optional[str] = None,
    ) -> None:
        if settle_operation == MESSAGE_COMPLETE:
            return await handler.settle_messages_async(message.delivery_id, 'accepted')
        if settle_operation == MESSAGE_ABANDON:
            return await handler.settle_messages_async(
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=False
            )
        if settle_operation == MESSAGE_DEAD_LETTER:
            return await handler.settle_messages_async(
                message.delivery_id,
                'rejected',
                error=AMQPErrors.AMQPError(
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
                message.delivery_id,
                'modified',
                delivery_failed=True,
                undeliverable_here=True
            )
        raise ValueError(
            f"Unsupported settle operation type: {settle_operation}"
        )

    @staticmethod
    async def on_attach_async(receiver, attach_frame):
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

    #@staticmethod
    #async def _callback_task(consumer, batch, max_batch_size, max_wait_time):
    #    while consumer._callback_task_run: # pylint: disable=protected-access
    #        async with consumer._message_buffer_lock: # pylint: disable=protected-access
    #            messages = [
    #                consumer._message_buffer.popleft() # pylint: disable=protected-access
    #                for _ in range(min(max_batch_size, len(consumer._message_buffer))) # pylint: disable=protected-access
    #            ]
    #        events = [EventData._from_message(message) for message in messages] # pylint: disable=protected-access
    #        now_time = time.time()
    #        if len(events) > 0:
    #            await consumer._on_event_received(events if batch else events[0]) # pylint: disable=protected-access
    #            consumer._last_callback_called_time = now_time # pylint: disable=protected-access
    #        else:
    #            if max_wait_time and (now_time - consumer._last_callback_called_time) > max_wait_time: # pylint: disable=protected-access
    #                # no events received, and need to callback
    #                await consumer._on_event_received([] if batch else None) # pylint: disable=protected-access
    #                consumer._last_callback_called_time = now_time # pylint: disable=protected-access
    #            # backoff a bit to avoid throttling CPU when no events are coming
    #            await asyncio.sleep(0.05)

    @staticmethod
    async def _receive_task(consumer):
        # pylint:disable=protected-access
        max_retries = consumer._client._config.max_retries
        retried_times = 0
        running = True
        try:
            while retried_times <= max_retries and running and consumer._callback_task_run:
                try:
                    await consumer._open() # pylint: disable=protected-access
                    running = await cast(ReceiveClientAsync, consumer._handler).do_work_async(batch=consumer._prefetch)
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    raise
                except Exception as exception:  # pylint: disable=broad-except
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
                        raise last_exception
        finally:
            consumer._callback_task_run = False

    @staticmethod
    async def message_received_async(consumer, message: Message) -> None:
        async with consumer._message_buffer_lock: # pylint: disable=protected-access
            consumer._message_buffer.append(message) # pylint: disable=protected-access

    @staticmethod
    async def receive_messages_async(consumer, batch, max_batch_size, max_wait_time):
        """
        Receives messages, creates events, and returns them by calling the on received callback.
        :param ~azure.eventhub.aio.EventHubConsumer consumer: The EventHubConsumer.
        :param bool batch: If receive batch or single event.
        :param int max_batch_size: Max batch size.
        :param int or None max_wait_time: Max wait time.
        """
        # pylint:disable=protected-access
        consumer._callback_task_run = True
        consumer._last_callback_called_time = time.time()
        callback_task = asyncio.create_task(
            PyamqpTransportAsync._callback_task(consumer, batch, max_batch_size, max_wait_time)
        )
        receive_task = asyncio.create_task(PyamqpTransportAsync._receive_task(consumer))

        tasks = [callback_task, receive_task]
        try:
            await asyncio.gather(*tasks)
        finally:
            consumer._callback_task_run = False
            for t in tasks:
                if not t.done():
                    await asyncio.wait([t], timeout=1)

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
        # TODO: figure out why we're passing all these args to pyamqp JWTTokenAuth, which aren't being used
        update_token = kwargs.pop("update_token")  # pylint: disable=unused-variable
        if update_token:
            # update_token not actually needed by pyamqp
            # just using to detect wh
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
        # if update_token:
        #    token_auth.update_token()  # TODO: why don't we need to update in pyamqp?

    @staticmethod
    def create_mgmt_client(address, mgmt_auth, config):  # pylint: disable=unused-argument
        """
        Creates and returns the mgmt AMQP client.
        :param _Address address: Required. The Address.
        :param JWTTokenAuth mgmt_auth: Auth for client.
        :param ~azure.eventhub._configuration.Configuration config: The configuration.
        """

        return AMQPClientAsync(
            config.hostname,
            auth=mgmt_auth,
            network_trace=config.network_tracing,
            transport_type=config.transport_type,
            http_proxy=config.http_proxy,
            custom_endpoint_address=config.custom_endpoint_address,
            connection_verify=config.connection_verify,
        )

    @staticmethod
    async def get_updated_token_async(mgmt_auth):
        """
        Return updated auth token.
        :param mgmt_auth: Auth.
        """
        return await mgmt_auth.get_token()

    @staticmethod
    async def mgmt_client_request_async(
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
        status, description, response = await mgmt_client.mgmt_request_async(
            mgmt_msg,
            operation=amqp_string_value(operation.decode("UTF-8")),
            operation_type=amqp_string_value(operation_type),
            node=node,
            timeout=timeout,  # TODO: check if this should be seconds * 1000 if timeout else None,
        )
        return callback(status, response, description, amqp_transport=PyamqpTransportAsync)
