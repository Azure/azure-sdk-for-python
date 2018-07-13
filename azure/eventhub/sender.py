# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

import uamqp
from uamqp import constants, errors
from uamqp import SendClient

from azure.eventhub.common import EventHubError


class Sender:
    """
    Implements a Sender.
    """
    TIMEOUT = 60.0

    def __init__(self, client, target, partition=None):
        """
        Instantiate an EventHub event Sender handler.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient.
        :param target: The URI of the EventHub to send to.
        :type target: str
        """
        self.redirected = None
        self.error = None
        self.debug = client.debug
        self.partition = partition
        self.retry_policy = uamqp.sender.RetryPolicy(max_retries=3, on_error=self._error_handler)
        if partition:
            target += "/Partitions/" + partition
        self._handler = SendClient(
            target,
            auth=client.auth,
            debug=self.debug,
            msg_timeout=Sender.TIMEOUT,
            retry_policy=self.retry_policy)
        self._outcome = None
        self._condition = None

    def open(self, connection):
        """
        Open the Sender using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp.connection.Connection
        """
        if self.redirected:
            self._handler = SendClient(
                self.redirected.address,
                auth=None,
                debug=self.debug,
                msg_timeout=Sender.TIMEOUT,
                retry_policy=self.retry_policy)
        self._handler.open(connection)

    def get_handler_state(self):
        """
        Get the state of the underlying handler with regards to start
        up processes.

        :rtype: ~uamqp.constants.MessageSenderState
        """
        # pylint: disable=protected-access
        return self._handler._message_sender.get_state()

    def has_started(self):
        """
        Whether the handler has completed all start up processes such as
        establishing the connection, session, link and authentication, and
        is not ready to process messages.

        :rtype: bool
        """
        # pylint: disable=protected-access
        timeout = False
        auth_in_progress = False
        if self._handler._connection.cbs:
            timeout, auth_in_progress = self._handler._auth.handle_token()
        if timeout:
            raise EventHubError("Authorization timeout.")
        elif auth_in_progress:
            return False
        elif not self._handler._client_ready():
            return False
        else:
            return True

    def close(self, exception=None):
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception
        """
        if self.error:
            return
        elif isinstance(exception, errors.LinkRedirect):
            self.redirected = exception
        elif isinstance(exception, EventHubError):
            self.error = exception
        elif exception:
            self.error = EventHubError(str(exception))
        else:
            self.error = EventHubError("This send handler is now closed.")
        self._handler.close()

    def send(self, event_data):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :raises: ~azure.eventhub.common.EventHubError if the message fails to
         send.
        :return: The outcome of the message send.
        :rtype: ~uamqp.constants.MessageSendResult
        """
        if self.error:
            raise self.error
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        event_data.message.on_send_complete = self._on_outcome
        try:
            self._handler.send_message(event_data.message)
            if self._outcome != constants.MessageSendResult.Ok:
                raise Sender._error(self._outcome, self._condition)
        except errors.LinkDetach as detach:
            error = EventHubError(str(detach))
            self.close(exception=error)
            raise error
        except Exception as e:
            error = EventHubError("Send failed: {}".format(e))
            self.close(exception=error)
            raise error
        else:
            return self._outcome

    def transfer(self, event_data, callback=None):
        """
        Transfers an event data and notifies the callback when the operation is done.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :param callback: Callback to be run once the message has been send.
         This must be a function that accepts two arguments.
        :type callback: func[~uamqp.constants.MessageSendResult, ~azure.eventhub.common.EventHubError]
        """
        if self.error:
            raise self.error
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    def wait(self):
        """
        Wait until all transferred events have been sent.
        """
        if self.error:
            raise self.error
        try:
            self._handler.wait()
        except Exception as e:
            raise EventHubError("Send failed: {}".format(e))

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        """
        self._outcome = outcome
        self._condition = condition

    def _error_handler(self, error):
        """
        Called internally when an event has failed to send so we
        can parse the error to determine whether we should attempt
        to retry sending the event again.
        Returns the action to take according to error type.

        :param error: The error received in the send attempt.
        :type error: list[list[bytes]]
        :rtype: ~uamqp.sender.SendFailedAction
        """
        if isinstance(error, list) and isinstance(error[0], list):
            error_type = error[0][0].decode('UTF-8')
            if error_type == 'com.microsoft:server-busy':
                return uamqp.sender.SendFailedAction(retry=True, backoff=4)
        return uamqp.sender.SendFailedAction(retry=True, backoff=4)

    @staticmethod
    def _error(outcome, condition):
        return None if outcome == constants.MessageSendResult.Ok else EventHubError(outcome, condition)
