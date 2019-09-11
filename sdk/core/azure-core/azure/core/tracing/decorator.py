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
"""The decorator to apply if you want the given function traced."""

import functools

import azure.core.tracing.common as common
from azure.core.settings import settings
from azure.core.tracing.context import tracing_context

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Callable, Any


def distributed_trace(func=None, name_of_span=None):
    # type: (Callable, str) -> Callable[[Any], Any]
    if func is None:
        return functools.partial(distributed_trace, name_of_span=name_of_span)

    @functools.wraps(func)
    def wrapper_use_tracer(*args, **kwargs):
        # type: (Any, Any) -> Any
        span_impl_type = settings.tracing_implementation()
        if span_impl_type is None:
            return func(*args, **kwargs) # type: ignore

        # Tracing mode

        # Get original context
        original_wrapped_span = tracing_context.current_span.get()  # type: AbstractSpan
        original_span_instance = span_impl_type.get_current_span()

        passed_in_parent = kwargs.pop("parent_span", None)
        parent_span = common.get_parent_span(passed_in_parent)

        if parent_span is not None and original_wrapped_span is None:
            common.set_span_contexts(parent_span)
            name = name_of_span or common.get_function_and_class_name(func, *args)  # type: ignore
            child = parent_span.span(name=name)
            child.start()
            common.set_span_contexts(child)
            try:
                ans = func(*args, **kwargs) # type: ignore
            finally:
                child.finish()
                # This test means "get_parent" created the span, so I need to finish it.
                if original_wrapped_span is None and passed_in_parent is None and original_span_instance is None:
                    parent_span.finish()
                common.set_span_contexts(original_wrapped_span, span_instance=original_span_instance)
        else:
            ans = func(*args, **kwargs) # type: ignore
        return ans

    return wrapper_use_tracer
