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

try:
    from collections.abc import MutableMapping
    from collections.abc import Sequence
except ImportError:
    from collections import MutableMapping
    from collections import Sequence

from collections import OrderedDict
from collections import deque
from datetime import datetime
from itertools import chain
import threading

from opencensus.common import utils
from opencensus.trace import attributes as attributes_module
from opencensus.trace import base_span
from opencensus.trace import link as link_module
from opencensus.trace import stack_trace as stack_trace_module
from opencensus.trace import status as status_module
from opencensus.trace import time_event
from opencensus.trace.span_context import generate_span_id
from opencensus.trace.tracers import base


# https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/TraceConfig.md  # noqa
MAX_NUM_ATTRIBUTES = 32
MAX_NUM_ANNOTATIONS = 32
MAX_NUM_MESSAGE_EVENTS = 128
MAX_NUM_LINKS = 32


class BoundedList(Sequence):
    """An append only list with a fixed max size."""
    def __init__(self, maxlen):
        self.dropped = 0
        self._dq = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def __repr__(self):
        return ("{}({}, maxlen={})"
                .format(
                    type(self).__name__,
                    list(self._dq),
                    self._dq.maxlen
                ))

    def __getitem__(self, index):
        return self._dq[index]

    def __len__(self):
        return len(self._dq)

    def __iter__(self):
        return iter(self._dq)

    def append(self, item):
        with self._lock:
            if len(self._dq) == self._dq.maxlen:
                self.dropped += 1
            self._dq.append(item)

    def extend(self, seq):
        with self._lock:
            to_drop = len(seq) + len(self._dq) - self._dq.maxlen
            if to_drop > 0:
                self.dropped += to_drop
            self._dq.extend(seq)

    @classmethod
    def from_seq(cls, maxlen, seq):
        seq = tuple(seq)
        if len(seq) > maxlen:
            raise ValueError
        bounded_list = cls(maxlen)
        bounded_list._dq = deque(seq, maxlen=maxlen)
        return bounded_list


class BoundedDict(MutableMapping):
    """A dict with a fixed max capacity."""
    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.dropped = 0
        self._dict = OrderedDict()
        self._lock = threading.Lock()

    def __repr__(self):
        return ("{}({}, maxlen={})"
                .format(
                    type(self).__name__,
                    dict(self._dict),
                    self.maxlen
                ))

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        with self._lock:
            if key in self._dict:
                del self._dict[key]
            elif len(self._dict) == self.maxlen:
                del self._dict[next(iter(self._dict.keys()))]
                self.dropped += 1
            self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    @classmethod
    def from_map(cls, maxlen, mapping):
        mapping = OrderedDict(mapping)
        if len(mapping) > maxlen:
            raise ValueError
        bounded_dict = cls(maxlen)
        bounded_dict._dict = mapping
        return bounded_dict


class SpanKind(object):
    UNSPECIFIED = 0
    SERVER = 1
    CLIENT = 2


class Span(base_span.BaseSpan):
    """A span is an individual timed event which forms a node of the trace
    tree. Each span has its name, span id and parent id. The parent id
    indicates the causal relationships between the individual spans in a
    single distributed trace. Span that does not have a parent id is called
    root span. All spans associated with a specific trace also share a common
    trace id. Spans do not need to be continuous, there can be gaps between
    two spans.

    :type name: str
    :param name: The name of the span.

    :type parent_span: :class:`~opencensus.trace.span.Span`
    :param parent_span: (Optional) Parent span.

    :type attributes: dict
    :param attributes: Collection of attributes associated with the span.
                   Attribute keys must be less than 128 bytes.
                   Attribute values must be less than 16 kilobytes.

    :type start_time: str
    :param start_time: (Optional) Start of the time interval (inclusive)
                       during which the trace data was collected from the
                       application.

    :type end_time: str
    :param end_time: (Optional) End of the time interval (inclusive) during
                     which the trace data was collected from the application.

    :type span_id: int
    :param span_id: Identifier for the span, unique within a trace.

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

    :type context_tracer: :class:`~opencensus.trace.tracers.context_tracer.
                                 ContextTracer`
    :param context_tracer: The tracer that holds a stack of spans. If this is
                           not None, then when exiting a span, use the end_span
                           method in the tracer class to finish a span. If no
                           tracer is passed in, then just finish the span using
                           the finish method in the Span class.

    :type span_kind: int
    :param span_kind: (Optional) Highly recommended flag that denotes the type
                        of span (valid values defined by :class:
                        `opencensus.trace.span.SpanKind`)
    """

    def __init__(
            self,
            name,
            parent_span=None,
            attributes=None,
            start_time=None,
            end_time=None,
            span_id=None,
            stack_trace=None,
            annotations=None,
            message_events=None,
            links=None,
            status=None,
            same_process_as_parent_span=None,
            context_tracer=None,
            span_kind=SpanKind.UNSPECIFIED):
        self.name = name
        self.parent_span = parent_span
        self.start_time = start_time
        self.end_time = end_time

        if span_id is None:
            span_id = generate_span_id()

        if attributes is None:
            self.attributes = BoundedDict(MAX_NUM_ATTRIBUTES)
        else:
            self.attributes = BoundedDict.from_map(
                MAX_NUM_ATTRIBUTES, attributes)

        # Do not manipulate spans directly using the methods in Span Class,
        # make sure to use the Tracer.
        if parent_span is None:
            parent_span = base.NullContextManager()

        if annotations is None:
            self.annotations = BoundedList(MAX_NUM_ANNOTATIONS)
        else:
            self.annotations = BoundedList.from_seq(MAX_NUM_LINKS, annotations)

        if message_events is None:
            self.message_events = BoundedList(MAX_NUM_MESSAGE_EVENTS)
        else:
            self.message_events = BoundedList.from_seq(
                MAX_NUM_LINKS, message_events)

        if links is None:
            self.links = BoundedList(MAX_NUM_LINKS)
        else:
            self.links = BoundedList.from_seq(MAX_NUM_LINKS, links)

        if status is None:
            self.status = status_module.Status.as_ok()
        else:
            self.status = status

        self.span_id = span_id
        self.stack_trace = stack_trace
        self.same_process_as_parent_span = same_process_as_parent_span
        self._child_spans = []
        self.context_tracer = context_tracer
        self.span_kind = span_kind
        for callback in Span._on_create_callbacks:
            callback(self)

    _on_create_callbacks = []

    @staticmethod
    def on_create(callback):
        Span._on_create_callbacks.append(callback)

    @property
    def children(self):
        """The child spans of the current span."""
        return self._child_spans

    def span(self, name='child_span'):
        """Create a child span for the current span and append it to the child
        spans list.

        :type name: str
        :param name: (Optional) The name of the child span.

        :rtype: :class: `~opencensus.trace.span.Span`
        :returns: A child Span to be added to the current span.
        """
        child_span = Span(name, parent_span=self)
        self._child_spans.append(child_span)
        return child_span

    def add_attribute(self, attribute_key, attribute_value):
        """Add attribute to span.

        :type attribute_key: str
        :param attribute_key: Attribute key.

        :type attribute_value:str
        :param attribute_value: Attribute value.
        """
        self.attributes[attribute_key] = attribute_value

    def add_annotation(self, description, **attrs):
        """Add an annotation to span.

        :type description: str
        :param description: A user-supplied message describing the event.
                        The maximum length for the description is 256 bytes.

        :type attrs: kwargs
        :param attrs: keyworded arguments e.g. failed=True, name='Caching'
        """
        self.annotations.append(time_event.Annotation(
            datetime.utcnow(),
            description,
            attributes_module.Attributes(attrs)
        ))

    def add_message_event(self, message_event):
        """Add a message event to this span.

        :type message_event: :class:`opencensus.trace.time_event.MessageEvent`
        :param message_event: The message event to attach to this span.
        """
        self.message_events.append(message_event)

    def add_link(self, link):
        """Add a Link.

        :type link: :class: `~opencensus.trace.link.Link`
        :param link: A Link object.
        """
        if isinstance(link, link_module.Link):
            self.links.append(link)
        else:
            raise TypeError("Type Error: received {}, but requires Link.".
                            format(type(link).__name__))

    def set_status(self, status):
        """Sets span status.

        :type code: :class: `~opencensus.trace.status.Status`
        :param code: A Status object.
        """
        if isinstance(status, status_module.Status):
            self.status = status
        else:
            raise TypeError("Type Error: received {}, but requires Status.".
                            format(type(status).__name__))

    def start(self):
        """Set the start time for a span."""
        self.start_time = utils.to_iso_str()

    def finish(self):
        """Set the end time for a span."""
        self.end_time = utils.to_iso_str()

    def __iter__(self):
        """Iterate through the span tree."""
        for span in chain(*(map(iter, self.children))):
            yield span
        yield self

    def __enter__(self):
        """Start a span."""
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        if traceback is not None:
            self.stack_trace =\
                stack_trace_module.StackTrace.from_traceback(traceback)
        if exception_value is not None:
            self.status = status_module.Status.from_exception(exception_value)
        if self.context_tracer is not None:
            self.context_tracer.end_span()
            return

        self.finish()


def format_span_json(span):
    """Helper to format a Span in JSON format.

    :type span: :class:`~opencensus.trace.span.Span`
    :param span: A Span to be transferred to JSON format.

    :rtype: dict
    :returns: Formatted Span.
    """
    span_json = {
        'displayName': utils.get_truncatable_str(span.name),
        'spanId': span.span_id,
        'startTime': span.start_time,
        'endTime': span.end_time,
        'childSpanCount': len(span._child_spans)
    }

    parent_span_id = None

    if span.parent_span is not None:
        parent_span_id = span.parent_span.span_id

    if parent_span_id is not None:
        span_json['parentSpanId'] = parent_span_id

    if span.attributes:
        span_json['attributes'] = attributes_module.Attributes(
            span.attributes).format_attributes_json()

    if span.stack_trace is not None:
        span_json['stackTrace'] = span.stack_trace.format_stack_trace_json()

    formatted_time_events = []
    if span.annotations:
        formatted_time_events.extend(
            {'time': aa.timestamp,
             'annotation': aa.format_annotation_json()}
            for aa in span.annotations)
    if span.message_events:
        formatted_time_events.extend(
            {'time': aa.timestamp,
             'message_event': aa.format_message_event_json()}
            for aa in span.message_events)
    if formatted_time_events:
        span_json['timeEvents'] = {
            'timeEvent': formatted_time_events
        }

    if span.links:
        span_json['links'] = {
            'link': [
                link.format_link_json() for link in span.links]
        }

    if span.status is not None:
        span_json['status'] = span.status.format_status_json()

    if span.same_process_as_parent_span is not None:
        span_json['sameProcessAsParentSpan'] = \
            span.same_process_as_parent_span

    return span_json
