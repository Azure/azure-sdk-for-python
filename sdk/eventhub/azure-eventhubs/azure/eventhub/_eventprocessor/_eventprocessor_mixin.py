# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from contextlib import contextmanager

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from azure.eventhub import EventPosition

from .._utils import trace_link_message


class EventProcessorMixin(object):

    def get_init_event_position(self, partition_id, checkpoint):
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None
        if checkpoint_offset:
            initial_event_position = EventPosition(checkpoint_offset)
        elif isinstance(self._initial_event_position, EventPosition):
            initial_event_position = self._initial_event_position
        elif isinstance(self._initial_event_position, dict):
            initial_event_position = self._initial_event_position.get(partition_id, EventPosition("-1"))
        else:
            initial_event_position = EventPosition(self._initial_event_position)
        return initial_event_position

    def create_consumer(self, partition_id, initial_event_position, on_event_received):
        consumer = self._eventhub_client._create_consumer(  # pylint: disable=protected-access
            self._consumer_group,
            partition_id,
            initial_event_position,
            on_event_received=on_event_received,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
        )
        return consumer

    @contextmanager
    def _context(self, event):
        # Tracing
        span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
        if span_impl_type is None:
            yield
        else:
            child = span_impl_type(name="Azure.EventHubs.process")
            self._eventhub_client._add_span_request_attributes(child)  # pylint: disable=protected-access
            child.kind = SpanKind.SERVER

            trace_link_message(event, child)
            with child:
                yield
