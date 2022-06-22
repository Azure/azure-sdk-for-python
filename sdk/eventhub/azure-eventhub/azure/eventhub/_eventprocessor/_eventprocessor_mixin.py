# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
from contextlib import contextmanager
from typing import (
    Union,
    List,
    Iterable,
    Dict,
    Callable,
    Any,
    Type,
    Iterator,
    Tuple,
    Optional,
    cast,
    TYPE_CHECKING,
)

from azure.core.tracing import SpanKind, Link
from azure.core.settings import settings

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from azure.core.tracing import AbstractSpan
    from .._common import EventData
    from .._consumer import EventHubConsumer
    from .._consumer_client import EventHubConsumerClient
    from ..aio._consumer_async import EventHubConsumer as EventHubConsumerAsync
    from ..aio._consumer_client_async import (
        EventHubConsumerClient as EventHubConsumerClientAsync,
    )


class EventProcessorMixin(object):

    _eventhub_client = (
        None
    )  # type: Optional[Union[EventHubConsumerClient, EventHubConsumerClientAsync]]
    _consumer_group = ""  # type: str
    _owner_level = None  # type: Optional[int]
    _prefetch = None  # type: Optional[int]
    _track_last_enqueued_event_properties = False  # type: bool
    _initial_event_position_inclusive = {}  # type: Union[bool, Dict[str, bool]]
    _initial_event_position = (
        {}
    )  # type: Union[int, str, datetime, Dict[str, Union[int, str, datetime]]]

    def get_init_event_position(self, partition_id, checkpoint):
        # type: (str, Optional[Dict[str, Any]]) -> Tuple[Union[str, int, datetime], bool]
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None

        event_position_inclusive = False
        if isinstance(self._initial_event_position_inclusive, dict):
            event_position_inclusive = self._initial_event_position_inclusive.get(
                partition_id, False
            )
        elif isinstance(self._initial_event_position_inclusive, bool):
            event_position_inclusive = self._initial_event_position_inclusive

        event_position = "-1"  # type: Union[int, str, datetime]
        if checkpoint_offset:
            event_position = checkpoint_offset
        elif isinstance(self._initial_event_position, dict):
            event_position = self._initial_event_position.get(partition_id, "-1")  # type: ignore
        else:
            event_position = cast(
                Union[int, str, datetime], self._initial_event_position
            )

        return event_position, event_position_inclusive

    def create_consumer(
        self,
        partition_id,  # type: str
        initial_event_position,  # type: Union[str, int, datetime]
        initial_event_position_inclusive,  # type: bool
        on_event_received,  # type: Callable[[Union[Optional[EventData], List[EventData]]], None]
        **kwargs  # type: Any
    ):
        # type: (...) -> Union[EventHubConsumer, EventHubConsumerAsync]
        consumer = self._eventhub_client._create_consumer(  # type: ignore  # pylint: disable=protected-access
            self._consumer_group,
            partition_id,
            initial_event_position,
            on_event_received,  # type: ignore
            event_position_inclusive=initial_event_position_inclusive,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
            **kwargs
        )
        return consumer

    @contextmanager
    def _context(self, links=None):
        # type: (List[Link]) -> Iterator[None]
        """Tracing"""
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is None:
            yield
        else:
            child = span_impl_type(
                name="Azure.EventHubs.process", kind=SpanKind.CONSUMER, links=links
            )
            self._eventhub_client._add_span_request_attributes(child)  # type: ignore  # pylint: disable=protected-access
            with child:
                yield
