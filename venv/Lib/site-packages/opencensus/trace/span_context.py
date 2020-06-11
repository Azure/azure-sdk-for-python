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

"""SpanContext encapsulates the current context within the request's trace."""

import logging
import re
import six
import random

from opencensus.trace import trace_options as trace_options_module

_INVALID_TRACE_ID = '0' * 32
INVALID_SPAN_ID = '0' * 16

TRACE_ID_PATTERN = re.compile('[0-9a-f]{32}?')
SPAN_ID_PATTERN = re.compile('[0-9a-f]{16}?')

# Default options, don't force sampling
DEFAULT_OPTIONS = '0'


class SpanContext(object):
    """SpanContext includes 3 fields: traceId, spanId, and an trace_options flag
    which indicates whether or not the request is being traced. It contains the
    current context to be propagated to the child spans.

    :type trace_id: str
    :param trace_id: (Optional) Trace_id is a 32 digits uuid for the trace.
                     If not given, will generate one automatically.

    :type span_id: str
    :param span_id: (Optional) Identifier for the span, unique within a trace.

    :type trace_options: :class: `~opencensus.trace.trace_options.TraceOptions`
    :param trace_options: (Optional) TraceOptions indicates 8 trace options.

    :type from_header: bool
    :param from_header: (Optional) Indicates whether the trace context is
                        generated from request header.
    """
    def __init__(
            self,
            trace_id=None,
            span_id=None,
            trace_options=None,
            tracestate=None,
            from_header=False):
        if trace_id is None:
            trace_id = generate_trace_id()

        if trace_options is None:
            trace_options = trace_options_module.TraceOptions(DEFAULT_OPTIONS)

        self.from_header = from_header
        self.trace_id = self._check_trace_id(trace_id)
        self.span_id = self._check_span_id(span_id)
        self.trace_options = trace_options
        self.tracestate = tracestate

    def __repr__(self):
        """Returns a string form of the SpanContext.

        :rtype: str
        :returns: String form of the SpanContext.
        """
        fmt = '{}(trace_id={}, span_id={}, trace_options={}, tracestate={})'
        return fmt.format(
            type(self).__name__,
            self.trace_id,
            self.span_id,
            self.trace_options,
            self.tracestate,
        )

    def _check_span_id(self, span_id):
        """Check the format of the span_id to ensure it is 16-character hex
        value representing a 64-bit number. If span_id is invalid, logs a
        warning message and returns None

        :type span_id: str
        :param span_id: Identifier for the span, unique within a span.

        :rtype: str
        :returns: Span_id for the current span.
        """
        if span_id is None:
            return None
        assert isinstance(span_id, six.string_types)

        if span_id is INVALID_SPAN_ID:
            logging.warning(
                'Span_id %s is invalid (cannot be all zero)', span_id)
            self.from_header = False
            return None

        match = SPAN_ID_PATTERN.match(span_id)

        if match:
            return span_id
        else:
            logging.warning(
                'Span_id %s does not the match the '
                'required format', span_id)
            self.from_header = False
            return None

    def _check_trace_id(self, trace_id):
        """Check the format of the trace_id to ensure it is 32-character hex
        value representing a 128-bit number. If trace_id is invalid, returns a
        randomly generated trace id

        :type trace_id: str
        :param trace_id:

        :rtype: str
        :returns: Trace_id for the current context.
        """
        assert isinstance(trace_id, six.string_types)

        if trace_id is _INVALID_TRACE_ID:
            logging.warning(
                'Trace_id %s is invalid (cannot be all zero), '
                'generating a new one.', trace_id)
            self.from_header = False
            return generate_trace_id()

        match = TRACE_ID_PATTERN.match(trace_id)

        if match:
            return trace_id
        else:
            logging.warning(
                'Trace_id %s does not the match the required format,'
                'generating a new one instead.', trace_id)
            self.from_header = False
            return generate_trace_id()


def generate_span_id():
    """Return the random generated span ID for a span. Must be a 16 character
    hexadecimal encoded string

    :rtype: str
    :returns: 16 digit randomly generated hex trace id.
    """
    return '{:016x}'.format(random.getrandbits(64))


def generate_trace_id():
    """Generate a random 32 char hex trace_id.

    :rtype: str
    :returns: 32 digit randomly generated hex trace id.
    """
    return '{:032x}'.format(random.getrandbits(128))
