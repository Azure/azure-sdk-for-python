# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from azure.core.tracing import tracing_context
from azure.core.tracing import AbstractSpan


class TestContext(unittest.TestCase):
    def test_get_context_class(self):
        slot = tracing_context._get_context_class("temp", 1)
        assert slot.get() == 1
        slot.set(2)
        assert slot.get() == 2

    def test_current_span(self):
        assert tracing_context.current_span.get() is None
        val = mock.Mock(spec=AbstractSpan)
        tracing_context.current_span.set(val)
        assert tracing_context.current_span.get() == val

    def test_tracing_impl(self):
        assert tracing_context.tracing_impl.get() is None
        val = AbstractSpan
        tracing_context.tracing_impl.set(val)
        assert tracing_context.tracing_impl.get() == val

    def test_with_current_context(self):
        from threading import Thread
        mock_impl = AbstractSpan
        tracing_context.tracing_impl.set(mock_impl)
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
