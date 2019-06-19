# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time

from uamqp import constants, errors
from uamqp import compat
from uamqp import SendClient
from uamqp.constants import MessageSendResult

from azure.eventhub.common import EventData, _BatchSendEventData
from azure.eventhub.error import EventHubError, ConnectError, \
    AuthenticationError, EventDataError, EventDataSendError, ConnectionLostError, _error_handler

log = logging.getLogger(__name__)


class EventHubProducer(object):
    """
    Implements a EventHubProducer.

    """

    def __init__(self, client, target, partition=None, send_timeout=60, keep_alive=None, auto_reconnect=True):
        """
        Instantiate an EventHub event EventHubProducer handler.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient.
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param partition: The specific partition ID to send to. Default is None, in which case the service
         will assign to all partitions using round-robin.
        :type partition: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: float
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is None, i.e. no keep alive pings.
        :type keep_alive: float
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
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.name = "EHSender-{}".format(uuid.uuid4())
        self.unsent_events = None
        if partition:
            self.target += "/Partitions/" + partition
            self.name += "-partition{}".format(partition)
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(self.client.config.user_agent))  # pylint: disable=protected-access
        self._outcome = None
        self._condition = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_val)

    def _open(self):
        """
        Open the EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        self._check_closed()
        if self.redirected:
            self.target = self.redirected.address
            self._handler = SendClient(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.config.network_tracing,
                msg_timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent))
        if not self.running:
            self._connect()
            self.running = True

    def _connect(self):
        connected = self._build_connection()
        if not connected:
            time.sleep(self.reconnect_backoff)
            while not self._build_connection(is_reconnect=True):
                time.sleep(self.reconnect_backoff)

    def _build_connection(self, is_reconnect=False):
        """

        :param is_reconnect: True - trying to reconnect after fail to connect or a connection is lost.
                             False - the 1st time to connect
        :return: True - connected.  False - not connected
        """
        # pylint: disable=protected-access
        if is_reconnect:
            self._handler.close()
            self._handler = SendClient(
                self.target,
                auth=self.client.get_auth(),
                debug=self.client.config.network_tracing,
                msg_timeout=self.timeout,
                error_policy=self.retry_policy,
                keep_alive_interval=self.keep_alive,
                client_name=self.name,
                properties=self.client._create_properties(self.client.config.user_agent))
        try:
            self._handler.open()
            while not self._handler.client_ready():
                time.sleep(0.05)
            return True
        except errors.AuthenticationException as shutdown:
            if is_reconnect:
                log.info("EventHubProducer couldn't authenticate. Shutting down. (%r)", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer couldn't authenticate. Attempting reconnect.")
                return False
        except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
            if shutdown.action.retry:
                log.info("EventHubProducer detached. Attempting reconnect.")
                return False
            else:
                log.info("EventHubProducer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
        except errors.MessageHandlerError as shutdown:
            if is_reconnect:
                log.info("EventHubProducer detached. Shutting down.")
                error = ConnectError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer detached. Attempting reconnect.")
                return False
        except errors.AMQPConnectionError as shutdown:
            if is_reconnect:
                log.info("EventHubProducer connection error (%r). Shutting down.", shutdown)
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer couldn't authenticate. Attempting reconnect.")
                return False
        except compat.TimeoutException as shutdown:
            if is_reconnect:
                log.info("EventHubProducer authentication timed out. Shutting down.")
                error = AuthenticationError(str(shutdown), shutdown)
                self.close(exception=error)
                raise error
            else:
                log.info("EventHubProducer authentication timed out. Attempting reconnect.")
                return False
        except Exception as e:
            log.info("Unexpected error occurred (%r). Shutting down.", e)
            error = EventHubError("EventHubProducer failed to connect: {}".format(e))
            self.close(exception=error)
            raise error

    def _reconnect(self):
        return self._build_connection(is_reconnect=True)

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

    def _send_event_data(self):
        self._open()
        max_retries = self.client.config.max_retries
        connecting_count = 0
        while True:
            connecting_count += 1
            try:
                if self.unsent_events:
                    self._handler.queue_message(*self.unsent_events)
                    self._handler.wait()
                    self.unsent_events = self._handler.pending_messages
                if self._outcome != constants.MessageSendResult.Ok:
                    EventHubProducer._error(self._outcome, self._condition)
                return
            except (errors.MessageAccepted,
                    errors.MessageAlreadySettled,
                    errors.MessageModified,
                    errors.MessageRejected,
                    errors.MessageReleased,
                    errors.MessageContentTooLarge) as msg_error:
                raise EventDataError(str(msg_error), msg_error)
            except errors.MessageException as failed:
                log.info("Send event data error (%r)", failed)
                error = EventDataSendError(str(failed), failed)
                self.close(exception=error)
                raise error
            except errors.AuthenticationException as auth_error:
                if connecting_count < max_retries:
                    log.info("EventHubProducer disconnected due to token error. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubProducer authentication failed. Shutting down.")
                    error = AuthenticationError(str(auth_error), auth_error)
                    self.close(auth_error)
                    raise error
            except (errors.LinkDetach, errors.ConnectionClose) as shutdown:
                if shutdown.action.retry:
                    log.info("EventHubProducer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubProducer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(exception=error)
                    raise error
            except errors.MessageHandlerError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer detached. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubProducer detached. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except errors.AMQPConnectionError as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer connection lost. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubProducer connection lost. Shutting down.")
                    error = ConnectionLostError(str(shutdown), shutdown)
                    self.close(error)
                    raise error
            except compat.TimeoutException as shutdown:
                if connecting_count < max_retries:
                    log.info("EventHubProducer timed out sending event data. Attempting reconnect.")
                    self._reconnect()
                else:
                    log.info("EventHubProducer timed out. Shutting down.")
                    self.close(shutdown)
                    raise TimeoutError(str(shutdown), shutdown)
            except Exception as e:
                log.info("Unexpected error occurred (%r). Shutting down.", e)
                error = EventHubError("Send failed: {}".format(e))
                self.close(exception=error)
                raise error

    def _check_closed(self):
        if self.error:
            raise EventHubError("This sender has been closed. Please create a new sender to send event data.", self.error)

    @staticmethod
    def _set_partition_key(event_datas, partition_key):
        ed_iter = iter(event_datas)
        for ed in ed_iter:
            ed._set_partition_key(partition_key)
            yield ed

    def send(self, event_data, partition_key=None):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent.
        :type event_data: ~azure.eventhub.common.EventData
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :type batching_label: str
        :raises: ~azure.eventhub.common.EventHubError if the message fails to
         send.
        :return: None
        :rtype: None

        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sync_send]
                :end-before: [END eventhub_client_sync_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """
        self._check_closed()
        if isinstance(event_data, EventData):
            if partition_key:
                event_data._set_partition_key(partition_key)
            wrapper_event_data = event_data
        else:
            wrapper_event_data = _BatchSendEventData(
                self._set_partition_key(event_data, partition_key),
                partition_key=partition_key) if partition_key else _BatchSendEventData(event_data)
        wrapper_event_data.message.on_send_complete = self._on_outcome
        self.unsent_events = [wrapper_event_data.message]
        self._send_event_data()

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        :param condition: Detail information of the outcome.

        """
        self._outcome = outcome
        self._condition = condition

    @staticmethod
    def _error(outcome, condition):
        if outcome != MessageSendResult.Ok:
            raise condition
