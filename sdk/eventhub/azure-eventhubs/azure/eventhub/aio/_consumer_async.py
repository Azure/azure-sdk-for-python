# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import uuid
import logging
import time

import uamqp  # type: ignore
from uamqp import errors, types, utils  # type: ignore
from uamqp import ReceiveClientAsync, Source  # type: ignore
from uamqp.compat import queue

from ._client_base_async import ConsumerProducerMixin
from .._common import EventData, EventPosition
from ..exceptions import _error_handler
from .._utils import create_properties, trace_link_message
from .._constants import (
    EPOCH_SYMBOL,
    TIMEOUT_SYMBOL,
    RECEIVER_RUNTIME_METRIC_SYMBOL
)

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

        self.running = False
        self.closed = False

        self._on_event_received = kwargs.get("on_event_received")
        self._loop = loop or asyncio.get_event_loop()
        self._client = client
        self._source = source
        self._offset = event_position
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
            self._link_properties[types.AMQPSymbol(EPOCH_SYMBOL)] = types.AMQPLong(int(owner_level))
        link_property_timeout_ms = (self._client._config.receive_timeout or self._timeout) * 1000  # pylint:disable=protected-access
        self._link_properties[types.AMQPSymbol(TIMEOUT_SYMBOL)] = types.AMQPLong(int(link_property_timeout_ms))
        self._handler = None
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties
        self._last_enqueued_event_properties = {}
        self._event_queue = queue.Queue()
        self._last_received_event = None

    def _create_handler(self):
        source = Source(self._source)
        if self._offset is not None:
            source.set_filter(self._offset._selector())  # pylint:disable=protected-access
        if self._track_last_enqueued_event_properties:
            symbol_array = [types.AMQPSymbol(RECEIVER_RUNTIME_METRIC_SYMBOL)]
            desired_capabilities = {"desired_capabilities": utils.data_factory(types.AMQPArray(symbol_array))}
        else:
            desired_capabilities = {"desired_capabilities": None}
        properties = create_properties(self._client._config.user_agent)  # pylint:disable=protected-access
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
            properties=properties,
            desired_capabilities=desired_capabilities,
            loop=self._loop)

        self._handler._streaming_receive = True  # pylint:disable=protected-access
        self._handler._message_received_callback = self._message_received  # pylint:disable=protected-access

    async def _open_with_retry(self):
        return await self._do_retryable_operation(self._open, operation_need_param=False)

    def _message_received(self, message):
        # pylint:disable=protected-access
        event_data = EventData._from_message(message)
        trace_link_message(event_data)
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
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except uamqp.errors.LinkDetach as ld_error:
                if ld_error.condition == uamqp.constants.ErrorCodes.LinkStolen:
                    raise await self._handle_exception(ld_error)
            except Exception as exception:  # pylint: disable=broad-except
                if not self.running:  # exit by close
                    return
                if self._last_received_event:
                    self._offset = EventPosition(self._last_received_event.offset)
                last_exception = await self._handle_exception(exception)
                retried_times += 1

        log.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
        raise last_exception
