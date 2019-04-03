# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time

from uamqp import constants, errors
from uamqp import SendClient

from azure.eventhub.common import EventHubError, _error_handler

log = logging.getLogger(__name__)


class Sender(object):
    """
    Implements a Sender.

    Example:
        .. literalinclude:: ../examples/test_examples_eventhub.py
            :start-after: [START create_eventhub_client_sender_instance]
            :end-before: [END create_eventhub_client_sender_instance]
            :language: python
            :dedent: 4
            :caption: Create a new instance of the Sender.

    """

    def __init__(self, client, target, partition=None, send_timeout=60, keep_alive=None, auto_reconnect=True):
        """
        Instantiate an EventHub event Sender handler.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient.
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param partition: The specific partition ID to send to. Default is None, in which case the service
         will assign to all partitions using round-robin.
        :type partition: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: int
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is None, i.e. no keep alive pings.
        :type keep_alive: int
        :param auto_reconnect: Whether to automatically reconnect the sender if a retryable error occurs.
         Default value is `True`.
        :type auto_reconnect: bool
        """
        self.running = False
        self.client = client
        self.target = target
        self.partition = partition
        self.timeout = send_timeout
        self.redirected = None
        self.error = None
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.retry_policy = errors.ErrorPolicy(max_retries=3, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.name = "EHSender-{}".format(uuid.uuid4())
        if partition:
            self.target += "/Partitions/" + partition
            self.name += "-partition{}".format(partition)
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties())
        self._outcome = None
        self._condition = None

    def open(self):
        """
        Open the Sender using the supplied conneciton.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        :param connection: The underlying client shared connection.
        :type: connection: ~uamqp.connection.Connection

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sender_open]
                :end-before: [END eventhub_client_sender_open]
                :language: python
                :dedent: 4
                :caption: Open the Sender using the supplied conneciton.

        """
        self.running = True
        if self.redirected:
            self.target = self.redirected.address
            self._handler = SendClient(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.debug,
                msg_timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client.create_properties())
        self._handler.open()
        while not self._handler.client_ready():
            time.sleep(0.05)

    def _reconnect(self):
        # pylint: disable=protected-access
        self._handler.close()
        unsent_events = self._handler.pending_messages
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.debug,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client.create_properties())
        try:
            self._handler.open()
            self._handler.queue_message(*unsent_events)
            self._handler.wait()
            return True
        except errors.TokenExpired as shutdown:
            log.info("Sender disconnected due to token expiry. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            self.close(exception=error)
            raise error
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                return False
            log.info("Sender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            self.close(exception=error)
            raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                return False
            log.info("Sender reconnect failed. Shutting down.")
            error = EventHubError(str(shutdown), shutdown)
            self.close(exception=error)
            raise error
        except errors.AMQPConnectionError as shutdown:
            if str(shutdown).startswith("Unable to open authentication session") and self.auto_reconnect:
                log.info("Sender couldn't authenticate. Attempting reconnect.")
                return False
            log.info("Sender connection error (%r). Shutting down.", shutdown)
            error = EventHubError(str(shutdown))
            self.close(exception=error)
            raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("Sender Reconnect failed: {}".format(e))
            self.close(exception=error)
            raise error

    def reconnect(self):
        """If the Sender was disconnected from the service with
        a retryable error - attempt to reconnect."""
        while not self._reconnect():
            time.sleep(self.reconnect_backoff)

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
        **This function is now deprecated and will be removed in v2.0+.**

        :rtype: bool
        """
        # pylint: disable=protected-access
        timeout = False
        auth_in_progress = False
        if self._handler._connection.cbs:
            timeout, auth_in_progress = self._handler._auth.handle_token()
        if timeout:
            raise EventHubError("Authorization timeout.")
        if auth_in_progress:
            return False
        if not self._handler._client_ready():
            return False
        return True

    def close(self, exception=None):
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sender_close]
                :end-before: [END eventhub_client_sender_close]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        self.running = False
        if self.error:
            return
        if isinstance(exception, errors.LinkRedirect):
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

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sync_send]
                :end-before: [END eventhub_client_sync_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to send until client has been started.")
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
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("Sender disconnected due to token error. Attempting reconnect.")
            self.reconnect()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
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
        :type callback: callable[~uamqp.constants.MessageSendResult, ~azure.eventhub.common.EventHubError]

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_transfer]
                :end-before: [END eventhub_client_transfer]
                :language: python
                :dedent: 4
                :caption: Transfers an event data and notifies the callback when the operation is done.

        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to send until client has been started.")
        if event_data.partition_key and self.partition:
            raise ValueError("EventData partition key cannot be used with a partition sender.")
        if callback:
            event_data.message.on_send_complete = lambda o, c: callback(o, Sender._error(o, c))
        self._handler.queue_message(event_data.message)

    def wait(self):
        """
        Wait until all transferred events have been sent.

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_transfer]
                :end-before: [END eventhub_client_transfer]
                :language: python
                :dedent: 4
                :caption: Wait until all transferred events have been sent.

        """
        if self.error:
            raise self.error
        if not self.running:
            raise ValueError("Unable to send until client has been started.")
        try:
            self._handler.wait()
        except (errors.TokenExpired, errors.AuthenticationException):
            log.info("Sender disconnected due to token error. Attempting reconnect.")
            self.reconnect()
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry and self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if self.auto_reconnect:
                log.info("Sender detached. Attempting reconnect.")
                self.reconnect()
            else:
                log.info("Sender detached. Shutting down.")
                error = EventHubError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except Exception as e:
            log.info("Unexpected error occurred (%r).", e)
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
