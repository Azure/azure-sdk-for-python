import threading
from os import environ
from typing import List
import six

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Callable

try:
    import contextvars
except ImportError:
    contextvars = None

__all__ = ["tracing_context"]


class ContextProtocol:
    def __init__(self, name, default, lock):
        # type: (string, Any, threading.Lock) -> None
        pass

    def clear(self):
        # type: () -> None
        pass

    def get(self):
        # type: () -> Any
        pass

    def set(self, value):
        # type: (Any) -> None
        pass


class ContextAsyc:
    def __init__(self, name, default, lock):
        self.name = name
        self.contextvar = contextvars.ContextVar(name)
        self.default = default if callable(default) else (lambda: default)
        self.lock = lock

    def clear(self):
        self.contextvar.set(self.default())

    def get(self):
        try:
            return self.contextvar.get()
        except LookupError:
            value = self.default()
            self.set(value)
            return value

    def set(self, value):
        with self.lock:
            self.contextvar.set(value)


class Context:
    _thread_local = threading.local()

    def __init__(self, name, default, lock):
        self.name = name
        self.default = default if callable(default) else (lambda: default)
        self.lock = lock

    def clear(self):
        setattr(self._thread_local, self.name, self.default())

    def get(self):
        try:
            return getattr(self._thread_local, self.name)
        except AttributeError:
            value = self.default()
            self.set(value)
            return value

    def set(self, value):
        with self.lock:
            setattr(self._thread_local, self.name, value)


class TracingContext:
    _lock = threading.Lock()
    _context = ContextAsyc if contextvars else Context

    def __init__(self):
        # type: () -> None
        self.current_span = TracingContext.register_slot("current_span", None)
        self.tracing_impl = TracingContext.register_slot("tracing_impl", None)

    def with_current_context(self, func):
        # type: (Callable[Any, Any]) -> Any
        wrapped_span = tracing_context.current_span.get()
        wrapper_class = self.tracing_impl.get()
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
    def register_slot(cls, name, default_val):
        # type: (str, Any) -> ContextProtocol
        return cls._context(name, default_val, cls._lock)


tracing_context = TracingContext()
