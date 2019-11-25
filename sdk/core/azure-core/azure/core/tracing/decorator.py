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

from .common import change_context, get_function_and_class_name
from ..settings import settings

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Callable, Any


def distributed_trace(func=None, name_of_span=None):
    # type: (Callable, str) -> Callable[[Any], Any]
    """Decorator to apply to function to get traced automatically.

    Span will use the func name or "name_of_span".

    :param callable func: A function to decorate
    :param str name_of_span: The span name to replace func name if necessary
    """
    if func is None:
        return functools.partial(distributed_trace, name_of_span=name_of_span)

    @functools.wraps(func)
    def wrapper_use_tracer(*args, **kwargs):
        # type: (Any, Any) -> Any
        merge_span = kwargs.pop('merge_span', False)
        passed_in_parent = kwargs.pop("parent_span", None)

        span_impl_type = settings.tracing_implementation()
        if span_impl_type is None:
            return func(*args, **kwargs) # type: ignore

        # Merge span is parameter is set, but only if no explicit parent are passed
        if merge_span and not passed_in_parent:
            return func(*args, **kwargs) # type: ignore

        with change_context(passed_in_parent):
            name = name_of_span or get_function_and_class_name(func, *args)  # type: ignore
            with span_impl_type(name=name):
                return func(*args, **kwargs) # type: ignore

    return wrapper_use_tracer
