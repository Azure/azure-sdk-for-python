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
    from typing import Any, Callable
    from typing_extensions import Protocol
else:
    Protocol = object

try:
    import contextvars
except ImportError:
    contextvars = None


class ContextProtocol(Protocol):
    """
     Implements set and get variables in a thread safe way.
     """

    def __init__(self, name, default, lock):
        # type: (string, Any, threading.Lock) -> None
        pass

    def clear(self):
        # type: () -> None
        """Reset the value to the default value"""
        pass

    def get(self):
        # type: () -> Any
        """Get the stored value."""
        pass

    def set(self, value):
        # type: (Any) -> None
        """Set the value in the context."""
        pass


class _AsyncContext(object):
    """
    Uses contextvars to set and get variables globally in a thread safe way.
    """

    def __init__(self, name, default, lock):
        self.name = name
        self.contextvar = contextvars.ContextVar(name)
        self.default = default if callable(default) else (lambda: default)
        self.lock = lock

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
        with self.lock:
            self.contextvar.set(value)


class _ThreadLocalContext(object):
    """
    Uses thread local storage to set and get variables globally in a thread safe way.
    """
    _thread_local = threading.local()

    def __init__(self, name, default, lock):
        # type: (str, Any, threading.Lock) -> None
        self.name = name
        self.default = default if callable(default) else (lambda: default)
        self.lock = lock

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
        with self.lock:
            setattr(self._thread_local, self.name, value)


class TracingContext:
    _lock = threading.Lock()

    def __init__(self):
        # type: () -> None
        self.current_span = TracingContext._get_context_class("current_span", None)

    def with_current_context(self, func):
        # type: (Callable[[Any], Any]) -> Any
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

    @classmethod
    def _get_context_class(cls, name, default_val):
        # type: (str, Any) -> ContextProtocol
        """
        Returns an instance of the the context class that stores the variable.
        :param name: The key to store the variable in the context class
        :param default_val: The default value of the variable if unset
        :return: An instance that implements the context protocol class
        """
        context_class = _AsyncContext if contextvars else _ThreadLocalContext
        return context_class(name, default_val, cls._lock)


tracing_context = TracingContext()
