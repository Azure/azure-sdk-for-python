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

from azure.core.tracing.common import get_parent_span
from azure.core.tracing import SpanKind

from azure.eventhub.common import EventData, EventDataBatch
from azure.eventhub.error import _error_handler, OperationTimeoutError, EventDataError
from ..producer import _error, _set_partition_key
from ._consumer_producer_mixin_async import ConsumerProducerMixin

log = logging.getLogger(__name__)


class EventHubProducer(ConsumerProducerMixin):  # pylint: disable=too-many-instance-attributes
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
    grouped together in batches. Depending on the options specified at creation, the producer may
    be created to allow event data to be automatically routed to an available partition or specific
    to a partition.

    Please use the method `create_producer` on `EventHubClient` for creating `EventHubProducer`.
    """
    _timeout_symbol = b'com.microsoft:timeout'

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
        self._loop = loop or asyncio.get_event_loop()
        self._max_message_size_on_link = None
        self._running = False
        self._client = client
        self._target = target
        self._partition = partition
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._timeout = send_timeout
        self._retry_policy = errors.ErrorPolicy(max_retries=self._client._config.max_retries, on_error=_error_handler)  # pylint:disable=protected-access
        self._reconnect_backoff = 1
        self._name = "EHProducer-{}".format(uuid.uuid4())
        self._unsent_events = None
        self._redirected = None
        self._error = None
        if partition:
            self._target += "/Partitions/" + partition
            self._name += "-partition{}".format(partition)
        self._handler = None
        self._outcome = None
        self._condition = None
        self._link_properties = {types.AMQPSymbol(self._timeout_symbol): types.AMQPLong(int(self._timeout * 1000))}

    def _create_handler(self):
        self._handler = SendClientAsync(
            self._target,
            auth=self._client._get_auth(),  # pylint:disable=protected-access
            debug=self._client._config.network_tracing,  # pylint:disable=protected-access
            msg_timeout=self._timeout,
            error_policy=self._retry_policy,
            keep_alive_interval=self._keep_alive,
            client_name=self._name,
            link_properties=self._link_properties,
            properties=self._client._create_properties(  # pylint: disable=protected-access
                self._client._config.user_agent),  # pylint:disable=protected-access
            loop=self._loop)

    async def _open(self):
        """
        Open the EventHubProducer using the supplied connection.
        If the handler has previously been redirected, the redirect
        context will be used to create a new handler before opening it.

        """
        if not self._running and self._redirected:
            self._client._process_redirect_uri(self._redirected)  # pylint: disable=protected-access
            self._target = self._redirected.address
        await super(EventHubProducer, self)._open()

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open, operation_need_param=False)

    async def _send_event_data(self, timeout_time=None, last_exception=None):
        if self._unsent_events:
            await self._open()
            remaining_time = timeout_time - time.time()
            if remaining_time <= 0.0:
                if last_exception:
                    error = last_exception
                else:
                    error = OperationTimeoutError("send operation timed out")
                log.info("%r send operation timed out. (%r)", self._name, error)
                raise error
            self._handler._msg_timeout = remaining_time  # pylint: disable=protected-access
            self._handler.queue_message(*self._unsent_events)
            await self._handler.wait_async()
            self._unsent_events = self._handler.pending_messages
            if self._outcome != constants.MessageSendResult.Ok:
                if self._outcome == constants.MessageSendResult.Timeout:
                    self._condition = OperationTimeoutError("send operation timed out")
                _error(self._outcome, self._condition)
        return

    async def _send_event_data_with_retry(self, timeout=None):
        return await self._do_retryable_operation(self._send_event_data, timeout=timeout)

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
            await self._open_with_retry()

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
        # Tracing code
        parent_span = get_parent_span()
        if parent_span:
            child = parent_span.span(name="Azure.EventHubs.send")
            child.kind = SpanKind.CLIENT  # Should be PRODUCER

        def trace_message(message):
            message_span = child.span(name="Azure.EventHubs.message")
            message_span.start()
            app_prop = dict(message.application_properties)
            app_prop.setdefault(b"Diagnostic-Id", message_span.get_trace_parent().encode('ascii'))
            message.application_properties = app_prop
            message_span.finish()

        self._check_closed()
        if isinstance(event_data, EventData):
            if partition_key:
                event_data._set_partition_key(partition_key)  # pylint: disable=protected-access
            wrapper_event_data = event_data
            trace_message(wrapper_event_data)
        else:
            if isinstance(event_data, EventDataBatch):
                if partition_key and partition_key != event_data._partition_key:  # pylint: disable=protected-access
                    raise EventDataError('The partition_key does not match the one of the EventDataBatch')
                wrapper_event_data = event_data  #type: ignore
            else:
                if partition_key:
                    event_data = _set_partition_key(event_data, partition_key)
                wrapper_event_data = EventDataBatch._from_batch(event_data, partition_key)  # pylint: disable=protected-access
            for internal_message in wrapper_event_data.message._body_gen:
                trace_message(internal_message)

        wrapper_event_data.message.on_send_complete = self._on_outcome
        self._unsent_events = [wrapper_event_data.message]

        if parent_span:
            with child:
                self._client._add_span_request_attributes(child)
                await self._send_event_data_with_retry(timeout=timeout)  # pylint:disable=unexpected-keyword-arg # TODO: to refactor
        else:
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
