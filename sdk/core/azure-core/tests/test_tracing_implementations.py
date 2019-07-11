# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.tracing.ext.opencensus_wrapper import OpencensusSpanWrapper
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.ext.azure.trace_exporter import AzureExporter
import os


class ContextHelper(object):
    def __init__(self, environ={}):
        self.orig_tracer = OpencensusSpanWrapper.get_current_tracer()
        self.orig_current_span = OpencensusSpanWrapper.get_current_span()
        self.os_env = mock.patch.dict(os.environ, environ)

    def __enter__(self):
        self.orig_tracer = OpencensusSpanWrapper.get_current_tracer()
        self.orig_current_span = OpencensusSpanWrapper.get_current_span()
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpencensusSpanWrapper.set_current_tracer(self.orig_tracer)
        OpencensusSpanWrapper.set_current_span(self.orig_current_span)
        self.os_env.stop()


class TestOpencensusWrapper(unittest.TestCase):
    def test_span_passed_in(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            with tracer.start_span(name="parent") as parent:
                wrapped_span = OpencensusSpanWrapper(parent)
            assert wrapped_span.span_instance.name == "parent"
            assert (
                wrapped_span.span_instance.context_tracer.trace_id
                == tracer.span_context.trace_id
            )
            wrapped_span.finish()
            tracer.finish()

    def test_no_span_passed_in_with_no_environ(self):
        with ContextHelper() as ctx:
            tracer = OpencensusSpanWrapper.get_current_tracer()
            wrapped_span = OpencensusSpanWrapper()
            assert wrapped_span.span_instance.name == "parent_span"
            assert (
                wrapped_span.span_instance.context_tracer.span_context.trace_id
                == tracer.span_context.trace_id
            )
            assert ctx.orig_tracer == tracer
            wrapped_span.finish()

    def test_no_span_but_in_trace(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            wrapped_span = OpencensusSpanWrapper()
            assert wrapped_span.span_instance.name == "parent_span"
            assert (
                wrapped_span.span_instance.context_tracer.trace_id
                == tracer.span_context.trace_id
            )
            wrapped_span.finish()
            tracer.finish()

    def test_span(self):
        with ContextHelper() as ctx:
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            wrapped_class = OpencensusSpanWrapper()
            child = wrapped_class.span()
            assert child.span_instance.name == "child_span"
            assert (
                child.span_instance.parent_span.context_tracer.trace_id
                == tracer.span_context.trace_id
            )
            assert len(wrapped_class.span_instance.children) == 1
            assert wrapped_class.span_instance.children[0] == child.span_instance

    def test_start_finish(self):
        with ContextHelper() as ctx:
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent = OpencensusSpanWrapper()
            wrapped_class = parent.span()
            assert wrapped_class.span_instance.start_time is None
            assert wrapped_class.span_instance.end_time is None
            wrapped_class.start()
            wrapped_class.finish()
            assert wrapped_class.span_instance.start_time is not None
            assert wrapped_class.span_instance.end_time is not None
            parent.finish()

    def test_to_and_from_header(self):
        with ContextHelper() as ctx:
            og_header = {
                "traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"
            }
            tracer = OpencensusSpanWrapper.from_header(og_header)
            assert tracer.span_context.trace_id == "2578531519ed94423ceae67588eff2c9"
            wrapped_class = OpencensusSpanWrapper()
            headers = wrapped_class.to_header()
            new_header = {
                "traceparent": "00-2578531519ed94423ceae67588eff2c9-{}-01".format(
                    wrapped_class.span_instance.span_id
                )
            }
            assert headers == new_header


if __name__ == "__main__":
    unittest.main()
