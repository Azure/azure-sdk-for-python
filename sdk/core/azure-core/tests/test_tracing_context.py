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
import os


class ContextHelper(object):
    def __init__(self, environ={}):
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.orig_sdk_context_tracing_impl = tracing_context.tracing_impl.get()
        self.os_env = mock.patch.dict(os.environ, environ)

    def __enter__(self):
        self.orig_sdk_context_span = tracing_context.current_span.get()
        self.orig_sdk_context_tracing_impl = tracing_context.tracing_impl.get()
        self.os_env.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        tracing_context.current_span.set(self.orig_sdk_context_span)
        tracing_context.tracing_impl.set(self.orig_sdk_context_tracing_impl)
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

    def test_tracing_impl(self):
        with ContextHelper():
            assert tracing_context.tracing_impl.get() is None
            val = AbstractSpan
            tracing_context.tracing_impl.set(val)
            assert tracing_context.tracing_impl.get() == val

    def test_with_current_context(self):
        with ContextHelper():
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


if __name__ == "__main__":
    unittest.main()
