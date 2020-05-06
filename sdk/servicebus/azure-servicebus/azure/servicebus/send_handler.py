# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import logging

from uamqp import SendClient
from uamqp import authentication
from uamqp import constants, types, errors

from azure.servicebus.base_handler import BaseHandler
from azure.servicebus.common.errors import MessageSendFailed
from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.common.message import Message
from azure.servicebus.common.constants import (
    REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
    REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION)


_log = logging.getLogger(__name__)


class Sender(BaseHandler, mixins.SenderMixin):
    """A message sender.

    This handler is for sending messages to a Service Bus entity.
    It operates a single connection that must be opened and closed on completion.
    The Sender can be run within a context manager to ensure that the connection is closed on exit.
    The Sender should not be instantiated directly, and should be accessed from a `QueueClient` or
    `TopicClient` using the `get_sender()` method.

    .. note:: This object is not thread-safe.

    :param handler_id: The ID used as the connection name for the Sender.
    :type handler_id: str
    :param target: The endpoint to send messages to.
    :type target: ~uamqp.Target
    :param auth_config: The SASL auth credentials.
    :type auth_config: dict[str, str]
    :param session: An optional session ID. If supplied, all outgoing messages will have this
     session ID added (unless they already have one specified).
    :type session: str
    :param connection: A shared connection [not yet supported].
    :type connection: ~uamqp.Connection
    :param encoding: The encoding used for string properties. Default is 'UTF-8'.
    :type encoding: str
    :param debug: Whether to enable network trace debug logs.
    :type debug: bool

    .. admonition:: Example:
        .. literalinclude:: ../samples/sync_samples/test_examples.py
            :start-after: [START create_sender_client]
            :end-before: [END create_sender_client]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Sender

    """

    def __init__(
            self, handler_id, target, auth_config, session=None,
            connection=None, encoding='UTF-8', debug=False, **kwargs):
        self.name = "SBSender-{}".format(handler_id)
        self.session_id = session
        super(Sender, self).__init__(
            target, auth_config, connection=connection, encoding=encoding, debug=debug, **kwargs)

    def _build_handler(self):
        auth = None if self.connection else authentication.SASTokenAuth.from_shared_access_key(**self.auth_config)
        self._handler = SendClient(
            self.endpoint,
            auth=auth,
            debug=self.debug,
            properties=self.properties,
            client_name=self.name,
            error_policy=self.error_policy,
            encoding=self.encoding,
            **self.handler_kwargs)

    def send(self, message):
        """Send a message and blocks until acknowledgement is received or the operation fails.

        :param message: The message to be sent.
        :type message: ~azure.servicebus.common.message.Message
        :raises: ~azure.servicebus.common.errors.MessageSendFailed if the message fails to send.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START send_message]
                :end-before: [END send_message]
                :language: python
                :dedent: 4
                :caption: Send a message and block

        """
        if not isinstance(message, Message):
            raise TypeError("Value of message must be of type 'Message'.")
        if not self.running:
            self.open()
        if self.session_id and not message.properties.group_id:
            message.properties.group_id = self.session_id

        try:
            self._handler.send_message(message.message)
        except (errors.ConnectionClose,
                errors.AuthenticationException,
                errors.MessageHandlerError,
                errors.LinkDetach):
            try:
                self.reconnect()
            except Exception as e:  # pylint: disable=broad-except
                raise MessageSendFailed(e)
        except Exception as e:  # pylint: disable=broad-except
            raise MessageSendFailed(e)

    def schedule(self, schedule_time, *messages):
        """Send one or more messages to be enqueued at a specific time.

        Returns a list of the sequence numbers of the enqueued messages.

        :param schedule_time: The date and time to enqueue the messages.
        :type schedule_time: ~datetime.datetime
        :param messages: The messages to schedule.
        :type messages: ~azure.servicebus.common.message.Message
        :rtype: list[int]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START scheduling_messages]
                :end-before: [END scheduling_messages]
                :language: python
                :dedent: 4
                :caption: Schedule a message to be sent in future

        """
        if not self.running:
            self.open()
        request_body = self._build_schedule_request(schedule_time, *messages)
        return self._mgmt_request_response(
            REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
            request_body,
            mgmt_handlers.schedule_op)

    def cancel_scheduled_messages(self, *sequence_numbers):
        """Cancel one or more messages that have previsouly been scheduled and are still pending.

        :param sequence_numbers: The seqeuence numbers of the scheduled messages.
        :type sequence_numbers: int

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START cancel_scheduled_messages]
                :end-before: [END cancel_scheduled_messages]
                :language: python
                :dedent: 4
                :caption: Cancelling messages scheduled to be sent in future

        """
        if not self.running:
            self.open()
        numbers = [types.AMQPLong(s) for s in sequence_numbers]
        request_body = {'sequence-numbers': types.AMQPArray(numbers)}
        return self._mgmt_request_response(
            REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION,
            request_body,
            mgmt_handlers.default)

    def send_pending_messages(self):
        """Wait until all transferred events have been sent.

        :returns: A list of the send results of all the pending messages. Each
         send result is a tuple with two values. The first is a boolean, indicating `True`
         if the message sent, or `False` if it failed. The second is an error if the message
         failed, otherwise it will be `None`.
        :rtype: list[tuple[bool, ~azure.servicebus.common.errors.MessageSendFailed]]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START queue_and_send_messages]
                :end-before: [END queue_and_send_messages]
                :language: python
                :dedent: 4
                :caption: Send the queued messages

        """
        if not self.running:
            self.open()
        try:
            pending = self._handler._pending_messages[:]  # pylint: disable=protected-access
            _log.debug("Sending %r pending messages", len(pending))
            self._handler.wait()
            results = []
            for m in pending:
                if m.state == constants.MessageState.SendFailed:
                    results.append((False, MessageSendFailed(m._response)))  # pylint: disable=protected-access
                else:
                    results.append((True, None))
            return results
        except Exception as e:
            raise MessageSendFailed(e)

    def reconnect(self):
        """Reconnect the handler.

        If the handler was disconnected from the service with
        a retryable error - attempt to reconnect.
        This method will be called automatically for most retryable errors.
        Also attempts to re-queue any messages that were pending before the reconnect.
        """
        unsent_events = self._handler.pending_messages
        super(Sender, self).reconnect()
        try:
            self._handler.queue_message(*unsent_events)
            self._handler.wait()
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)


class SessionSender(Sender):
    """A session message sender.

    This handler is for sending messages to a sessionful Service Bus entity.
    It operates a single connection that must be opened and closed on completion.
    The Sender can be run within a context manager to ensure that the connection is closed on exit.
    The Sender should not be instantiated directly, and should be accessed from a `QueueClient` or
    `TopicClient` using the `get_sender()` method.
    An attempt to send a message without a session ID specified either on the Sender or the message
    will raise a `ValueError`.

    .. note:: This object is not thread-safe.

    :param handler_id: The ID used as the connection name for the Sender.
    :type handler_id: str
    :param target: The endpoint to send messages to.
    :type target: ~uamqp.Target
    :param auth_config: The SASL auth credentials.
    :type auth_config: dict[str, str]
    :param session: An optional session ID. If supplied, all outgoing messages will have this
     session ID added (unless they already have one specified).
    :type session: str
    :param connection: A shared connection [not yet supported].
    :type connection: ~uamqp.Connection
    :param encoding: The encoding used for string properties. Default is 'UTF-8'.
    :type encoding: str
    :param debug: Whether to enable network trace debug logs.
    :type debug: bool

    """

    def send(self, message):
        """Send a message and blocks until acknowledgement is received or the operation fails.

        If neither the Sender nor the message has a session ID, a `ValueError` will be raised.

        :param message: The message to be sent.
        :type message: ~azure.servicebus.common.message.Message
        :raises: ~azure.servicebus.common.errors.MessageSendFailed if the message fails to
         send.
        :raises: ValueError if there is no session ID specified.

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START send_message]
                :end-before: [END send_message]
                :language: python
                :dedent: 4
                :caption: Send a message and block

        """
        if not isinstance(message, Message):
            raise TypeError("Value of message must be of type 'Message'.")
        if not self.session_id and not message.properties.group_id:
            raise ValueError("Message must have Session ID.")
        super(SessionSender, self).send(message)

    def queue_message(self, message):
        """Queue a message to be sent later.

        This operation should be followed up with send_pending_messages. If neither the Sender nor the message
        has a session ID, a `ValueError` will be raised.

        :param message: The message to be sent.
        :type message: ~azure.servicebus.Message

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START queue_and_send_session_messages]
                :end-before: [END queue_and_send_session_messages]
                :language: python
                :dedent: 4
                :caption: Put the message to be sent later in the queue

        """
        if not self.session_id and not message.properties.group_id:
            raise ValueError("Message must have Session ID.")
        super(SessionSender, self).queue_message(message)

    def schedule(self, schedule_time, *messages):
        """Send one or more messages to be enqueued at a specific time.

        Returns a list of the sequence numbers of the enqueued messages.

        :param schedule_time: The date and time to enqueue the messages.
        :type schedule_time: ~datetime.datetime
        :param messages: The messages to schedule.
        :type messages: ~azure.servicebus.common.message.Message
        :rtype: list[int]

        .. admonition:: Example:
            .. literalinclude:: ../samples/sync_samples/test_examples.py
                :start-after: [START scheduling_messages]
                :end-before: [END scheduling_messages]
                :language: python
                :dedent: 4
                :caption: Schedule a message to be sent in future

        """
        for message in messages:
            if not self.session_id and not message.properties.group_id:
                raise ValueError("Message must have Session ID.")
        return super(SessionSender, self).schedule(schedule_time, *messages)
