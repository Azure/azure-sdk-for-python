import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from azure.core.trace.context import tracing_context
from azure.core.trace.abstract_span import AbstractSpan


class TestContext(unittest.TestCase):
    def test_register(self):
        slot = tracing_context.register_slot("temp", 1)
        assert slot.get() == 1
        slot.set(2)
        assert slot.get() == 2

    def test_current_span(self):
        assert tracing_context.current_span.get() == None
        val = "Some Span"
        tracing_context.current_span.set(val)
        assert tracing_context.current_span.get() == val

    def test_tracing_impl(self):
        assert tracing_context.tracing_impl.get() == None
        val = "Some Span"
        tracing_context.tracing_impl.set(val)
        assert tracing_context.tracing_impl.get() == val

    def test_with_current_context(self):
        from threading import Thread
        mock_impl = mock.Mock(spec=AbstractSpan)
        tracing_context.tracing_impl.set(mock_impl)
        current_span = {"val": 0}
        tracing_context.current_span.set(current_span)

        def work():
            span = tracing_context.current_span.get()
            assert span == {"val": 0}
            span["val"] = 1

        thread = Thread(target=tracing_context.with_current_context(work))
        thread.start()
        thread.join()

        span = tracing_context.current_span.get()
        assert span == {"val": 1}
