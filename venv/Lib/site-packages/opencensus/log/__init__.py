# Copyright 2019, OpenCensus Authors
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

from collections import namedtuple
from copy import copy
import logging

from opencensus.trace import execution_context


_meta_logger = logging.getLogger(__name__)

TRACE_ID_KEY = 'traceId'
SPAN_ID_KEY = 'spanId'
SAMPLING_DECISION_KEY = 'traceSampled'

LogAttrs = namedtuple('LogAttrs', ['trace_id', 'span_id', 'sampling_decision'])
ATTR_DEFAULTS = LogAttrs("00000000000000000000000000000000",
                         "0000000000000000", False)


def get_log_attrs():
    """Get logging attributes from the opencensus context.

    :rtype: :class:`LogAttrs`
    :return: The current span's trace ID, span ID, and sampling decision.
    """
    try:
        tracer = execution_context.get_opencensus_tracer()
        if tracer is None:
            raise RuntimeError
    except Exception:  # noqa
        _meta_logger.error("Failed to get opencensus tracer")
        return ATTR_DEFAULTS

    try:
        trace_id = tracer.span_context.trace_id
        if trace_id is None:
            trace_id = ATTR_DEFAULTS.trace_id
    except Exception:  # noqa
        _meta_logger.error("Failed to get opencensus trace ID")
        trace_id = ATTR_DEFAULTS.trace_id

    try:
        span_id = tracer.span_context.span_id
        if span_id is None:
            span_id = ATTR_DEFAULTS.span_id
    except Exception:  # noqa
        _meta_logger.error("Failed to get opencensus span ID")
        span_id = ATTR_DEFAULTS.span_id

    try:
        sampling_decision = tracer.span_context.trace_options.get_enabled()
        if sampling_decision is None:
            sampling_decision = ATTR_DEFAULTS.sampling_decision
    except AttributeError:
        sampling_decision = ATTR_DEFAULTS.sampling_decision
    except Exception:  # noqa
        _meta_logger.error("Failed to get opencensus sampling decision")
        sampling_decision = ATTR_DEFAULTS.sampling_decision

    return LogAttrs(trace_id, span_id, sampling_decision)


def _set_extra_attrs(extra):
    trace_id, span_id, sampling_decision = get_log_attrs()
    extra.setdefault(TRACE_ID_KEY, trace_id)
    extra.setdefault(SPAN_ID_KEY, span_id)
    extra.setdefault(SAMPLING_DECISION_KEY, sampling_decision)


# See
# https://docs.python.org/3.7/library/logging.html#loggeradapter-objects,
# https://docs.python.org/3.7/howto/logging-cookbook.html#context-info
class TraceLoggingAdapter(logging.LoggerAdapter):
    """Adapter to add opencensus context attrs to records."""
    def process(self, msg, kwargs):
        kwargs = copy(kwargs)
        if self.extra:
            extra = copy(self.extra)
        else:
            extra = {}
        extra.update(kwargs.get('extra', {}))
        _set_extra_attrs(extra)
        kwargs['extra'] = extra

        return (msg, kwargs)


# This is the idiomatic way to stack logger customizations, see
# https://docs.python.org/3.7/library/logging.html#logging.getLoggerClass
class TraceLogger(logging.getLoggerClass()):
    """Logger class that adds opencensus context attrs to records."""
    def makeRecord(self, *args, **kwargs):
        try:
            extra = args[8]
            if extra is None:
                extra = {}
                args = tuple(list(args[:8]) + [extra] + list(args[9:]))
        except IndexError:  # pragma: NO COVER
            extra = kwargs.setdefault('extra', {})
            if extra is None:
                kwargs['extra'] = extra
        _set_extra_attrs(extra)
        return super(TraceLogger, self).makeRecord(*args, **kwargs)
