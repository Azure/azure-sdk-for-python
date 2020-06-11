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

from opencensus.trace.span_context import SpanContext
from opencensus.trace.trace_options import TraceOptions

_OPENCENSUS_TRACE_PREFIX = 'opencensus-trace'
_TRACE_ID_KEY = '{}-traceid'.format(_OPENCENSUS_TRACE_PREFIX)
_SPAN_ID_KEY = '{}-spanid'.format(_OPENCENSUS_TRACE_PREFIX)
_TRACE_OPTIONS_KEY = '{}-traceoptions'.format(_OPENCENSUS_TRACE_PREFIX)

DEFAULT_TRACE_OPTIONS = '1'


class TextFormatPropagator(object):
    """This class provides the basic utilities for extracting the trace
    information from a carrier which is a dict to form a SpanContext. And
    generating a dict using the provided SpanContext.
    """
    def from_carrier(self, carrier):
        """Generate a SpanContext object using the information in the carrier.

        :type carrier: dict
        :param carrier: The carrier which has the trace_id, span_id, options
                        information for creating a SpanContext.

        :rtype: :class:`~opencensus.trace.span_context.SpanContext`
        :returns: SpanContext generated from the carrier.
        """
        trace_id = None
        span_id = None
        trace_options = None

        for key in carrier:
            key = key.lower()
            if key == _TRACE_ID_KEY:
                trace_id = carrier[key]
            if key == _SPAN_ID_KEY:
                span_id = carrier[key]
            if key == _TRACE_OPTIONS_KEY:
                trace_options = bool(carrier[key])

        if trace_options is None:
            trace_options = DEFAULT_TRACE_OPTIONS

        return SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            trace_options=TraceOptions(trace_options),
            from_header=True)

    def to_carrier(self, span_context, carrier):
        """Inject the SpanContext fields to carrier dict.

        :type span_context:
            :class:`~opencensus.trace.span_context.SpanContext`
        :param span_context: SpanContext object.

        :type carrier: dict
        :param carrier: The carrier which holds the trace_id, span_id, options
                        information from a SpanContext.

        :rtype: dict
        :returns: The carrier which holds the span context information.
        """
        carrier[_TRACE_ID_KEY] = str(span_context.trace_id)

        if span_context.span_id is not None:
            carrier[_SPAN_ID_KEY] = str(span_context.span_id)

        carrier[_TRACE_OPTIONS_KEY] = str(
            span_context.trace_options.trace_options_byte)

        return carrier
