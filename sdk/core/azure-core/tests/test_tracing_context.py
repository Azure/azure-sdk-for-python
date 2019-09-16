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
from tracing_common import ContextHelper
import os


class TestContext(unittest.TestCase):
    def test_current_span(self):
        with ContextHelper():
            assert not tracing_context.current_span.get()
            val = mock.Mock(spec=AbstractSpan)
            tracing_context.current_span.set(val)
            assert tracing_context.current_span.get() == val
            tracing_context.current_span.clear()
            assert not tracing_context.current_span.get()

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
