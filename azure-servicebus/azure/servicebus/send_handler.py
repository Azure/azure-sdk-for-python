#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging

from uamqp import SendClient
from uamqp import authentication
from uamqp import constants, types

from azure.servicebus.base_handler import BaseHandler
from azure.servicebus.common.errors import MessageSendFailed
from azure.servicebus.common.message import Message
from azure.servicebus.common import mgmt_handlers, mixins
from azure.servicebus.common.constants import (
    REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
    REQUEST_RESPONSE_CANCEL_SCHEDULED_MESSAGE_OPERATION)


_log = logging.getLogger(__name__)


class Sender(BaseHandler, mixins.SenderMixin):
    """
    Implements a Sender.
    """

    def __init__(
            self, handler_id, target, auth_config, session=None,
            connection=None, encoding='UTF-8', debug=False, **kwargs):
        """
        Instantiate a Service Bus event Sender client.
        :param target: The URI of the Service Bus to send to.
        :type target: str
        """
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
        """
        Sends a message and blocks until acknowledgement is
        received or operation times out.
        :param message: The message to be sent.
        :type message: ~azure.servicebus.Message
        :raises: ~azure.servicebus.common.errors.MessageSendFailed if the message fails to
         send.
        """
        if not isinstance(message, Message):
            message = Message(message)
        if not self.running:
            self.open()
        if self.session_id and not message.properties.group_id:
            message.properties.group_id = self.session_id
        try:
            self._handler.send_message(message.message)
        except Exception as e:
            raise MessageSendFailed(e)

    def schedule(self, schedule_time, *messages):
        """Send one or more messages to be enqueued at a specific time.
        Returns a list of the sequence numbers of the enqueued messages.

        :param schedule_time: The date and time to enqueue the messages.
        :type schedule_time: ~datetime.datetime
        :param messages: The messages to schedule.
        :type messages: ~azure.servicebus.common.message.Message
        :returns: list[int]
        """
        if not self.running:
            self.open()
        request_body = self._build_schedule_request(schedule_time, *messages)
        return self._mgmt_request_response(
            REQUEST_RESPONSE_SCHEDULE_MESSAGE_OPERATION,
            request_body,
            mgmt_handlers.schedule_op)

    def cancel_scheduled_messages(self, *sequence_numbers):
        """Cancel one or more messages that have previsouly been scheduled and are
        still pending.

        :param sequence_numbers: The seqeuence numbers of the scheduled messages.
        :type sequence_numbers: int
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
        :raises: ~azure.servicebus.common.errors.MessageSendFailed if the message fails to
         send.
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
        """If the handler was disconnected from the service with
        a retryable error - attempt to reconnect."""
        unsent_events = self._handler.pending_messages
        super(Sender, self).reconnect()
        try:
            self._handler.queue_message(*unsent_events)
            self._handler.wait()
        except Exception as e:  # pylint: disable=broad-except
            self._handle_exception(e)


class SessionSender(Sender):

    def send(self, message):
        """
        Sends a message and blocks until acknowledgement is
        received or operation times out.
        :param message: The message to be sent.
        :type message: ~azure.servicebus.Message
        :raises: ~azure.servicebus.common.errors.MessageSendFailed if the message fails to
         send.
        :returns: The outcome of the message send ~uamqp.constants.MessageSendResult
        """
        if not isinstance(message, Message):
            message = Message(message)
        if not self.session_id and not message.properties.group_id:
            raise ValueError("Message must have Session ID.")
        super(SessionSender, self).send(message)

    def queue_message(self, message):
        """
        Queue a message to be sent later. This operation should be followed up
        with send_pending_messages.
        :param message: The message to be sent.
        :type message: ~azure.servicebus.Message
        """
        if not isinstance(message, Message):
            message = Message(message)
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
        :returns: list[int]
        """
        for message in messages:
            if not isinstance(message, Message):
                message = Message(message)
            if not self.session_id and not message.properties.group_id:
                raise ValueError("Message must have Session ID.")
        return super(SessionSender, self).schedule(schedule_time, *messages)
