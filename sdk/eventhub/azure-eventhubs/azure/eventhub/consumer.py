# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import unicode_literals

import uuid
import logging
import time
from typing import List

from uamqp import types, errors
from uamqp import compat
from uamqp import ReceiveClient, Source

from azure.eventhub.common import EventData, EventPosition
from azure.eventhub.error import EventHubError, AuthenticationError, ConnectError, ConnectionLostError, _error_handler


log = logging.getLogger(__name__)


class EventHubConsumer(object):
    """
    A consumer responsible for reading EventData from a specific Event Hub
     partition and as a member of a specific consumer group.

    A consumer may be exclusive, which asserts ownership over the partition for the consumer
     group to ensure that only one consumer from that group is reading the from the partition.
     These exclusive consumers are sometimes referred to as "Epoch Consumers."

    A consumer may also be non-exclusive, allowing multiple consumers from the same consumer
     group to be actively reading events from the partition.  These non-exclusive consumers are
     sometimes referred to as "Non-Epoch Consumers."

    """
    timeout = 0
    _epoch = b'com.microsoft:epoch'

    def __init__(self, client, source, event_position=None, prefetch=300, owner_level=None,
                 keep_alive=None, auto_reconnect=True):
        """
        Instantiate a consumer. EventHubConsumer should be instantiated by calling the `create_consumer` method
         in EventHubClient.

        :param client: The parent EventHubClient.
        :type client: ~azure.eventhub.client.EventHubClient
        :param source: The source EventHub from which to receive events.
        :type source: str
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param owner_level: The priority of the exclusive consumer. It will an exclusive
         consumer if owner_level is set.
        :type owner_level: int
        """
        self.running = False
        self.client = client
        self.source = source
        self.offset = event_position
        self.messages_iter = None
        self.prefetch = prefetch
        self.owner_level = owner_level
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.properties = None
        self.redirected = None
        self.error = None
        partition = self.source.split('/')[-1]
        self.name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset._selector())  # pylint: disable=protected-access
        if owner_level:
            self.properties = {types.AMQPSymbol(self._epoch): types.AMQPLong(int(owner_level))}
        self._handler = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(exc_val)

    def __iter__(self):
        return self

    def __next__(self):
        max_retries = self.client.config.max_retries
        retry_count = 0
        while True:
            try:
                self._open()
                if not self.messages_iter:
                    self.messages_iter = self._handler.receive_messages_iter()
                message = next(self.messages_iter)
                event_data = EventData(message=message)
                self.offset = EventPosition(event_data.offset, inclusive=False)
                return event_data
            except Exception as exception:
                self._handle_exception(exception, retry_count, max_retries)
                retry_count += 1

    def _check_closed(self):
        if self.error:
            raise EventHubError("This consumer has been closed. Please create a new consumer to receive event data.",
                                self.error)

    def _create_handler(self):
        alt_creds = {
            "username": self.client._auth_config.get("iot_username"),
            "password": self.client._auth_config.get("iot_password")}
        source = Source(self.source)
        if self.offset is not None:
            source.set_filter(self.offset._selector())
        self._handler = ReceiveClient(
            source,
            auth=self.client.get_auth(**alt_creds),
            debug=self.client.config.network_tracing,
            prefetch=self.prefetch,
            link_properties=self.properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(
                self.client.config.user_agent))  # pylint: disable=protected-access
        self.messages_iter = None

    def _redirect(self, redirect):
        self.redirected = redirect
        self.running = False
        self.messages_iter = None
        self._close_connection()

    def _open(self):
        """
        Open the EventHubConsumer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        if not self.running:
            if self.redirected:
                self.client._process_redirect_uri(self.redirected)
                self.source = self.redirected.address
            self._create_handler()
            self._handler.open(connection=self.client._conn_manager.get_connection(
                self.client.address.hostname,
                self.client.get_auth()
            ))
            while not self._handler.client_ready():
                time.sleep(0.05)
            self.running = True

    def _close_handler(self):
        self._handler.close()  # close the link (sharing connection) or connection (not sharing)
        self.running = False

    def _close_connection(self):
        self._close_handler()
        self.client._conn_manager.close_connection()  # close the shared connection.

    def _handle_exception(self, exception, retry_count, max_retries):
        if isinstance(exception, KeyboardInterrupt):
            log.info("EventHubConsumer stops due to keyboard interrupt")
            self.close()
            raise
        elif retry_count >= max_retries:
            log.info("EventHubConsumer has an error and has exhausted retrying. (%r)", exception)
            if isinstance(exception, errors.AuthenticationException):
                log.info("EventHubConsumer authentication failed. Shutting down.")
                error = AuthenticationError(str(exception), exception)
            elif isinstance(exception, errors.LinkDetach):
                log.info("EventHubConsumer link detached. Shutting down.")
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.ConnectionClose):
                log.info("EventHubConsumer connection closed. Shutting down.")
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.MessageHandlerError):
                log.info("EventHubConsumer detached. Shutting down.")
                error = ConnectionLostError(str(exception), exception)
            elif isinstance(exception, errors.AMQPConnectionError):
                log.info("EventHubConsumer connection lost. Shutting down.")
                error_type = AuthenticationError if str(exception).startswith("Unable to open authentication session") \
                    else ConnectError
                error = error_type(str(exception), exception)
            elif isinstance(exception, compat.TimeoutException):
                log.info("EventHubConsumer timed out. Shutting down.")
                error = ConnectionLostError(str(exception), exception)
            else:
                log.error("Unexpected error occurred (%r). Shutting down.", exception)
                error = EventHubError("Receive failed: {}".format(exception), exception)
            self.close(exception=error)
            raise error
        else:
            log.info("EventHubConsumer has an exception (%r). Retrying...", exception)
            if isinstance(exception, errors.AuthenticationException):
                self._close_connection()
            elif isinstance(exception, errors.LinkRedirect):
                log.info("EventHubConsumer link redirected. Redirecting...")
                redirect = exception
                self._redirect(redirect)
            elif isinstance(exception, errors.LinkDetach):
                self._close_handler()
            elif isinstance(exception, errors.ConnectionClose):
                self._close_connection()
            elif isinstance(exception, errors.MessageHandlerError):
                self._close_handler()
            elif isinstance(exception, errors.AMQPConnectionError):
                self._close_connection()
            elif isinstance(exception, compat.TimeoutException):
                pass  # Timeout doesn't need to recreate link or exception
            else:
                self._close_connection()

    @property
    def queue_size(self):
        # type:() -> int
        """
        The current size of the unprocessed Event queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    def receive(self, max_batch_size=None, timeout=None):
        # type:(int, float) -> List[EventData]
        """
        Receive events from the EventHub.

        :param max_batch_size: Receive a batch of events. Batch size will
         be up to the maximum specified, but will return as soon as service
         returns no new events. If combined with a timeout and no events are
         retrieve before the time, the result will be empty. If no batch
         size is supplied, the prefetch size will be the maximum.
        :type max_batch_size: int
        :param timeout: The maximum wait time to build up the requested message count for the batch.
         If not specified, the default wait time specified when the consumer was created will be used.
        :type timeout: float
        :rtype: list[~azure.eventhub.common.EventData]
        :raises: ~azure.eventhub.AuthenticationError, ~azure.eventhub.ConnectError, ~azure.eventhub.ConnectionLostError,
                ~azure.eventhub.EventHubError
        Example:
            .. literalinclude:: ../examples/test_examples_eventhub.py
                :start-after: [START eventhub_client_sync_receive]
                :end-before: [END eventhub_client_sync_receive]
                :language: python
                :dedent: 4
                :caption: Receive events from the EventHub.

        """
        self._check_closed()

        max_batch_size = min(self.client.config.max_batch_size, self.prefetch) if max_batch_size is None else max_batch_size
        timeout = self.client.config.receive_timeout if timeout is None else timeout

        data_batch = []  # type: List[EventData]
        max_retries = self.client.config.max_retries
        retry_count = 0
        while True:
            try:
                self._open()
                timeout_ms = 1000 * timeout if timeout else 0
                message_batch = self._handler.receive_message_batch(
                    max_batch_size=max_batch_size - (len(data_batch) if data_batch else 0),
                    timeout=timeout_ms)
                for message in message_batch:
                    event_data = EventData(message=message)
                    self.offset = EventPosition(event_data.offset)
                    data_batch.append(event_data)
                return data_batch
            except Exception as exception:
                self._handle_exception(exception, retry_count, max_retries)
                retry_count += 1

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
                :start-after: [START eventhub_client_receiver_close]
                :end-before: [END eventhub_client_receiver_close]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        if self.messages_iter:
            self.messages_iter.close()
            self.messages_iter = None
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
            self.error = EventHubError("This receive handler is now closed.")
        self._handler.close()  # this will close link if sharing connection. Otherwise close connection

    next = __next__  # for python2.7
