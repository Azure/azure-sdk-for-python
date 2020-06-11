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

import logging
import re

from opencensus.trace.span_context import SpanContext
from opencensus.trace.trace_options import TraceOptions

_TRACE_CONTEXT_HEADER_NAME = 'X-Cloud-Trace-Context'
_TRACE_CONTEXT_HEADER_FORMAT = r'([0-9a-f]{32})(\/([\d]{0,20}))?(;o=(\d+))?'
_TRACE_CONTEXT_HEADER_RE = re.compile(_TRACE_CONTEXT_HEADER_FORMAT)
_TRACE_ID_DELIMETER = '/'
_SPAN_ID_DELIMETER = ';'


class GoogleCloudFormatPropagator(object):
    """This class is for converting the trace header in google cloud format
    and generate a SpanContext, or converting a SpanContext to a google cloud
    format header. Later we will add implementation for supporting other
    format like binary format and zipkin, opencensus format.
    """
    def from_header(self, header):
        """Generate a SpanContext object using the trace context header.
        The value of enabled parsed from header is int. Need to convert to
        bool.

        :type header: str
        :param header: Trace context header which was extracted from the HTTP
                       request headers.

        :rtype: :class:`~opencensus.trace.span_context.SpanContext`
        :returns: SpanContext generated from the trace context header.
        """
        if header is None:
            return SpanContext()

        try:
            match = re.search(_TRACE_CONTEXT_HEADER_RE, header)
        except TypeError:
            logging.warning(
                'Header should be str, got %s. Cannot parse the header.',
                header.__class__.__name__)
            raise

        if match:
            trace_id = match.group(1)
            span_id = match.group(3)
            trace_options = match.group(5)

            if trace_options is None:
                trace_options = 1

            if span_id:
                span_id = '{:016x}'.format(int(span_id))

            span_context = SpanContext(
                trace_id=trace_id,
                span_id=span_id,
                trace_options=TraceOptions(trace_options),
                from_header=True)
            return span_context
        else:
            logging.warning(
                'Cannot parse the header %s, generate a new context instead.',
                header)
            return SpanContext()

    def from_headers(self, headers):
        """Generate a SpanContext object using the trace context header.

        :type headers: dict
        :param headers: HTTP request headers.

        :rtype: :class:`~opencensus.trace.span_context.SpanContext`
        :returns: SpanContext generated from the trace context header.
        """
        if headers is None:
            return SpanContext()
        header = headers.get(_TRACE_CONTEXT_HEADER_NAME)
        if header is None:
            return SpanContext()
        return self.from_header(header)

    def to_header(self, span_context):
        """Convert a SpanContext object to header string.

        :type span_context:
            :class:`~opencensus.trace.span_context.SpanContext`
        :param span_context: SpanContext object.

        :rtype: str
        :returns: A trace context header string in google cloud format.
        """
        trace_id = span_context.trace_id
        span_id = span_context.span_id
        trace_options = span_context.trace_options.trace_options_byte

        header = '{}/{};o={}'.format(
            trace_id,
            int(span_id, 16),
            int(trace_options))
        return header

    def to_headers(self, span_context):
        """Convert a SpanContext object to HTTP request headers.

        :type span_context:
            :class:`~opencensus.trace.span_context.SpanContext`
        :param span_context: SpanContext object.

        :rtype: dict
        :returns: Trace context headers in google cloud format.
        """
        return {
            _TRACE_CONTEXT_HEADER_NAME: self.to_header(span_context),
        }
