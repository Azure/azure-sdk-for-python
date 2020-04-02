# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import threading
import time
import datetime
import functools
import uuid

import six

from uamqp import ReceiveClient
from uamqp import authentication
from uamqp import constants, types, errors

from azure.servicebus.common.message import Message
from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.base_handler import BaseHandler
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


class Receiver(BaseHandler):  # pylint: disable=too-many-instance-attributes
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
    :param connection: A shared connection [not yet supported].
    :type connection: ~uamqp.Connection
    :param mode: The receive connection mode. Value must be either PeekLock or ReceiveAndDelete.
    :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
    :param encoding: The encoding used for string properties. Default is 'UTF-8'.
    :type encoding: str
    :param debug: Whether to enable network trace debug logs.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START get_receiver]
            :end-before: [END get_receiver]
            :language: python
            :dedent: 4
            :caption: Get the receiver client from Service Bus client

    """

    def __init__(
            self, handler_id, source, auth_config, connection=None,
            mode=ReceiveSettleMode.PeekLock, encoding='UTF-8', debug=False, **kwargs):
        self._used = threading.Event()
        self.name = "SBReceiver-{}".format(handler_id)
        self.last_received = None
        self.mode = mode
        self.message_iter = None
        super(Receiver, self).__init__(
            source, auth_config, connection=connection, encoding=encoding, debug=debug, **kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        self._can_run()
        while True:
            if self.receiver_shutdown:
                self.close()
                raise StopIteration
            try:
                received = next(self.message_iter)
                wrapped = self._build_message(received)
                return wrapped
            except StopIteration:
                self.close()
                raise
            except Exception as e:  # pylint: disable=broad-except
                self._handle_exception(e)

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAuth.from_shared_access_key(**self.auth_config)
        self._handler = ReceiveClient(
            self.endpoint,
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            client_name=self.name,
            auto_complete=False,
            encoding=self.encoding,
            **self.handler_kwargs)

    def _build_message(self, received):
        message = Message(None, message=received)
        message._receiver = self  # pylint: disable=protected-access
        self.last_received = message.sequence_number
        return message

    def _can_run(self):
        if self._used.is_set():
            raise InvalidHandlerState("Receiver has already closed.")
        if self.receiver_shutdown:
            self.close()
            raise InvalidHandlerState("Receiver has already closed.")
        if not self.running:
            self.open()

    def _renew_locks(self, *lock_tokens):
        message = {'lock-tokens': types.AMQPArray(lock_tokens)}
        return self._mgmt_request_response(
            REQUEST_RESPONSE_RENEWLOCK_OPERATION,
            message,
            mgmt_handlers.lock_renew_op)

    def _settle_deferred(self, settlement, lock_tokens, dead_letter_details=None):
        message = {
            'disposition-status': settlement,
            'lock-tokens': types.AMQPArray(lock_tokens)}
        if dead_letter_details:
            message.update(dead_letter_details)
        return self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default)

    def _build_receiver(self):
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
            encoding=self._handler._encoding)
        if self.mode != ReceiveSettleMode.PeekLock:
            self._handler.message_handler.send_settle_mode = constants.SenderSettleMode.Settled
            self._handler.message_handler.receive_settle_mode = constants.ReceiverSettleMode.ReceiveAndDelete
            self._handler.message_handler._settle_mode = constants.ReceiverSettleMode.ReceiveAndDelete
        self._handler.message_handler.open()

    def next(self):
        return self.__next__()

    @property
    def receiver_shutdown(self):
        if self._handler:
            return self._handler._shutdown  # pylint: disable=protected-access
        return True

    @receiver_shutdown.setter
    def receiver_shutdown(self, value):
        if self._handler:
            self._handler._shutdown = value  # pylint: disable=protected-access
        else:
            raise ValueError("Receiver has no AMQP handler")

    @property
    def queue_size(self):
        """The current size of the unprocessed message queue.

        :rtype: int

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START queue_size]
                :end-before: [END queue_size]
                :language: python
                :dedent: 4
                :caption: Get the number of unprocessed messages in the queue

        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    def peek(self, count=1, start_from=None):
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
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START peek_messages]
                :end-before: [END peek_messages]
                :language: python
                :dedent: 4
                :caption: Look at pending messages in the queue

        """
        if not start_from:
            start_from = self.last_received or 1
        if int(count) < 1:
            raise ValueError("count must be 1 or greater.")
        if int(start_from) < 1:
            raise ValueError("start_from must be 1 or greater.")

        self._can_run()
        message = {
            'from-sequence-number': types.AMQPLong(start_from),
            'message-count': count
        }
        return self._mgmt_request_response(
            REQUEST_RESPONSE_PEEK_OPERATION,
            message,
            mgmt_handlers.peek_op)

    def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock):
        """Receive messages that have previously been deferred.

        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :rtype: list[~azure.servicebus.common.message.DeferredMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START receive_deferred_messages]
                :end-before: [END receive_deferred_messages]
                :language: python
                :dedent: 8
                :caption: Get the messages which were previously deferred

        """
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        self._can_run()
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode)
        }
        handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode)
        messages = self._mgmt_request_response(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler)
        for m in messages:
            m._receiver = self  # pylint: disable=protected-access
        return messages

    def open(self):
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
            self._handler.open(connection=self.connection)
            self.message_iter = self._handler.receive_messages_iter()
            while not self._handler.auth_complete():
                time.sleep(0.05)
            self._build_receiver()
            while not self._handler.client_ready():
                time.sleep(0.05)
        except Exception as e:  # pylint: disable=broad-except
            try:
                self._handle_exception(e)
            except:
                self.running = False
                raise

    def close(self, exception=None):
        """Close down the receiver connection.

        If the receiver has already closed, this operation will do nothing. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.
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
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START open_close_receiver_connection]
                :end-before: [END open_close_receiver_connection]
                :language: python
                :dedent: 4
                :caption: Close the connection and shutdown the receiver

        """
        if not self.running:
            return
        self.running = False
        self.receiver_shutdown = True
        self._used.set()
        super(Receiver, self).close(exception=exception)

    def fetch_next(self, max_batch_size=None, timeout=None):
        """Receive a batch of messages at once.

        This approach it optimal if you wish to process multiple messages simultaneously. Note that the
        number of messages retrieved in a single batch will be dependent on
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
        :rtype: list[~azure.servicebus.common.message.Message]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START fetch_next_messages]
                :end-before: [END fetch_next_messages]
                :language: python
                :dedent: 4
                :caption: Get the messages in batch from the receiver

        """
        self._can_run()
        wrapped_batch = []
        max_batch_size = max_batch_size or self._handler._prefetch  # pylint: disable=protected-access
        try:
            timeout_ms = 1000 * timeout if timeout else 0
            batch = self._handler.receive_message_batch(
                max_batch_size=max_batch_size,
                timeout=timeout_ms)
            for received in batch:
                message = self._build_message(received)
                wrapped_batch.append(message)
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)
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
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_session_receiver_client]
            :end-before: [END create_session_receiver_client]
            :language: python
            :dedent: 4
            :caption: Running a session receiver within a context manager.

        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_receiver_session_nextavailable]
            :end-before: [END create_receiver_session_nextavailable]
            :language: python
            :dedent: 4
            :caption: Running a session receiver for the next available session.

    """

    def __init__(
            self, handler_id, source, auth_config, session=None,
            connection=None, encoding='UTF-8', debug=False, **kwargs):
        self.session_id = None
        self.session_filter = session
        self.locked_until = None
        self.session_start = None
        self.auto_reconnect = False
        self.auto_renew_error = None
        super(SessionReceiver, self).__init__(
            handler_id, source, auth_config,
            connection=connection, encoding=encoding, debug=debug, **kwargs)

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAuth.from_shared_access_key(**self.auth_config)
        self._handler = ReceiveClient(
            self._get_source(),
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            error_policy=self.error_policy,
            client_name=self.name,
            on_attach=self._on_attach,
            auto_complete=False,
            encoding=self.encoding,
            **self.handler_kwargs)

    def _can_run(self):
        super(SessionReceiver, self)._can_run()
        if self.expired:
            raise SessionLockExpired(inner_exception=self.auto_renew_error)

    def _handle_exception(self, exception):
        if isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_LOST:
            error = SessionLockExpired("Connection detached - lock on Session {} lost.".format(self.session_id))
            self.close(exception=error)
            raise error
        elif isinstance(exception, errors.LinkDetach) and exception.condition == SESSION_LOCK_TIMEOUT:
            error = NoActiveSession("Queue has no active session to receive from.")
            self.close(exception=error)
            raise error
        return super(SessionReceiver, self)._handle_exception(exception)

    def _settle_deferred(self, settlement, lock_tokens, dead_letter_details=None):
        message = {
            'disposition-status': settlement,
            'lock-tokens': types.AMQPArray(lock_tokens),
            'session-id': self.session_id}
        if dead_letter_details:
            message.update(dead_letter_details)
        return self._mgmt_request_response(
            REQUEST_RESPONSE_UPDATE_DISPOSTION_OPERATION,
            message,
            mgmt_handlers.default)

    def get_session_state(self):
        """Get the session state.

        Returns None if no state has been set.

        :rtype: str

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START get_session_state]
                :end-before: [END get_session_state]
                :language: python
                :dedent: 4
                :caption: Get the session state of the receiver

        """
        self._can_run()
        response = self._mgmt_request_response(
            REQUEST_RESPONSE_GET_SESSION_STATE_OPERATION,
            {'session-id': self.session_id},
            mgmt_handlers.default)
        session_state = response.get(b'session-state')
        if isinstance(session_state, six.binary_type):
            session_state = session_state.decode('UTF-8')
        return session_state

    def set_session_state(self, state):
        """Set the session state.

        :param state: The state value.
        :type state: str, bytes or bytearray

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START set_session_state]
                :end-before: [END set_session_state]
                :language: python
                :dedent: 4
                :caption: Set the session state of the receiver

        """
        self._can_run()
        state = state.encode(self.encoding) if isinstance(state, six.text_type) else state
        return self._mgmt_request_response(
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {'session-id': self.session_id, 'session-state': bytearray(state)},
            mgmt_handlers.default)

    def renew_lock(self):
        """Renew the session lock.

        This operation must be performed periodically in order to retain a lock on the
        session to continue message processing.
        Once the lock is lost the connection will be closed. This operation can
        also be performed as a threaded background task by registering the session
        with an `azure.servicebus.AutoLockRenew` instance.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START renew_lock]
                :end-before: [END renew_lock]
                :language: python
                :dedent: 4
                :caption: Renew the session lock before it expires

        """
        self._can_run()
        expiry = self._mgmt_request_response(
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {'session-id': self.session_id},
            mgmt_handlers.default)
        self.locked_until = datetime.datetime.fromtimestamp(expiry[b'expiration']/1000.0)

    def peek(self, count=1, start_from=None):
        """Browse messages currently pending in the queue.

        Peeked messages are not removed from queue, nor are they locked. They cannot be completed,
        deferred or dead-lettered.
        This operation will only peek pending messages in the current session.

        :param count: The maximum number of messages to try and peek. The default
         value is 1.
        :type count: int
        :param start_from: A message sequence number from which to start browsing messages.
        :type start_from: int
        :rtype: list[~azure.servicebus.common.message.PeekMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START peek_messages]
                :end-before: [END peek_messages]
                :language: python
                :dedent: 4
                :caption: Look at pending messages in the queue

        """
        if not start_from:
            start_from = self.last_received or 1
        if int(count) < 1:
            raise ValueError("count must be 1 or greater.")
        if int(start_from) < 1:
            raise ValueError("start_from must be 1 or greater.")

        self._can_run()
        message = {
            'from-sequence-number': types.AMQPLong(start_from),
            'message-count': count,
            'session-id': self.session_id}
        return self._mgmt_request_response(
            REQUEST_RESPONSE_PEEK_OPERATION,
            message,
            mgmt_handlers.peek_op)

    def receive_deferred_messages(self, sequence_numbers, mode=ReceiveSettleMode.PeekLock):
        """Receive messages that have previously been deferred.

        This operation can only receive deferred messages from the current session.
        When receiving deferred messages from a partitioned entity, all of the supplied
        sequence numbers must be messages from the same partition.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :rtype: list[~azure.servicebus.common.message.DeferredMessage]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START receive_deferred_messages]
                :end-before: [END receive_deferred_messages]
                :language: python
                :dedent: 4
                :caption: Get the messages which were previously deferred in the session

        """
        if not sequence_numbers:
            raise ValueError("At least one sequence number must be specified.")
        self._can_run()
        try:
            receive_mode = mode.value.value
        except AttributeError:
            receive_mode = int(mode)
        message = {
            'sequence-numbers': types.AMQPArray([types.AMQPLong(s) for s in sequence_numbers]),
            'receiver-settle-mode': types.AMQPuInt(receive_mode),
            'session-id': self.session_id
        }
        handler = functools.partial(mgmt_handlers.deferred_message_op, mode=receive_mode)
        messages = self._mgmt_request_response(
            REQUEST_RESPONSE_RECEIVE_BY_SEQUENCE_NUMBER,
            message,
            handler)
        for m in messages:
            m._receiver = self  # pylint: disable=protected-access
        return messages

    def list_sessions(self, updated_since=None, max_results=100, skip=0):
        """List session IDs.

        List the Session IDs with pending messages in the queue where the state of the session
        has been updated since the timestamp provided. If no timestamp is provided, all will be returned.
        If the state of a Session has never been set, it will not be returned regardless of whether
        there are messages pending.

        :param updated_since: The UTC datetime from which to return updated pending Session IDs.
        :type updated_since: datetime.datetime
        :param max_results: The maximum number of Session IDs to return. Default value is 100.
        :type max_results: int
        :param skip: The page value to jump to. Default value is 0.
        :type skip: int
        :rtype: list[str]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START list_sessions]
                :end-before: [END list_sessions]
                :language: python
                :dedent: 4
                :caption: List the ids of sessions with pending messages

        """
        if int(max_results) < 1:
            raise ValueError("max_results must be 1 or greater.")

        self._can_run()
        message = {
            'last-updated-time': updated_since or datetime.datetime.utcfromtimestamp(0),
            'skip': skip,
            'top': max_results,
        }
        return self._mgmt_request_response(
            REQUEST_RESPONSE_GET_MESSAGE_SESSIONS_OPERATION,
            message,
            mgmt_handlers.list_sessions_op,
            keep_alive_associated_link=False)
