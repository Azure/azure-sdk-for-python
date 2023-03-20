# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations
import functools
from typing import TYPE_CHECKING, Optional

from ..._pyamqp import constants
from ..._pyamqp.message import BatchMessage
from ..._pyamqp.utils import amqp_string_value
from ..._pyamqp.aio import AMQPClientAsync, SendClientAsync, ReceiveClientAsync
from ..._pyamqp.aio._authentication_async import JWTTokenAuthAsync
from ..._pyamqp.aio._connection_async import Connection as ConnectionAsync
from ..._pyamqp.error import (
    AMQPError,
    MessageException,
)

from ._base_async import AmqpTransportAsync
from ..._common.utils import (
    utc_from_timestamp,
    utc_now,
    get_receive_links,
    receive_trace_context_manager
)
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
    async def send_messages_async(sender, message, logger, timeout, last_exception):
        """
        Handles sending of service bus messages.
        :param sender: The sender with handler to send messages.
        :param int timeout: Timeout time.
        :param last_exception: Exception to raise if message timed out. Only used by uamqp transport.
        :param logger: Logger.
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
        except TimeoutError:
            raise OperationTimeoutError(message="Send operation timed out")
        except MessageException as e:
            raise PyamqpTransportAsync.create_servicebus_exception(logger, e)

    @staticmethod
    def create_receive_client(receiver, **kwargs):  # pylint:disable=unused-argument
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
            **kwargs,
        )

    @staticmethod
    async def iter_contextual_wrapper_async(receiver, max_wait_time=None):
        while True:
            try:
                message = await receiver._inner_anext(wait_time=max_wait_time)
                links = get_receive_links(message)
                with receive_trace_context_manager(receiver, links=links):
                    yield message
            except StopAsyncIteration:
                break

    @staticmethod
    async def iter_next_async(receiver, wait_time=None): # pylint: disable=protected-access
        try:
            receiver._receive_context.set()
            await receiver._open()
            if not receiver._message_iter or wait_time:
                receiver._message_iter = await receiver._handler.receive_messages_iter_async(timeout=wait_time)
            pyamqp_message = await receiver._message_iter.__anext__()
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
    async def reset_link_credit_async(handler, link_credit):
        """
        Resets the link credit on the link.
        :param ReceiveClientAsync handler: Client with link to reset link credit.
        :param int link_credit: Link credit needed.
        :rtype: None
        """
        await handler._link.flow(link_credit=link_credit)   # pylint: disable=protected-access

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

    @staticmethod
    async def message_received_async(consumer, message: Message) -> None:
        async with consumer._message_buffer_lock: # pylint: disable=protected-access
            consumer._message_buffer.append(message) # pylint: disable=protected-access

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
