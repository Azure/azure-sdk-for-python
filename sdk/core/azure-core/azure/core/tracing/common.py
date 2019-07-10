import functools
from os import environ
import re

from azure.core.trace.context import tracing_context
from azure.core.trace.abstract_span import AbstractSpan
from azure.core.settings import settings


def is_opencensus_installed():
    try:
        import opencensus

        return True
    except ImportError:
        return False


def get_opencensus_wrapper():
    from azure.core.tracing.ext.opencensus import OpencensusWrapper

    return OpencensusWrapper


def set_span_contexts(span, span_instance=None, wrapper_class=None):
    # type: (AbstractSpan, AbstractSpan) -> None
    tracing_context.current_span.set(span)
    if span is not None or (span_instance is not None and wrapper_class is not None):
        span_instance = span_instance or span.span_instance
        span = wrapper_class or span
        span.set_current_span(span_instance)


def get_parent(kwargs, *args):
    # type: (Any) -> Tuple(Any, Any)
    parent_span = kwargs.pop("parent_span", None)  # type: AbstractSpan
    wrapper_class = tracing_context.convert_tracing_impl(
        settings.tracing_implementation()
    )
    orig_context = tracing_context.current_span.get()

    if parent_span is None:
        parent_span = orig_context
    else:
        wrapper_class = wrapper_class or get_opencensus_wrapper()
        parent_span = wrapper_class(parent_span)

    if wrapper_class is None and is_opencensus_installed():
        wrapper_class = get_opencensus_wrapper()

    if parent_span is None and wrapper_class is not None:
        current_span = wrapper_class.get_current_span()
        parent_span = (
            wrapper_class(span=current_span)
            if current_span
            else wrapper_class(name="azure-sdk-for-python-first_parent_span")
        )

    original_span_instance = None
    if wrapper_class is not None:
        original_span_instance = wrapper_class.get_current_span()

    return parent_span, orig_context, original_span_instance


def should_use_trace(parent_span):
    # type: (AbstractSpan, List[str], str)
    only_propagate = settings.tracing_should_only_propagate()
    return parent_span and not only_propagate
