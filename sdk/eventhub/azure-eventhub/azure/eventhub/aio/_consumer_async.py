# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import uuid
import logging
from typing import TYPE_CHECKING, Callable, Awaitable, cast, Dict, Optional

import uamqp  # type: ignore
from uamqp import errors, types, utils  # type: ignore
from uamqp import ReceiveClientAsync, Source  # type: ignore
from uamqp.compat import queue

from ._client_base_async import ConsumerProducerMixin
from .._common import EventData
from ..exceptions import _error_handler
from .._utils import create_properties, trace_link_message, event_position_selector
from ._eventprocessor.utils import get_running_loop
from .._constants import (
    EPOCH_SYMBOL,
    TIMEOUT_SYMBOL,
    RECEIVER_RUNTIME_METRIC_SYMBOL
)

if TYPE_CHECKING:
    from uamqp.authentication import JWTTokenAsync
    from ._consumer_client_async import EventHubConsumerClient
    from ._eventprocessor.partition_context import PartitionContext

_LOGGER = logging.getLogger(__name__)


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

    Please use the method `_create_consumer` on `EventHubClient` for creating `EventHubConsumer`.

    :param client: The parent EventHubConsumerClient.
    :type client: ~azure.eventhub.aio.EventHubConsumerClient
    :param source: The source EventHub from which to receive events.
    :type source: ~uamqp.address.Source
    :keyword event_position: The position from which to start receiving.
    :paramtype event_position: int, str, datetime.datetime
    :keyword int prefetch: The number of events to prefetch from the service
        for processing. Default is 300.
    :keyword int owner_level: The priority of the exclusive consumer. An exclusive
        consumer will be created if owner_level is set.
    :keyword bool track_last_enqueued_event_properties: Indicates whether or not the consumer should request information
        on the last enqueued event on its associated partition, and track that information as events are received.
        When information about the partition's last enqueued event is being tracked, each event received from the
        Event Hubs service will carry metadata about the partition. This results in a small amount of additional
        network bandwidth consumption that is generally a favorable trade-off when considered against periodically
        making requests for partition properties using the Event Hub client.
        It is set to `False` by default.
    :keyword ~asyncio.AbstractEventLoop loop: An event loop.
    """

    def __init__(self, client: 'EventHubConsumerClient', source: str, **kwargs) -> None:
        event_position = kwargs.get("event_position", None)
        prefetch = kwargs.get("prefetch", 300)
        owner_level = kwargs.get("owner_level", None)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)
        track_last_enqueued_event_properties = kwargs.get("track_last_enqueued_event_properties", False)
        idle_timeout = kwargs.get("idle_timeout", None)
        loop = kwargs.get("loop", None)

        self.running = False
        self.closed = False

        self._on_event_received = kwargs["on_event_received"]  # type: Callable[[EventData], Awaitable[None]]
        self._loop = loop or get_running_loop()
        self._client = client
        self._source = source
        self._offset = event_position
        self._offset_inclusive = kwargs.get("event_position_inclusive", False)
        self._prefetch = prefetch
        self._owner_level = owner_level
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._retry_policy = errors.ErrorPolicy(max_retries=self._client._config.max_retries, on_error=_error_handler)  # pylint:disable=protected-access
        self._reconnect_backoff = 1
        self._timeout = 0
        self._idle_timeout = (idle_timeout * 1000) if idle_timeout else None
        self._link_properties = {}  # type: Dict[types.AMQPType, types.AMQPType]
        partition = self._source.split('/')[-1]
        self._partition = partition
        self._name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        if owner_level:
            self._link_properties[types.AMQPSymbol(EPOCH_SYMBOL)] = types.AMQPLong(int(owner_level))
        link_property_timeout_ms = (self._client._config.receive_timeout or self._timeout) * 1000  # pylint:disable=protected-access
        self._link_properties[types.AMQPSymbol(TIMEOUT_SYMBOL)] = types.AMQPLong(int(link_property_timeout_ms))
        self._handler = None  # type: Optional[ReceiveClientAsync]
        self._track_last_enqueued_event_properties = track_last_enqueued_event_properties
        self._event_queue = queue.Queue()
        self._last_received_event = None  # type: Optional[EventData]

    def _create_handler(self, auth: 'JWTTokenAsync') -> None:
        source = Source(self._source)
        if self._offset is not None:
            source.set_filter(event_position_selector(self._offset, self._offset_inclusive))
        desired_capabilities = None
        if self._track_last_enqueued_event_properties:
            symbol_array = [types.AMQPSymbol(RECEIVER_RUNTIME_METRIC_SYMBOL)]
            desired_capabilities = utils.data_factory(types.AMQPArray(symbol_array))

        properties = create_properties(self._client._config.user_agent)  # pylint:disable=protected-access
        self._handler = ReceiveClientAsync(
            source,
            auth=auth,
            debug=self._client._config.network_tracing,  # pylint:disable=protected-access
            prefetch=self._prefetch,
            link_properties=self._link_properties,
            timeout=self._timeout,
            idle_timeout=self._idle_timeout,
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

    async def _open_with_retry(self) -> None:
        await self._do_retryable_operation(self._open, operation_need_param=False)

    def _message_received(self, message: uamqp.Message) -> None:
        self._event_queue.put(message)

    async def receive(self) -> None:
        retried_times = 0
        last_exception = None
        max_retries = self._client._config.max_retries  # pylint:disable=protected-access

        while retried_times <= max_retries:
            try:
                await self._open()
                await cast(ReceiveClientAsync, self._handler).do_work_async()
                while not self._event_queue.empty():
                    message = self._event_queue.get()
                    event_data = EventData._from_message(message)  # pylint:disable=protected-access
                    self._last_received_event = event_data
                    trace_link_message(event_data)
                    await self._on_event_received(event_data)
                    self._event_queue.task_done()
                return
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint: disable=broad-except
                if isinstance(exception, uamqp.errors.LinkDetach) and \
                        exception.condition == uamqp.constants.ErrorCodes.LinkStolen:  # pylint: disable=no-member
                    raise await self._handle_exception(exception)
                if not self.running:  # exit by close
                    return
                if self._last_received_event:
                    self._offset = self._last_received_event.offset
                last_exception = await self._handle_exception(exception)
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info("%r operation has exhausted retry. Last exception: %r.", self._name, last_exception)
                    raise last_exception
