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


def distributed_trace_async(func=None, name_of_span=None):
    # type: (Callable, str) -> Callable[[Any], Any]
    if func is None:
        return functools.partial(distributed_trace_async, name_of_span=name_of_span)

    @functools.wraps(func)
    async def wrapper_use_tracer(*args, **kwargs):
        # type: (Any, Any) -> Any
        passed_in_parent = kwargs.pop("parent_span", None)
        orig_wrapped_span = tracing_context.current_span.get()
        wrapper_class = settings.tracing_implementation()
        original_span_instance = None
        if wrapper_class is not None:
            original_span_instance = wrapper_class.get_current_span()
        parent_span = common.get_parent_span(passed_in_parent)
        ans = None
        if parent_span is not None and orig_wrapped_span is None:
            common.set_span_contexts(parent_span)
            name = name_of_span or common.get_function_and_class_name(func, *args)  # type: ignore
            child = parent_span.span(name=name)
            child.start()
            common.set_span_contexts(child)
            ans = await func(*args, **kwargs)   # type: ignore
            child.finish()
            common.set_span_contexts(parent_span)
            if orig_wrapped_span is None and passed_in_parent is None and original_span_instance is None:
                parent_span.finish()
            common.set_span_contexts(orig_wrapped_span, span_instance=original_span_instance)
        else:
            ans = await func(*args, **kwargs)   # type: ignore
        return ans

    return wrapper_use_tracer
