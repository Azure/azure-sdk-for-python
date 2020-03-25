# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import datetime
import functools
import uuid
import collections

import six

from uamqp import ReceiveClientAsync
from uamqp import authentication
from uamqp import constants, types, errors

from azure.servicebus.aio import Message, DeferredMessage
from azure.servicebus.aio.async_base_handler import BaseHandler
from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.common.errors import (
    InvalidHandlerState,
    NoActiveSession,
    SessionLockExpired)
from azure.servicebus.common.constants import (
    SESSION_LOCK_LOST,
    SESSION_LOCK_TIMEOUT,
    REQUEST_RESPONSE_RENEWLOCK_OPERATION,
    REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
    REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
    REQUEST_RESPONSE_PEEK_OPERATION,
    REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
    REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
    REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
    ReceiveSettleMode)


class Receiver(collections.abc.AsyncIterator, BaseHandler):  # pylint: disable=too-many-instance-attributes
    """A message receiver.

    This receive handler acts as an iterable message stream for retrieving
    messages for a Service Bus entity. It operates a single connection that must be opened and
    closed on completion. The service connection will remain open for the entirety of the iterator.
    If you find yourself only partially iterating the message stream, you should run the receiver
    in a `with` statement to ensure the connection is closed.
    The Receiver should not be instantiated directly, and should be accessed from a `QueueClient` or
    `SubscriptionClient` using the `get_receiver()` method.

    .. note:: This object is not thread-safe.

    :param handler_id: The ID used as the connection name for the Receiver.
    :type handler_id: str
    :param source: The endpoint from which to receive messages.
    :type source: ~uamqp.Source
    :param auth_config: The SASL auth credentials.
    :type auth_config: dict[str, str]
    :param loop: An async event loop
    :type loop: ~asyncio.EventLoop
    :param connection: A shared connection [not yet supported].
    :type connection: ~uamqp.Connection
    :param mode: The receive connection mode. Value must be either PeekLock or ReceiveAndDelete.
    :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
    :param encoding: The encoding used for string properties. Default is 'UTF-8'.
    :type encoding: str
    :param debug: Whether to enable network trace debug logs.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/async_samples/test_examples_async.py
            :start-after: [START open_close_receiver_context]
            :end-before: [END open_close_receiver_context]
            :language: python
            :dedent: 4
            :caption: Running a queue receiver within a context manager.

    """

    def __init__(
            self, handler_id, source, auth_config, *, loop=None, connection=None,
            mode=ReceiveSettleMode.PeekLock, encoding='UTF-8', debug=False, **kwargs):
        self._used = asyncio.Event()
        self.name = "SBReceiver-{}".format(handler_id)
        self.last_received = None
        self.mode = mode
        self.message_iter = None
        super(Receiver, self).__init__(
            source, auth_config, loop=loop, connection=connection, encoding=encoding, debug=debug, **kwargs)

    async def __anext__(self):
        await self._can_run()
        while True:
            if self.receiver_shutdown:
                await self.close()
                raise StopAsyncIteration
            try:
                received = await self.message_iter.__anext__()
                wrapped = self._build_message(received)
                return wrapped
            except StopAsyncIteration:
                await self.close()
                raise
            except Exception as e:  # pylint: disable=broad-except
                await self._handle_exception(e)

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAsync.from_shared_access_key(**self.auth_config)
        self._handler = ReceiveClientAsync(
            self.endpoint,
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            client_name=self.name,
            auto_complete=False,
            encoding=self.encoding,
            loop=self.loop,
            **self.handler_kwargs)

    async def _build_receiver(self):
        """This is a temporary patch pending a fix in uAMQP."""
        # pylint: disable=protected-access
        self._handler.message_handler = self._handler.receiver_type(
            self._handler._session,
            self._handler._remote_address,
            self._handler._name,
            on_message_received=self._handler._message_received,
            name='receiver-link-{}'.format(uuid.uuid4()),
            debug=self._handler._debug_trace,
            prefetch=self._handler._prefetch,
            max_message_size=self._handler._max_message_size,
            properties=self._handler._link_properties,
            error_policy=self._handler._error_policy,
            encoding=self._handler._encoding,
            loop=self._handler.loop)
        if self.mode != ReceiveSettleMode.PeekLock:
            self._handler.message_handler.send_settle_mode = constants.SenderSettleMode.Settled
            self._handler.message_handler.receive_settle_mode = constants.ReceiverSettleMode.ReceiveAndDelete
            self._handler.message_handler._settle_mode = constants.ReceiverSettleMode.ReceiveAndDelete
        await self._handler.message_handler.open_async()

    def _build_message(self, received):
        message = Message(None, message=received)
        message._receiver = self  # pylint: disable=protected-access
        self.last_received = message.sequence_number
        return message

    async def _can_run(self):
        if self._used.is_set():
            raise InvalidHandlerState("Receiver has already closed.")
        if self.receiver_shutdown:
            await self.close()
            raise InvalidHandlerState("Receiver has already closed.")
        if not self.running:
            await self.open()

    async def _renew_locks(self, *lock_tokens):
        message = {'lock-tokens': types.AMQPArray(lock_tokens)}
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_RENEWLOCK_OPERATION,
            message,
            mgmt_handlers.lock_renew_op)

    async def _settle_deferred(self, settlement, lock_tokens, dead_letter_details=None):
        message = {
            'disposition-status': settlement,
            'lock-tokens': types.AMQPArray(lock_tokens)}
        if dead_letter_details:
            message.update(dead_letter_details)
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default)

    @property
    def receiver_shutdown(self):
        """Whether the receiver connection has been marked for shutdown.

        If this value is `True` - it does not indicate that the connection
        has yet been closed.
        This property is used internally and should not be relied upon to asses
        the status of the connection.

        :rtype: bool
        """
        if self._handler:
            return self._handler._shutdown  # pylint: disable=protected-access
        return True

    @receiver_shutdown.setter
    def receiver_shutdown(self, value):
        """Mark the connection as ready for shutdown.

        This property is used internally and should not be set in normal usage.

        :param bool value: Whether to shutdown the connection.
        """
        if self._handler:
            self._handler._shutdown = value  # pylint: disable=protected-access
        else:
            raise ValueError("Receiver has no AMQP handler")

    @property
    def queue_size(self):
        """The current size of the unprocessed message queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    async def open(self):
        """Open receiver connection and authenticate session.

        If the receiver is already open, this operation will do nothing.
        This method will be called automatically when one starts to iterate
        messages in the receiver, so there should be no need to call it directly.
        A receiver opened with this method must be explicitly closed.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.

        .. note:: This operation is not thread-safe.

        """
        if self.running:
            return
        self.running = True
        try:
            await self._handler.open_async(connection=self.connection)
            self.message_iter = self._handler.receive_messages_iter_async()
            while not await self._handler.auth_complete_async():
                await asyncio.sleep(0.05)
            await self._build_receiver()
            while not await self._handler.client_ready_async():
                await asyncio.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                await self._handle_exception(e)
            except:
                self.running = False
                raise

    async def close(self, exception=None):
        """Close down the receiver connection.

        If the receiver has already closed, this operation will do nothing. An optional
        exception can be passed in to indicate that the handler was shutdown due to error.
        It is recommended to open a handler within a context manager as
        opposed to calling the method directly.
        The receiver will be implicitly closed on completion of the message iterator,
        however this method will need to be called explicitly if the message iterator is not run
        to completion.

        .. note:: This operation is not thread-safe.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START open_close_receiver_directly]
                :end-before: [END open_close_receiver_directly]
                :language: python
                :dedent: 4
                :caption: Iterate then explicitly close a Receiver.

        """
        if not self.running:
            return
        self.running = False
        self.receiver_shutdown = True
        self._used.set()
        await super(Receiver, self).close(exception=exception)

    async def peek(self, count=1, start_from=0):
        """Browse messages currently pending in the queue.

        Peeked messages are not removed from queue, nor are they locked. They cannot be completed,
        deferred or dead-lettered.

        :param count: The maximum number of messages to try and peek. The default
         value is 1.
        :type count: int
        :param start_from: A message sequence number from which to start browsing messages.
        :type start_from: int
        :rtype: list[~azure.servicebus.common.message.PeekMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_peek_messages]
                :end-before: [END receiver_peek_messages]
                :language: python
                :dedent: 4
                :caption: Peek messages in the queue.

        """
        await self._can_run()
        if not start_from:
            start_from = self.last_received or 1
        if int(count) < 1:
            raise ValueError("count must be 1 or greater.")
        if int(start_from) < 1:
            raise ValueError("start_from must be 1 or greater.")

        message = {
            'from-sequence-number': types.AMQPLong(start_from),
            'message-count': count
        }
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_PEEK_OPERATION,
            message,
            mgmt_handlers.peek_op)

    async def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock):
        """Receive messages that have previously been deferred.

        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :rtype: list[~azure.servicebus.aio.async_message.DeferredMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_defer_messages]
                :end-before: [END receiver_defer_messages]
                :language: python
                :dedent: 8
                :caption: Defer messages, then retrieve them by sequence number.

        """
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        await self._can_run()
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode)
        }
        handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode, message_type=DeferredMessage)
        messages = await self._mgmt_request_response(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler)
        for m in messages:
            m._receiver = self  # pylint: disable=protected-access
        return messages

    async def fetch_next(self, max_batch_size=None, timeout=None):
        """Receive a batch of messages at once.

        This approach it optimal if you wish to process multiple messages simultaneously.
        Note that the number of messages retrieved in a single batch will be dependent on
        whether `prefetch` was set for the receiver. This call will prioritize returning
        quickly over meeting a specified batch size, and so will return as soon as at least
        one message is received and there is a gap in incoming messages regardless
        of the specified batch size.

        :param max_batch_size: Maximum number of messages in the batch. Actual number
         returned will depend on prefetch size and incoming stream rate.
        :type max_batch_size: int
        :param timeout: The time to wait in seconds for the first message to arrive.
         If no messages arrive, and no timeout is specified, this call will not return
         until the connection is closed. If specified, an no messages arrive within the
         timeout period, an empty list will be returned.
        :rtype: list[~azure.servicebus.aio.async_message.Message]

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_fetch_batch]
                :end-before: [END receiver_fetch_batch]
                :language: python
                :dedent: 4
                :caption: Fetch a batch of messages.

        """
        await self._can_run()
        wrapped_batch = []
        max_batch_size = max_batch_size or self._handler._prefetch  # pylint: disable=protected-access
        try:
            timeout_ms = 1000 * timeout if timeout else 0
            batch = await self._handler.receive_message_batch_async(
                max_batch_size=max_batch_size,
                timeout=timeout_ms)
            for received in batch:
                message = self._build_message(received)
                wrapped_batch.append(message)
        except Exception as e:  # pylint: disable=broad-except
            await self._handle_exception(e)
        return wrapped_batch


class SessionReceiver(Receiver, mixins.SessionMixin):
    """A session message receiver.

    This receive handler acts as an iterable message stream for retrieving
    messages for a sessionful Service Bus entity. It operates a single connection that must be opened and
    closed on completion. The service connection will remain open for the entirety of the iterator.
    If you find yourself only partially iterating the message stream, you should run the receiver
    in a `with` statement to ensure the connection is closed.
    The Receiver should not be instantiated directly, and should be accessed from a `QueueClient` or
    `SubscriptionClient` using the `get_receiver()` method.
    When receiving messages from a session, connection errors that would normally be automatically
    retried will instead raise an error due to the loss of the lock on a particular session.
    A specific session can be specified, or the receiver can retrieve any available session using
    the `NEXT_AVAILABLE` constant.

    .. note:: This object is not thread-safe.

    :param handler_id: The ID used as the connection name for the Receiver.
    :type handler_id: str
    :param source: The endpoint from which to receive messages.
    :type source: ~uamqp.Source
    :param auth_config: The SASL auth credentials.
    :type auth_config: dict[str, str]
    :param session: The ID of the session to receive from.
    :type session: str or ~azure.servicebus.common.constants.NEXT_AVAILABLE
    :param loop: An async event loop
    :type loop: ~asyncio.EventLoop
    :param connection: A shared connection [not yet supported].
    :type connection: ~uamqp.Connection
    :param mode: The receive connection mode. Value must be either PeekLock or ReceiveAndDelete.
    :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
    :param encoding: The encoding used for string properties. Default is 'UTF-8'.
    :type encoding: str
    :param debug: Whether to enable network trace debug logs.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/async_samples/test_examples_async.py
            :start-after: [START open_close_receiver_session_context]
            :end-before: [END open_close_receiver_session_context]
            :language: python
            :dedent: 4
            :caption: Running a session receiver within a context manager.

        .. literalinclude:: ../samples/async_samples/test_examples_async.py
            :start-after: [START open_close_receiver_session_nextavailable]
            :end-before: [END open_close_receiver_session_nextavailable]
            :language: python
            :dedent: 4
            :caption: Running a session receiver for the next available session.

    """

    def __init__(
            self, handler_id, source, auth_config, *, session=None, loop=None,
            connection=None, encoding='UTF-8', debug=False, **kwargs):
        self.session_id = None
        self.session_filter = session
        self.locked_until = None
        self.session_start = None
        self.auto_reconnect = False
        self.auto_renew_error = None
        super(SessionReceiver, self).__init__(
            handler_id, source, auth_config, loop=loop,
            connection=connection, encoding=encoding, debug=debug, **kwargs)

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAsync.from_shared_access_key(**self.auth_config)
        self._handler = ReceiveClientAsync(
            self._get_source(),
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            client_name=self.name,
            on_attach=self._on_attach,
            auto_complete=False,
            encoding=self.encoding,
            loop=self.loop,
            **self.handler_kwargs)

    async def _can_run(self):
        await super(SessionReceiver, self)._can_run()
        if self.expired:
            raise SessionLockExpired(inner_exception=self.auto_renew_error)

    async def _handle_exception(self, exception):
        if isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_LOST:
            error = SessionLockExpired("Connection detached - lock on Session {} lost.".format(self.session_id))
            await self.close(exception=error)
            raise error
        elif isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_TIMEOUT:
            error = NoActiveSession("Queue has no active session to receive from.")
            await self.close(exception=error)
            raise error
        return await super(SessionReceiver, self)._handle_exception(exception)

    async def _settle_deferred(self, settlement, lock_tokens, dead_letter_details=None):
        message = {
            'disposition-status': settlement,
            'lock-tokens': types.AMQPArray(lock_tokens),
            'session-id': self.session_id}
        if dead_letter_details:
            message.update(dead_letter_details)
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default)

    async def get_session_state(self):
        """Get the session state.

        Returns None if no state has been set.

        :rtype: str

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START set_session_state]
                :end-before: [END set_session_state]
                :language: python
                :dedent: 4
                :caption: Getting and setting the state of a session.

        """
        await self._can_run()
        response = await self._mgmt_request_response(
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {'session-id': self.session_id},
            mgmt_handlers.default)
        session_state = response.get(b'session-state')
        if isinstance(session_state, six.binary_type):
            session_state = session_state.decode('UTF-8')
        return session_state

    async def set_session_state(self, state):
        """Set the session state.

        :param state: The state value.
        :type state: str or bytes or bytearray

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START set_session_state]
                :end-before: [END set_session_state]
                :language: python
                :dedent: 4
                :caption: Getting and setting the state of a session.

        """
        await self._can_run()
        state = state.encode(self.encoding) if isinstance(state, six.text_type) else state
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {'session-id': self.session_id, 'session-state': bytearray(state)},
            mgmt_handlers.default)

    async def renew_lock(self):
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the session
        to continue message processing. Once the lock is lost the connection will be closed.
        This operation can also be performed as an asynchronous background task by registering the session
        with an `azure.servicebus.aio.AutoLockRenew` instance.

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_renew_session_lock]
                :end-before: [END receiver_renew_session_lock]
                :language: python
                :dedent: 4
                :caption: Renew the sesison lock.

        """
        await self._can_run()
        expiry = await self._mgmt_request_response(
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {'session-id': self.session_id},
            mgmt_handlers.default)
        self.locked_until = datetime.datetime.fromtimestamp(expiry[b'expiration']/1000.0)

    async def peek(self, count=1, start_from=0):
        """Browse messages currently pending in the queue.

        Peeked messages are not removed from queue, nor are they locked.
        They cannot be completed, deferred or dead-lettered.
        This operation will only peek pending messages in the current session.

        :param count: The maximum number of messages to try and peek. The default
         value is 1.
        :type count: int
        :param start_from: A message sequence number from which to start browsing messages.
        :type start_from: int
        :rtype: list[~azure.servicebus.common.message.PeekMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_peek_session_messages]
                :end-before: [END receiver_peek_session_messages]
                :language: python
                :dedent: 8
                :caption: Peek messages in the queue.

        """
        if not start_from:
            start_from = self.last_received or 1
        if int(count) < 1:
            raise ValueError("count must be 1 or greater.")
        if int(start_from) < 1:
            raise ValueError("start_from must be 1 or greater.")

        await self._can_run()
        message = {
            'from-sequence-number': types.AMQPLong(start_from),
            'message-count': count,
            'session-id': self.session_id}
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_PEEK_OPERATION,
            message,
            mgmt_handlers.peek_op)

    async def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock):
        """Receive messages that have previously been deferred.

        This operation can only receive deferred messages from the current session.
        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :rtype: list[~azure.servicebus.aio.async_message.DeferredMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/async_samples/test_examples_async.py
                :start-after: [START receiver_defer_session_messages]
                :end-before: [END receiver_defer_session_messages]
                :language: python
                :dedent: 8
                :caption: Defer messages, then retrieve them by sequence number.

        """
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        await self._can_run()
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode),
            'session-id': self.session_id
        }
        handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode, message_type=DeferredMessage)
        messages = await self._mgmt_request_response(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler)
        for m in messages:
            m._receiver = self  # pylint: disable=protected-access
        return messages

    async def list_sessions(self, updated_since=None, max_results=100, skip=0):
        """List session IDs.

        List the IDs of sessions in the queue with pending messages and where the state of the session
        has been updated since the timestamp provided. If no timestamp is provided, all will be returned.
        If the state of a session has never been set, it will not be returned regardless of whether
        there are messages pending.

        :param updated_since: The UTC datetime from which to return updated pending session IDs.
        :type updated_since: ~datetime.datetime
        :param max_results: The maximum number of session IDs to return. Default value is 100.
        :type max_results: int
        :param skip: The page value to jump to. Default value is 0.
        :type skip: int
        :rtype: list[str]
        """
        if int(max_results) < 1:
            raise ValueError("max_results must be 1 or greater.")

        await self._can_run()
        message = {
            'last-updated-time': updated_since or datetime.datetime.utcfromtimestamp(0),
            'skip': skip,
            'top': max_results,
        }
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
            message,
            mgmt_handlers.list_sessions_op,
            keep_alive_associated_link=False)
