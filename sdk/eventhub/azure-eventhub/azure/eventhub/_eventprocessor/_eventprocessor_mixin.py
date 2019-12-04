# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
from contextlib import contextmanager
import six

from azure.core.tracing import SpanKind  # type: ignore
from azure.core.settings import settings  # type: ignore

from .._utils import trace_link_message


class EventProcessorMixin(object):

    def get_init_event_position(self, partition_id, checkpoint):
        checkpoint_offset = checkpoint.get("offset") if checkpoint else None

        event_position_inclusive = False
        if isinstance(self._initial_event_position_inclusive, dict):
            event_position_inclusive = self._initial_event_position_inclusive.get(partition_id, False)
        elif isinstance(self._initial_event_position_inclusive, bool):
            event_position_inclusive = self._initial_event_position_inclusive

        event_position = "-1"
        if checkpoint_offset:
            event_position = checkpoint_offset
        elif isinstance(self._initial_event_position, (str, six.integer_types, datetime.datetime)):
            event_position = self._initial_event_position
        elif isinstance(self._initial_event_position, dict):
            event_position = self._initial_event_position.get(partition_id, "-1")
        else:
            event_position = self._initial_event_position

        return event_position, event_position_inclusive

    def create_consumer(
            self,
            partition_id,
            initial_event_position,
            initial_event_position_inclusive,
            on_event_received,
            **kwargs
    ):
        consumer = self._eventhub_client._create_consumer(  # pylint: disable=protected-access
            self._consumer_group,
            partition_id,
            initial_event_position,
            event_position_inclusive=initial_event_position_inclusive,
            on_event_received=on_event_received,
            owner_level=self._owner_level,
            track_last_enqueued_event_properties=self._track_last_enqueued_event_properties,
            prefetch=self._prefetch,
            **kwargs
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
