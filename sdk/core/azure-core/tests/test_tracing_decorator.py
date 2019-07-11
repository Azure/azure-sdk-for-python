# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import sys
import os
from azure.core.tracing import common, AbstractSpan
from azure.core.tracing.context import tracing_context
from azure.core.settings import settings
from azure.core.tracing.ext.opencensus_wrapper import OpencensusSpanWrapper
from opencensus.trace import tracer as tracer_module
from opencensus.trace.samplers import AlwaysOnSampler


class ContextHelper(object):
    def __init__(self, environ={}):
        self.orig_tracer = OpencensusSpanWrapper.get_current_tracer()
        self.orig_current_span = OpencensusSpanWrapper.get_current_span()
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.orig_sdk_context_tracing_impl = tracing_context.tracing_impl.get()
        self.os_env = mock.patch.dict(os.environ, environ)

    def __enter__(self):
        self.orig_tracer = OpencensusSpanWrapper.get_current_tracer()
        self.orig_current_span = OpencensusSpanWrapper.get_current_span()
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.orig_sdk_context_tracing_impl = tracing_context.tracing_impl.get()
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        OpencensusSpanWrapper.set_current_tracer(self.orig_tracer)
        OpencensusSpanWrapper.set_current_span(self.orig_current_span)
        tracing_context.current_span.set(self.orig_sdk_context_span)
        tracing_context.tracing_impl.set(self.orig_sdk_context_tracing_impl)
        self.os_env.stop()


class TestCommon(unittest.TestCase):
    def test_get_opencensus_wrapper_if_opencensus_is_imported(self):
        opencensus = sys.modules["opencensus"]
        del sys.modules["opencensus"]
        assert common.get_opencensus_wrapper_if_opencensus_is_imported() == None
        sys.modules["opencensus"] = opencensus
        assert (
            common.get_opencensus_wrapper_if_opencensus_is_imported()
            is OpencensusSpanWrapper
        )

    def test_set_span_context(self):
        with ContextHelper(environ={"AZURE_SDK_TRACING_IMPLEMENTATION": "opencensus"}):
            wrapper = settings.tracing_implementation()
            assert tracing_context.current_span.get() is None
            assert wrapper.get_current_span() is None
            parent = OpencensusSpanWrapper()
            common.set_span_contexts(parent)
            assert parent.span_instance == wrapper.get_current_span()
            assert tracing_context.current_span.get() == parent

    def test_get_parent(self):
        with ContextHelper():
            opencensus = sys.modules["opencensus"]
            del sys.modules["opencensus"]

            parent, orig_tracing_context, orig_span_inst = common.get_parent()
            assert orig_span_inst is None
            assert parent is None
            assert orig_tracing_context is None

            sys.modules["opencensus"] = opencensus
            parent, orig_tracing_context, orig_span_inst = common.get_parent()
            assert orig_span_inst is None
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"
            assert orig_tracing_context is None

            tracer = tracer_module.Tracer(sampler=AlwaysOnSampler())
            parent, orig_tracing_context, orig_span_inst = common.get_parent()
            assert orig_span_inst is None
            assert parent.span_instance.name == "azure-sdk-for-python-first_parent_span"
            assert orig_tracing_context is None
            parent.finish()

            some_span = tracer.start_span(name="some_span")
            new_parent, orig_tracing_context, orig_span_inst = common.get_parent()
            assert orig_span_inst == some_span
            assert new_parent.span_instance.name == "some_span"
            assert orig_tracing_context is None

            should_be_old_parent, orig_tracing_context, orig_span_inst = common.get_parent(
                parent_span=parent.span_instance
            )
            assert orig_span_inst == some_span
            assert should_be_old_parent.span_instance == parent.span_instance
            assert orig_tracing_context is None

    def test_should_use_trace(self):
        with ContextHelper(environ={"AZURE_TRACING_ONLY_PROPAGATE": "yes"}):
            parent_span = OpencensusSpanWrapper()
            assert common.should_use_trace(parent_span) == False
            assert common.should_use_trace(None) == False
        parent_span = OpencensusSpanWrapper()
        assert common.should_use_trace(parent_span)
        assert common.should_use_trace(None) == False

class TestDecorator(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
