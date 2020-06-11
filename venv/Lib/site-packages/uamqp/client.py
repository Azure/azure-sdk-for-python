#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=too-many-lines

import logging
import threading
import time
import uuid

from uamqp import (Connection, Session, address, authentication, c_uamqp,
                   compat, constants, errors, receiver, sender)
from uamqp.constants import TransportType

_logger = logging.getLogger(__name__)


class AMQPClient(object):
    """An AMQP client.

    :param remote_address: The AMQP endpoint to connect to. This could be a send target
     or a receive source.
    :type remote_address: str, bytes or ~uamqp.address.Address
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
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
            self, remote_address, auth=None, client_name=None, debug=False,
            error_policy=None, keep_alive_interval=None, **kwargs):
        self._encoding = kwargs.pop('encoding', None) or 'UTF-8'
        self._transport_type = kwargs.pop('transport_type', None) or TransportType.Amqp
        self._http_proxy = kwargs.pop('http_proxy', None)
        self._remote_address = remote_address if isinstance(remote_address, address.Address) \
            else address.Address(remote_address)
        self._hostname = self._remote_address.hostname
        if not auth:
            username = self._remote_address.username
            password = self._remote_address.password
            if username and password:
                username = compat.unquote_plus(username)
                password = compat.unquote_plus(password)
                auth = authentication.SASLPlain(
                    self._hostname, username, password,
                    http_proxy=self._http_proxy,
                    transport_type=self._transport_type)

        self._auth = auth if auth else authentication.SASLAnonymous(
            self._hostname,
            http_proxy=self._http_proxy,
            transport_type=self._transport_type)
        self._name = client_name if client_name else str(uuid.uuid4())
        self._debug_trace = debug
        self._counter = c_uamqp.TickCounter()
        self._shutdown = False
        self._connection = None
        self._ext_connection = False
        self._session = None
        self._backoff = 0
        self._error_policy = error_policy or errors.ErrorPolicy()
        self._keep_alive_interval = int(keep_alive_interval) if keep_alive_interval else 0
        self._keep_alive_thread = None

        # Connection settings
        self._max_frame_size = kwargs.pop('max_frame_size', None) or constants.MAX_FRAME_SIZE_BYTES
        self._channel_max = kwargs.pop('channel_max', None)
        self._idle_timeout = kwargs.pop('idle_timeout', None)
        self._properties = kwargs.pop('properties', None)
        self._remote_idle_timeout_empty_frame_send_ratio = kwargs.pop(
            'remote_idle_timeout_empty_frame_send_ratio', None)

        # Session settings
        self._outgoing_window = kwargs.pop('outgoing_window', None) or constants.MAX_FRAME_SIZE_BYTES
        self._incoming_window = kwargs.pop('incoming_window', None) or constants.MAX_FRAME_SIZE_BYTES
        self._handle_max = kwargs.pop('handle_max', None)
        self._on_attach = kwargs.pop('on_attach', None)

        # Link settings
        self._send_settle_mode = kwargs.pop('send_settle_mode', None) or constants.SenderSettleMode.Unsettled
        self._receive_settle_mode = kwargs.pop('receive_settle_mode', None) or constants.ReceiverSettleMode.PeekLock
        self._desired_capabilities = kwargs.pop('desired_capabilities', None)

        # AMQP object settings
        self.message_handler = None
        self.connection_type = Connection
        self.session_type = Session

        if kwargs:
            raise ValueError("Received unrecognized kwargs: {}".format(", ".join(kwargs.keys())))

    def __enter__(self):
        """Run Client in a context manager."""
        self.open()
        return self

    def __exit__(self, *args):
        """Close and destroy Client on exiting a context manager."""
        self.close()

    def _keep_alive(self):
        start_time = self._counter.get_current_ms()
        try:
            while self._connection and not self._shutdown:
                current_time = self._counter.get_current_ms()
                elapsed_time = (current_time - start_time)/1000
                if elapsed_time >= self._keep_alive_interval:
                    _logger.debug("Keeping %r connection alive.", self.__class__.__name__)
                    self._connection.work()
                    start_time = current_time
                time.sleep(1)
        except Exception as e:  # pylint: disable=broad-except
            _logger.info("Connection keep-alive for %r failed: %r.", self.__class__.__name__, e)

    def _client_ready(self):  # pylint: disable=no-self-use
        """Determine whether the client is ready to start sending and/or
        receiving messages. To be ready, the connection must be open and
        authentication complete.

        :rtype: bool
        """
        return True

    def _client_run(self):
        """Perform a single Connection iteration."""
        self._connection.work()

    def _redirect(self, redirect, auth):
        """Redirect the client endpoint using a Link DETACH redirect
        response.

        :param redirect: The Link DETACH redirect details.
        :type redirect: ~uamqp.errors.LinkRedirect
        :param auth: Authentication credentials to the redirected endpoint.
        :type auth: ~uamqp.authentication.common.AMQPAuth
        """
        if not self._connection._cbs:  # pylint: disable=protected-access
            _logger.debug("Closing non-CBS session.")
            self._session.destroy()
        self._session = None
        self._auth = auth
        self._hostname = self._remote_address.hostname
        self._connection.redirect(redirect, auth)
        self._build_session()

    def _build_session(self):
        """Build self._session based on current self.connection.
        """
        # pylint: disable=protected-access
        if not self._connection._cbs and isinstance(self._auth, authentication.CBSAuthMixin):
            self._connection._cbs = self._auth.create_authenticator(
                self._connection,
                debug=self._debug_trace,
                incoming_window=self._incoming_window,
                outgoing_window=self._outgoing_window,
                handle_max=self._handle_max,
                on_attach=self._on_attach)
            self._session = self._auth._session  # pylint: disable=protected-access
        elif self._connection._cbs:
            self._session = self._auth._session  # pylint: disable=protected-access
        else:
            self._session = self.session_type(
                self._connection,
                incoming_window=self._incoming_window,
                outgoing_window=self._outgoing_window,
                handle_max=self._handle_max,
                on_attach=self._on_attach)

    def open(self, connection=None):
        """Open the client. The client can create a new Connection
        or an existing Connection can be passed in. This existing Connection
        may have an existing CBS authentication Session, which will be
        used for this client as well. Otherwise a new Session will be
        created.

        :param connection: An existing Connection that may be shared between
         multiple clients.
        :type connetion: ~uamqp.connection.Connection
        """
        # pylint: disable=protected-access
        if self._session:
            return  # already open.
        _logger.debug("Opening client connection.")
        try:
            if connection:
                _logger.debug("Using existing connection.")
                self._auth = connection.auth
                self._ext_connection = True
                connection.lock()
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
                encoding=self._encoding)
            self._build_session()
            if self._keep_alive_interval:
                self._keep_alive_thread = threading.Thread(target=self._keep_alive)
                self._keep_alive_thread.start()
        finally:
            if self._ext_connection:
                connection.release()

    def close(self):
        """Close the client. This includes closing the Session
        and CBS authentication layer as well as the Connection.
        If the client was opened using an external Connection,
        this will be left intact.

        No further messages can be sent or received and the client
        cannot be re-opened.

        All pending, unsent messages will remain uncleared to allow
        them to be inspected and queued to a new client.
        """
        if self.message_handler:
            self.message_handler.destroy()
            self.message_handler = None
        self._shutdown = True
        if self._keep_alive_thread:
            self._keep_alive_thread.join()
            self._keep_alive_thread = None
        if not self._session:
            return  # already closed.
        if not self._connection._cbs:  # pylint: disable=protected-access
            _logger.debug("Closing non-CBS session.")
            self._session.destroy()
        else:
            _logger.debug("CBS session pending.")
        self._session = None
        if not self._ext_connection:
            _logger.debug("Closing exclusive connection.")
            self._connection.destroy()
        else:
            _logger.debug("Shared connection remaining open.")
        self._connection = None

    def mgmt_request(self, message, operation, op_type=None, node=None, callback=None, **kwargs):
        """Run a request/response operation. These are frequently used for management
        tasks against a $management node, however any node name can be specified
        and the available options will depend on the target service.

        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :param operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :type operation: bytes
        :param op_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :type op_type: bytes
        :param node: The target node. Default is `b"$management"`.
        :type node: bytes
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
        :type status_code_field: bytes
        :param description_fields: Provide an alternate name for the description in the
         response body which can vary between services due to the spec still being in draft.
         The default is `b"statusDescription"`.
        :type description_fields: bytes
        :rtype: ~uamqp.message.Message
        """
        while not self.auth_complete():
            time.sleep(0.05)
        response = self._session.mgmt_request(
            message,
            operation,
            op_type=op_type,
            node=node,
            callback=callback,
            encoding=self._encoding,
            debug=self._debug_trace,
            **kwargs)
        return response

    def auth_complete(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :rtype: bool
        """
        timeout = False
        auth_in_progress = False
        if self._connection._cbs:  # pylint: disable=protected-access
            timeout, auth_in_progress = self._auth.handle_token()
            if timeout is None and auth_in_progress is None:
                _logger.debug("No work done.")
                return False
        if timeout:
            raise compat.TimeoutException("Authorization timeout.")
        if auth_in_progress:
            self._connection.work()
            return False
        return True

    def client_ready(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :rtype: bool
        """
        if not self.auth_complete():
            return False
        if not self._client_ready():
            self._connection.work()
            return False
        return True

    def do_work(self):
        """Run a single connection iteration.
        This will return `True` if the connection is still open
        and ready to be used for further work, or `False` if it needs
        to be shut down.

        :rtype: bool
        :raises: TimeoutError or ~uamqp.errors.ClientTimeout if CBS authentication timeout reached.
        """
        if self._shutdown:
            return False
        if not self.client_ready():
            return True
        return self._client_run()


class SendClient(AMQPClient):
    """An AMQP client for sending messages.

    :param target: The target AMQP service endpoint. This can either be the URI as
     a string or a ~uamqp.address.Target object.
    :type target: str, bytes or ~uamqp.address.Target
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
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
            self, target, auth=None, client_name=None, debug=False, msg_timeout=0,
            error_policy=None, keep_alive_interval=None, **kwargs):
        target = target if isinstance(target, address.Address) else address.Target(target)
        self._msg_timeout = msg_timeout
        self._pending_messages = []
        self._waiting_messages = []
        self._shutdown = None

        # Sender and Link settings
        self._max_message_size = kwargs.pop('max_message_size', None) or constants.MAX_MESSAGE_LENGTH_BYTES
        self._link_properties = kwargs.pop('link_properties', None)
        self._link_credit = kwargs.pop('link_credit', None)

        # AMQP object settings
        self.sender_type = sender.MessageSender

        super(SendClient, self).__init__(
            target,
            auth=auth,
            client_name=client_name,
            debug=debug,
            error_policy=error_policy,
            keep_alive_interval=keep_alive_interval,
            **kwargs)

    def _client_ready(self):
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
                link_credit=self._link_credit,
                properties=self._link_properties,
                error_policy=self._error_policy,
                encoding=self._encoding)
            self.message_handler.open()
            return False
        if self.message_handler.get_state() == constants.MessageSenderState.Error:
            raise errors.MessageHandlerError(
                "Message Sender Client is in an error state. "
                "Please confirm credentials and access permissions."
                "\nSee debug trace for more details.")
        if self.message_handler.get_state() != constants.MessageSenderState.Open:
            return False
        return True

    def _on_message_sent(self, message, result, delivery_state=None):
        """Callback run on a message send operation. If message
        has a user defined callback, it will be called here. If the result
        of the operation is failure, the message state will be reverted
        to 'pending' up to the maximum retry count.

        :param message: The message that was sent.
        :type message: ~uamqp.message.Message
        :param result: The result of the send operation.
        :type result: int
        :param error: An Exception if an error ocurred during the send operation.
        :type error: ~Exception
        """
        # pylint: disable=protected-access
        try:
            exception = delivery_state
            result = constants.MessageSendResult(result)
            if result == constants.MessageSendResult.Error:
                if isinstance(delivery_state, Exception):
                    exception = errors.ClientMessageError(delivery_state, info=delivery_state)
                    exception.action = errors.ErrorAction(retry=True)
                elif delivery_state:
                    error = errors.ErrorResponse(delivery_state)
                    exception = errors._process_send_error(
                        self._error_policy,
                        error.condition,
                        error.description,
                        error.info)
                else:
                    exception = errors.MessageSendFailed(constants.ErrorCodes.UnknownError)
                    exception.action = errors.ErrorAction(retry=True)

                if exception.action.retry == errors.ErrorAction.retry \
                        and message.retries < self._error_policy.max_retries:
                    if exception.action.increment_retries:
                        message.retries += 1
                    self._backoff = exception.action.backoff
                    _logger.debug("Message error, retrying. Attempts: %r, Error: %r", message.retries, exception)
                    message.state = constants.MessageState.WaitingToBeSent
                    return
                if exception.action.retry == errors.ErrorAction.retry:
                    _logger.info("Message error, %r retries exhausted. Error: %r", message.retries, exception)
                else:
                    _logger.info("Message error, not retrying. Error: %r", exception)
                message.state = constants.MessageState.SendFailed
                message._response = exception

            else:
                _logger.debug("Message sent: %r, %r", result, exception)
                message.state = constants.MessageState.SendComplete
                message._response = errors.MessageAlreadySettled()
            if message.on_send_complete:
                message.on_send_complete(result, exception)
        except KeyboardInterrupt:
            _logger.error("Received shutdown signal while processing message send completion.")
            self.message_handler._error = errors.AMQPClientShutdown()

    def _get_msg_timeout(self, message):
        current_time = self._counter.get_current_ms()
        elapsed_time = (current_time - message.idle_time)
        if self._msg_timeout > 0 and elapsed_time > self._msg_timeout:
            return None
        return self._msg_timeout - elapsed_time if self._msg_timeout > 0 else 0

    def _transfer_message(self, message, timeout):
        sent = self.message_handler.send(message, self._on_message_sent, timeout=timeout)
        if not sent:
            _logger.info("Message not sent, raising RuntimeError.")
            raise RuntimeError("Message sender failed to add message data to outgoing queue.")

    def _filter_pending(self):
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
                        self._transfer_message(message, timeout)
                except Exception as exp:  # pylint: disable=broad-except
                    self._on_message_sent(message, constants.MessageSendResult.Error, delivery_state=exp)
                    if message.state != constants.MessageState.WaitingToBeSent:
                        continue
            filtered.append(message)
        return filtered

    def _client_run(self):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        # pylint: disable=protected-access
        self.message_handler.work()
        self._waiting_messages = 0
        self._pending_messages = self._filter_pending()
        if self._backoff and not self._waiting_messages:
            _logger.info("Client told to backoff - sleeping for %r seconds", self._backoff)
            self._connection.sleep(self._backoff)
            self._backoff = 0
        self._connection.work()
        return True

    @property
    def _message_sender(self):
        """Temporary property to support backwards compatibility
        with EventHubs.
        """
        return self.message_handler

    @property
    def pending_messages(self):
        return [m for m in self._pending_messages if m.state in constants.PENDING_STATES]

    def redirect(self, redirect, auth):
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
            self.message_handler.destroy()
            self.message_handler = None
        self._pending_messages = []
        self._remote_address = address.Target(redirect.address)
        self._redirect(redirect, auth)

    def queue_message(self, *messages):
        """Add one or more messages to the send queue.
        No further action will be taken until either `SendClient.wait()`
        or `SendClient.send_all_messages()` has been called.
        The client does not need to be open yet for messages to be added
        to the queue. Multiple messages can be queued at once:
            - `send_client.queue_message(my_message)`
            - `send_client.queue_message(message_1, message_2, message_3)`
            - `send_client.queue_message(*my_message_list)`

        :param messages: A message to send. This can either be a single instance
         of `Message`, or multiple messages wrapped in an instance of `BatchMessage`.
        :type message: ~uamqp.message.Message
        """
        for message in messages:
            for internal_message in message.gather():
                internal_message.idle_time = self._counter.get_current_ms()
                internal_message.state = constants.MessageState.WaitingToBeSent
                self._pending_messages.append(internal_message)

    def send_message(self, messages, close_on_done=False):
        """Send a single message or batched message.

        :param messages: A message to send. This can either be a single instance
         of `Message`, or multiple messages wrapped in an instance of `BatchMessage`.
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
            self._pending_messages.append(message)
            pending_batch.append(message)
        self.open()
        running = True
        try:
            while running and any([m for m in pending_batch if m.state not in constants.DONE_STATES]):
                running = self.do_work()
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
            if close_on_done or not running:
                self.close()

    def messages_pending(self):
        """Check whether the client is holding any unsent
        messages in the queue.

        :rtype: bool
        """
        return bool(self._pending_messages)

    def wait(self):
        """Run the client until all pending message in the queue
        have been processed. Returns whether the client is still running after the
        messages have been processed, or whether a shutdown has been initiated.

        :rtype: bool
        """
        running = True
        while running and self.messages_pending():
            running = self.do_work()
        return running

    def send_all_messages(self, close_on_done=True):
        """Send all pending messages in the queue. This will return a list
        of the send result of all the pending messages so it can be
        determined if any messages failed to send.
        This function will open the client if it is not already open.

        :param close_on_done: Close the client once the messages are sent.
         Default is `True`.
        :type close_on_done: bool
        :rtype: list[~uamqp.constants.MessageState]
        """
        self.open()
        running = True
        try:
            messages = self._pending_messages[:]
            running = self.wait()
            results = [m.state for m in messages]
            return results
        finally:
            if close_on_done or not running:
                self.close()


class ReceiveClient(AMQPClient):
    """An AMQP client for receiving messages.

    :param target: The source AMQP service endpoint. This can either be the URI as
     a string or a ~uamqp.address.Source object.
    :type target: str, bytes or ~uamqp.address.Source
    :param auth: Authentication for the connection. This should be one of the subclasses of
     uamqp.authentication.AMQPAuth. Currently this includes:
        - uamqp.authentication.SASLAnonymous
        - uamqp.authentication.SASLPlain
        - uamqp.authentication.SASTokenAuth
     If no authentication is supplied, SASLAnnoymous will be used by default.
    :type auth: ~uamqp.authentication.common.AMQPAuth
    :param client_name: The name for the client, also known as the Container ID.
     If no name is provided, a random GUID will be used.
    :type client_name: str or bytes
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
            self, source, auth=None, client_name=None, debug=False, timeout=0,
            auto_complete=True, error_policy=None, **kwargs):
        source = source if isinstance(source, address.Address) else address.Source(source)
        self._timeout = timeout
        self._last_activity_timestamp = None
        self._was_message_received = False
        self._message_received_callback = None
        self._streaming_receive = False
        self._received_messages = compat.queue.Queue()

        # Receiver and Link settings
        self._max_message_size = kwargs.pop('max_message_size', None) or constants.MAX_MESSAGE_LENGTH_BYTES
        self._prefetch = kwargs.pop('prefetch', None) or 300
        self._link_properties = kwargs.pop('link_properties', None)

        # AMQP object settings
        self.receiver_type = receiver.MessageReceiver
        self.auto_complete = auto_complete

        super(ReceiveClient, self).__init__(
            source, auth=auth, client_name=client_name, error_policy=error_policy, debug=debug, **kwargs)

    @property
    def _message_receiver(self):
        """Temporary property to support backwards compatibility
        with EventHubs.
        """
        return self.message_handler

    def _client_ready(self):
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
                desired_capabilities=self._desired_capabilities)
            self.message_handler.open()
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

    def _client_run(self):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        self.message_handler.work()
        self._connection.work()
        now = self._counter.get_current_ms()
        if self._last_activity_timestamp and not self._was_message_received:
            # If no messages are coming through, back off a little to keep CPU use low.
            time.sleep(0.05)
            if self._timeout > 0:
                timespan = now - self._last_activity_timestamp
                if timespan >= self._timeout:
                    _logger.info("Timeout reached, closing receiver.")
                    self._shutdown = True
        else:
            self._last_activity_timestamp = now
        self._was_message_received = False
        return True

    def _complete_message(self, message, auto):  # pylint: disable=no-self-use
        if not message or not auto:
            return
        message.accept()

    def _message_generator(self):
        """Iterate over processed messages in the receive queue.

        :rtype: generator[~uamqp.message.Message]
        """
        self.open()
        auto_complete = self.auto_complete
        self.auto_complete = False
        receiving = True
        message = None
        try:
            while receiving:
                while receiving and self._received_messages.empty():
                    receiving = self.do_work()
                while not self._received_messages.empty():
                    message = self._received_messages.get()
                    self._received_messages.task_done()
                    yield message
                    self._complete_message(message, auto_complete)
        finally:
            self._complete_message(message, auto_complete)
            self.auto_complete = auto_complete
            self.close()

    def _message_received(self, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param message: Received message.
        :type message: ~uamqp.message.Message
        """
        self._was_message_received = True
        if self._message_received_callback:
            self._message_received_callback(message)
        self._complete_message(message, self.auto_complete)

        if not self._streaming_receive:
            self._received_messages.put(message)
        elif not message.settled:
            # Message was received with callback processing and wasn't settled.
            _logger.info("Message was not settled.")

    def receive_message_batch(self, max_batch_size=None, on_message_received=None, timeout=0):
        """Receive a batch of messages. Messages returned in the batch have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback. This method will return as soon as some messages are
        available rather than waiting to achieve a specific batch size, and therefore the
        number of messages returned per call will vary up to the maximum allowed.

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
        :param timeout: I timeout in milliseconds for which to wait to receive any messages.
         If no messages are received in this time, an empty list will be returned. If set to
         0, the client will continue to wait until at least one message is received. The
         default is 0.
        :type timeout: float
        """
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._prefetch
        if max_batch_size > self._prefetch:
            raise ValueError(
                'Maximum batch size cannot be greater than the '
                'connection link credit: {}'.format(self._prefetch))
        timeout = self._counter.get_current_ms() + timeout if timeout else 0
        expired = False
        self.open()
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
                receiving = self.do_work()
                received = self._received_messages.qsize() - before
                if self._received_messages.qsize() > 0 and received == 0:
                    # No new messages arrived, but we have some - so return what we have.
                    expired = True
                    break
            while not self._received_messages.empty() and len(batch) < max_batch_size:
                batch.append(self._received_messages.get())
                self._received_messages.task_done()
        return batch

    def receive_messages(self, on_message_received):
        """Receive messages. This function will run indefinitely, until the client
        closes either via timeout, error or forced interruption (e.g. keyboard interrupt).

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
        self.open()
        self._message_received_callback = on_message_received
        receiving = True
        try:
            while receiving:
                receiving = self.do_work()
        except:
            receiving = False
            raise
        finally:
            self._streaming_receive = False
            if not receiving:
                self.close()

    def receive_messages_iter(self, on_message_received=None):
        """Receive messages by generator. Messages returned in the generator have already been
        accepted - if you wish to add logic to accept or reject messages based on custom
        criteria, pass in a callback.

        :param on_message_received: A callback to process messages as they arrive from the
         service. It takes a single argument, a ~uamqp.message.Message object.
        :type on_message_received: callable[~uamqp.message.Message]
        """
        self._message_received_callback = on_message_received
        return self._message_generator()

    def redirect(self, redirect, auth):
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
            self.message_handler.destroy()
            self.message_handler = None
        self._shutdown = False
        self._last_activity_timestamp = None
        self._was_message_received = False
        self._received_messages = compat.queue.Queue()

        self._remote_address = address.Source(redirect.address)
        self._redirect(redirect, auth)
