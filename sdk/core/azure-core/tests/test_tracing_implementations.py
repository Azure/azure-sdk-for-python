# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.tracing.ext.opencensus_wrapper import OpencensusWrapper
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.common.utils import timestamp_to_microseconds
import os
import time


class ContextHelper(object):
    def __init__(self, environ={}):
        self.orig_tracer = OpencensusWrapper.get_current_tracer()
        self.orig_current_span = OpencensusWrapper.get_current_span()
        self.os_env = mock.patch.dict(os.environ, environ)

    def __enter__(self):
        self.orig_tracer = OpencensusWrapper.get_current_tracer()
        self.orig_current_span = OpencensusWrapper.get_current_span()
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpencensusWrapper.set_current_tracer(self.orig_tracer)
        OpencensusWrapper.set_current_span(self.orig_current_span)
        self.os_env.stop()


class TestOpencensusWrapper(unittest.TestCase):
    def test_span_passed_in(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            with tracer.start_span(name="parent") as parent:
                wrapped_span = OpencensusWrapper(parent)
            assert wrapped_span.span_instance.name == "parent"
            assert (
                wrapped_span.span_instance.context_tracer.trace_id
                == tracer.span_context.trace_id
            )
            wrapped_span.finish()
            tracer.finish()

    def test_no_span_passed_in_with_no_environ(self):
        with ContextHelper():
            tracer = OpencensusWrapper.get_current_tracer()
            wrapped_span = OpencensusWrapper()
            assert wrapped_span.span_instance.name == "parent_span"
            assert (
                wrapped_span.span_instance.context_tracer.span_context.trace_id
                == tracer.span_context.trace_id
            )
            wrapped_span.finish()

    def test_no_span_passed_in_with_environ(self):
        with ContextHelper(environ={"APPINSIGHTS_INSTRUMENTATIONKEY": "instrumentation_key"}) as ctx:
            assert os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] == "instrumentation_key"
            wrapped_span = OpencensusWrapper()
            assert wrapped_span.span_instance.name == "parent_span"
            tracer = OpencensusWrapper.get_current_tracer()
            assert (
                wrapped_span.tracer.span_context.trace_id
                == tracer.span_context.trace_id
            )
            assert (
                not wrapped_span.span_instance.context_tracer.span_context.trace_id
                == ctx.orig_tracer.span_context.trace_id
            )
            assert isinstance(tracer.exporter, AzureExporter)
            wrapped_span.finish()

    def test_no_span_but_in_trace(self):
        with ContextHelper():
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            wrapped_span = OpencensusWrapper()
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
            wrapped_class = OpencensusWrapper()
            child = wrapped_class.span()
            assert child.span_instance.name == "child_span"
            assert child.tracer.span_context.trace_id == tracer.span_context.trace_id
            assert len(wrapped_class.span_instance.children) == 1
            assert wrapped_class.span_instance.children[0] == child.span_instance

    def test_start_finish(self):
        with ContextHelper() as ctx:
            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            wrapped_class = OpencensusWrapper()
            wrapped_class.start()
            time.sleep(1)
            wrapped_class.finish()
            latency = timestamp_to_microseconds(
                wrapped_class.span_instance.end_time
            ) - timestamp_to_microseconds(wrapped_class.span_instance.start_time)
            latency = int(latency / 10000)
            assert latency == 100

    def test_to_and_from_header(self):
        with ContextHelper() as ctx:
            wrapped_class = OpencensusWrapper()
            og_header = {
                "traceparent": "00-2578531519ed94423ceae67588eff2c9-231ebdc614cb9ddd-01"
            }
            tracer = wrapped_class.from_header(og_header)
            assert tracer.span_context.trace_id == "2578531519ed94423ceae67588eff2c9"
            headers = wrapped_class.to_header({})
            assert headers == og_header

    def test_end_tracer(self):
        with ContextHelper() as ctx:
            tracer = mock.Mock(spec=tracer_module.Tracer)
            OpencensusWrapper.end_tracer(tracer)
            assert tracer.finish.called


if __name__ == "__main__":
    unittest.main()
