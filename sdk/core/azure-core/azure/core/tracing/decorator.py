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

from typing import Callable, Any, TypeVar, overload, Optional, Mapping
from typing_extensions import ParamSpec
from .common import change_context
from ..settings import settings
from ._models import TracingOptions, SpanKind
from ._tracer import default_tracer_provider, TracerProvider


P = ParamSpec("P")
T = TypeVar("T")


@overload
def distributed_trace(__func: Callable[P, T]) -> Callable[P, T]:
    pass


@overload
def distributed_trace(
    *,
    name_of_span: Optional[str] = None,
    kind: Optional["SpanKind"] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    pass


def distributed_trace(
    __func: Optional[Callable[P, T]] = None,  # pylint: disable=unused-argument
    *,
    name_of_span: Optional[str] = None,
    kind: Optional["SpanKind"] = None,
    tracing_attributes: Optional[Mapping[str, Any]] = None,
    tracer_provider: Optional[TracerProvider] = None,
    **kwargs: Any,
) -> Any:
    """Decorator to apply to function to get traced automatically.

    Span will use the func name or "name_of_span".

    Note:

    This decorator SHOULD NOT be used by application developers. It's
    intended to be called by Azure client libraries only.

    Application developers should use OpenTelemetry or other tracing libraries to
    instrument their applications.

    :param callable __func: A function to decorate
    :keyword name_of_span: The span name to replace func name if necessary
    :paramtype name_of_span: str
    :keyword kind: The kind of the span. INTERNAL by default.
    :paramtype kind: ~azure.core.tracing.SpanKind
    :keyword tracing_attributes: Attributes to add to the span.
    :paramtype tracing_attributes: Mapping[str, Any] or None
    :keyword tracer_provider: The tracer provider to use. If not provided, a default tracer provider will be used.
    :paramtype tracer_provider: ~azure.core.tracing.TracerProvider
    :return: The decorated function
    :rtype: Any
    """
    if tracing_attributes is None:
        tracing_attributes = {}
    if kind is None:
        kind = SpanKind.INTERNAL

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper_use_tracer(*args: Any, **kwargs: Any) -> T:
            merge_span = kwargs.pop("merge_span", False)
            passed_in_parent = kwargs.pop("parent_span", None)

            # Assume this will be popped in DistributedTracingPolicy.
            tracing_options: TracingOptions = kwargs.get("tracing_options", {})
            tracing_enabled = settings.tracing_enabled()

            # User can explicitly disable tracing for this request.
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return func(*args, **kwargs)

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not tracing_enabled and user_enabled is None:
                return func(*args, **kwargs)

            # Merge span is parameter is set, but only if no explicit parent are passed
            if merge_span and not passed_in_parent:
                return func(*args, **kwargs)

            # Assume this will be popped in DistributedTracingPolicy.
            func_tracing_attributes = kwargs.get("tracing_attributes", tracing_attributes)
            span_attributes = {**func_tracing_attributes, **tracing_options.get("attributes", {})}

            span_impl_type = settings.tracing_implementation()

            name = name_of_span or func.__qualname__
            if span_impl_type:
                print(span_impl_type)
                with change_context(passed_in_parent):
                    with span_impl_type(name=name, kind=kind) as span:
                        for key, value in span_attributes.items():
                            span.add_attribute(key, value)  # type: ignore
                        return func(*args, **kwargs)
            else:
                method_tracer = (
                    tracer_provider.get_tracer() if tracer_provider else default_tracer_provider.get_tracer()
                )
                if not method_tracer:
                    return func(*args, **kwargs)
                with method_tracer.start_span(
                    name=name,
                    kind=kind,
                    attributes=span_attributes,
                    record_exception=tracing_options.get("record_exception", True),
                ):
                    return func(*args, **kwargs)

        return wrapper_use_tracer

    return decorator if __func is None else decorator(__func)
