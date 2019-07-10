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
from azure.core.settings import settings


def _get_opencensus_wrapper():
    # type: () -> OpencensusWrapper
    """Returns the OpencensusWrapper if opencensus is installed else returns None"""
    try:
        from azure.core.tracing.ext.opencensus_wrapper  import OpencensusWrapper

        return OpencensusWrapper
    except ImportError:
        return None


def set_span_contexts(wrapped_span, span_instance=None, impl_wrapper=None):
    # type: (AbstractSpan, AbstractSpan) -> None
    tracing_context.current_span.set(wrapped_span)
    impl_wrapper = impl_wrapper or wrapped_span
    tracing_context.tracing_impl.set(impl_wrapper.__class__)
    if wrapped_span is not None or (
        span_instance is not None and impl_wrapper is not None
    ):
        span_instance = span_instance or wrapped_span.span_instance
        impl_wrapper.set_current_span(span_instance)


def get_parent(kwargs, *args):
    # type: (Any) -> Tuple(Any, Any, Any)
    """Returns the parent span that of the span that represents the function and the spans before that parent span"""
    parent_span = kwargs.pop("parent_span", None)  # type: AbstractSpan
    orig_wrapped_span = tracing_context.current_span.get()

    # wrapper class get from tracing_context, settings or assume OpencensusWrapper if opencesus is installed
    wrapper_class = (
        tracing_context.tracing_impl.get()
        or settings.tracing_implementation()
        or _get_opencensus_wrapper()
    )
    if wrapper_class is None:
        return None, orig_wrapped_span, None

    # parent span is given, get from my context, get from the implementation context or make our own
    parent_span = (
        orig_wrapped_span if parent_span is None else wrapper_class(parent_span)
    )
    if parent_span is None:
        current_span = wrapper_class.get_current_span()
        parent_span = (
            wrapper_class(span=current_span)
            if current_span
            else wrapper_class(name="azure-sdk-for-python-first_parent_span")
        )

    return parent_span, orig_wrapped_span, wrapper_class.get_current_span()


def should_use_trace(parent_span):
    # type: (AbstractSpan, List[str], str)
    """Given Parent Span Returns whether the function should be traced"""
    only_propagate = settings.tracing_should_only_propagate()
    return parent_span and not only_propagate
