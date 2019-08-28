# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""The context for the azure.core.tracing. Holds global variables in a thread and async safe way."""

import threading
from azure.core.settings import settings

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Callable, Optional, Type, Union
    from typing_extensions import Protocol
else:
    Protocol = object

try:
    import contextvars
except ImportError:
    pass


class ContextProtocol(Protocol):
    """
     Implements set and get variables in a thread safe way.
     """

    def __init__(self, name, default):  # pylint: disable=super-init-not-called
        # type: (str, Any) -> None
        pass

    def clear(self):
        # type: () -> None
        """Reset the value to the default value"""

    def get(self):
        # type: () -> Any
        """Get the stored value."""

    def set(self, value):
        # type: (Any) -> None
        """Set the value in the context."""


class _AsyncContext(object):
    """
    Uses contextvars to set and get variables globally in a thread safe way.
    """

    def __init__(self, name, default):
        # type: (str, Any) -> None
        self.name = name
        self.contextvar = contextvars.ContextVar(name)  # type: contextvars.ContextVar
        self.default = default if callable(default) else (lambda: default)

    def clear(self):
        # type: () -> None
        """Reset the value to the default value"""
        self.contextvar.set(self.default())

    def get(self):
        # type: () -> Any
        """Get the stored value."""
        try:
            return self.contextvar.get()
        except LookupError:
            value = self.default()
            self.set(value)
            return value

    def set(self, value):
        # type: (Any) -> None
        """Set the value in the context."""
        self.contextvar.set(value)


class _ThreadLocalContext(object):
    """
    Uses thread local storage to set and get variables globally in a thread safe way.
    """

    _thread_local = threading.local()

    def __init__(self, name, default):
        # type: (str, Any) -> None
        self.name = name
        self.default = default if callable(default) else (lambda: default)

    def clear(self):
        # type: () -> None
        """Reset the value to the default value"""
        setattr(self._thread_local, self.name, self.default())

    def get(self):
        # type: () -> Any
        """Get the stored value."""
        try:
            return getattr(self._thread_local, self.name)
        except AttributeError:
            value = self.default()
            self.set(value)
            return value

    def set(self, value):
        # type: (Any) -> None
        """Set the value in the context."""
        setattr(self._thread_local, self.name, value)


class TracingContext(object):
    def __init__(self):
        # type: () -> None
        try:
            self.current_span = _AsyncContext("current_span", None)  # type: Union[_AsyncContext, _ThreadLocalContext]
        except NameError:
            self.current_span = _ThreadLocalContext("current_span", None)

    def with_current_context(self, func):
        # type: (Callable) -> Any
        """
        Passes the current spans to the new context the function will be run in.
        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
        wrapped_span = tracing_context.current_span.get()
        wrapper_class = settings.tracing_implementation()
        if wrapper_class is not None:
            current_impl_span = wrapper_class.get_current_span()
            current_impl_tracer = wrapper_class.get_current_tracer()

        def call_with_current_context(*args, **kwargs):
            if wrapper_class is not None:
                wrapper_class.set_current_span(current_impl_span)
                wrapper_class.set_current_tracer(current_impl_tracer)
                current_span = wrapped_span or wrapper_class(current_impl_span)
                self.current_span.set(current_span)
            return func(*args, **kwargs)

        return call_with_current_context


tracing_context = TracingContext()
