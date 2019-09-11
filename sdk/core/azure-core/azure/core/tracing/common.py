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
    from typing import Any, Optional, Union, Callable, List


def get_function_and_class_name(func, *args):
    # type: (Callable, List[Any]) -> str
    """
    Given a function and its unamed arguments, returns class_name.function_name. It assumes the first argument
    is `self`. If there are no arguments then it only returns the function name.

    :param func: the function passed in
    :type func: `collections.abc.Callable`
    :param args: List of arguments passed into the function
    :type args: List[Any]
    """
    try:
        return func.__qualname__
    except AttributeError:
        if args:
            return "{}.{}".format(args[0].__class__.__name__, func.__name__)  # pylint: disable=protected-access
        return func.__name__


def set_span_contexts(wrapped_span, span_instance=None):
    # type: (Union[AbstractSpan, None], Optional[AbstractSpan]) -> None
    """
    Set the sdk context and the implementation context. `span_instance` will be used to set the implementation context
    ONLY if wrapped_span is None. Otherwise, will use internal implementation span.

    :param wrapped_span: The `AbstractSpan` to set as the sdk context
    :type wrapped_span: `azure.core.tracing.abstract_span.AbstractSpan`
    :param span_instance: The span to set as the current span for the implementation context if wrapped_span is None.
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is None:
        return

    # Store the current wrapped span into our SDK context
    tracing_context.current_span.set(wrapped_span)
    if wrapped_span is None:
        span_impl_type.set_current_span(span_instance)
    else:
        span_impl_type.set_current_span(wrapped_span.span_instance)


def get_parent_span(parent_span=None):
    # type: (Any) -> Optional[AbstractSpan]
    """
    Returns the current span so that the function's span will be its child. It will create a new span if there is
    no current span in any of the context.

    The only possiblity to get None is if there is no tracing plugin available.

    Algorithm is:
    - Return a SDK span if parent_span exists
    - ELSE return the SDK current span if exists
    - ELSE return the a new SDK span based on implementation if exists
    - ELSE creates a new implementation and SDK span and return it

    If this method creates a span, it will NOT store it in SDK context.

    :param parent_span: The parent_span arg that the user passes into the top level function
    :returns: the parent_span of the function to be traced
    :rtype: `azure.core.tracing.abstract_span.AbstractSpan`
    """
    span_impl_type = settings.tracing_implementation()  # type: Type[AbstractSpan]
    if span_impl_type is None:
        return None

    if parent_span is not None:
        return span_impl_type(parent_span)  # This span is NOT stored in SDK context yet.

    orig_wrapped_span = tracing_context.current_span.get()  # type: AbstractSpan
    if orig_wrapped_span is not None:
        return orig_wrapped_span

    current_span = span_impl_type.get_current_span()
    if current_span is not None:
        return span_impl_type(current_span)

    # Everything is None, SDK has no span and customer didn't create one. Create the base one for the customer
    return span_impl_type(name="azure-sdk-for-python-first_parent_span")
