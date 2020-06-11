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

import re

from opencensus.trace.span_context import SpanContext
from opencensus.trace.trace_options import TraceOptions
from opencensus.trace.propagation.tracestate_string_format \
    import TracestateStringFormatter

_TRACEPARENT_HEADER_NAME = 'traceparent'
_TRACESTATE_HEADER_NAME = 'tracestate'
_TRACEPARENT_HEADER_FORMAT = \
    '^[ \t]*([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})' + \
    '(-.*)?[ \t]*$'
_TRACEPARENT_HEADER_FORMAT_RE = re.compile(_TRACEPARENT_HEADER_FORMAT)


class TraceContextPropagator(object):
    """Propagator for processing the trace context HTTP header format."""

    def from_headers(self, headers):
        """Generate a SpanContext object using the W3C Distributed Tracing headers.

        :type headers: dict
        :param headers: HTTP request headers.

        :rtype: :class:`~opencensus.trace.span_context.SpanContext`
        :returns: SpanContext generated from the trace context header.
        """
        if headers is None:
            return SpanContext()

        header = headers.get(_TRACEPARENT_HEADER_NAME)
        if header is None:
            return SpanContext()

        match = re.search(_TRACEPARENT_HEADER_FORMAT_RE, header)
        if not match:
            return SpanContext()

        version = match.group(1)
        trace_id = match.group(2)
        span_id = match.group(3)
        trace_options = match.group(4)

        if trace_id == '0' * 32 or span_id == '0' * 16:
            return SpanContext()

        if version == '00':
            if match.group(5):
                return SpanContext()
        if version == 'ff':
            return SpanContext()

        span_context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            trace_options=TraceOptions(trace_options),
            from_header=True)

        header = headers.get(_TRACESTATE_HEADER_NAME)
        if header is None:
            return span_context
        try:
            tracestate = TracestateStringFormatter().from_string(header)
            if tracestate.is_valid():
                span_context.tracestate = \
                    TracestateStringFormatter().from_string(header)
        except ValueError:
            pass
        return span_context

    def to_headers(self, span_context):
        """Convert a SpanContext object to W3C Distributed Tracing headers,
        using version 0.

        :type span_context:
            :class:`~opencensus.trace.span_context.SpanContext`
        :param span_context: SpanContext object.

        :rtype: dict
        :returns: W3C Distributed Tracing headers.
        """
        trace_id = span_context.trace_id
        span_id = span_context.span_id
        trace_options = span_context.trace_options.enabled

        # Convert the trace options
        trace_options = '01' if trace_options else '00'

        headers = {
            _TRACEPARENT_HEADER_NAME: '00-{}-{}-{}'.format(
                trace_id,
                span_id,
                trace_options
            ),
        }
        tracestate = span_context.tracestate
        if tracestate:
            headers[_TRACESTATE_HEADER_NAME] = \
                TracestateStringFormatter().to_string(tracestate)
        return headers
