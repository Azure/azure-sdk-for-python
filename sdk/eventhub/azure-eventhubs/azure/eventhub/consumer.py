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
from uamqp import ReceiveClient, Source

from azure.eventhub.common import EventData, EventPosition
from azure.eventhub.error import _error_handler
from ._consumer_producer_mixin import ConsumerProducerMixin, _retry_decorator


log = logging.getLogger(__name__)


class EventHubConsumer(ConsumerProducerMixin):
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
    _timeout = b'com.microsoft:timeout'

    def __init__(self, client, source, **kwargs):
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
        event_position = kwargs.get("event_position", None)
        prefetch = kwargs.get("prefetch", 300)
        owner_level = kwargs.get("owner_level", None)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)

        super(EventHubConsumer, self).__init__()
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
        self._link_properties = {}
        self.redirected = None
        self.error = None
        partition = self.source.split('/')[-1]
        self.partition = partition
        self.name = "EHConsumer-{}-partition{}".format(uuid.uuid4(), partition)
        if owner_level:
            self._link_properties[types.AMQPSymbol(self._epoch)] = types.AMQPLong(int(owner_level))
        link_property_timeout_ms = (self.client.config.receive_timeout or self.timeout) * 1000
        self._link_properties[types.AMQPSymbol(self._timeout)] = types.AMQPLong(int(link_property_timeout_ms))
        self._handler = None

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
                event_data = EventData._from_message(message)
                self.offset = EventPosition(event_data.offset, inclusive=False)
                retry_count = 0
                return event_data
            except Exception as exception:
                self._handle_exception(exception, retry_count, max_retries)
                retry_count += 1

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
            link_properties=self._link_properties,
            timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            properties=self.client._create_properties(
                self.client.config.user_agent))  # pylint: disable=protected-access
        self.messages_iter = None

    def _redirect(self, redirect):
        self.messages_iter = None
        super(EventHubConsumer, self)._redirect(redirect)

    def _open(self, timeout_time=None):
        """
        Open the EventHubConsumer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        # pylint: disable=protected-access
        if not self.running and self.redirected:
            self.client._process_redirect_uri(self.redirected)
            self.source = self.redirected.address
        super(EventHubConsumer, self)._open(timeout_time)

    def _receive(self, timeout_time=None, max_batch_size=None, **kwargs):
        last_exception = kwargs.get("last_exception")
        data_batch = kwargs.get("data_batch")

        self._open(timeout_time)
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                log.info("%r receive operation timed out. (%r)", self.name, last_exception)
                raise last_exception
            return data_batch
        remaining_time_ms = 1000 * remaining_time
        message_batch = self._handler.receive_message_batch(
            max_batch_size=max_batch_size - (len(data_batch) if data_batch else 0),
            timeout=remaining_time_ms)
        for message in message_batch:
            event_data = EventData._from_message(message)
            self.offset = EventPosition(event_data.offset)
            data_batch.append(event_data)
        return data_batch

    @_retry_decorator
    def _receive_with_try(self, timeout_time=None, max_batch_size=None, **kwargs):
        return self._receive(timeout_time=timeout_time, max_batch_size=max_batch_size, **kwargs)

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
        # type: (int, float) -> List[EventData]
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

        timeout = timeout or self.client.config.receive_timeout
        max_batch_size = max_batch_size or min(self.client.config.max_batch_size, self.prefetch)
        data_batch = []  # type: List[EventData]

        return self._receive_with_try(timeout=timeout, max_batch_size=max_batch_size, data_batch=data_batch)

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
        super(EventHubConsumer, self).close(exception)

    next = __next__  # for python2.7
