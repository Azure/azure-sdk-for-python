# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.tracing.context import tracing_context
from azure.core.tracing import AbstractSpan
from azure.core.settings import settings
import os


class ContextHelper(object):
    def __init__(self, environ={}, tracer_to_use=None):
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.os_env = mock.patch.dict(os.environ, environ)
        self.tracer_to_use = tracer_to_use

    def __enter__(self):
        self.orig_sdk_context_span = tracing_context.current_span.get()
        settings.tracing_implementation.set_value(self.tracer_to_use)
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        tracing_context.current_span.set(self.orig_sdk_context_span)
        settings.tracing_implementation.unset_value()
        self.os_env.stop()


class TestContext(unittest.TestCase):
    def test_get_context_class(self):
        with ContextHelper():
            slot = tracing_context._get_context_class("temp", 1)
            assert slot.get() == 1
            slot.set(2)
            assert slot.get() == 2

    def test_current_span(self):
        with ContextHelper():
            assert tracing_context.current_span.get() is None
            val = mock.Mock(spec=AbstractSpan)
            tracing_context.current_span.set(val)
            assert tracing_context.current_span.get() == val

    def test_with_current_context(self):
        with ContextHelper(tracer_to_use=mock.Mock(AbstractSpan)):
            from threading import Thread

            current_span = mock.Mock(spec=AbstractSpan)
            tracing_context.current_span.set(current_span)

            def work():
                span = tracing_context.current_span.get()
                assert span == current_span
                setattr(span, "in_worker", True)

            thread = Thread(target=tracing_context.with_current_context(work))
            thread.start()
            thread.join()

            span = tracing_context.current_span.get()
            assert span == current_span
            assert getattr(span, "in_worker", False)
