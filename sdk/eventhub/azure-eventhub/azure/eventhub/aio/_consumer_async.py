# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
import uuid
import logging
from collections import deque
from typing import TYPE_CHECKING, Callable, Awaitable, Dict, Optional, Union, List

from ._client_base_async import ConsumerProducerMixin
from ._async_utils import get_dict_with_loop_if_needed
from .._common import EventData
from .._utils import create_properties, event_position_selector
from .._constants import EPOCH_SYMBOL, TIMEOUT_SYMBOL, RECEIVER_RUNTIME_METRIC_SYMBOL

if TYPE_CHECKING:
    from typing import Deque
    import uamqp
    from uamqp import ReceiveClientAsync, Source, types
    from uamqp.authentication import JWTTokenAsync
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

        self._amqp_transport = kwargs.pop("amqp_transport")
        self._on_event_received: Callable[[Union[Optional[EventData], List[EventData]]], Awaitable[None]] = kwargs[
            "on_event_received"
        ]
        self._internal_kwargs = get_dict_with_loop_if_needed(kwargs.get("loop", None))
        self._client = client
        self._source = source
        self._offset = event_position
        self._offset_inclusive = kwargs.get("event_position_inclusive", False)
        self._prefetch = prefetch
        self._owner_level = owner_level
        self._keep_alive = keep_alive
        self._auto_reconnect = auto_reconnect
        self._retry_policy = self._amqp_transport.create_retry_policy(self._client._config)
        self._reconnect_backoff = 1
        self._timeout = 0
        self._idle_timeout = (idle_timeout * self._amqp_transport.IDLE_TIMEOUT_FACTOR) if idle_timeout else None
        link_properties: Dict[types.AMQPType, types.AMQPType] = {}
        self._partition = self._source.split("/")[-1]
        self._name = f"EHReceiver-{uuid.uuid4()}-partition{self._partition}"
        if owner_level is not None:
            link_properties[EPOCH_SYMBOL] = int(owner_level)
        link_property_timeout_ms = (
            self._client._config.receive_timeout
            or self._timeout  # pylint:disable=protected-access
        ) * self._amqp_transport.IDLE_TIMEOUT_FACTOR
        link_properties[TIMEOUT_SYMBOL] = int(link_property_timeout_ms)
        self._link_properties = self._amqp_transport.create_link_properties(link_properties)
        self._handler: Optional[ReceiveClientAsync] = None
        self._track_last_enqueued_event_properties = (
            track_last_enqueued_event_properties
        )
        self._message_buffer: Deque[uamqp.Message] = deque()
        self._last_received_event: Optional[EventData] = None

    def _create_handler(self, auth: JWTTokenAsync) -> None:
        source = self._amqp_transport.create_source(
            self._source,
            self._offset,
            event_position_selector(self._offset, self._offset_inclusive)
        )
        desired_capabilities = [RECEIVER_RUNTIME_METRIC_SYMBOL] if self._track_last_enqueued_event_properties else None

        self._handler = self._amqp_transport.create_receive_client(
            config=self._client._config,    # pylint:disable=protected-access
            source=source,
            auth=auth,
            network_trace=self._client._config.network_tracing,  # pylint:disable=protected-access
            link_credit=self._prefetch,
            link_properties=self._link_properties,
            idle_timeout=self._idle_timeout,
            retry_policy=self._retry_policy,
            keep_alive_interval=self._keep_alive,
            client_name=self._name,
            properties=create_properties(
                self._client._config.user_agent, amqp_transport=self._amqp_transport  # pylint:disable=protected-access
            ),
            desired_capabilities=desired_capabilities,
            streaming_receive=True,
            message_received_callback=self._message_received,
        )

    async def _open_with_retry(self) -> None:
        await self._do_retryable_operation(self._open, operation_need_param=False)

    def _message_received(self, message: uamqp.Message) -> None:
        self._message_buffer.append(message)

    def _next_message_in_buffer(self):
        # pylint:disable=protected-access
        message = self._message_buffer.popleft()
        event_data = EventData._from_message(message)
        self._last_received_event = event_data
        return event_data

    async def receive(
        self, batch=False, max_batch_size=300, max_wait_time=None
    ) -> None:
        await self._amqp_transport.receive_messages(self, batch, max_batch_size, max_wait_time)
