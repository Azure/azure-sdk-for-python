# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import asyncio
import logging
from typing import Iterable, Union, Any
import time

from uamqp import types, constants, errors  # type: ignore
from uamqp import SendClientAsync  # type: ignore

from azure.eventhub.common import EventData, EventDataBatch
from azure.eventhub.error import _error_handler, OperationTimeoutError, EventDataError
from ..producer import _error, _set_partition_key
from ._consumer_producer_mixin_async import ConsumerProducerMixin, _retry_decorator


log = logging.getLogger(__name__)


class EventHubProducer(ConsumerProducerMixin):  # pylint: disable=too-many-instance-attributes
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
    grouped together in batches. Depending on the options specified at creation, the producer may
    be created to allow event data to be automatically routed to an available partition or specific
    to a partition.

    """
    _timeout = b'com.microsoft:timeout'

    def __init__(  # pylint: disable=super-init-not-called
            self, client, target, **kwargs):
        """
        Instantiate an async EventHubProducer. EventHubProducer should be instantiated by calling the `create_producer`
        method in EventHubClient.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.aio.EventHubClientAsync
        :param target: The URI of the EventHub to send to.
        :type target: str
        :param partition: The specific partition ID to send to. Default is `None`, in which case the service
         will assign to all partitions using round-robin.
        :type partition: str
        :param send_timeout: The timeout in seconds for an individual event to be sent from the time that it is
         queued. Default value is 60 seconds. If set to 0, there will be no timeout.
        :type send_timeout: float
        :param keep_alive: The time interval in seconds between pinging the connection to keep it alive during
         periods of inactivity. The default value is `None`, i.e. no keep alive pings.
        :type keep_alive: float
        :param auto_reconnect: Whether to automatically reconnect the producer if a retryable error occurs.
         Default value is `True`.
        :type auto_reconnect: bool
        :param loop: An event loop. If not specified the default event loop will be used.
        """
        partition = kwargs.get("partition", None)
        send_timeout = kwargs.get("send_timeout", 60)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)
        loop = kwargs.get("loop", None)

        super(EventHubProducer, self).__init__()
        self.loop = loop or asyncio.get_event_loop()
        self._max_message_size_on_link = None
        self.running = False
        self.client = client
        self.target = target
        self.partition = partition
        self.keep_alive = keep_alive
        self.auto_reconnect = auto_reconnect
        self.timeout = send_timeout
        self.retry_policy = errors.ErrorPolicy(max_retries=self.client.config.max_retries, on_error=_error_handler)
        self.reconnect_backoff = 1
        self.name = "EHProducer-{}".format(uuid.uuid4())
        self.unsent_events = None
        self.redirected = None
        self.error = None
        if partition:
            self.target += "/Partitions/" + partition
            self.name += "-partition{}".format(partition)
        self._handler = None
        self._outcome = None
        self._condition = None
        self._link_properties = {types.AMQPSymbol(self._timeout): types.AMQPLong(int(self.timeout * 1000))}

    def _create_handler(self):
        self._handler = SendClientAsync(
            self.target,
            auth=self.client.get_auth(),
            debug=self.client.config.network_tracing,
            msg_timeout=self.timeout,
            error_policy=self.retry_policy,
            keep_alive_interval=self.keep_alive,
            client_name=self.name,
            link_properties=self._link_properties,
            properties=self.client._create_properties(  # pylint: disable=protected-access
                self.client.config.user_agent),
            loop=self.loop)

    async def _open(self, timeout_time=None, **kwargs):  # pylint:disable=arguments-differ, unused-argument # TODO: to refactor
        """
        Open the EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        if not self.running and self.redirected:
            self.client._process_redirect_uri(self.redirected)  # pylint: disable=protected-access
            self.target = self.redirected.address
        await super(EventHubProducer, self)._open(timeout_time)

    @_retry_decorator
    async def _open_with_retry(self, timeout_time=None, **kwargs):
        return await self._open(timeout_time=timeout_time, **kwargs)

    async def _send_event_data(self, timeout_time=None, last_exception=None):
        if self.unsent_events:
            await self._open(timeout_time)
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
            await self._handler.wait_async()
            self.unsent_events = self._handler.pending_messages
            if self._outcome != constants.MessageSendResult.Ok:
                if self._outcome == constants.MessageSendResult.Timeout:
                    self._condition = OperationTimeoutError("send operation timed out")
                _error(self._outcome, self._condition)
        return

    @_retry_decorator
    async def _send_event_data_with_retry(self, timeout_time=None, last_exception=None):
        return await self._send_event_data(timeout_time=timeout_time, last_exception=last_exception)

    def _on_outcome(self, outcome, condition):
        """
        Called when the outcome is received for a delivery.

        :param outcome: The outcome of the message delivery - success or failure.
        :type outcome: ~uamqp.constants.MessageSendResult
        :param condition: Detail information of the outcome.

        """
        self._outcome = outcome
        self._condition = condition

    async def create_batch(self, max_size=None, partition_key=None):
        # type:(int, str) -> EventDataBatch
        """
        Create an EventDataBatch object with max size being max_size.
        The max_size should be no greater than the max allowed message size defined by the service side.

        :param max_size: The maximum size of bytes data that an EventDataBatch object can hold.
        :type max_size: int
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service.
        :type partition_key: str
        :return: an EventDataBatch instance
        :rtype: ~azure.eventhub.EventDataBatch

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_create_batch]
                :end-before: [END eventhub_client_async_create_batch]
                :language: python
                :dedent: 4
                :caption: Create EventDataBatch object within limited size

        """

        if not self._max_message_size_on_link:
            await self._open_with_retry(timeout=self.client.config.send_timeout)

        if max_size and max_size > self._max_message_size_on_link:
            raise ValueError('Max message size: {} is too large, acceptable max batch size is: {} bytes.'
                             .format(max_size, self._max_message_size_on_link))

        return EventDataBatch(max_size=(max_size or self._max_message_size_on_link), partition_key=partition_key)

    async def send(
            self, event_data: Union[EventData, EventDataBatch, Iterable[EventData]],
            *, partition_key: Union[str, bytes] = None, timeout: float = None):
        """
        Sends an event data and blocks until acknowledgement is
        received or operation times out.

        :param event_data: The event to be sent. It can be an EventData object, or iterable of EventData objects
        :type event_data: ~azure.eventhub.common.EventData, Iterator, Generator, list
        :param partition_key: With the given partition_key, event data will land to
         a particular partition of the Event Hub decided by the service. partition_key
         could be omitted if event_data is of type ~azure.eventhub.EventDataBatch.
        :type partition_key: str
        :param timeout: The maximum wait time to send the event data.
         If not specified, the default wait time specified when the producer was created will be used.
        :type timeout: float

        :raises: ~azure.eventhub.AuthenticationError, ~azure.eventhub.ConnectError, ~azure.eventhub.ConnectionLostError,
                ~azure.eventhub.EventDataError, ~azure.eventhub.EventDataSendError, ~azure.eventhub.EventHubError
        :return: None
        :rtype: None

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_send]
                :end-before: [END eventhub_client_async_send]
                :language: python
                :dedent: 4
                :caption: Sends an event data and blocks until acknowledgement is received or operation times out.

        """

        self._check_closed()
        if isinstance(event_data, EventData):
            if partition_key:
                event_data._set_partition_key(partition_key)  # pylint: disable=protected-access
            wrapper_event_data = event_data
        else:
            if isinstance(event_data, EventDataBatch):
                if partition_key and partition_key != event_data._partition_key:  # pylint: disable=protected-access
                    raise EventDataError('The partition_key does not match the one of the EventDataBatch')
                wrapper_event_data = event_data  #type: ignore
            else:
                if partition_key:
                    event_data = _set_partition_key(event_data, partition_key)
                wrapper_event_data = EventDataBatch._from_batch(event_data, partition_key)  # pylint: disable=protected-access
        wrapper_event_data.message.on_send_complete = self._on_outcome
        self.unsent_events = [wrapper_event_data.message]
        await self._send_event_data_with_retry(timeout=timeout)  # pylint:disable=unexpected-keyword-arg # TODO: to refactor

    async def close(self, exception=None):
        # type: (Exception) -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op. An optional exception can be passed in to
        indicate that the handler was shutdown due to error.

        :param exception: An optional exception if the handler is closing
         due to an error.
        :type exception: Exception

        Example:
            .. literalinclude:: ../examples/async_examples/test_examples_eventhub_async.py
                :start-after: [START eventhub_client_async_sender_close]
                :end-before: [END eventhub_client_async_sender_close]
                :language: python
                :dedent: 4
                :caption: Close down the handler.

        """
        await super(EventHubProducer, self).close(exception)
