# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time
from typing import Iterable, Union

from uamqp import types, constants, errors
from uamqp import compat
from uamqp import SendClient

from azure.eventhub.common import EventData, _BatchSendEventData
from azure.eventhub.error import OperationTimeoutError, _error_handler
from ._consumer_producer_mixin import ConsumerProducerMixin

log = logging.getLogger(__name__)


def _error(outcome, condition):
    if outcome != constants.MessageSendResult.Ok:
        raise condition


def _set_partition_key(event_datas, partition_key):
    ed_iter = iter(event_datas)
    for ed in ed_iter:
        ed._set_partition_key(partition_key)
        yield ed


class EventHubProducer(ConsumerProducerMixin):
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
     grouped together in batches. Depending on the options specified at creation, the producer may
     be created to allow event data to be automatically routed to an available partition or specific
     to a partition.

    """
    _timeout = b'com.microsoft:timeout'

    def __init__(self, client, target, partition=None, send_timeout=60, keep_alive=None, auto_reconnect=True):
        """
        Instantiate an EventHubProducer. EventHubProducer should be instantiated by calling the `create_producer` method
         in EventHubClient.

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
        :param auto_reconnect: Whether to automatically reconnect the producer if a retryable error occurs.
         Default value is `True`.
        :type auto_reconnect: bool
        """
        super(EventHubProducer, self).__init__()
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
        self.name = "EHProducer-{}".format(uuid.uuid4())
        self.unsent_events = None
        if partition:
            self.target += "/Partitions/" + partition
            self.name += "-partition{}".format(partition)
        self._handler = None
        self._outcome = None
        self._condition = None
        self._link_properties = {types.AMQPSymbol(self._timeout): types.AMQPLong(int(self.timeout * 1000))}

    def _create_handler(self):
        self._handler = SendClient(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            link_properties=self._link_properties,
            properties=self.client._create_properties(self.client.config.user_agent))  # pylint: disable=protected-access

    def _open(self, timeout_time=None):
        """
        Open the EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        if not self.running and self.redirected:
            self.client._process_redirect_uri(self.redirected)
            self.target = self.redirected.address
        super(EventHubProducer, self)._open(timeout_time)

    def _send_event_data(self, timeout=None):
        timeout = self.client.config.send_timeout if timeout is None else timeout
        if not timeout:
            timeout = 100_000  # timeout None or 0 mean no timeout. 100000 seconds is equivalent to no timeout
        start_time = time.time()
        timeout_time = start_time + timeout
        max_retries = self.client.config.max_retries
        retry_count = 0
        last_exception = None
        while True:
            try:
                if self.unsent_events:
                    self._open(timeout_time)
                    remaining_time = timeout_time - time.time()
                    if remaining_time <= 0.0:
                        if last_exception:
                            error = last_exception
                        else:
                            error = OperationTimeoutError("send operation timed out")
                        log.info("%r send operation timed out. (%r)", self.name, error)
                        raise error
                    self._handler._msg_timeout = remaining_time  # pylint: disable=protected-access
                    self._handler.queue_message(*self.unsent_events)
                    self._handler.wait()
                    self.unsent_events = self._handler.pending_messages
                    if self._outcome != constants.MessageSendResult.Ok:
                        if self._outcome == constants.MessageSendResult.Timeout:
                            self._condition = OperationTimeoutError("send operation timed out")
                        _error(self._outcome, self._condition)
                return
            except Exception as exception:
                last_exception = self._handle_exception(exception, retry_count, max_retries, timeout_time)
                retry_count += 1

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        :param condition: Detail information of the outcome.

        """
        self._outcome = outcome
        self._condition = condition

    def send(self, event_data, partition_key=None, timeout=None):
        # type:(Union[EventData, Iterable[EventData]], Union[str, bytes], float) -> None
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent. It can be an EventData object, or iterable of EventData objects
        :type event_data: ~azure.eventhub.common.EventData, Iterator, Generator, list
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :type partition_key: str
        :param timeout: The maximum wait time to send the event data.
         If not specified, the default wait time specified when the producer was created will be used.
        :type timeout:float
        :raises: ~azure.eventhub.AuthenticationError, ~azure.eventhub.ConnectError, ~azure.eventhub.ConnectionLostError,
                ~azure.eventhub.EventDataError, ~azure.eventhub.EventDataSendError, ~azure.eventhub.EventHubError

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
            event_data_with_pk = _set_partition_key(event_data, partition_key)
            wrapper_event_data = _BatchSendEventData(
                event_data_with_pk,
                partition_key=partition_key) if partition_key else _BatchSendEventData(event_data)
        wrapper_event_data.message.on_send_complete = self._on_outcome
        self.unsent_events = [wrapper_event_data.message]
        self._send_event_data(timeout=timeout)

    def close(self, exception=None):
        # type:(Exception) -> None
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
        super(EventHubProducer, self).close(exception)
