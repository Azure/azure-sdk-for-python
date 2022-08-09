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
from typing import Any, Dict, Literal, Optional, Tuple, Union, overload
import uuid
import time
import queue
import certifi
from functools import partial

from ..outcomes import Accepted, Modified, Received, Rejected, Released
from ._connection_async import Connection
from ._management_operation_async import ManagementOperation
from ._receiver_async import ReceiverLink
from ._sender_async import SenderLink
from ._session_async import Session
from ._cbs_async import CBSAuthenticator
from ..client import AMQPClient as AMQPClientSync
from ..client import ReceiveClient as ReceiveClientSync
from ..client import SendClient as SendClientSync
from ..message import _MessageDelivery
from ..endpoints import Source, Target
from ..constants import (
    SenderSettleMode,
    ReceiverSettleMode,
    MessageDeliveryState,
    SEND_DISPOSITION_ACCEPT,
    SEND_DISPOSITION_REJECT,
    LinkDeliverySettleReason,
    MESSAGE_DELIVERY_DONE_STATES,
    AUTH_TYPE_CBS,
)
from ..error import (
    AMQPError,
    ErrorResponse,
    ErrorCondition,
    AMQPException,
    MessageException
)
from ..constants import LinkState

_logger = logging.getLogger(__name__)


class AMQPClientAsync(AMQPClientSync):
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

    async def __aenter__(self):
        """Run Client in an async context manager."""
        await self.open_async()
        return self

    async def __aexit__(self, *args):
        """Close and destroy Client on exiting an async context manager."""
        await self.close_async()

    async def _client_ready_async(self):  # pylint: disable=no-self-use
        """Determine whether the client is ready to start sending and/or
        receiving messages. To be ready, the connection must be open and
        authentication complete.

        :rtype: bool
        """
        return True

    async def _client_run_async(self, **kwargs):
        """Perform a single Connection iteration."""
        await self._connection.listen(wait=self._socket_timeout)

    async def _close_link_async(self, **kwargs):
        if self._link and not self._link._is_closed:
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
                        # TODO: check if there's any other code that we want to close link?
                    if exc.condition in (ErrorCondition.ConnectionCloseForced, ErrorCondition.SocketError):
                        # if connection detach or socket error, close and open a new connection
                        await self.close_async()
                        # TODO: check if there's any other code we want to close connection
            except Exception:
                raise
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
        :type connetion: ~pyamqp.aio.Connection
        """
        # pylint: disable=protected-access
        if self._session:
            return  # already open.
        _logger.debug("Opening client connection.")
        if connection:
            self._connection = connection
            self._external_connection = True
        if not self._connection:
            self._connection = Connection(
                "amqps://" + self._hostname,
                sasl_credential=self._auth.sasl,
                ssl={'ca_certs': self._connection_verify or certifi.where()},
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
        self._shutdown = False

    async def close_async(self):
        """Close the client asynchronously. This includes closing the Session
        and CBS authentication layer as well as the Connection.
        If the client was opened using an external Connection,
        this will be left intact.
        """
        self._shutdown = True
        if not self._session:
            return  # already closed.
        await self._close_link_async(close=True)
        if self._cbs_authenticator:
            await self._cbs_authenticator.close()
            self._cbs_authenticator = None
        await self._session.end()
        self._session = None
        if not self._external_connection:
            await self._connection.close()
            self._connection = None

    async def auth_complete_async(self):
        """Whether the authentication handshake is complete during
        connection initialization.

        :rtype: bool
        """
        if self._cbs_authenticator and not (await self._cbs_authenticator.handle_token()):
            await self._connection.listen(wait=self._socket_timeout)
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

        :rtype: bool
        :raises: TimeoutError or ~uamqp.errors.ClientTimeout if CBS authentication timeout reached.
        """
        if self._shutdown:
            return False
        if not await self.client_ready_async():
            return True
        return await self._client_run_async(**kwargs)

    async def mgmt_request_async(self, message, **kwargs):
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
            await mgmt_link.open()

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
        if self._link.get_state() != LinkState.ATTACHED:  # ATTACHED
            return False
        return True

    async def _client_run_async(self, **kwargs):
        """MessageSender Link is now open - perform message send
        on all pending messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        try:
            await self._link.update_pending_deliveries()
            await self._connection.listen(**kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing sender.")
            self._shutdown = True
            return False
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

    async def _send_message_impl_async(self, message, **kwargs):
        timeout = kwargs.pop("timeout", 0)
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

        if message_delivery.state in (
            MessageDeliveryState.Error,
            MessageDeliveryState.Cancelled,
            MessageDeliveryState.Timeout
        ):
            try:
                raise message_delivery.error
            except TypeError:
                # This is a default handler
                raise MessageException(condition=ErrorCondition.UnknownError, description="Send failed.")

    async def send_message_async(self, message, **kwargs):
        """
        :param ~uamqp.message.Message message:
        :param int timeout: timeout in seconds
        """
        await self._do_retryable_operation_async(self._send_message_impl_async, message=message, **kwargs)


class ReceiveClientAsync(ReceiveClientSync, AMQPClientAsync):
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
    :param timeout: A timeout in seconds. The receiver will shut down if no
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
        if not self._link:
            self._link = self._session.create_receiver_link(
                source_address=self.source,
                link_credit=self._link_credit,
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
        if self._link.get_state() != LinkState.ATTACHED:  # ATTACHED
            return False
        return True

    async def _client_run_async(self, **kwargs):
        """MessageReceiver Link is now open - start receiving messages.
        Will return True if operation successful and client can remain open for
        further work.

        :rtype: bool
        """
        try:
            await self._link.flow()
            await self._connection.listen(wait=self._socket_timeout, **kwargs)
        except ValueError:
            _logger.info("Timeout reached, closing receiver.")
            self._shutdown = True
            return False
        return True

    async def _message_received_async(self, frame, message):
        """Callback run on receipt of every message. If there is
        a user-defined callback, this will be called.
        Additionally if the client is retrieving messages for a batch
        or iterator, the message will be added to an internal queue.

        :param message: Received message.
        :type message: ~uamqp.message.Message
        """
        if self._message_received_callback:
            print("CALLING MESSAGE RECEIVED")
            await self._message_received_callback(message)
        if not self._streaming_receive:
            self._received_messages.put((frame, message))
        # TODO: do we need settled property for a message?
        # elif not message.settled:
        #    # Message was received with callback processing and wasn't settled.
        #    _logger.info("Message was not settled.")

    async def _receive_message_batch_impl_async(self, max_batch_size=None, on_message_received=None, timeout=0):
        self._message_received_callback = on_message_received
        max_batch_size = max_batch_size or self._link_credit
        timeout_time = time.time() + timeout if timeout else 0
        receiving = True
        batch = []
        await self.open_async()
        while len(batch) < max_batch_size:
            try:
                # TODO: This looses the transfer frame data
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

    async def receive_message_batch_async(self, **kwargs):
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
        :param timeout: Timeout in seconds for which to wait to receive any messages.
         If no messages are received in this time, an empty list will be returned. If set to
         0, the client will continue to wait until at least one message is received. The
         default is 0.
        :type timeout: float
        """
        return await self._do_retryable_operation_async(
            self._receive_message_batch_impl_async,
            **kwargs
        )

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
            state = Accepted()
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
            first, last = delivery_id
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
