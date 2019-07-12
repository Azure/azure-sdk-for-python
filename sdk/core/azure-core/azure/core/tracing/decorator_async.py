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
import functools

import azure.core.tracing.common as common


def distributed_tracing_decorator_async(func):
    # type: (Callable[[Any], Any]) -> Callable[[Any], Any]
    @functools.wraps(func)
    async def wrapper_use_tracer(self, *args, **kwargs):
        # type: (Any) -> Any
        parent_span, original_span_from_sdk_context, original_span_instance = common.get_parent_and_original_contexts(
            kwargs
        )
        ans = None
        if common.should_use_trace(parent_span):
            common.set_span_contexts(parent_span)
            name = self.__class__.__name__ + "." + func.__name__
            child = parent_span.span(name=name)
            child.start()
            common.set_span_contexts(child)
            ans = await func(self, *args, **kwargs)
            child.finish()
            common.set_span_contexts(parent_span)
            if getattr(parent_span, "was_created_by_azure_sdk", False):
                parent_span.finish()
            common.set_span_contexts(original_span_from_sdk_context, span_instance=original_span_instance)
        else:
            ans = await func(self, *args, **kwargs)
        return ans

    return wrapper_use_tracer
