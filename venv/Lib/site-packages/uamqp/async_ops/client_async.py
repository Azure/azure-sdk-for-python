#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# TODO: check this
# pylint: disable=super-init-not-called,too-many-lines

import asyncio
import collections.abc
import logging
import uuid

from uamqp import address, authentication, client, constants, errors, compat
from uamqp.utils import get_running_loop
from uamqp.async_ops.connection_async import ConnectionAsync
from uamqp.async_ops.receiver_async import MessageReceiverAsync
from uamqp.async_ops.sender_async import MessageSenderAsync
from uamqp.async_ops.session_async import SessionAsync

try:
    TimeoutException = TimeoutError
except NameError:
    TimeoutException = errors.ClientTimeout

_logger = logging.getLogger(__name__)


class AMQPClientAsync(client.AMQPClient):
    """An asynchronous AMQP client.

    :param remote_address: The AMQP endpoint to connect to. This could be a send target
     or a receive source.
    :type remote_address: str, bytes or ~uamqp.address.Address
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAsync
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
    :param loop: A user specified event loop.
    :type loop: ~asycnio.AbstractEventLoop
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :param error_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type error_policy: ~uamqp.errors.ErrorPolicy
    :param keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :type keep_alive_interval: int
    :param max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :type max_frame_size: int
    :param channel_max: Maximum number of Session channels in the Connection.
    :type channel_max: int
    :param idle_timeout: Timeout in milliseconds after which the Connection will close
     if there is no further activity.
    :type idle_timeout: int
    :param properties: Connection properties.
    :type properties: dict
    :param remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :type remote_idle_timeout_empty_frame_send_ratio: float
    :param incoming_window: The size of the allowed window for incoming messages.
    :type incoming_window: int
    :param outgoing_window: The size of the allowed window for outgoing messages.
    :type outgoing_window: int
    :param handle_max: The maximum number of concurrent link handles.
    :type handle_max: int
    :param on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :type on_attach: func[~uamqp.address.Source, ~uamqp.address.Target, dict, ~uamqp.errors.AMQPConnectionError]
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    """

    def __init__(
            self,
            remote_address,
            auth=None,
            client_name=None,
            loop=None,
            debug=False,
            error_policy=None,
            keep_alive_interval=None,
            **kwargs):

        if loop:
            self.loop = loop
        else:
            try:
                if not self.loop:  # from sub class instance
                    self.loop = get_running_loop()
            except AttributeError:
                self.loop = get_running_loop()

        super(AMQPClientAsync, self).__init__(
            remote_address,
            auth=auth,
            client_name=client_name,
            debug=debug,
            error_policy=error_policy,
            keep_alive_interval=keep_alive_interval,
            **kwargs)

        # AMQP object settings
        self.connection_type = ConnectionAsync
        self.session_type = SessionAsync

    async def __aenter__(self):
        """Run Client in an async context manager."""
        await self.open_async()
        return self

    async def __aexit__(self, *args):
        """Close and destroy Client on exiting an async context manager."""
        await self.close_async()

    async def _keep_alive_async(self):
        start_time = self._counter.get_current_ms()
        try:
            while self._connection and not self._shutdown:
                current_time = self._counter.get_current_ms()
                elapsed_time = (current_time - start_time)/1000
                if elapsed_time >= self._keep_alive_interval:
                    _logger.info("Keeping %r connection alive. %r",
                                 self.__class__.__name__,
                                 self._connection.container_id)
                    await asyncio.shield(self._connection.work_async(), loop=self.loop)
                    start_time = current_time
                await asyncio.sleep(1, loop=self.loop)
        except Exception as e:  # pylint: disable=broad-except
            _logger.info("Connection keep-alive for %r failed: %r.", self.__class__.__name__, e)

    async def _client_ready_async(self):  # pylint: disable=no-self-use
        """Determine whether the client is ready to start sending and/or
        receiving messages. To be ready, the connection must be open and
        authentication complete.

        :rtype: bool
        """
        return True

    async def _client_run_async(self):
        """Perform a single Connection iteration."""
        await asyncio.shield(self._connection.work_async(), loop=self.loop)

    async def _redirect_async(self, redirect, auth):
        """Redirect the client endpoint using a Link DETACH redirect
        response.

        :param redirect: The Link DETACH redirect details.
        :type redirect: ~uamqp.errors.LinkRedirect
        :param auth: Authentication credentials to the redirected endpoint.
        :type auth: ~uamqp.authentication.common.AMQPAuth
        """
        # pylint: disable=protected-access
        if not self._connection._cbs:
            _logger.info("Closing non-CBS session.")
            await asyncio.shield(self._session.destroy_async(), loop=self.loop)
        self._session = None
        self._auth = auth
        self._hostname = self._remote_address.hostname
        await self._connection.redirect_async(redirect, auth)
        await self._build_session_async()

    async def _build_session_async(self):
        """Build self._session based on current self.connection.
        """
        # pylint: disable=protected-access
        if not self._connection._cbs and isinstance(self._auth, authentication.CBSAsyncAuthMixin):
            self._connection._cbs = await asyncio.shield(
                self._auth.create_authenticator_async(
                    self._connection,
                    debug=self._debug_trace,
                    incoming_window=self._incoming_window,
                    outgoing_window=self._outgoing_window,
                    handle_max=self._handle_max,
                    on_attach=self._on_attach,
                    loop=self.loop),
                loop=self.loop)
            self._session = self._auth._session  # pylint: disable=protected-access
        elif self._connection._cbs:
            self._session = self._auth._session  # pylint: disable=protected-access
        else:
            self._session = self.session_type(
                self._connection,
                incoming_window=self._incoming_window,
                outgoing_window=self._outgoing_window,
                handle_max=self._handle_max,
                on_attach=self._on_attach,
                loop=self.loop)

    async def open_async(self, connection=None):
        """Asynchronously open the client. The client can create a new Connection
        or an existing Connection can be passed in. This existing Connection
        may have an existing CBS authentication Session, which will be
        used for this client as well. Otherwise a new Session will be
        created.

        :param connection: An existing Connection that may be shared between
         multiple clients.
        :type connetion: ~uamqp.async_ops.connection_async.ConnectionAsync
        """
        # pylint: disable=protected-access
        if self._session:
            return  # already open
        try:
            if connection:
                _logger.info("Using existing connection.")
                self._auth = connection.auth
                self._ext_connection = True
                await connection.lock_async()
            self._connection = connection or self.connection_type(
                self._hostname,
                self._auth,
                container_id=self._name,
                max_frame_size=self._max_frame_size,
                channel_max=self._channel_max,
                idle_timeout=self._idle_timeout,
                properties=self._properties,
                remote_idle_timeout_empty_frame_send_ratio=self._remote_idle_timeout_empty_frame_send_ratio,
                error_policy=self._error_policy,
                debug=self._debug_trace,
                loop=self.loop)
            await self._build_session_async()
            if self._keep_alive_interval:
                self._keep_alive_thread = asyncio.ensure_future(self._keep_alive_async(), loop=self.loop)
        finally:
            if self._ext_connection:
                connection.release_async()

    async def close_async(self):
        """Close the client asynchronously. This includes closing the Session
        and CBS authentication layer as well as the Connection.
        If the client was opened using an external Connection,
        this will be left intact.
        """
        if self.message_handler:
            await self.message_handler.destroy_async()
            self.message_handler = None
        self._shutdown = True
        if self._keep_alive_thread:
            await self._keep_alive_thread
            self._keep_alive_thread = None
        if not self._session:
            return  # already closed.
        if not self._connection._cbs:  # pylint: disable=protected-access
            _logger.info("Closing non-CBS session.")
            await asyncio.shield(self._session.destroy_async(), loop=self.loop)
        else:
            _logger.info("CBS session pending %r.", self._connection.container_id)
        self._session = None
        if not self._ext_connection:
            _logger.info("Closing exclusive connection %r.", self._connection.container_id)
            await asyncio.shield(self._connection.destroy_async(), loop=self.loop)
        else:
            _logger.info("Shared connection remaining open.")
        self._connection = None

    async def mgmt_request_async(self, message, operation, op_type=None, node=None, callback=None, **kwargs):
        """Run an asynchronous request/response operation. These are frequently used
        for management tasks against a $management node, however any node name can be
        specified and the available options will depend on the target service.

        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :type operation: bytes or str
        :param op_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :type op_type: bytes
        :param node: The target node. Default is `b"$management"`.
        :type node: bytes or str
        :param timeout: Provide an optional timeout in milliseconds within which a response
         to the management request must be received.
        :type timeout: float
        :param callback: The function to process the returned parameters of the management
         request including status code and a description if available. This can be used
         to reformat the response or raise an error based on content. The function must
         take 3 arguments - status code, response message and description.
        :type callback: ~callable[int, bytes, ~uamqp.message.Message]
        :param status_code_field: Provide an alternate name for the status code in the
         response body which can vary between services due to the spec still being in draft.
         The default is `b"statusCode"`.
        :type status_code_field: bytes or str
        :param description_fields: Provide an alternate name for the description in the
         response body which can vary between services due to the spec still being in draft.
         The default is `b"statusDescription"`.
        :type description_fields: bytes or str
        :rtype: ~uamqp.message.Message
        """
        while not await self.auth_complete_async():
            await asyncio.sleep(0.05, loop=self.loop)
        response = await asyncio.shield(
            self._session.mgmt_request_async(
                message,
                operation,
                op_type=op_type,
                node=node,
                callback=callback,
                encoding=self._encoding,
                debug=self._debug_trace,
                **kwargs),
            loop=self.loop)
        return response

    async def auth_complete_async(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :rtype: bool
        """
        timeout = False
        auth_in_progress = False
        if self._connection._cbs:  # pylint: disable=protected-access
            timeout, auth_in_progress = await self._auth.handle_token_async()
            if timeout is None and auth_in_progress is None:
                _logger.debug("No work done.")
                return False
        if timeout:
            _logger.info("CBS authentication timeout on connection: %r.", self._connection.container_id)
            raise TimeoutException("Authorization timeout.")
        if auth_in_progress:
            await self._connection.work_async()
            return False
        return True

    async def client_ready_async(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :rtype: bool
        """
        if not await self.auth_complete_async():
            return False
        if not await self._client_ready_async():
            await self._connection.work_async()
            return False
        return True

    async def do_work_async(self):
        """Run a single connection iteration asynchronously.
        This will return `True` if the connection is still open
        and ready to be used for further work, or `False` if it needs
        to be shut down.

        :rtype: bool
        :raises: TimeoutError or ~uamqp.errors.ClientTimeout if CBS authentication timeout reached.
        """
        if self._shutdown:
            return False
        if not await self.client_ready_async():
            return True
        return await self._client_run_async()


class SendClientAsync(client.SendClient, AMQPClientAsync):
    """An AMQP client for sending messages asynchronously.

    :param target: The target AMQP service endpoint. This can either be the URI as
     a string or a ~uamqp.address.Target object.
    :type target: str, bytes or ~uamqp.address.Target
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAsync
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
    :param loop: A user specified event loop.
    :type loop: ~asycnio.AbstractEventLoop
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :param msg_timeout: A timeout in milliseconds for messages from when they have been
     added to the send queue to when the message is actually sent. This prevents potentially
     expired data from being sent. If set to 0, messages will not expire. Default is 0.
    :type msg_timeout: int
    :param error_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type error_policy: ~uamqp.errors.ErrorPolicy
    :param keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :type keep_alive_interval: int
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param link_properties: Metadata to be sent in the Link ATTACH frame.
    :type link_properties: dict
    :param link_credit: The sender Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
    :type link_credit: int
    :param max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :type max_frame_size: int
    :param channel_max: Maximum number of Session channels in the Connection.
    :type channel_max: int
    :param idle_timeout: Timeout in milliseconds after which the Connection will close
     if there is no further activity.
    :type idle_timeout: int
    :param properties: Connection properties.
    :type properties: dict
    :param remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :type remote_idle_timeout_empty_frame_send_ratio: float
    :param incoming_window: The size of the allowed window for incoming messages.
    :type incoming_window: int
    :param outgoing_window: The size of the allowed window for outgoing messages.
    :type outgoing_window: int
    :param handle_max: The maximum number of concurrent link handles.
    :type handle_max: int
    :param on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :type on_attach: func[~uamqp.address.Source, ~uamqp.address.Target, dict, ~uamqp.errors.AMQPConnectionError]
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    """

    def __init__(
            self,
            target,
            auth=None,
            client_name=None,
            loop=None,
            debug=False,
            msg_timeout=0,
            error_policy=None,
            keep_alive_interval=None,
            **kwargs):
        self.loop = loop or get_running_loop()
        client.SendClient.__init__(
            self,
            target,
            auth=auth,
            client_name=client_name,
            debug=debug,
            msg_timeout=msg_timeout,
            error_policy=error_policy,
            keep_alive_interval=keep_alive_interval,
            **kwargs)

        # AMQP object settings
        self.sender_type = MessageSenderAsync
        self._pending_messages_lock = asyncio.Lock(loop=self.loop)

    async def _client_ready_async(self):
        """Determine whether the client is ready to start sending messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageSender must be open and in non-errored
        states.

        :rtype: bool
        :raises: ~uamqp.errors.MessageHandlerError if the MessageSender
         goes into an error state.
        """
        # pylint: disable=protected-access
        if not self.message_handler:
            self.message_handler = self.sender_type(
                self._session, self._name, self._remote_address,
                name='sender-link-{}'.format(uuid.uuid4()),
                debug=self._debug_trace,
                send_settle_mode=self._send_settle_mode,
                receive_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                properties=self._link_properties,
                error_policy=self._error_policy,
                encoding=self._encoding,
                loop=self.loop)
            await asyncio.shield(self.message_handler.open_async(), loop=self.loop)
            return False
        if self.message_handler.get_state() == constants.MessageSenderState.Error:
            raise errors.MessageHandlerError(
                "Message Sender Client is in an error state. "
                "Please confirm credentials and access permissions."
                "\nSee debug trace for more details.")
        if self.message_handler.get_state() != constants.MessageSenderState.Open:
            return False
        return True

    async def _transfer_message_async(self, message, timeout):
        sent = await asyncio.shield(
            self.message_handler.send_async(message, self._on_message_sent, timeout=timeout),
            loop=self.loop)
        if not sent:
            _logger.info("Message not sent, raising RuntimeError.")
            raise RuntimeError("Message sender failed to add message data to outgoing queue.")

    async def _filter_pending_async(self):
        filtered = []
        for message in self._pending_messages:
            if message.state in constants.DONE_STATES:
                continue
            elif message.state == constants.MessageState.WaitingForSendAck:
                self._waiting_messages += 1
            elif message.state == constants.MessageState.WaitingToBeSent:
                message.state = constants.MessageState.WaitingForSendAck
                try:
                    timeout = self._get_msg_timeout(message)
                    if timeout is None:
                        self._on_message_sent(message, constants.MessageSendResult.Timeout)
                        if message.state != constants.MessageState.WaitingToBeSent:
                            continue
                    else:
                        await self._transfer_message_async(message, timeout)
                except Exception as exp:  # pylint: disable=broad-except
                    self._on_message_sent(message, constants.MessageSendResult.Error, delivery_state=exp)
                    if message.state != constants.MessageState.WaitingToBeSent:
                        continue
            filtered.append(message)
        return filtered

    async def _client_run_async(self):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        # pylint: disable=protected-access
        await self.message_handler.work_async()
        self._waiting_messages = 0
        async with self._pending_messages_lock:
            self._pending_messages = await self._filter_pending_async()
        if self._backoff and not self._waiting_messages:
            _logger.info("Client told to backoff - sleeping for %r seconds", self._backoff)
            await self._connection.sleep_async(self._backoff)
            self._backoff = 0
        await asyncio.shield(self._connection.work_async(), loop=self.loop)
        return True

    async def redirect_async(self, redirect, auth):
        """Redirect the client endpoint using a Link DETACH redirect
        response.

        :param redirect: The Link DETACH redirect details.
        :type redirect: ~uamqp.errors.LinkRedirect
        :param auth: Authentication credentials to the redirected endpoint.
        :type auth: ~uamqp.authentication.common.AMQPAuth
        """
        if self._ext_connection:
            raise ValueError(
                "Clients with a shared connection cannot be "
                "automatically redirected.")
        if self.message_handler:
            await self.message_handler.destroy_async()
            self.message_handler = None
        async with self._pending_messages_lock:
            self._pending_messages = []

        self._remote_address = address.Target(redirect.address)
        await self._redirect_async(redirect, auth)

    async def close_async(self):
        """Close down the client asynchronously. No further
        messages can be sent and the client cannot be re-opened.

        All pending, unsent messages will remain uncleared to allow
        them to be inspected and queued to a new client.
        """
        await super(SendClientAsync, self).close_async()

    async def wait_async(self):
        """Run the client asynchronously until all pending messages
        in the queue have been processed.
        """
        while self.messages_pending():
            await self.do_work_async()

    async def send_message_async(self, messages, close_on_done=False):
        """Send a single message or batched message asynchronously.

        :param messages: A message to send. This can either be a single instance
         of ~uamqp.message.Message, or multiple messages wrapped in an instance
         of ~uamqp.message.BatchMessage.
        :type message: ~uamqp.message.Message
        :param close_on_done: Close the client once the message is sent. Default is `False`.
        :type close_on_done: bool
        :raises: ~uamqp.errors.MessageException if message fails to send after retry policy
         is exhausted.
        """
        batch = messages.gather()
        pending_batch = []
        for message in batch:
            message.idle_time = self._counter.get_current_ms()
            async with self._pending_messages_lock:
                self._pending_messages.append(message)
            pending_batch.append(message)
        await self.open_async()
        try:
            while any([m for m in pending_batch if m.state not in constants.DONE_STATES]):
                await self.do_work_async()
            failed = [m for m in pending_batch if m.state == constants.MessageState.SendFailed]
            if any(failed):
                details = {"total_messages": len(pending_batch), "number_failed": len(failed)}
                details['failed_messages'] = {}
                exception = None
                for failed_message in failed:
                    exception = failed_message._response  # pylint: disable=protected-access
                    details['failed_messages'][failed_message] = exception
                raise errors.ClientMessageError(exception, info=details)
        finally:
            if close_on_done:
                await self.close_async()

    async def send_all_messages_async(self, close_on_done=True):
        """Send all pending messages in the queue asynchronously.
        This will return a list of the send result of all the pending
        messages so it can be determined if any messages failed to send.
        This function will open the client if it is not already open.

        :param close_on_done: Close the client once the messages are sent.
         Default is `True`.
        :type close_on_done: bool
        :rtype: list[~uamqp.constants.MessageState]
        """
        await self.open_async()
        try:
            async with self._pending_messages_lock:
                messages = self._pending_messages[:]
            await self.wait_async()
            results = [m.state for m in messages]
            return results
        finally:
            if close_on_done:
                await self.close_async()


class ReceiveClientAsync(client.ReceiveClient, AMQPClientAsync):
    """An AMQP client for receiving messages asynchronously.

    :param target: The source AMQP service endpoint. This can either be the URI as
     a string or a ~uamqp.address.Source object.
    :type target: str, bytes or ~uamqp.address.Source
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAsync
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
    :param loop: A user specified event loop.
    :type loop: ~asycnio.AbstractEventLoop
    :param debug: Whether to turn on network trace logs. If `True`, trace logs
     will be logged at INFO level. Default is `False`.
    :type debug: bool
    :param timeout: A timeout in milliseconds. The receiver will shut down if no
     new messages are received after the specified timeout. If set to 0, the receiver
     will never timeout and will continue to listen. The default is 0.
    :type timeout: float
    :param auto_complete: Whether to automatically settle message received via callback
     or via iterator. If the message has not been explicitly settled after processing
     the message will be accepted. Alternatively, when used with batch receive, this setting
     will determine whether the messages are pre-emptively settled during batching, or otherwise
     let to the user to be explicitly settled.
    :type auto_complete: bool
    :param error_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type error_policy: ~uamqp.errors.ErrorPolicy
    :param keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :type keep_alive_interval: int
    :param send_settle_mode: The mode by which to settle message send
     operations. If set to `Unsettled`, the client will wait for a confirmation
     from the service that the message was successfully sent. If set to 'Settled',
     the client will not wait for confirmation and assume success.
    :type send_settle_mode: ~uamqp.constants.SenderSettleMode
    :param receive_settle_mode: The mode by which to settle message receive
     operations. If set to `PeekLock`, the receiver will lock a message once received until
     the client accepts or rejects the message. If set to `ReceiveAndDelete`, the service
     will assume successful receipt of the message and clear it from the queue. The
     default is `PeekLock`.
    :type receive_settle_mode: ~uamqp.constants.ReceiverSettleMode
    :param desired_capabilities: The extension capabilities desired from the peer endpoint.
     To create an desired_capabilities object, please do as follows:
        - 1. Create an array of desired capability symbols: `capabilities_symbol_array = [types.AMQPSymbol(string)]`
        - 2. Transform the array to AMQPValue object: `utils.data_factory(types.AMQPArray(capabilities_symbol_array))`
    :type desired_capabilities: ~uamqp.c_uamqp.AMQPValue
    :param max_message_size: The maximum allowed message size negotiated for the Link.
    :type max_message_size: int
    :param link_properties: Metadata to be sent in the Link ATTACH frame.
    :type link_properties: dict
    :param prefetch: The receiver Link credit that determines how many
     messages the Link will attempt to handle per connection iteration.
     The default is 300.
    :type prefetch: int
    :param max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :type max_frame_size: int
    :param channel_max: Maximum number of Session channels in the Connection.
    :type channel_max: int
    :param idle_timeout: Timeout in milliseconds after which the Connection will close
     if there is no further activity.
    :type idle_timeout: int
    :param properties: Connection properties.
    :type properties: dict
    :param remote_idle_timeout_empty_frame_send_ratio: Ratio of empty frames to
     idle time for Connections with no activity. Value must be between
     0.0 and 1.0 inclusive. Default is 0.5.
    :type remote_idle_timeout_empty_frame_send_ratio: float
    :param incoming_window: The size of the allowed window for incoming messages.
    :type incoming_window: int
    :param outgoing_window: The size of the allowed window for outgoing messages.
    :type outgoing_window: int
    :param handle_max: The maximum number of concurrent link handles.
    :type handle_max: int
    :param on_attach: A callback function to be run on receipt of an ATTACH frame.
     The function must take 4 arguments: source, target, properties and error.
    :type on_attach: func[~uamqp.address.Source, ~uamqp.address.Target, dict, ~uamqp.errors.AMQPConnectionError]
    :param encoding: The encoding to use for parameters supplied as strings.
     Default is 'UTF-8'
    :type encoding: str
    """

    def __init__(
            self,
            source,
            auth=None,
            client_name=None,
            loop=None,
            debug=False,
            timeout=0,
            auto_complete=True,
            error_policy=None,
            keep_alive_interval=None,
            **kwargs):
        self.loop = loop or get_running_loop()
        client.ReceiveClient.__init__(
            self,
            source,
            auth=auth,
            client_name=client_name,
            debug=debug,
            timeout=timeout,
            auto_complete=auto_complete,
            error_policy=error_policy,
            keep_alive_interval=keep_alive_interval,
            **kwargs)

        # AMQP object settings
        self.receiver_type = MessageReceiverAsync

    async def _client_ready_async(self):
        """Determine whether the client is ready to start receiving messages.
        To be ready, the connection must be open and authentication complete,
        The Session, Link and MessageReceiver must be open and in non-errored
        states.

        :rtype: bool
        :raises: ~uamqp.errors.MessageHandlerError if the MessageReceiver
         goes into an error state.
        """
        # pylint: disable=protected-access
        if not self.message_handler:
            self.message_handler = self.receiver_type(
                self._session, self._remote_address, self._name,
                on_message_received=self._message_received,
                name='receiver-link-{}'.format(uuid.uuid4()),
                debug=self._debug_trace,
                receive_settle_mode=self._receive_settle_mode,
                send_settle_mode=self._send_settle_mode,
                prefetch=self._prefetch,
                max_message_size=self._max_message_size,
                properties=self._link_properties,
                error_policy=self._error_policy,
                encoding=self._encoding,
                desired_capabilities=self._desired_capabilities,
                loop=self.loop)
            await asyncio.shield(self.message_handler.open_async(), loop=self.loop)
            return False
        if self.message_handler.get_state() == constants.MessageReceiverState.Error:
            raise errors.MessageHandlerError(
                "Message Receiver Client is in an error state. "
                "Please confirm credentials and access permissions."
                "\nSee debug trace for more details.")
        if self.message_handler.get_state() != constants.MessageReceiverState.Open:
            self._last_activity_timestamp = self._counter.get_current_ms()
            return False
        return True

    async def _client_run_async(self):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        await self.message_handler.work_async()
        await self._connection.work_async()
        now = self._counter.get_current_ms()
        if self._last_activity_timestamp and not self._was_message_received:
            # If no messages are coming through, back off a little to keep CPU use low.
            await asyncio.sleep(0.05, loop=self.loop)
            if self._timeout > 0:
                timespan = now - self._last_activity_timestamp
                if timespan >= self._timeout:
                    _logger.info("Timeout reached, closing receiver.")
                    self._shutdown = True
        else:
            self._last_activity_timestamp = now
        self._was_message_received = False
        return True

    async def receive_messages_async(self, on_message_received):
        """Receive messages asynchronously. This function will run indefinitely,
        until the client closes either via timeout, error or forced
        interruption (e.g. keyboard interrupt).

        If the receive client is configured with `auto_complete=True` then the messages that
        have not been settled on completion of the provided callback will automatically be
        accepted provided it has not expired. If an error occurs or the message has expired
        it will be released. Alternatively if `auto_complete=False`, each message will need
        to be explicitly settled during the callback, otherwise it will be released.

        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~uamqp.message.Message object.
        :type on_message_received: callable[~uamqp.message.Message]
        """
        self._streaming_receive = True
        await self.open_async()
        self._message_received_callback = on_message_received
        receiving = True
        try:
            while receiving:
                receiving = await self.do_work_async()
        except:
            receiving = False
            raise
        finally:
            self._streaming_receive = False
            if not receiving:
                await self.close_async()

    async def receive_message_batch_async(self, max_batch_size=None, on_message_received=None, timeout=0):
        """Receive a batch of messages asynchronously. This method will return as soon as some
        messages are available rather than waiting to achieve a specific batch size, and
        therefore the number of messages returned per call will vary up to the maximum allowed.

        If the receive client is configured with `auto_complete=True` then the messages received
        in the batch returned by this function will already be settled. Alternatively, if
        `auto_complete=False`, then each message will need to be explicitly settled before
        it expires and is released.

        :param max_batch_size: The maximum number of messages that can be returned in
         one call. This value cannot be larger than the prefetch value, and if not specified,
         the prefetch value will be used.
        :type max_batch_size: int
        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~uamqp.message.Message object.
        :type on_message_received: callable[~uamqp.message.Message]
        :param timeout: Timeout in milliseconds for which to wait to receive any messages.
         If no messages are received in this time, an empty list will be returned. If set to
         0, the client will continue to wait until at least one message is received. The
         default is 0.
        :type timeout: float
        """
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._prefetch
        if max_batch_size > self._prefetch:
            raise ValueError(
                'Maximum batch size {} cannot be greater than the '
                'connection link credit: {}'.format(max_batch_size, self._prefetch))
        timeout = self._counter.get_current_ms() + int(timeout) if timeout else 0
        expired = False
        await self.open_async()
        receiving = True
        batch = []
        while not self._received_messages.empty() and len(batch) < max_batch_size:
            batch.append(self._received_messages.get())
            self._received_messages.task_done()
        if len(batch) >= max_batch_size:
            return batch

        while receiving and not expired and len(batch) < max_batch_size:
            while receiving and self._received_messages.qsize() < max_batch_size:
                if timeout and self._counter.get_current_ms() > timeout:
                    expired = True
                    break
                before = self._received_messages.qsize()
                receiving = await self.do_work_async()
                received = self._received_messages.qsize() - before
                if self._received_messages.qsize() > 0 and received == 0:
                    # No new messages arrived, but we have some - so return what we have.
                    expired = True
                    break

            while not self._received_messages.empty() and len(batch) < max_batch_size:
                batch.append(self._received_messages.get())
                self._received_messages.task_done()
        return batch

    def receive_messages_iter_async(self, on_message_received=None):
        """Receive messages by asynchronous generator. Messages returned in the
        generator have already been accepted - if you wish to add logic to accept
        or reject messages based on custom criteria, pass in a callback.

        If the receive client is configured with `auto_complete=True` then the messages received
        from the iterator returned by this function will be automatically settled when the iterator
        is incremented. Alternatively, if `auto_complete=False`, then each message will need to
        be explicitly settled before it expires and is released.

        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~uamqp.message.Message object.
        :type on_message_received: callable[~uamqp.message.Message]
        :rtype: Generator[~uamqp.message.Message]
        """
        self._message_received_callback = on_message_received
        return AsyncMessageIter(self, auto_complete=self.auto_complete)

    async def redirect_async(self, redirect, auth):
        """Redirect the client endpoint using a Link DETACH redirect
        response.

        :param redirect: The Link DETACH redirect details.
        :type redirect: ~uamqp.errors.LinkRedirect
        :param auth: Authentication credentials to the redirected endpoint.
        :type auth: ~uamqp.authentication.common.AMQPAuth
        """
        if self._ext_connection:
            raise ValueError(
                "Clients with a shared connection cannot be "
                "automatically redirected.")
        if self.message_handler:
            await self.message_handler.destroy_async()
            self.message_handler = None
        self._shutdown = False
        self._last_activity_timestamp = None
        self._was_message_received = False
        self._received_messages = compat.queue.Queue()

        self._remote_address = address.Source(redirect.address)
        await self._redirect_async(redirect, auth)

    async def close_async(self):
        """Asynchonously close the receive client."""
        await super(ReceiveClientAsync, self).close_async()


class AsyncMessageIter(collections.abc.AsyncIterator):  # pylint: disable=no-member
    """Python 3.5 and 3.6 compatible asynchronous generator.

    :param recv_client: The receiving client.
    :type recv_client: ~uamqp.async_ops.client_async.ReceiveClientAsync
    """

    def __init__(self, rcv_client, auto_complete=True):
        self._client = rcv_client
        self._client.auto_complete = False
        self.receiving = True
        self.auto_complete = auto_complete
        self.current_message = None

    async def __anext__(self):
        # pylint: disable=protected-access
        await self._client.open_async()
        if self.current_message and self.auto_complete:
            self.current_message.accept()
        try:
            while self.receiving and self._client._received_messages.empty():
                self.receiving = await self._client.do_work_async()
            if not self._client._received_messages.empty():
                message = self._client._received_messages.get()
                self._client._received_messages.task_done()
                self.current_message = message
                return message
            raise StopAsyncIteration("Message receiver closing.")  # pylint: disable=undefined-variable
        except:
            self.receiving = False
            raise
        finally:
            if not self.receiving:
                await self._client.close_async()
