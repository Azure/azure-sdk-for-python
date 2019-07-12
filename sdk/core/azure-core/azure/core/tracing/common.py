# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
from os import environ
import re

from azure.core.tracing.context import tracing_context
from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.settings import settings, get_opencensus_span


def set_span_contexts(wrapped_span, span_instance=None):
    # type: (AbstractSpan, AbstractSpan) -> None
    tracing_context.current_span.set(wrapped_span)
    impl_wrapper = settings.tracing_implementation()
    if wrapped_span is not None:
        span_instance = wrapped_span.span_instance
    if impl_wrapper is not None:
        impl_wrapper.set_current_span(span_instance)


def get_parent(kwargs):
    # type: (Any) -> Tuple(AbstractSpan, AbstractSpan, Any)
    """Returns the parent span that of the span that represents the function and the spans before that parent span"""
    parent_span = kwargs.pop("parent_span", None)  # type: AbstractSpan
    orig_wrapped_span = tracing_context.current_span.get()

    wrapper_class = settings.tracing_implementation()
    if wrapper_class is None:
        return None, orig_wrapped_span, None
    original_wrapper_span_instance = wrapper_class.get_current_span()
    # parent span is given, get from my context, get from the implementation context or make our own
    parent_span = orig_wrapped_span if parent_span is None else wrapper_class(parent_span)
    if parent_span is None:
        current_span = wrapper_class.get_current_span()
        parent_span = (
            wrapper_class(span=current_span)
            if current_span
            else wrapper_class(name="azure-sdk-for-python-first_parent_span")
        )

    return parent_span, orig_wrapped_span, original_wrapper_span_instance


def should_use_trace(parent_span):
    # type: (AbstractSpan) -> bool
    """Given Parent Span Returns whether the function should be traced"""
    only_propagate = settings.tracing_should_only_propagate()
    return bool(parent_span and not only_propagate)
