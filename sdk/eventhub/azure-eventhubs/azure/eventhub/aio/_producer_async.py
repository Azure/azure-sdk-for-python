# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import uuid
import asyncio
import logging
from typing import Iterable, Union, Type
import time

from uamqp import types, constants, errors  # type: ignore
from uamqp import SendClientAsync  # type: ignore

from azure.core.tracing import SpanKind, AbstractSpan  # type: ignore
from azure.core.settings import settings  # type: ignore

from .._common import EventData, EventDataBatch
from ..exceptions import _error_handler, OperationTimeoutError
from .._producer import _set_partition_key, _set_trace_message
from .._utils import create_properties, set_message_partition_key, trace_message
from .._constants import TIMEOUT_SYMBOL
from ._client_base_async import ConsumerProducerMixin

_LOGGER = logging.getLogger(__name__)


class EventHubProducer(ConsumerProducerMixin):  # pylint: disable=too-many-instance-attributes
    """
    A producer responsible for transmitting EventData to a specific Event Hub,
    grouped together in batches. Depending on the options specified at creation, the producer may
    be created to allow event data to be automatically routed to an available partition or specific
    to a partition.

    Please use the method `create_producer` on `EventHubClient` for creating `EventHubProducer`.
    """

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
        idle_timeout = kwargs.get("idle_timeout", None)

        self.running = False
        self.closed = False

        self._loop = loop or asyncio.get_event_loop()
        self._max_message_size_on_link = None
        self._client = client
        self._target = target
        self._partition = partition
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._timeout = send_timeout
        self._idle_timeout = (idle_timeout * 1000) if idle_timeout else None
        self._retry_policy = errors.ErrorPolicy(
            max_retries=self._client._config.max_retries, on_error=_error_handler)  # pylint:disable=protected-access
        self._reconnect_backoff = 1
        self._name = "EHProducer-{}".format(uuid.uuid4())
        self._unsent_events = None
        self._error = None
        if partition:
            self._target += "/Partitions/" + partition
            self._name += "-partition{}".format(partition)
        self._handler = None
        self._outcome = None
        self._condition = None
        self._lock = asyncio.Lock()
        self._link_properties = {types.AMQPSymbol(TIMEOUT_SYMBOL): types.AMQPLong(int(self._timeout * 1000))}

    def _create_handler(self, auth):
        self._handler = SendClientAsync(
            self._target,
            auth=auth,
            debug=self._client._config.network_tracing,  # pylint:disable=protected-access
            msg_timeout=self._timeout * 1000,
            idle_timeout=self._idle_timeout,
            error_policy=self._retry_policy,
            keep_alive_interval=self._keep_alive,
            client_name=self._name,
            link_properties=self._link_properties,
            properties=create_properties(self._client._config.user_agent),  # pylint:disable=protected-access
            loop=self._loop)

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open, operation_need_param=False)

    def _set_msg_timeout(self, timeout_time, last_exception):
        if not timeout_time:
            return
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                error = last_exception
            else:
                error = OperationTimeoutError("Send operation timed out")
            _LOGGER.info("%r send operation timed out. (%r)", self._name, error)
            raise error
        self._handler._msg_timeout = remaining_time * 1000  # pylint: disable=protected-access

    async def _send_event_data(self, timeout_time=None, last_exception=None):
        if self._unsent_events:
            await self._open()
            self._set_msg_timeout(timeout_time, last_exception)
            self._handler.queue_message(*self._unsent_events)
            await self._handler.wait_async()
            self._unsent_events = self._handler.pending_messages
            if self._outcome != constants.MessageSendResult.Ok:
                if self._outcome == constants.MessageSendResult.Timeout:
                    self._condition = OperationTimeoutError("Send operation timed out")
                raise self._condition

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

    def _wrap_eventdata(self, event_data, span, partition_key):
        if isinstance(event_data, EventData):
            if partition_key:
                set_message_partition_key(event_data.message, partition_key)
            wrapper_event_data = event_data
            trace_message(wrapper_event_data, span)
        else:
            if isinstance(event_data, EventDataBatch):  # The partition_key in the param will be omitted.
                if partition_key and partition_key != event_data._partition_key:  # pylint: disable=protected-access
                    raise ValueError('The partition_key does not match the one of the EventDataBatch')
                wrapper_event_data = event_data  # type:ignore
            else:
                if partition_key:
                    event_data = _set_partition_key(event_data, partition_key)
                event_data = _set_trace_message(event_data)
                wrapper_event_data = EventDataBatch._from_batch(event_data, partition_key)  # pylint: disable=protected-access
        wrapper_event_data.message.on_send_complete = self._on_outcome
        return wrapper_event_data

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
        """
        # Tracing code
        async with self._lock:
            span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
            child = None
            if span_impl_type is not None:
                child = span_impl_type(name="Azure.EventHubs.send")
                child.kind = SpanKind.CLIENT  # Should be PRODUCER
            self._check_closed()
            wrapper_event_data = self._wrap_eventdata(event_data, child, partition_key)
            self._unsent_events = [wrapper_event_data.message]

            if span_impl_type is not None and child is not None:
                with child:
                    self._client._add_span_request_attributes(child)  # pylint: disable=protected-access
                    await self._send_event_data_with_retry(timeout=timeout)  # pylint:disable=unexpected-keyword-arg # TODO: to refactor
            else:
                await self._send_event_data_with_retry(timeout=timeout)  # pylint:disable=unexpected-keyword-arg # TODO: to refactor

    async def close(self):
        # type: () -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        async with self._lock:
            await super(EventHubProducer, self).close()
