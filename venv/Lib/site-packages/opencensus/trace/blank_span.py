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

from opencensus.trace import base_span
from opencensus.trace.span_context import generate_span_id
from opencensus.trace.tracers import base


class BlankSpan(base_span.BaseSpan):
    """A BlankSpan is an individual timed event which forms a node of the trace
    tree. All operations are no-op.

    :type name: str
    :param name: The name of the span.

    :type parent_span: :class:`~opencensus.trace.blank_span.BlankSpan`
    :param parent_span: (Optional) Parent span.

    :type status: :class: `~opencensus.trace.status.Status`
    :param status: (Optional) An optional final status for this span.

    :type context_tracer: :class:`~opencensus.trace.tracers.noop_tracer.
                                 NoopTracer`
    :param context_tracer: The tracer that holds a stack of spans. If this is
                           not None, then when exiting a span, use the end_span
                           method in the tracer class to finish a span. If no
                           tracer is passed in, then just finish the span using
                           the finish method in the Span class.
    """

    def __init__(
            self,
            name=None,
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
            span_kind=None):
        self.name = name
        self.parent_span = parent_span
        self.start_time = start_time
        self.end_time = end_time

        self.span_id = generate_span_id()
        self.parent_span = base.NullContextManager()

        self.attributes = {}
        self.stack_trace = stack_trace
        self.annotations = annotations
        self.message_events = message_events
        self.links = []
        self.status = status
        self.same_process_as_parent_span = same_process_as_parent_span
        self._child_spans = []
        self.context_tracer = context_tracer
        self.span_kind = span_kind

    @staticmethod
    def on_create(callback):
        pass

    @property
    def children(self):
        """The child spans of the current BlankSpan."""
        return list()

    def span(self, name='child_span'):
        """Create a child span for the current span and append it to the child
        spans list.

        :type name: str
        :param name: (Optional) The name of the child span.

        :rtype: :class: `~opencensus.trace.blankspan.BlankSpan`
        :returns: A child Span to be added to the current span.
        """
        child_span = BlankSpan(name, parent_span=self)
        self._child_spans.append(child_span)
        return child_span

    def add_attribute(self, attribute_key, attribute_value):
        """No-op implementation of this method.

        :type attribute_key: str
        :param attribute_key: Attribute key.

        :type attribute_value:str
        :param attribute_value: Attribute value.
        """
        pass

    def add_annotation(self, description, **attrs):
        """No-op implementation of this method.

        :type description: str
        :param description: A user-supplied message describing the event.
                        The maximum length for the description is 256 bytes.

        :type attrs: kwargs
        :param attrs: keyworded arguments e.g. failed=True, name='Caching'
        """
        pass

    def add_message_event(self, message_event):
        """No-op implementation of this method.

        :type message_event: :class:`opencensus.trace.time_event.MessageEvent`
        :param message_event: The message event to attach to this span.
        """
        pass

    def add_link(self, link):
        """No-op implementation of this method.

        :type link: :class: `~opencensus.trace.link.Link`
        :param link: A Link object.
        """
        pass

    def set_status(self, status):
        """No-op implementation of this method.

        :type code: :class: `~opencensus.trace.status.Status`
        :param code: A Status object.
        """
        pass

    def start(self):
        """No-op implementation of this method."""
        pass

    def finish(self):
        """No-op implementation of this method."""
        pass

    def __iter__(self):
        """Iterate through the span tree."""
        yield self

    def __enter__(self):
        """Start a span."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""
        pass
