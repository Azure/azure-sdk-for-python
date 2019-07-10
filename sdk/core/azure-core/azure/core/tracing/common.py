from os import environ
import re

from azure.core.trace.context import tracing_context
from azure.core.trace.abstract_span import AbstractSpan
from azure.core.settings import settings


def is_opencensus_installed():
    # type: () -> bool
    """Returns true if opencensus is installed else returns false"""
    try:
        import opencensus

        return True
    except ImportError:
        return False


def get_opencensus_wrapper():
    # type: () -> OpencensusWrapper
    """Returns the OpencensusWrapper if opencensus is installed else returns None"""
    if is_opencensus_installed():
        from azure.core.tracing.ext.opencensus import OpencensusWrapper

        return OpencensusWrapper
    else:
        return None


def set_span_contexts(wrapped_span, span_instance=None, impl_wrapper=None):
    # type: (AbstractSpan, AbstractSpan) -> None
    tracing_context.current_span.set(wrapped_span)
    impl_wrapper = impl_wrapper or wrapped_span
    tracing_context.tracing_impl.set(impl_wrapper)
    if wrapped_span is not None or (
        span_instance is not None and impl_wrapper is not None
    ):
        span_instance = span_instance or wrapped_span.span_instance
        impl_wrapper.set_current_span(span_instance)


def get_parent(kwargs, *args):
    # type: (Any) -> Tuple(Any, Any)
    """"""
    parent_span = kwargs.pop("parent_span", None)  # type: AbstractSpan
    orig_wrapped_span = tracing_context.current_span.get()

    # wrapper class get from tracing_context, settings or assume OpencensusWrapper if opencesus is installed
    wrapper_class = (
        tracing_context.tracing_impl.get()
        or settings.tracing_implementation()
        or get_opencensus_wrapper()
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
