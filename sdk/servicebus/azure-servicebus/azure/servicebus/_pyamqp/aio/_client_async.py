#-------------------------------------------------------------------------  # pylint: disable=client-suffix-needed
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
# TODO: Check types of kwargs (issue exists for this)
# pylint: disable=too-many-lines
import asyncio
import logging
import time
import queue
from functools import partial
from typing import Any, Callable, Coroutine, List, Dict, Optional, Tuple, Union, overload, cast
from typing_extensions import Literal
import certifi

from ..outcomes import Accepted, Modified, Received, Rejected, Released
from ._connection_async import Connection
from ._management_operation_async import ManagementOperation
from ._cbs_async import CBSAuthenticator
from ..client import (
    AMQPClient as AMQPClientSync,
    ReceiveClient as ReceiveClientSync,
    SendClient as SendClientSync,
    Outcomes
)
from ..message import _MessageDelivery, Message
from ..constants import (
    MessageDeliveryState,
    SEND_DISPOSITION_ACCEPT,
    SEND_DISPOSITION_REJECT,
    LinkDeliverySettleReason,
    MESSAGE_DELIVERY_DONE_STATES,
    AUTH_TYPE_CBS,
)
from ..error import (
    AMQPError,
    ErrorCondition,
    AMQPException,
    MessageException
)

_logger = logging.getLogger(__name__)


class AMQPClientAsync(AMQPClientSync):
    """An asynchronous AMQP client.

    :param hostname: The AMQP endpoint to connect to.
    :type hostname: str
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the Event Hubs service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    :keyword float socket_timeout: The maximum time in seconds that the underlying socket in the transport should
     wait when reading or writing data before timing out. The default value is 0.2 (for transport type Amqp),
     and 1 for transport type AmqpOverWebsocket.
    """

    def __init__(self, hostname, **kwargs):
        self._mgmt_link_lock_async = asyncio.Lock()
        super().__init__(hostname,**kwargs)


    async def _keep_alive_async(self):
        start_time = time.time()
        try:
            while self._connection and not self._shutdown:
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time >= self._keep_alive_interval:
                    await asyncio.shield(self._connection.listen(wait=self._socket_timeout,
                        batch=self._link.current_link_credit))
                    start_time = current_time
                await asyncio.sleep(1)
        except Exception as e:  # pylint: disable=broad-except
            _logger.info(
                "Connection keep-alive for %r failed: %r.",
                self.__class__.__name__,
                e,
                extra=self._network_trace_params
            )

    async def __aenter__(self):
        """Run Client in an async context manager.
        :return: The Client object.
        :rtype: ~pyamqp.AMQPClient
        """
        await self.open_async()
        return self

    async def __aexit__(self, *args):
        """Close and destroy Client on exiting an async context manager.
        :param any args: Ignored.
        """
        await self.close_async()

    async def _client_ready_async(self):
        """Determine whether the client is ready to start sending and/or
        receiving messages. To be ready, the connection must be open and
        authentication complete.

        :return: Whether or not the client is ready for operation.
        :rtype: bool
        """
        return True

    async def _client_run_async(self, **kwargs):
        """Perform a single Connection iteration."""
        await self._connection.listen(wait=self._socket_timeout, **kwargs)

    async def _close_link_async(self):
        if self._link and not self._link._is_closed: # pylint: disable=protected-access
            await self._link.detach(close=True)
            self._link = None

    async def _do_retryable_operation_async(self, operation, *args, **kwargs):
        retry_settings = self._retry_policy.configure_retries()
        retry_active = True
        absolute_timeout = kwargs.pop("timeout", 0) or 0
        start_time = time.time()
        while retry_active:
            try:
                if absolute_timeout < 0:
                    raise TimeoutError("Operation timed out.")
                return await operation(*args, timeout=absolute_timeout, **kwargs)
            except AMQPException as exc:
                if not self._retry_policy.is_retryable(exc):
                    raise
                if absolute_timeout >= 0:
                    retry_active = self._retry_policy.increment(retry_settings, exc)
                    if not retry_active:
                        break
                    await asyncio.sleep(self._retry_policy.get_backoff_time(retry_settings, exc))
                    if exc.condition == ErrorCondition.LinkDetachForced:
                        await self._close_link_async()  # if link level error, close and open a new link
                    if exc.condition in (ErrorCondition.ConnectionCloseForced, ErrorCondition.SocketError):
                        # if connection detach or socket error, close and open a new connection
                        await self.close_async()
            finally:
                end_time = time.time()
                if absolute_timeout > 0:
                    absolute_timeout -= (end_time - start_time)
        raise retry_settings['history'][-1]

    async def open_async(self, connection=None):
        """Asynchronously open the client. The client can create a new Connection
        or an existing Connection can be passed in. This existing Connection
        may have an existing CBS authentication Session, which will be
        used for this client as well. Otherwise a new Session will be
        created.

        :param connection: An existing Connection that may be shared between
         multiple clients.
        :type connection: ~pyamqp.aio.Connection
        """
        # pylint: disable=protected-access
        if self._session:
            return  # already open.
        if connection:
            self._connection = connection
            self._external_connection = True
        if not self._connection:
            self._connection = Connection(
                "amqps://" + self._hostname,
                sasl_credential=self._auth.sasl,
                ssl_opts={'ca_certs': self._connection_verify or certifi.where()},
                container_id=self._name,
                max_frame_size=self._max_frame_size,
                channel_max=self._channel_max,
                idle_timeout=self._idle_timeout,
                properties=self._properties,
                network_trace=self._network_trace,
                transport_type=self._transport_type,
                http_proxy=self._http_proxy,
                custom_endpoint_address=self._custom_endpoint_address,
                socket_timeout=self._socket_timeout,
            )
            await self._connection.open()
        if not self._session:
            self._session = self._connection.create_session(
                incoming_window=self._incoming_window,
                outgoing_window=self._outgoing_window
            )
            await self._session.begin()
        if self._auth.auth_type == AUTH_TYPE_CBS:
            self._cbs_authenticator = CBSAuthenticator(
                session=self._session,
                auth=self._auth,
                auth_timeout=self._auth_timeout
            )
            await self._cbs_authenticator.open()
        self._network_trace_params["amqpConnection"] = self._connection._container_id
        self._network_trace_params["amqpSession"] = self._session.name
        self._shutdown = False

        if self._keep_alive_interval:
            self._keep_alive_thread = asyncio.ensure_future(self._keep_alive_async())

    async def close_async(self):
        """Close the client asynchronously. This includes closing the Session
        and CBS authentication layer as well as the Connection.
        If the client was opened using an external Connection,
        this will be left intact.
        """
        self._shutdown = True
        if not self._session:
            return  # already closed.
        await self._close_link_async()
        if self._cbs_authenticator:
            await self._cbs_authenticator.close()
            self._cbs_authenticator = None
        await self._session.end()
        self._session = None
        if not self._external_connection:
            await self._connection.close()
            self._connection = None
        if self._keep_alive_thread:
            await self._keep_alive_thread
            self._keep_alive_thread = None
        self._network_trace_params["amqpConnection"] = ""
        self._network_trace_params["amqpSession"] = ""

    async def auth_complete_async(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :return: Whether the authentication handshake is complete.
        :rtype: bool
        """
        if self._cbs_authenticator and not await self._cbs_authenticator.handle_token():
            await self._connection.listen(wait=self._socket_timeout)
            return False
        return True

    async def client_ready_async(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :return: Whether the client is ready to process messages.
        :rtype: bool
        """
        if not await self.auth_complete_async():
            return False
        if not await self._client_ready_async():
            try:
                await self._connection.listen(wait=self._socket_timeout)
            except ValueError:
                return True
            return False
        return True

    async def do_work_async(self, **kwargs):
        """Run a single connection iteration asynchronously.
        This will return `True` if the connection is still open
        and ready to be used for further work, or `False` if it needs
        to be shut down.

        :return: Whether the connection is still open and ready for work.
        :rtype: bool
        :raises: TimeoutError if CBS authentication timeout reached.
        """

        if self._shutdown:
            return False
        if not await self.client_ready_async():
            return True
        return await self._client_run_async(**kwargs)

    async def mgmt_request_async(
            self,
            message,
            *,
            operation: Optional[Union[bytes, str]] = None,
            operation_type: Optional[Union[bytes, str]] = None,
            node: str = "$management",
            timeout: float = 0,
            **kwargs
        ):
        """
        :param message: The message to send in the management request.
        :type message: ~pyamqp.message.Message
        :keyword str operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :keyword str operation_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :keyword str node: The target node. Default node is `$management`.
        :keyword float timeout: Provide an optional timeout in seconds within which a response
         to the management request must be received.
        :return: The response to the management request.
        :rtype: ~pyamqp.message.Message
        """

        # The method also takes "status_code_field" and "status_description_field"
        # keyword arguments as alternate names for the status code and description
        # in the response body. Those two keyword arguments are used in Azure services only.
        async with self._mgmt_link_lock_async:
            try:
                mgmt_link = self._mgmt_links[node]
            except KeyError:
                mgmt_link = ManagementOperation(self._session, endpoint=node, **kwargs)
                self._mgmt_links[node] = mgmt_link
                await mgmt_link.open()

        while not self.client_ready_async():
            await asyncio.sleep(0.05)

        while not await mgmt_link.ready():
            await self._connection.listen(wait=False)

        operation_type = operation_type or b'empty'
        status, description, response = await mgmt_link.execute(
            message,
            operation=operation,
            operation_type=operation_type,
            timeout=timeout
        )
        return status, description, response


class SendClientAsync(SendClientSync, AMQPClientAsync):

    """An asynchronous AMQP client.

    :param target: The target AMQP service endpoint. This can either be the URI as
     a string or a ~pyamqp.endpoint.Target object.
    :type target: str, bytes or ~pyamqp.endpoint.Target
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the Event Hubs service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    """

    async def _client_ready_async(self):
        """Determine whether the client is ready to start receiving messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageReceiver must be open and in non-errored
        states.

        :return: Whether or not the client is ready to start sending messages.
        :rtype: bool
        """
        # pylint: disable=protected-access
        if not self._link:
            self._link = self._session.create_sender_link(
                target_address=self.target,
                link_credit=self._link_credit,
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                properties=self._link_properties)
            await self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    async def _client_run_async(self, **kwargs):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :return: Whether or not the client should remain open for further work.
        :rtype: bool
        """
        await self._link.update_pending_deliveries()
        await self._connection.listen(wait=self._socket_timeout, **kwargs)
        return True

    async def _transfer_message_async(self, message_delivery, timeout=0):
        message_delivery.state = MessageDeliveryState.WaitingForSendAck
        on_send_complete = partial(self._on_send_complete_async, message_delivery)
        delivery = await self._link.send_transfer(
            message_delivery.message,
            on_send_complete=on_send_complete,
            timeout=timeout,
            send_async=True
        )
        return delivery

    async def _on_send_complete_async(self, message_delivery, reason, state):
        message_delivery.reason = reason
        if reason == LinkDeliverySettleReason.DISPOSITION_RECEIVED:
            if state and SEND_DISPOSITION_ACCEPT in state:
                message_delivery.state = MessageDeliveryState.Ok
            else:
                try:
                    error_info = state[SEND_DISPOSITION_REJECT]
                    self._process_send_error(
                        message_delivery,
                        condition=error_info[0][0],
                        description=error_info[0][1],
                        info=error_info[0][2]
                    )
                except TypeError:
                    self._process_send_error(
                        message_delivery,
                        condition=ErrorCondition.UnknownError
                    )
        elif reason == LinkDeliverySettleReason.SETTLED:
            message_delivery.state = MessageDeliveryState.Ok
        elif reason == LinkDeliverySettleReason.TIMEOUT:
            message_delivery.state = MessageDeliveryState.Timeout
            message_delivery.error = TimeoutError("Sending message timed out.")
        else:
            # NotDelivered and other unknown errors
            self._process_send_error(
                message_delivery,
                condition=ErrorCondition.UnknownError
            )

    async def _send_message_impl_async(self, message, *, timeout: float = 0):
        expire_time = (time.time() + timeout) if timeout else None
        await self.open_async()
        message_delivery = _MessageDelivery(
            message,
            MessageDeliveryState.WaitingToBeSent,
            expire_time
        )

        while not await self.client_ready_async():
            await asyncio.sleep(0.05)

        await self._transfer_message_async(message_delivery, timeout)

        running = True
        while running and message_delivery.state not in MESSAGE_DELIVERY_DONE_STATES:
            running = await self.do_work_async()
        if message_delivery.state not in MESSAGE_DELIVERY_DONE_STATES:
            raise MessageException(
                condition=ErrorCondition.ClientError,
                description="Send failed - connection not running."
            )

        if message_delivery.state in (
            MessageDeliveryState.Error,
            MessageDeliveryState.Cancelled,
            MessageDeliveryState.Timeout
        ):
            try:
                raise message_delivery.error  # pylint: disable=raising-bad-type
            except TypeError:
                # This is a default handler
                raise MessageException(condition=ErrorCondition.UnknownError, description="Send failed.") from None

    async def send_message_async(self, message, *, timeout: float = 0, **kwargs):
        """
        :param ~pyamqp.message.Message message: The message to send.
        :keyword float timeout: timeout in seconds. If set to
         0, the client will continue to wait until the message is sent or error happens. The
         default is 0.
        """
        await self._do_retryable_operation_async(
            self._send_message_impl_async,
            message=message,
            timeout=timeout,
            **kwargs
        )


class ReceiveClientAsync(ReceiveClientSync, AMQPClientAsync):
    """An asynchronous AMQP client.

    :param source: The source AMQP service endpoint. This can either be the URI as
     a string or a ~pyamqp.endpoint.Source object.
    :type source: str, bytes or ~pyamqp.endpoint.Source
    :keyword auth: Authentication for the connection. This should be one of the following:
        - pyamqp.authentication.SASLAnonymous
        - pyamqp.authentication.SASLPlain
        - pyamqp.authentication.SASTokenAuth
        - pyamqp.authentication.JWTTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :paramtype auth: ~pyamqp.authentication
    :keyword client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :paramtype client_name: str or bytes
    :keyword network_trace: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :paramtype network_trace: bool
    :keyword retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :paramtype retry_policy: ~pyamqp.error.RetryPolicy
    :keyword keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :paramtype keep_alive_interval: int
    :keyword max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :paramtype max_frame_size: int
    :keyword channel_max: Maximum number of Session channels in the Connection.
    :paramtype channel_max: int
    :keyword idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :paramtype idle_timeout: int
    :keyword auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :paramtype auth_timeout: int
    :keyword properties: Connection properties.
    :paramtype properties: dict[str, any]
    :keyword remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :paramtype remote_idle_timeout_empty_frame_send_ratio: float
    :keyword incoming_window: The size of the allowed window for incoming messages.
    :paramtype incoming_window: int
    :keyword outgoing_window: The size of the allowed window for outgoing messages.
    :paramtype outgoing_window: int
    :keyword handle_max: The maximum number of concurrent link handles.
    :paramtype handle_max: int
    :keyword on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :paramtype on_attach: func[
     ~pyamqp.endpoint.Source, ~pyamqp.endpoint.Target, dict, ~pyamqp.error.AMQPConnectionError]
    :keyword send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :paramtype send_settle_mode: ~pyamqp.constants.SenderSettleMode
    :keyword receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :paramtype receive_settle_mode: ~pyamqp.constants.ReceiverSettleMode
    :keyword desired_capabilities: The extension capabilities desired from the peer endpoint.
    :paramtype desired_capabilities: list[bytes]
    :keyword max_message_size: The maximum allowed message size negotiated for the Link.
    :paramtype max_message_size: int
    :keyword link_properties: Metadata to be sent in the Link ATTACH frame.
    :paramtype link_properties: dict[str, any]
    :keyword link_credit: The Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :paramtype link_credit: int
    :keyword transport_type: The type of transport protocol that will be used for communicating with
     the service. Default is `TransportType.Amqp` in which case port 5671 is used.
     If the port 5671 is unavailable/blocked in the network environment, `TransportType.AmqpOverWebsocket` could
     be used instead which uses port 443 for communication.
    :paramtype transport_type: ~pyamqp.constants.TransportType
    :keyword http_proxy: HTTP proxy settings. This must be a dictionary with the following
     keys: `'proxy_hostname'` (str value) and `'proxy_port'` (int value).
     Additionally the following keys may also be present: `'username', 'password'`.
    :paramtype http_proxy: dict[str, str]
    :keyword custom_endpoint_address: The custom endpoint address to use for establishing a connection to
     the Event Hubs service, allowing network requests to be routed through any application gateways or
     other paths needed for the host environment. Default is None.
     If port is not specified in the `custom_endpoint_address`, by default port 443 will be used.
    :paramtype custom_endpoint_address: str
    :keyword connection_verify: Path to the custom CA_BUNDLE file of the SSL certificate which is used to
     authenticate the identity of the connection endpoint.
     Default is None in which case `certifi.where()` will be used.
    :paramtype connection_verify: str
    """

    async def _client_ready_async(self):
        """Determine whether the client is ready to start receiving messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageReceiver must be open and in non-errored
        states.

        :return: Whether the client is ready to start receiving messages.
        :rtype: bool
        """
        # pylint: disable=protected-access
        if not self._link:
            self._link = self._session.create_receiver_link(
                source_address=self.source,
                link_credit=0,  # link_credit=0 on flow frame sent before client is ready
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                on_transfer=self._message_received_async,
                properties=self._link_properties,
                desired_capabilities=self._desired_capabilities,
                on_attach=self._on_attach
            )
            await self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    async def _client_run_async(self, **kwargs):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :return: Whether the client can remain open for further work.
        :rtype: bool
        """
        try:
            if self._link.current_link_credit <= 0:
                await self._link.flow(link_credit=self._link_credit)
            await self._connection.listen(wait=self._socket_timeout, **kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing receiver.", extra=self._network_trace_params)
            self._shutdown = True
            return False
        return True

    async def _message_received_async(self, frame, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param tuple frame: Received frame.
        :param message: Received message.
        :type message: ~pyamqp.message.Message
        """
        self._last_activity_timestamp = time.time()
        if self._message_received_callback:
            await self._message_received_callback(message)
        if not self._streaming_receive:
            self._received_messages.put((frame, message))

    async def _receive_message_batch_impl_async(
            self,
            max_batch_size: Optional[int] = None,
            on_message_received: Optional[Callable] = None,
            timeout: float = 0,
        ):
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._link_credit
        timeout_time = time.time() + timeout if timeout else 0
        receiving = True
        batch: List[Message] = []
        await self.open_async()
        while len(batch) < max_batch_size:
            try:
                # TODO: This drops the transfer frame data
                _, message = self._received_messages.get_nowait()
                batch.append(message)
                self._received_messages.task_done()
            except queue.Empty:
                break
        else:
            return batch

        to_receive_size = max_batch_size - len(batch)
        before_queue_size = self._received_messages.qsize()

        while receiving and to_receive_size > 0:
            now_time = time.time()
            if timeout_time and now_time > timeout_time:
                break

            try:
                receiving = await asyncio.wait_for(
                    self.do_work_async(batch=to_receive_size),
                    timeout=timeout_time - now_time if timeout else None
                )
            except asyncio.TimeoutError:
                break

            cur_queue_size = self._received_messages.qsize()
            # after do_work, check how many new messages have been received since previous iteration
            received = cur_queue_size - before_queue_size
            if to_receive_size < max_batch_size and received == 0:
                # there are already messages in the batch, and no message is received in the current cycle
                # return what we have
                break

            to_receive_size -= received
            before_queue_size = cur_queue_size

        while len(batch) < max_batch_size:
            try:
                _, message = self._received_messages.get_nowait()
                batch.append(message)
                self._received_messages.task_done()
            except queue.Empty:
                break
        return batch

    async def close_async(self):
        self._received_messages = queue.Queue()
        await super(ReceiveClientAsync, self).close_async()

    async def receive_message_batch_async( # pylint: disable=unused-argument
            self,
            *,
            max_batch_size: Optional[int] = None,
            on_message_received: Optional[Callable] = None,
            timeout: float = 0,
            **kwargs
        ) -> Coroutine[Any, Any, list]:
        """Receive a batch of messages. Messages returned in the batch have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback. This method will return as soon as some messages are
        available rather than waiting to achieve a specific batch size, and therefore the
        number of messages returned per call will vary up to the maximum allowed.

        :keyword max_batch_size: The maximum number of messages that can be returned in
         one call. This value cannot be larger than the prefetch value, and if not specified,
         the prefetch value will be used.
        :paramtype max_batch_size: int
        :keyword on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~pyamqp.message.Message object.
        :paramtype on_message_received: callable[~pyamqp.message.Message]
        :keyword timeout: Timeout in seconds for which to wait to receive any messages.
         If no messages are received in this time, an empty list will be returned. If set to
         0, the client will continue to wait until at least one message is received. The
         default is 0.
        :paramtype timeout: float
        :returns: Retryable operation coroutine.
        :rtype: Coroutine[Any, Any, list]
        """
        return await self._do_retryable_operation_async(
            self._receive_message_batch_impl_async,
            max_batch_size=max_batch_size,
            on_message_received=on_message_received,
            timeout=timeout,
        )

    async def receive_messages_iter_async(self, timeout=None, on_message_received=None):
        """Receive messages by generator. Messages returned in the generator have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback.

        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~pyamqp.message.Message object.
        :type on_message_received: callable[~pyamqp.message.Message]
        :param float timeout: Timeout in seconds for which to wait to receive any messages.
        :return: A generator of messages.
        :rtype: generator[~pyamqp.message.Message]
        """
        self._message_received_callback = on_message_received
        return self._message_generator_async(timeout=timeout)

    async def _message_generator_async(self, timeout=None):
        """Iterate over processed messages in the receive queue.

        :param float timeout: Timeout in seconds for which to wait to receive any messages.
        :return: A generator of messages.
        :rtype: generator[~pyamqp.message.Message]
        """
        self.open()
        receiving = True
        message = None
        self._last_activity_timestamp = time.time()
        self._timeout_reached = False
        self._timeout = timeout if timeout else self._timeout
        try:
            while receiving and not self._timeout_reached:
                if self._timeout > 0:
                    if time.time() - self._last_activity_timestamp >= self._timeout:
                        self._timeout_reached = True

                if not self._timeout_reached:
                    receiving = await self.do_work_async()

                while not self._received_messages.empty():
                    message = self._received_messages.get()
                    self._last_activity_timestamp = time.time()
                    self._received_messages.task_done()
                    yield message

        finally:
            if self._shutdown:
                await self.close_async()

    @overload
    async def settle_messages_async(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["accepted"],
        *,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    async def settle_messages_async(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["released"],
        *,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    async def settle_messages_async(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["rejected"],
        *,
        error: Optional[AMQPError] = None,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    async def settle_messages_async(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["modified"],
        *,
        delivery_failed: Optional[bool] = None,
        undeliverable_here: Optional[bool] = None,
        message_annotations: Optional[Dict[Union[str, bytes], Any]] = None,
        batchable: Optional[bool] = None
    ):
        ...

    @overload
    async def settle_messages_async(
        self,
        delivery_id: Union[int, Tuple[int, int]],
        outcome: Literal["received"],
        *,
        section_number: int,
        section_offset: int,
        batchable: Optional[bool] = None
    ):
        ...

    async def settle_messages_async(self, delivery_id: Union[int, Tuple[int, int]], outcome: str, **kwargs):
        batchable = kwargs.pop('batchable', None)
        if outcome.lower() == 'accepted':
            state: Outcomes = Accepted()
        elif outcome.lower() == 'released':
            state = Released()
        elif outcome.lower() == 'rejected':
            state = Rejected(**kwargs)
        elif outcome.lower() == 'modified':
            state = Modified(**kwargs)
        elif outcome.lower() == 'received':
            state = Received(**kwargs)
        else:
            raise ValueError("Unrecognized message output: {}".format(outcome))
        try:
            first, last = cast(Tuple, delivery_id)
        except TypeError:
            first = delivery_id
            last = None
        await self._link.send_disposition(
            first_delivery_id=first,
            last_delivery_id=last,
            settled=True,
            delivery_state=state,
            batchable=batchable,
            wait=True
        )
