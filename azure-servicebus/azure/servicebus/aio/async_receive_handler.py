#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

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


class Receiver(collections.abc.AsyncIterator, BaseHandler):
    """
    Implements a Receiver.
    """

    def __init__(
            self, handler_id, source, auth_config, *, loop=None, connection=None,
            mode=ReceiveSettleMode.PeekLock, encoding='UTF-8', debug=False, **kwargs):
        """
        Instantiate a receiver.
        :param source: The source entity from which to receive messages.
        :type source: ~uamqp.Source
        """
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
        """This is a temporary patch pending a fix in uAMQP"""
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
        """
        The current size of the unprocessed message queue.
        :returns: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    async def open(self):
        """Open handler connection."""
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
        """Close handler connection."""
        if not self.running:
            return
        self.running = False
        self.receiver_shutdown = True
        self._used.set()
        await super(Receiver, self).close(exception=exception)

    async def peek(self, count=1, start_from=None):
        """Browse messages pending in the queue. This operation does not remove
        messages from the queue, nor does it lock them.

        :param count: How many message to try and peek.
        :type count: int
        :param start_from: An enqueue timestamp from which to peek at messages.
        :type start_from: ~datetime.datetime
        :returns: list[~azure.servicebus.common.message.PeekMessage]
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

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :returns: list[~azure.servicebus.aio.async_message.Message]
        """
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
        """
        Receive messages from ServiceBus entity.

        :param max_batch_size: Receive a batch of messages. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new messages. If combined with a timeout and no messages are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :returns: list[~azure.servicebus.aio.async_message.Message]
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

    def __init__(
            self, handler_id, target, auth_config, *, session=None, loop=None,
            connection=None, encoding='UTF-8', debug=False, **kwargs):
        self.session_id = None
        self.session_filter = session
        self.locked_until = None
        self.session_start = None
        self.auto_reconnect = False
        self.auto_renew_error = None
        super(SessionReceiver, self).__init__(
            handler_id, target, auth_config, loop=loop,
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
        """Get the session state. Returns None if no state
        has been set.

        :returns: str
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
        :type state: str, bytes or bytearray
        """
        await self._can_run()
        state = state.encode(self.encoding) if isinstance(state, six.text_type) else state
        return await self._mgmt_request_response(
            REQUEST_RESPONSE_SET_SESSION_STATE_OPERATION,
            {'session-id': self.session_id, 'session-state': bytearray(state)},
            mgmt_handlers.default)

    async def renew_lock(self):
        """Renew session lock."""
        await self._can_run()
        expiry = await self._mgmt_request_response(
            REQUEST_RESPONSE_RENEW_SESSION_LOCK_OPERATION,
            {'session-id': self.session_id},
            mgmt_handlers.default)
        self.locked_until = datetime.datetime.fromtimestamp(expiry[b'expiration']/1000.0)

    async def peek(self, count=1, start_from=None):
        """Browse messages pending in the session. This operation does not remove
        messages from the queue, nor does it lock them.

        :param count: How many message to try and peek.
        :type count: int
        :param start_from: An enqueue timestamp from which to peek at messages.
        :type start_from: ~datetime.datetime
        :returns: list[~azure.servicebus.common.message.PeekMessage]
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
        Deferred messages must have had same Session ID as the current receiver.

        :param sequence_numbers: A list of the sequence numbers of messages that have been
         deferred.
        :type sequence_numbers: list[int]
        :param mode: The receive mode, default value is PeekLock.
        :type mode: ~azure.servicebus.common.constants.ReceiveSettleMode
        :returns: list[~azure.servicebus.aio.async_message.Message]
        """
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
        """List the Session IDs with pending messages in the queue where the 'State' of the session
        has been updated since the timestamp provided. If no timestamp is provided, all will be returned.
        If the state of a Session has never been set, it will not be returned regardless of whether
        there are messages pending.
        :param updated_since: The UTC datetime from which to return updated pending Session IDs.
        :type updated_since: datetime.datetime
        :param max_results: The maximum number of Session IDs to return. Default value is 100.
        :type max_results: int
        :param skip: The page value to jump to. Default value is 0.
        :type skip: int
        :returns: list[str]
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
            mgmt_handlers.list_sessions_op)
