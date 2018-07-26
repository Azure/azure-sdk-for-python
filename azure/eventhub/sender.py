# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time

import uamqp
from uamqp import constants, errors
from uamqp import SendClient

from azure.eventhub.common import EventHubError, _error_handler


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
        self.client = client
        self.target = target
        self.partition = partition
        self.redirected = None
        self.error = None
        self.retry_policy = errors.ErrorPolicy(max_retries=3, on_error=_error_handler)
        if partition:
            self.target += "/Partitions/" + partition
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            msg_timeout=Sender.TIMEOUT,
            error_policy=self.retry_policy,
            keep_alive_interval=30,
            properties=self.client.create_properties())
        self._outcome = None
        self._condition = None

    def open(self): #, connection):
        """
        Open the Sender using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp.connection.Connection
        """
        if self.redirected:
            self.target = self.redirected.address
            self._handler = SendClient(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.debug,
                msg_timeout=Sender.TIMEOUT,
                error_policy=self.retry_policy,
                keep_alive_interval=30,
                properties=self.client.create_properties())
        self._handler.open() #connection)
        while not self.has_started():
            self._handler._connection.work()

    def reconnect(self):
        """If the Sender was disconnected from the service with
        a retryable error - attempt to reconnect."""
        pending_states = (constants.MessageState.WaitingForSendAck, constants.MessageState.WaitingToBeSent)
        unsent_events = [e for e in self._handler._pending_messages if e.state in pending_states]
        self._handler.close()
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            msg_timeout=Sender.TIMEOUT,
            error_policy=self.retry_policy,
            keep_alive_interval=30,
            properties=self.client.create_properties())
        self._handler.open()
        self._handler._pending_messages = unsent_events
        self._handler.wait()

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
        except errors.MessageException as failed:
            error = EventHubError(str(failed), failed)
            self.close(exception=error)
            raise error
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                self.reconnect()
            else:
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except (errors.MessageHandlerError):
            self.reconnect()
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
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                self.reconnect()
            else:
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except (errors.MessageHandlerError):
            self.reconnect()
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

    @staticmethod
    def _error(outcome, condition):
        return None if outcome == constants.MessageSendResult.Ok else EventHubError(outcome, condition)
