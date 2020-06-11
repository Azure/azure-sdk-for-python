# Copyright 2017, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections

from opencensus.common import utils
from opencensus.trace import attributes

_SpanData = collections.namedtuple(
    '_SpanData',
    (
        'name',
        'context',
        'span_id',
        'parent_span_id',
        'attributes',
        'start_time',
        'end_time',
        'child_span_count',
        'stack_trace',
        'annotations',
        'message_events',
        'links',
        'status',
        'same_process_as_parent_span',
        'span_kind',
    ),
)


class SpanData(_SpanData):
    """Immutable representation of all data collected by a
     :class: `~opencensus.trace.span.Span`.

    :type name: str
    :param name: The name of the span.

    :type: context: :class: `~opencensus.trace.span_context.SpanContext`
    :param context: The SpanContext of the Span

    :type span_id: int
    :param span_id: Identifier for the span, unique within a trace.

    :type parent_span_id: int
    :param parent_span_id: (Optional) Parent span id.

    :type attributes: dict
    :param attributes: Collection of attributes associated with the span.

    :type start_time: str
    :param start_time: (Optional) Start of the time interval (inclusive)
                       during which the trace data was collected from the
                       application.

    :type end_time: str
    :param end_time: (Optional) End of the time interval (inclusive) during
                     which the trace data was collected from the application.

    :type child_span_count: int
    :param child_span_count: the number of child spans that were
                            generated while the span was active.

    :type stack_trace: :class: `~opencensus.trace.stack_trace.StackTrace`
    :param stack_trace: (Optional) A call stack appearing in a trace

    :type annotations: list(:class:`opencensus.trace.time_event.Annotation`)
    :param annotations: (Optional) The list of span annotations.

    :type message_events:
        list(:class:`opencensus.trace.time_event.MessageEvent`)
    :param message_events: (Optional) The list of span message events.

    :type links: list
    :param links: (Optional) Links associated with the span. You can have up
                  to 128 links per Span.

    :type status: :class: `~opencensus.trace.status.Status`
    :param status: (Optional) An optional final status for this span.

    :type same_process_as_parent_span: bool
    :param same_process_as_parent_span: (Optional) A highly recommended but not
                                        required flag that identifies when a
                                        trace crosses a process boundary.
                                        True when the parent_span belongs to
                                        the same process as the current span.
    :type span_kind: int
    :param span_kind: (Optional) Highly recommended flag that denotes the type
                        of span (valid values defined by :class:
                        `opencensus.trace.span.SpanKind`)

    """
    __slots__ = ()


def _format_legacy_span_json(span_data):
    """
    :param SpanData span_data: SpanData object to convert
    :rtype: dict
    :return: Dictionary representing the Span
    """
    span_json = {
        'displayName': utils.get_truncatable_str(span_data.name),
        'spanId': span_data.span_id,
        'startTime': span_data.start_time,
        'endTime': span_data.end_time,
        'childSpanCount': span_data.child_span_count,
        'kind': span_data.span_kind
    }

    if span_data.parent_span_id is not None:
        span_json['parentSpanId'] = span_data.parent_span_id

    if span_data.attributes:
        span_json['attributes'] = attributes.Attributes(
            span_data.attributes).format_attributes_json()

    if span_data.stack_trace is not None:
        span_json['stackTrace'] = \
            span_data.stack_trace.format_stack_trace_json()

    formatted_time_events = []
    if span_data.annotations:
        formatted_time_events.extend(
            {'time': aa.timestamp,
             'annotation': aa.format_annotation_json()}
            for aa in span_data.annotations)
    if span_data.message_events:
        formatted_time_events.extend(
            {'time': aa.timestamp,
             'message_event': aa.format_message_event_json()}
            for aa in span_data.message_events)
    if formatted_time_events:
        span_json['timeEvents'] = {
            'timeEvent': formatted_time_events
        }

    if span_data.links:
        span_json['links'] = {
            'link': [
                link.format_link_json() for link in span_data.links]
        }

    if span_data.status is not None:
        span_json['status'] = span_data.status.format_status_json()

    if span_data.same_process_as_parent_span is not None:
        span_json['sameProcessAsParentSpan'] = \
            span_data.same_process_as_parent_span

    return span_json


def format_legacy_trace_json(span_datas):
    """Formats a list of SpanData tuples into the legacy 'trace' dictionary
    format for backwards compatibility
    :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
    :param list of opencensus.trace.span_data.SpanData span_datas:
        SpanData tuples to emit
    :rtype: dict
    :return: Legacy 'trace' dictionary representing given SpanData tuples
    """
    if not span_datas:
        return {}
    top_span = span_datas[0]
    assert isinstance(top_span, SpanData)
    trace_id = top_span.context.trace_id if top_span.context is not None \
        else None
    assert trace_id is not None
    return {
        'traceId': trace_id,
        'spans': [_format_legacy_span_json(sd) for sd in span_datas],
    }
