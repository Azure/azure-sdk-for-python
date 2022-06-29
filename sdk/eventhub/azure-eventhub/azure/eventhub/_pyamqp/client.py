#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# pylint: disable=too-many-lines

import logging
import time
import uuid
import certifi
import queue
from functools import partial

from ._connection import Connection
from .message import _MessageDelivery
from .session import Session
from .sender import SenderLink
from .receiver import ReceiverLink
from .sasl import SASLTransport
from .endpoints import Source, Target
from .error import (
    AMQPConnectionError,
    AMQPException,
    ErrorResponse,
    ErrorCondition,
    MessageException,
    MessageSendFailed,
    RetryPolicy
)

from .constants import (
    MessageDeliveryState,
    SenderSettleMode,
    ReceiverSettleMode,
    LinkDeliverySettleReason,
    TransportType,
    SEND_DISPOSITION_ACCEPT,
    SEND_DISPOSITION_REJECT,
    AUTH_TYPE_CBS,
    MAX_FRAME_SIZE_BYTES,
    INCOMING_WINDOW,
    OUTGOING_WIDNOW,
    DEFAULT_AUTH_TIMEOUT,
    MESSAGE_DELIVERY_DONE_STATES,
)

from .management_operation import ManagementOperation
from .cbs import CBSAuthenticator
from .authentication import _CBSAuth


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
    :param retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type retry_policy: ~uamqp.errors.RetryPolicy
    :param keep_alive_interval: If set, a thread will be started to keep the connection
     alive during periods of user inactivity. The value will determine how long the
     thread will sleep (in seconds) between pinging the connection. If 0 or None, no
     thread will be started.
    :type keep_alive_interval: int
    :param max_frame_size: Maximum AMQP frame size. Default is 63488 bytes.
    :type max_frame_size: int
    :param channel_max: Maximum number of Session channels in the Connection.
    :type channel_max: int
    :param idle_timeout: Timeout in seconds after which the Connection will close
     if there is no further activity.
    :type idle_timeout: int
    :param auth_timeout: Timeout in seconds for CBS authentication. Otherwise this value will be ignored.
     Default value is 60s.
    :type auth_timeout: int
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

    def __init__(self, hostname, auth=None, **kwargs):
        self._hostname = hostname
        self._auth = auth
        self._name = kwargs.pop("client_name", str(uuid.uuid4()))
        self._shutdown = False
        self._connection = None
        self._session = None
        self._link = None
        self._socket_timeout = False
        self._external_connection = False
        self._cbs_authenticator = None
        self._auth_timeout = kwargs.pop("auth_timeout", DEFAULT_AUTH_TIMEOUT)
        self._mgmt_links = {}
        self._retry_policy = kwargs.pop("retry_policy", RetryPolicy())

        # Connection settings
        self._max_frame_size = kwargs.pop('max_frame_size', None) or MAX_FRAME_SIZE_BYTES
        self._channel_max = kwargs.pop('channel_max', None) or 65535
        self._idle_timeout = kwargs.pop('idle_timeout', None)
        self._properties = kwargs.pop('properties', None)
        self._network_trace = kwargs.pop("network_trace", False)

        # Session settings
        self._outgoing_window = kwargs.pop('outgoing_window', None) or OUTGOING_WIDNOW
        self._incoming_window = kwargs.pop('incoming_window', None) or INCOMING_WINDOW
        self._handle_max = kwargs.pop('handle_max', None)

        # Link settings
        self._send_settle_mode = kwargs.pop('send_settle_mode', SenderSettleMode.Unsettled)
        self._receive_settle_mode = kwargs.pop('receive_settle_mode', ReceiverSettleMode.Second)
        self._desired_capabilities = kwargs.pop('desired_capabilities', None)

        # transport
        if kwargs.get('transport_type') is TransportType.Amqp and kwargs.get('http_proxy') is not None:
            raise ValueError("Http proxy settings can't be passed if transport_type is explicitly set to Amqp")
        self._transport_type = kwargs.pop('transport_type', TransportType.Amqp)
        self._http_proxy = kwargs.pop('http_proxy', None)

        # Custom Endpoint
        self._custom_endpoint_address = kwargs.get("custom_endpoint_address")
        self._connection_verify = kwargs.get("connection_verify")

    def __enter__(self):
        """Run Client in a context manager."""
        self.open()
        return self

    def __exit__(self, *args):
        """Close and destroy Client on exiting a context manager."""
        self.close()

    def _client_ready(self):  # pylint: disable=no-self-use
        """Determine whether the client is ready to start sending and/or
        receiving messages. To be ready, the connection must be open and
        authentication complete.

        :rtype: bool
        """
        return True

    def _client_run(self, **kwargs):
        """Perform a single Connection iteration."""
        self._connection.listen(wait=self._socket_timeout)

    def _close_link(self, **kwargs):
        if self._link and not self._link._is_closed:
            self._link.detach(close=True)
            self._link = None

    def _do_retryable_operation(self, operation, *args, **kwargs):
        retry_settings = self._retry_policy.configure_retries()
        retry_active = True
        absolute_timeout = kwargs.pop("timeout", 0) or 0
        start_time = time.time()
        while retry_active:
            try:
                if absolute_timeout < 0:
                    raise TimeoutError("Operation timed out.")
                return operation(*args, timeout=absolute_timeout, **kwargs)
            except AMQPException as exc:
                if not self._retry_policy.is_retryable(exc):
                    raise
                if absolute_timeout >= 0:
                    retry_active = self._retry_policy.increment(retry_settings, exc)
                    if not retry_active:
                        break
                    time.sleep(self._retry_policy.get_backoff_time(retry_settings, exc))
                    if exc.condition == ErrorCondition.LinkDetachForced:
                        self._close_link()  # if link level error, close and open a new link
                        # TODO: check if there's any other code that we want to close link?
                    if exc.condition in (ErrorCondition.ConnectionCloseForced, ErrorCondition.SocketError):
                        # if connection detach or socket error, close and open a new connection
                        self.close()
                        # TODO: check if there's any other code we want to close connection
            except Exception:
                raise
            finally:
                end_time = time.time()
                if absolute_timeout > 0:
                    absolute_timeout -= (end_time - start_time)
        raise retry_settings['history'][-1]

    def open(self):
        """Open the client. The client can create a new Connection
        or an existing Connection can be passed in. This existing Connection
        may have an existing CBS authentication Session, which will be
        used for this client as well. Otherwise a new Session will be
        created.

        :param connection: An existing Connection that may be shared between
         multiple clients.
        :type connetion: ~uamqp.Connection
        """
        # pylint: disable=protected-access
        if self._session:
            return  # already open.
        _logger.debug("Opening client connection.")
        if not self._connection:
            self._connection = Connection(
                "amqps://" + self._hostname,
                sasl_credential=self._auth.sasl,
                ssl={'ca_certs':self._connection_verify or certifi.where()},
                container_id=self._name,
                max_frame_size=self._max_frame_size,
                channel_max=self._channel_max,
                idle_timeout=self._idle_timeout,
                properties=self._properties,
                network_trace=self._network_trace,
                transport_type=self._transport_type,
                http_proxy=self._http_proxy,
                custom_endpoint_address=self._custom_endpoint_address
            )
            self._connection.open()
        if not self._session:
            self._session = self._connection.create_session(
                incoming_window=self._incoming_window,
                outgoing_window=self._outgoing_window
            )
            self._session.begin()
        if self._auth.auth_type == AUTH_TYPE_CBS:
            self._cbs_authenticator = CBSAuthenticator(
                session=self._session,
                auth=self._auth,
                auth_timeout=self._auth_timeout
            )
            self._cbs_authenticator.open()
        self._shutdown = False

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
        self._shutdown = True
        if not self._session:
            return  # already closed.
        self._close_link(close=True)
        if self._cbs_authenticator:
            self._cbs_authenticator.close()
            self._cbs_authenticator = None
        self._session.end()
        self._session = None
        if not self._external_connection:
            self._connection.close()
            self._connection = None

    def auth_complete(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :rtype: bool
        """
        if self._cbs_authenticator and not self._cbs_authenticator.handle_token():
            self._connection.listen(wait=self._socket_timeout)
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
            try:
                self._connection.listen(wait=self._socket_timeout)
            except ValueError:
                return True
            return False
        return True

    def do_work(self, **kwargs):
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
        return self._client_run(**kwargs)

    def mgmt_request(self, message, **kwargs):
        """
        :param message: The message to send in the management request.
        :type message: ~uamqp.message.Message
        :keyword str operation: The type of operation to be performed. This value will
         be service-specific, but common values include READ, CREATE and UPDATE.
         This value will be added as an application property on the message.
        :keyword str operation_type: The type on which to carry out the operation. This will
         be specific to the entities of the service. This value will be added as
         an application property on the message.
        :keyword str node: The target node. Default node is `$management`.
        :keyword float timeout: Provide an optional timeout in seconds within which a response
         to the management request must be received.
        :rtype: ~uamqp.message.Message
        """

        # The method also takes "status_code_field" and "status_description_field"
        # keyword arguments as alternate names for the status code and description
        # in the response body. Those two keyword arguments are used in Azure services only.
        operation = kwargs.pop("operation", None)
        operation_type = kwargs.pop("operation_type", None)
        node = kwargs.pop("node", "$management")
        timeout = kwargs.pop('timeout', 0)
        try:
            mgmt_link = self._mgmt_links[node]
        except KeyError:

            mgmt_link = ManagementOperation(self._session, endpoint=node, **kwargs)
            self._mgmt_links[node] = mgmt_link
            mgmt_link.open()

            while not mgmt_link.ready():
                self._connection.listen(wait=False)

        operation_type = operation_type or b'empty'
        _logger.debug('args to execute: %r', (operation, operation_type, timeout))
        status, description, response = mgmt_link.execute(
            message,
            operation=operation,
            operation_type=operation_type,
            timeout=timeout
        )
        _logger.debug('status, description, response: %r', (status, description, response))
        return response


class SendClient(AMQPClient):
    def __init__(self, hostname, target, auth=None, **kwargs):
        self.target = target
        # Sender and Link settings
        self._max_message_size = kwargs.pop('max_message_size', None) or MAX_FRAME_SIZE_BYTES
        self._link_properties = kwargs.pop('link_properties', None)
        self._link_credit = kwargs.pop('link_credit', None)
        super(SendClient, self).__init__(hostname, auth=auth, **kwargs)

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
        if not self._link:
            self._link = self._session.create_sender_link(
                target_address=self.target,
                link_credit=self._link_credit,
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                properties=self._link_properties)
            self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    def _client_run(self, **kwargs):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        try:
            self._connection.listen(wait=self._socket_timeout, **kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing sender.")
            self._shutdown = True
            return False
        return True

    def _transfer_message(self, message_delivery, timeout=0):
        message_delivery.state = MessageDeliveryState.WaitingForSendAck
        on_send_complete = partial(self._on_send_complete, message_delivery)
        delivery = self._link.send_transfer(
            message_delivery.message,
            on_send_complete=on_send_complete,
            timeout=timeout
        )
        if not delivery.sent:
            raise RuntimeError("Message is not sent.")

    @staticmethod
    def _process_send_error(message_delivery, condition, description=None, info=None):
        try:
            amqp_condition = ErrorCondition(condition)
        except ValueError:
            error = MessageException(condition, description=description, info=info)
        else:
            error = MessageSendFailed(amqp_condition, description=description, info=info)
        message_delivery.state = MessageDeliveryState.Error
        message_delivery.error = error

    def _on_send_complete(self, message_delivery, reason, state):
        # TODO: check whether the callback would be called in case of message expiry or link going down
        #  and if so handle the state in the callback
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

    def _send_message_impl(self, message, **kwargs):
        timeout = kwargs.pop("timeout", 0)
        expire_time = (time.time() + timeout) if timeout else None
        self.open()
        message_delivery = _MessageDelivery(
            message,
            MessageDeliveryState.WaitingToBeSent,
            expire_time
        )

        while not self.client_ready():
            time.sleep(0.05)

        self._transfer_message(message_delivery, timeout)

        running = True
        while running and message_delivery.state not in MESSAGE_DELIVERY_DONE_STATES:
            running = self.do_work()
            if message_delivery.expiry and time.time() > message_delivery.expiry:
                self._on_send_complete(message_delivery, LinkDeliverySettleReason.TIMEOUT, None)

        if message_delivery.state in (MessageDeliveryState.Error, MessageDeliveryState.Cancelled, MessageDeliveryState.Timeout):
            try:
                raise message_delivery.error
            except TypeError:
                # This is a default handler
                raise MessageException(condition=ErrorCondition.UnknownError, description="Send failed.")

    def send_message(self, message, **kwargs):
        """
        :param ~uamqp.message.Message message:
        :keyword float timeout: timeout in seconds. If set to
         0, the client will continue to wait until the message is sent or error happens. The
         default is 0.
        """
        self._do_retryable_operation(self._send_message_impl, message=message, **kwargs)


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
    :param auto_complete: Whether to automatically settle message received via callback
     or via iterator. If the message has not been explicitly settled after processing
     the message will be accepted. Alternatively, when used with batch receive, this setting
     will determine whether the messages are pre-emptively settled during batching, or otherwise
     let to the user to be explicitly settled.
    :type auto_complete: bool
    :param retry_policy: A policy for parsing errors on link, connection and message
     disposition to determine whether the error should be retryable.
    :type retry_policy: ~uamqp.errors.RetryPolicy
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
    :param idle_timeout: Timeout in seconds after which the Connection will close
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

    def __init__(self, hostname, source, auth=None, **kwargs):
        self.source = source
        self._streaming_receive = kwargs.pop("streaming_receive", False)  # TODO: whether public?
        self._received_messages = queue.Queue()
        self._message_received_callback = kwargs.pop("message_received_callback", None)  # TODO: whether public?

        # Sender and Link settings
        self._max_message_size = kwargs.pop('max_message_size', None) or MAX_FRAME_SIZE_BYTES
        self._link_properties = kwargs.pop('link_properties', None)
        self._link_credit = kwargs.pop('link_credit', 300)
        super(ReceiveClient, self).__init__(hostname, auth=auth, **kwargs)

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
        if not self._link:
            self._link = self._session.create_receiver_link(
                source_address=self.source,
                link_credit=self._link_credit,
                send_settle_mode=self._send_settle_mode,
                rcv_settle_mode=self._receive_settle_mode,
                max_message_size=self._max_message_size,
                on_message_received=self._message_received,
                properties=self._link_properties,
                desired_capabilities=self._desired_capabilities
            )
            self._link.attach()
            return False
        if self._link.get_state().value != 3:  # ATTACHED
            return False
        return True

    def _client_run(self, **kwargs):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        try:
            self._connection.listen(wait=self._socket_timeout, **kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing receiver.")
            self._shutdown = True
            return False
        return True

    def _message_received(self, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param message: Received message.
        :type message: ~uamqp.message.Message
        """
        if self._message_received_callback:
            self._message_received_callback(message)
        if not self._streaming_receive:
            self._received_messages.put(message)
        # TODO: do we need settled property for a message?
        #elif not message.settled:
        #    # Message was received with callback processing and wasn't settled.
        #    _logger.info("Message was not settled.")

    def _receive_message_batch_impl(self, max_batch_size=None, on_message_received=None, timeout=0):
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._link_credit
        timeout = time.time() + timeout if timeout else 0
        receiving = True
        batch = []
        self.open()
        while len(batch) < max_batch_size:
            try:
                batch.append(self._received_messages.get_nowait())
                self._received_messages.task_done()
            except queue.Empty:
                break
        else:
            return batch

        to_receive_size = max_batch_size - len(batch)
        before_queue_size = self._received_messages.qsize()

        while receiving and to_receive_size > 0:
            if timeout and time.time() > timeout:
                break

            receiving = self.do_work(batch=to_receive_size)
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
                batch.append(self._received_messages.get_nowait())
                self._received_messages.task_done()
            except queue.Empty:
                break
        return batch

    def close(self):
        self._received_messages = queue.Queue()
        super(ReceiveClient, self).close()

    def receive_message_batch(self, **kwargs):
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
        return self._do_retryable_operation(
            self._receive_message_batch_impl,
            **kwargs
        )
