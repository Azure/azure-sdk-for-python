# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
from datetime import datetime
from typing import (
    Mapping,
    Union,
    List,
    Dict,
    Callable,
    Any,
    Tuple,
    Optional,
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from .._common import EventData
    from .._consumer import EventHubConsumer
    from ..aio._consumer_async import EventHubConsumer as EventHubConsumerAsync
    from .._consumer_client import EventHubConsumerClient
    from ..aio._consumer_client_async import (
        EventHubConsumerClient as EventHubConsumerClientAsync,
    )


class EventProcessorMixin:

    _eventhub_client: Optional[Union[EventHubConsumerClient, EventHubConsumerClientAsync]] = None
    _consumer_group: str = ""
    _owner_level: Optional[int] = None
    _prefetch: Optional[int] = None
    _track_last_enqueued_event_properties: bool = False
    _initial_event_position_inclusive: Union[bool, Mapping[str, bool]] = {}
    _initial_event_position: Union[int, str, datetime, Mapping[str, Union[int, str, datetime]]] = {}

    def get_init_event_position(
        self, partition_id: str, checkpoint: Optional[Dict[str, Any]]
    ) -> Tuple[Union[str, int, datetime], bool]:
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None

        event_position_inclusive = False
        if isinstance(self._initial_event_position_inclusive, Mapping):
            event_position_inclusive = self._initial_event_position_inclusive.get(partition_id, False)
        elif isinstance(self._initial_event_position_inclusive, bool):
            event_position_inclusive = self._initial_event_position_inclusive

        event_position: Union[str, int, datetime] = "-1"
        if checkpoint_offset:
            event_position = checkpoint_offset
        elif isinstance(self._initial_event_position, Mapping):
            event_position = self._initial_event_position.get(partition_id, "-1")  # type: ignore
        else:
            event_position = cast(Union[int, str, datetime], self._initial_event_position)

        return event_position, event_position_inclusive

    def create_consumer(
        self,
        partition_id: str,
        initial_event_position: Union[str, int, datetime],
        initial_event_position_inclusive: bool,
        on_event_received: Callable[[Union[Optional[EventData], List[EventData]]], None],
        **kwargs: Any,
    ) -> Union[EventHubConsumer, EventHubConsumerAsync]:
        consumer = self._eventhub_client._create_consumer(  # type: ignore  # pylint: disable=protected-access
            self._consumer_group,
            partition_id,
            initial_event_position,
            on_event_received,  # type: ignore
            event_position_inclusive=initial_event_position_inclusive,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
            **kwargs,
        )
        return consumer
