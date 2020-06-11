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

from opencensus.common.runtime_context import RuntimeContext
from opencensus.trace.tracers import noop_tracer

_attrs_slot = RuntimeContext.register_slot('attrs', lambda: {})
_current_span_slot = RuntimeContext.register_slot('current_span', None)
_exporter_slot = RuntimeContext.register_slot('is_exporter', False)
_tracer_slot = RuntimeContext.register_slot('tracer', noop_tracer.NoopTracer())


def is_exporter():
    return RuntimeContext.is_exporter


def set_is_exporter(is_exporter):
    RuntimeContext.is_exporter = is_exporter


def get_opencensus_tracer():
    """Get the opencensus tracer from runtime context."""
    return RuntimeContext.tracer


def set_opencensus_tracer(tracer):
    """Add the tracer to runtime context."""
    RuntimeContext.tracer = tracer


def set_opencensus_attr(attr_key, attr_value):
    attrs = RuntimeContext.attrs.copy()
    attrs[attr_key] = attr_value
    RuntimeContext.attrs = attrs


def set_opencensus_attrs(attrs):
    RuntimeContext.attrs = attrs


def get_opencensus_attr(attr_key):
    return RuntimeContext.attrs.get(attr_key)


def get_opencensus_attrs():
    return RuntimeContext.attrs


def get_current_span():
    return RuntimeContext.current_span


def set_current_span(current_span):
    RuntimeContext.current_span = current_span


def get_opencensus_full_context():
    attrs = RuntimeContext.attrs
    current_span = RuntimeContext.current_span
    tracer = RuntimeContext.tracer
    return tracer, current_span, attrs


def set_opencensus_full_context(tracer, span, attrs):
    set_opencensus_tracer(tracer)
    set_current_span(span)
    set_opencensus_attrs(attrs or {})


def clean():
    _attrs_slot.clear()
    _current_span_slot.clear()
    _tracer_slot.clear()


def clear():
    """Clear the context, used in test."""
    clean()
