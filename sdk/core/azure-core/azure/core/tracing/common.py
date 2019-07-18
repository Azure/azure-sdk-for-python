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
"""Common functions shared by both the sync and the async decorators."""

from azure.core.tracing.context import tracing_context
from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.settings import settings


try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional


def set_span_contexts(wrapped_span, span_instance=None):
    # type: (AbstractSpan, Optional[AbstractSpan]) -> None
    """
    Set the sdk context and the implementation context. `span_instance` will be used to set the implementation context
    if passed in else will use `wrapped_span.span_instance`.

    :param wrapped_span: The `AbstractSpan` to set as the sdk context
    :type wrapped_span: `azure.core.tracing.abstract_span.AbstractSpan`
    :param span_instance: The span to set as the current span for the implementation context
    """
    tracing_context.current_span.set(wrapped_span)
    impl_wrapper = settings.tracing_implementation()
    if wrapped_span is not None:
        span_instance = wrapped_span.span_instance
    if impl_wrapper is not None:
        impl_wrapper.set_current_span(span_instance)


def get_parent_span(parent_span):
    # type: (Any) -> Tuple(AbstractSpan, AbstractSpan, Any)
    """
    Returns the current span so that the function's span will be its child. It will create a new span if there is
    no current span in any of the context.

    :param parent_span: The parent_span arg that the user passes into the top level function
    :returns: the parent_span of the function to be traced
    :rtype: `azure.core.tracing.abstract_span.AbstractSpan`
    """
    wrapper_class = settings.tracing_implementation()
    if wrapper_class is None:
        return None

    orig_wrapped_span = tracing_context.current_span.get()
    # parent span is given, get from my context, get from the implementation context or make our own
    parent_span = orig_wrapped_span if parent_span is None else wrapper_class(parent_span)
    if parent_span is None:
        current_span = wrapper_class.get_current_span()
        parent_span = (
            wrapper_class(span=current_span)
            if current_span
            else wrapper_class(name="azure-sdk-for-python-first_parent_span")
        )

    return parent_span


def should_use_trace(parent_span):
    # type: (AbstractSpan) -> bool
    """Given Parent Span Returns whether the function should be traced"""
    only_propagate = settings.tracing_should_only_propagate()
    return bool(parent_span and not only_propagate)
