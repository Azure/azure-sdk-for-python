# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import uuid
import logging
from typing import List, Any
import time
from distutils.version import StrictVersion

import uamqp  # type: ignore
from uamqp import errors, types, utils  # type: ignore
from uamqp import ReceiveClientAsync, Source  # type: ignore
from uamqp.compat import queue

from ..common import EventData, EventPosition
from ..error import _error_handler
from ._consumer_producer_mixin_async import ConsumerProducerMixin

log = logging.getLogger(__name__)


class EventHubConsumer(ConsumerProducerMixin):  # pylint:disable=too-many-instance-attributes
    """
    A consumer responsible for reading EventData from a specific Event Hub
    partition and as a member of a specific consumer group.

    A consumer may be exclusive, which asserts ownership over the partition for the consumer
    group to ensure that only one consumer from that group is reading the from the partition.
    These exclusive consumers are sometimes referred to as "Epoch Consumers."

    A consumer may also be non-exclusive, allowing multiple consumers from the same consumer
    group to be actively reading events from the partition.  These non-exclusive consumers are
    sometimes referred to as "Non-Epoch Consumers."

    Please use the method `create_consumer` on `EventHubClient` for creating `EventHubConsumer`.
    """
    _timeout = 0
    _epoch_symbol = b'com.microsoft:epoch'
    _timeout_symbol = b'com.microsoft:timeout'
    _receiver_runtime_metric_symbol = b'com.microsoft:enable-receiver-runtime-metric'

    def __init__(  # pylint: disable=super-init-not-called
            self, client, source, **kwargs):
        """
        Instantiate an async consumer. EventHubConsumer should be instantiated by calling the `create_consumer` method
        in EventHubClient.

        :param client: The parent EventHubClientAsync.
        :type client: ~azure.eventhub.aio.EventHubClientAsync
        :param source: The source EventHub from which to receive events.
        :type source: ~uamqp.address.Source
        :param event_position: The position from which to start receiving.
        :type event_position: ~azure.eventhub.common.EventPosition
        :param prefetch: The number of events to prefetch from the service
         for processing. Default is 300.
        :type prefetch: int
        :param owner_level: The priority of the exclusive consumer. An exclusive
         consumer will be created if owner_level is set.
        :type owner_level: int
        :param track_last_enqueued_event_properties: Indicates whether or not the consumer should request information
         on the last enqueued event on its associated partition, and track that information as events are received.
         When information about the partition's last enqueued event is being tracked, each event received from the
         Event Hubs service will carry metadata about the partition. This results in a small amount of additional
         network bandwidth consumption that is generally a favorable trade-off when considered against periodically
         making requests for partition properties using the Event Hub client.
         It is set to `False` by default.
        :type track_last_enqueued_event_properties: bool
        :param loop: An event loop.
        """
        event_position = kwargs.get("event_position", None)
        prefetch = kwargs.get("prefetch", 300)
        owner_level = kwargs.get("owner_level", None)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)
        track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)
        loop = kwargs.get("loop", None)

        self._on_event_received = kwargs.get("on_event_received")

        super(EventHubConsumer, self).__init__()
        self._loop = loop or asyncio.get_event_loop()
        self._client = client
        self._source = source
        self._offset = event_position
        self._messages_iter = None
        self._prefetch = prefetch
        self._owner_level = owner_level
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._retry_policy = errors.ErrorPolicy(max_retries=self._client._config.max_retries, on_error=_error_handler)  # pylint:disable=protected-access
        self._reconnect_backoff = 1
        self._link_properties = {}
        partition = self._source.split('/')[-1]
        self._partition = partition
        self._name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        if owner_level:
            self._link_properties[types.AMQPSymbol(self._epoch_symbol)] = types.AMQPLong(int(owner_level))
        link_property_timeout_ms = (self._client._config.receive_timeout or self._timeout) * 1000  # pylint:disable=protected-access
        self._link_properties[types.AMQPSymbol(self._timeout_symbol)] = types.AMQPLong(int(link_property_timeout_ms))
        self._handler = None
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties
        self._last_enqueued_event_properties = {}

        self._event_queue = queue.Queue()
        self._last_received_event = None

    def _create_handler(self):
        source = Source(self._source)
        if self._offset is not None:
            source.set_filter(self._offset._selector())  # pylint:disable=protected-access

        if StrictVersion(uamqp.__version__) < StrictVersion("1.2.3"):  # backward compatible until uamqp 1.2.3 released
            desired_capabilities = {}
        elif self._track_last_enqueued_event_properties:
            symbol_array = [types.AMQPSymbol(self._receiver_runtime_metric_symbol)]
            desired_capabilities = {"desired_capabilities": utils.data_factory(types.AMQPArray(symbol_array))}
        else:
            desired_capabilities = {"desired_capabilities": None}

        self._handler = ReceiveClientAsync(
            source,
            auth=self._client._create_auth(),  # pylint:disable=protected-access
            debug=self._client._config.network_tracing,  # pylint:disable=protected-access
            prefetch=self._prefetch,
            link_properties=self._link_properties,
            timeout=self._timeout,
            error_policy=self._retry_policy,
            keep_alive_interval=self._keep_alive,
            client_name=self._name,
            receive_settle_mode=uamqp.constants.ReceiverSettleMode.ReceiveAndDelete,
            auto_complete=False,
            properties=self._client._create_properties(  # pylint:disable=protected-access
                self._client._config.user_agent),  # pylint:disable=protected-access
            **desired_capabilities,  # pylint:disable=protected-access
            loop=self._loop)
        self._messages_iter = None

        self._handler._streaming_receive = True
        self._handler._message_received_callback = self._message_received

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open, operation_need_param=False)

    async def _receive(self, timeout_time=None, max_batch_size=None, **kwargs):
        last_exception = kwargs.get("last_exception")
        data_batch = []

        await self._open()
        remaining_time = timeout_time - time.time()
        if remaining_time <= 0.0:
            if last_exception:
                log.info("%r receive operation timed out. (%r)", self._name, last_exception)
                raise last_exception
            return data_batch

        remaining_time_ms = 1000 * remaining_time
        message_batch = await self._handler.receive_message_batch_async(
            max_batch_size=max_batch_size,
            timeout=remaining_time_ms)
        for message in message_batch:
            event_data = EventData._from_message(message)  # pylint:disable=protected-access
            data_batch.append(event_data)
            event_data._trace_link_message()  # pylint:disable=protected-access

        if data_batch:
            self._offset = EventPosition(data_batch[-1].offset)

        if self._track_last_enqueued_event_properties and data_batch:
            self._last_enqueued_event_properties = data_batch[-1]._get_last_enqueued_event_properties()  # pylint:disable=protected-access

        return data_batch

    async def _receive_with_retry(self, timeout=None, max_batch_size=None, **kwargs):
        return await self._do_retryable_operation(self._receive, timeout=timeout,
                                                  max_batch_size=max_batch_size, **kwargs)

    def _message_received(self, message):
        # pylint:disable=protected-access
        event_data = EventData._from_message(message)
        event_data._trace_link_message()
        self._last_received_event = event_data
        self._event_queue.put(event_data)

    async def receive(self):

        retried_times = 0
        last_exception = None

        while retried_times < self._client._config.max_retries:  # pylint:disable=protected-access
            try:
                await self._open()
                await self._handler.do_work_async()

                while self._event_queue.qsize():
                    event_data = self._event_queue.get()
                    await self._on_event_received(event_data)
                    self._event_queue.task_done()
                return
            except asyncio.CancelledError:
                raise
            except Exception as exception:
                if self._last_received_event:
                    self._offset = EventPosition(self._last_received_event.offset)
                last_exception = await self._handle_exception(exception)
                await self._client._try_delay(retried_times=retried_times,
                                              last_exception=last_exception,
                                              entity_name=self._name)
                retried_times += 1

        log.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
        raise last_exception

    @property
    def last_enqueued_event_properties(self):
        """
        The latest enqueued event information. This property will be updated each time an event is received when
        the receiver is created with `track_last_enqueued_event_properties` being `True`.
        The dict includes following information of the partition:

            - `sequence_number`
            - `offset`
            - `enqueued_time`
            - `retrieval_time`

        :rtype: dict or None
        """
        return self._last_enqueued_event_properties if self._track_last_enqueued_event_properties else None

    @property
    def queue_size(self):
        # type: () -> int
        """
        The current size of the unprocessed Event queue.

        :rtype: int
        """
        # pylint: disable=protected-access
        if self._handler._received_messages:
            return self._handler._received_messages.qsize()
        return 0

    async def close(self):
        # type: () -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        await super(EventHubConsumer, self).close()
