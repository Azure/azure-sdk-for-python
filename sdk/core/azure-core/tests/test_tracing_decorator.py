# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from azure.core.tracing import common
from azure.core.tracing import tracing_context, AbstractSpan
from azure.core.settings import settings
from opencensus.trace import tracer as tracer_module


class TestCommon(unittest.TestCase):
    def test_set_span_context(self):
        wrapper = settings.tracing_implementation()
        assert tracing_context.current_span.get() is None
        assert wrapper.get_current_span() is None
        parent = OpencenusWrapper()
        common.set_span_contexts(parent)
        assert parent.span_instance == wrapper.get_current_span()
        assert tracing_context.current_span.get() == parent

    def test_get_parent(self):
        parent, orig_tracing_context, orig_span_inst = common.get_parent()
        assert orig_span_inst is None


if __name__ == "__main__":
    unittest.main()
