# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import asyncio
import uuid
import logging
from collections import deque
from typing import TYPE_CHECKING, Callable, Awaitable, cast, Dict, Optional, Union, List
from urllib.parse import urlparse

from .._pyamqp import (
    types,
    utils as pyamqp_utils,
    error,
    constants as pyamqp_constants
)
from .._pyamqp.endpoints import Source, ApacheFilters
from .._pyamqp.message import Message
from .._pyamqp.aio import ReceiveClientAsync

from ._client_base_async import ConsumerProducerMixin
from ._async_utils import get_dict_with_loop_if_needed
from .._common import EventData
from .._utils import create_properties, event_position_selector
from .._constants import EPOCH_SYMBOL, TIMEOUT_SYMBOL, RECEIVER_RUNTIME_METRIC_SYMBOL, NO_RETRY_ERRORS, \
    CUSTOM_CONDITION_BACKOFF

if TYPE_CHECKING:
    from typing import Deque
    from .._pyamqp.aio._authentication_async import JWTTokenAuthAsync
    from ._consumer_client_async import EventHubConsumerClient

_LOGGER = logging.getLogger(__name__)


class EventHubConsumer(
    ConsumerProducerMixin
):  # pylint:disable=too-many-instance-attributes
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
    """

    def __init__(self, client: "EventHubConsumerClient", source: str, **kwargs) -> None:
        super().__init__()
        event_position = kwargs.get("event_position", None)
        prefetch = kwargs.get("prefetch", 300)
        owner_level = kwargs.get("owner_level", None)
        keep_alive = kwargs.get("keep_alive", None)
        auto_reconnect = kwargs.get("auto_reconnect", True)
        track_last_enqueued_event_properties = kwargs.get(
            "track_last_enqueued_event_properties", False
        )
        idle_timeout = kwargs.get("idle_timeout", None)

        self.running = False
        self.closed = False

        self._on_event_received = kwargs[
            "on_event_received"
        ]  # type: Callable[[Union[Optional[EventData], List[EventData]]], Awaitable[None]]
        self._internal_kwargs = get_dict_with_loop_if_needed(kwargs.get("loop", None))
        self._client = client
        self._source = source
        self._offset = event_position
        self._offset_inclusive = kwargs.get("event_position_inclusive", False)
        self._prefetch = prefetch
        self._owner_level = owner_level
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._retry_policy = error.RetryPolicy(
            retry_total=self._client._config.max_retries,  # pylint:disable=protected-access
            retry_backoff_factor=self._client._config.backoff_factor,  # pylint:disable=protected-access
            retry_backoff_max=self._client._config.backoff_max,  # pylint:disable=protected-access
            retry_mode=self._client._config.retry_mode,  # pylint:disable=protected-access
            no_retry_condition=NO_RETRY_ERRORS,
            custom_condition_backoff=CUSTOM_CONDITION_BACKOFF,
        )
        self._reconnect_backoff = 1
        self._timeout = 0
        self._idle_timeout = idle_timeout
        self._link_properties = {}
        partition = self._source.split("/")[-1]
        self._partition = partition
        self._name = "EHReceiver-{}-partition{}".format(uuid.uuid4(), partition)
        if owner_level is not None:
            self._link_properties[EPOCH_SYMBOL] = pyamqp_utils.amqp_long_value(int(owner_level))
        link_property_timeout_ms = (
            self._client._config.receive_timeout or self._timeout # pylint:disable=protected-access
        ) * 1000
        self._link_properties[TIMEOUT_SYMBOL] = pyamqp_utils.amqp_long_value(int(link_property_timeout_ms))
        self._handler = None  # type: Optional[ReceiveClientAsync]
        self._track_last_enqueued_event_properties = (
            track_last_enqueued_event_properties
        )
        self._message_buffer = deque()  # type: Deque[Message]
        self._last_received_event = None  # type: Optional[EventData]
        self._message_buffer_lock = asyncio.Lock()
        self._last_callback_called_time = None
        self._callback_task_run = None

    def _create_handler(self, auth: "JWTTokenAuthAsync") -> None:
        source = Source(self._source, filters={})
        if self._offset is not None:
            filter_key = ApacheFilters.selector_filter
            source.filters[filter_key] = (
                filter_key,
                pyamqp_utils.amqp_string_value(
                    event_position_selector(
                        self._offset,
                        self._offset_inclusive
                    )
                )
            )
        desired_capabilities = [RECEIVER_RUNTIME_METRIC_SYMBOL] if self._track_last_enqueued_event_properties else None

        custom_endpoint_address = self._client._config.custom_endpoint_address
        transport_type = self._client._config.transport_type # pylint:disable=protected-access
        hostname = urlparse(source.address).hostname
        if transport_type.name == 'AmqpOverWebsocket':
            hostname += '/$servicebus/websocket/'
            if custom_endpoint_address:
                custom_endpoint_address += '/$servicebus/websocket/'
        self._handler = ReceiveClientAsync(
            hostname,
            source,
            auth=auth,
            idle_timeout=self._idle_timeout,
            network_trace=self._client._config.network_tracing,  # pylint:disable=protected-access
            link_credit=self._prefetch,
            link_properties=self._link_properties,
            transport_type=transport_type,
            http_proxy=self._client._config.http_proxy, # pylint:disable=protected-access
            retry_policy=self._retry_policy,
            client_name=self._name,
            receive_settle_mode=pyamqp_constants.ReceiverSettleMode.First,
            properties=create_properties(self._client._config.user_agent),  # pylint:disable=protected-access
            desired_capabilities=desired_capabilities,
            streaming_receive=True,
            message_received_callback=self._message_received,
            custom_endpoint_address=custom_endpoint_address,
            connection_verify=self._client._config.connection_verify,
        )

    async def _open_with_retry(self) -> None:
        await self._do_retryable_operation(self._open, operation_need_param=False)

    async def _message_received(self, message: Message) -> None:
        async with self._message_buffer_lock:
            self._message_buffer.append(message)

    def _next_message_in_buffer(self):
        # pylint:disable=protected-access
        message = self._message_buffer.popleft()
        event_data = EventData._from_message(message)
        self._last_received_event = event_data
        return event_data

    async def _callback_task(self, batch, max_batch_size, max_wait_time):
        while self._callback_task_run:
            async with self._message_buffer_lock:
                messages = [
                    self._message_buffer.popleft() for _ in range(min(max_batch_size, len(self._message_buffer)))
                ]
            events = [EventData._from_message(message) for message in messages]
            now_time = time.time()
            if len(events) > 0:
                await self._on_event_received(events if batch else events[0])
                self._last_callback_called_time = now_time
            else:
                if max_wait_time and (now_time - self._last_callback_called_time) > max_wait_time:
                    # no events received, and need to callback
                    await self._on_event_received([] if batch else None)
                    self._last_callback_called_time = now_time
                # backoff a bit to avoid throttling CPU when no events are coming
                await asyncio.sleep(0.05)

    async def _receive_task(self):
        max_retries = (
            self._client._config.max_retries  # pylint:disable=protected-access
        )
        retried_times = 0
        while retried_times <= max_retries:
            try:
                await self._open()
                await cast(ReceiveClientAsync, self._handler).do_work_async(batch=self._prefetch)
            except asyncio.CancelledError:  # pylint: disable=try-except-raise
                raise
            except Exception as exception:  # pylint: disable=broad-except
                if (
                        isinstance(exception, error.AMQPLinkError)
                        and exception.condition == error.ErrorCondition.LinkStolen  # pylint: disable=no-member
                ):
                    raise await self._handle_exception(exception)
                if not self.running:  # exit by close
                    return
                if self._last_received_event:
                    self._offset = self._last_received_event.offset
                last_exception = await self._handle_exception(exception)
                retried_times += 1
                if retried_times > max_retries:
                    _LOGGER.info(
                        "%r operation has exhausted retry. Last exception: %r.",
                        self._name,
                        last_exception,
                    )
                    raise last_exception

    async def receive(self, batch=False, max_batch_size=300, max_wait_time=None) -> None:
        self._callback_task_run = True
        self._last_callback_called_time = time.time()
        callback_task = asyncio.ensure_future(self._callback_task(batch, max_batch_size, max_wait_time))
        receive_task = asyncio.ensure_future(self._receive_task())

        try:
            await receive_task
        finally:
            self._callback_task_run = False
            await callback_task
