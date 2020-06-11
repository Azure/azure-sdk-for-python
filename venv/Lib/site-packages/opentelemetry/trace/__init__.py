# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The OpenTelemetry tracing API describes the classes used to generate
distributed traces.

The :class:`.Tracer` class controls access to the execution context, and
manages span creation. Each operation in a trace is represented by a
:class:`.Span`, which records the start, end time, and metadata associated with
the operation.

This module provides abstract (i.e. unimplemented) classes required for
tracing, and a concrete no-op :class:`.DefaultSpan` that allows applications
to use the API package alone without a supporting implementation.

To get a tracer, you need to provide the package name from which you are
calling the tracer APIs to OpenTelemetry by calling `TracerProvider.get_tracer`
with the calling module name and the version of your package.

The tracer supports creating spans that are "attached" or "detached" from the
context. New spans are "attached" to the context in that they are
created as children of the currently active span, and the newly-created span
can optionally become the new active span::

    from opentelemetry import trace

    tracer = trace.get_tracer(__name__)

    # Create a new root span, set it as the current span in context
    with tracer.start_as_current_span("parent"):
        # Attach a new child and update the current span
        with tracer.start_as_current_span("child"):
            do_work():
        # Close child span, set parent as current
    # Close parent span, set default span as current

When creating a span that's "detached" from the context the active span doesn't
change, and the caller is responsible for managing the span's lifetime::

    # Explicit parent span assignment
    child = tracer.start_span("child", parent=parent)

    try:
        do_work(span=child)
    finally:
        child.end()

Applications should generally use a single global TracerProvider, and use
either implicit or explicit context propagation consistently throughout.

.. versionadded:: 0.1.0
.. versionchanged:: 0.3.0
    `TracerProvider` was introduced and the global ``tracer`` getter was
    replaced by ``tracer_provider``.
.. versionchanged:: 0.5.0
    ``tracer_provider`` was replaced by `get_tracer_provider`,
    ``set_preferred_tracer_provider_implementation`` was replaced by
    `set_tracer_provider`.
"""

import abc
import enum
import types as python_types
import typing
from contextlib import contextmanager
from logging import getLogger

from opentelemetry.configuration import Configuration  # type: ignore
from opentelemetry.trace.status import Status
from opentelemetry.util import types

logger = getLogger(__name__)

# TODO: quarantine
ParentSpan = typing.Optional[typing.Union["Span", "SpanContext"]]


class LinkBase(abc.ABC):
    def __init__(self, context: "SpanContext") -> None:
        self._context = context

    @property
    def context(self) -> "SpanContext":
        return self._context

    @property
    @abc.abstractmethod
    def attributes(self) -> types.Attributes:
        pass


class Link(LinkBase):
    """A link to a `Span`.

    Args:
        context: `SpanContext` of the `Span` to link to.
        attributes: Link's attributes.
    """

    def __init__(
        self, context: "SpanContext", attributes: types.Attributes = None,
    ) -> None:
        super().__init__(context)
        self._attributes = attributes

    @property
    def attributes(self) -> types.Attributes:
        return self._attributes


class LazyLink(LinkBase):
    """A lazy link to a `Span`.

    Args:
        context: `SpanContext` of the `Span` to link to.
        link_formatter: Callable object that returns the attributes of the
            Link.
    """

    def __init__(
        self,
        context: "SpanContext",
        link_formatter: types.AttributesFormatter,
    ) -> None:
        super().__init__(context)
        self._link_formatter = link_formatter

    @property
    def attributes(self) -> types.Attributes:
        return self._link_formatter()


class SpanKind(enum.Enum):
    """Specifies additional details on how this span relates to its parent span.

    Note that this enumeration is experimental and likely to change. See
    https://github.com/open-telemetry/opentelemetry-specification/pull/226.
    """

    #: Default value. Indicates that the span is used internally in the
    # application.
    INTERNAL = 0

    #: Indicates that the span describes an operation that handles a remote
    # request.
    SERVER = 1

    #: Indicates that the span describes a request to some remote service.
    CLIENT = 2

    #: Indicates that the span describes a producer sending a message to a
    #: broker. Unlike client and server, there is usually no direct critical
    #: path latency relationship between producer and consumer spans.
    PRODUCER = 3

    #: Indicates that the span describes a consumer receiving a message from a
    #: broker. Unlike client and server, there is usually no direct critical
    #: path latency relationship between producer and consumer spans.
    CONSUMER = 4


class Span(abc.ABC):
    """A span represents a single operation within a trace."""

    @abc.abstractmethod
    def end(self, end_time: typing.Optional[int] = None) -> None:
        """Sets the current time as the span's end time.

        The span's end time is the wall time at which the operation finished.

        Only the first call to `end` should modify the span, and
        implementations are free to ignore or raise on further calls.
        """

    @abc.abstractmethod
    def get_context(self) -> "SpanContext":
        """Gets the span's SpanContext.

        Get an immutable, serializable identifier for this span that can be
        used to create new child spans.

        Returns:
            A :class:`.SpanContext` with a copy of this span's immutable state.
        """

    @abc.abstractmethod
    def set_attribute(self, key: str, value: types.AttributeValue) -> None:
        """Sets an Attribute.

        Sets a single Attribute with the key and value passed as arguments.
        """

    @abc.abstractmethod
    def add_event(
        self,
        name: str,
        attributes: types.Attributes = None,
        timestamp: typing.Optional[int] = None,
    ) -> None:
        """Adds an `Event`.

        Adds a single `Event` with the name and, optionally, a timestamp and
        attributes passed as arguments. Implementations should generate a
        timestamp if the `timestamp` argument is omitted.
        """

    @abc.abstractmethod
    def add_lazy_event(
        self,
        name: str,
        event_formatter: types.AttributesFormatter,
        timestamp: typing.Optional[int] = None,
    ) -> None:
        """Adds an `Event`.

        Adds a single `Event` with the name, an event formatter that calculates
        the attributes lazily and, optionally, a timestamp. Implementations
        should generate a timestamp if the `timestamp` argument is omitted.
        """

    @abc.abstractmethod
    def update_name(self, name: str) -> None:
        """Updates the `Span` name.

        This will override the name provided via :func:`Tracer.start_span`.

        Upon this update, any sampling behavior based on Span name will depend
        on the implementation.
        """

    @abc.abstractmethod
    def is_recording_events(self) -> bool:
        """Returns whether this span will be recorded.

        Returns true if this Span is active and recording information like
        events with the add_event operation and attributes using set_attribute.
        """

    @abc.abstractmethod
    def set_status(self, status: Status) -> None:
        """Sets the Status of the Span. If used, this will override the default
        Span status, which is OK.
        """

    def __enter__(self) -> "Span":
        """Invoked when `Span` is used as a context manager.

        Returns the `Span` itself.
        """
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[python_types.TracebackType],
    ) -> None:
        """Ends context manager and calls `end` on the `Span`."""

        self.end()


class TraceFlags(int):
    """A bitmask that represents options specific to the trace.

    The only supported option is the "sampled" flag (``0x01``). If set, this
    flag indicates that the trace may have been sampled upstream.

    See the `W3C Trace Context - Traceparent`_ spec for details.

    .. _W3C Trace Context - Traceparent:
        https://www.w3.org/TR/trace-context/#trace-flags
    """

    DEFAULT = 0x00
    SAMPLED = 0x01

    @classmethod
    def get_default(cls) -> "TraceFlags":
        return cls(cls.DEFAULT)

    @property
    def sampled(self) -> bool:
        return bool(self & TraceFlags.SAMPLED)


DEFAULT_TRACE_OPTIONS = TraceFlags.get_default()


class TraceState(typing.Dict[str, str]):
    """A list of key-value pairs representing vendor-specific trace info.

    Keys and values are strings of up to 256 printable US-ASCII characters.
    Implementations should conform to the `W3C Trace Context - Tracestate`_
    spec, which describes additional restrictions on valid field values.

    .. _W3C Trace Context - Tracestate:
        https://www.w3.org/TR/trace-context/#tracestate-field
    """

    @classmethod
    def get_default(cls) -> "TraceState":
        return cls()


DEFAULT_TRACE_STATE = TraceState.get_default()


def format_trace_id(trace_id: int) -> str:
    return "0x{:032x}".format(trace_id)


def format_span_id(span_id: int) -> str:
    return "0x{:016x}".format(span_id)


class SpanContext:
    """The state of a Span to propagate between processes.

    This class includes the immutable attributes of a :class:`.Span` that must
    be propagated to a span's children and across process boundaries.

    Args:
        trace_id: The ID of the trace that this span belongs to.
        span_id: This span's ID.
        trace_flags: Trace options to propagate.
        trace_state: Tracing-system-specific info to propagate.
        is_remote: True if propagated from a remote parent.
    """

    def __init__(
        self,
        trace_id: int,
        span_id: int,
        is_remote: bool,
        trace_flags: "TraceFlags" = DEFAULT_TRACE_OPTIONS,
        trace_state: "TraceState" = DEFAULT_TRACE_STATE,
    ) -> None:
        if trace_flags is None:
            trace_flags = DEFAULT_TRACE_OPTIONS
        if trace_state is None:
            trace_state = DEFAULT_TRACE_STATE
        self.trace_id = trace_id
        self.span_id = span_id
        self.trace_flags = trace_flags
        self.trace_state = trace_state
        self.is_remote = is_remote

    def __repr__(self) -> str:
        return (
            "{}(trace_id={}, span_id={}, trace_state={!r}, is_remote={})"
        ).format(
            type(self).__name__,
            format_trace_id(self.trace_id),
            format_span_id(self.span_id),
            self.trace_state,
            self.is_remote,
        )

    def is_valid(self) -> bool:
        """Get whether this `SpanContext` is valid.

        A `SpanContext` is said to be invalid if its trace ID or span ID is
        invalid (i.e. ``0``).

        Returns:
            True if the `SpanContext` is valid, false otherwise.
        """
        return (
            self.trace_id != INVALID_TRACE_ID
            and self.span_id != INVALID_SPAN_ID
        )


class DefaultSpan(Span):
    """The default Span that is used when no Span implementation is available.

    All operations are no-op except context propagation.
    """

    def __init__(self, context: "SpanContext") -> None:
        self._context = context

    def get_context(self) -> "SpanContext":
        return self._context

    def is_recording_events(self) -> bool:
        return False

    def end(self, end_time: typing.Optional[int] = None) -> None:
        pass

    def set_attribute(self, key: str, value: types.AttributeValue) -> None:
        pass

    def add_event(
        self,
        name: str,
        attributes: types.Attributes = None,
        timestamp: typing.Optional[int] = None,
    ) -> None:
        pass

    def add_lazy_event(
        self,
        name: str,
        event_formatter: types.AttributesFormatter,
        timestamp: typing.Optional[int] = None,
    ) -> None:
        pass

    def update_name(self, name: str) -> None:
        pass

    def set_status(self, status: Status) -> None:
        pass


INVALID_SPAN_ID = 0x0000000000000000
INVALID_TRACE_ID = 0x00000000000000000000000000000000
INVALID_SPAN_CONTEXT = SpanContext(
    trace_id=INVALID_TRACE_ID,
    span_id=INVALID_SPAN_ID,
    is_remote=False,
    trace_flags=DEFAULT_TRACE_OPTIONS,
    trace_state=DEFAULT_TRACE_STATE,
)
INVALID_SPAN = DefaultSpan(INVALID_SPAN_CONTEXT)


class TracerProvider(abc.ABC):
    @abc.abstractmethod
    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: str = "",
    ) -> "Tracer":
        """Returns a `Tracer` for use by the given instrumentation library.

        For any two calls it is undefined whether the same or different
        `Tracer` instances are returned, even for different library names.

        This function may return different `Tracer` types (e.g. a no-op tracer
        vs.  a functional tracer).

        Args:
            instrumenting_module_name: The name of the instrumenting module
                (usually just ``__name__``).

                This should *not* be the name of the module that is
                instrumented but the name of the module doing the instrumentation.
                E.g., instead of ``"requests"``, use
                ``"opentelemetry.ext.http_requests"``.

            instrumenting_library_version: Optional. The version string of the
                instrumenting library.  Usually this should be the same as
                ``pkg_resources.get_distribution(instrumenting_library_name).version``.
        """


class DefaultTracerProvider(TracerProvider):
    """The default TracerProvider, used when no implementation is available.

    All operations are no-op.
    """

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: str = "",
    ) -> "Tracer":
        # pylint:disable=no-self-use,unused-argument
        return DefaultTracer()


class Tracer(abc.ABC):
    """Handles span creation and in-process context propagation.

    This class provides methods for manipulating the context, creating spans,
    and controlling spans' lifecycles.
    """

    # Constant used to represent the current span being used as a parent.
    # This is the default behavior when creating spans.
    CURRENT_SPAN = DefaultSpan(INVALID_SPAN_CONTEXT)

    @abc.abstractmethod
    def get_current_span(self) -> "Span":
        """Gets the currently active span from the context.

        If there is no current span, return a placeholder span with an invalid
        context.

        Returns:
            The currently active :class:`.Span`, or a placeholder span with an
            invalid :class:`.SpanContext`.
        """

    @abc.abstractmethod
    def start_span(
        self,
        name: str,
        parent: ParentSpan = CURRENT_SPAN,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: typing.Optional[types.Attributes] = None,
        links: typing.Sequence[Link] = (),
        start_time: typing.Optional[int] = None,
        set_status_on_exception: bool = True,
    ) -> "Span":
        """Starts a span.

        Create a new span. Start the span without setting it as the current
        span in this tracer's context.

        By default the current span will be used as parent, but an explicit
        parent can also be specified, either a `Span` or a `SpanContext`. If
        the specified value is `None`, the created span will be a root span.

        The span can be used as context manager. On exiting, the span will be
        ended.

        Example::

            # tracer.get_current_span() will be used as the implicit parent.
            # If none is found, the created span will be a root instance.
            with tracer.start_span("one") as child:
                child.add_event("child's event")

        Applications that need to set the newly created span as the current
        instance should use :meth:`start_as_current_span` instead.

        Args:
            name: The name of the span to be created.
            parent: The span's parent. Defaults to the current span.
            kind: The span's kind (relationship to parent). Note that is
                meaningful even if there is no parent.
            attributes: The span's attributes.
            links: Links span to other spans
            start_time: Sets the start time of a span
            set_status_on_exception: Only relevant if the returned span is used
                in a with/context manager. Defines wether the span status will
                be automatically set to UNKNOWN when an uncaught exception is
                raised in the span with block. The span status won't be set by
                this mechanism if it was previousy set manually.

        Returns:
            The newly-created span.
        """

    @contextmanager  # type: ignore
    @abc.abstractmethod
    def start_as_current_span(
        self,
        name: str,
        parent: ParentSpan = CURRENT_SPAN,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: typing.Optional[types.Attributes] = None,
        links: typing.Sequence[Link] = (),
    ) -> typing.Iterator["Span"]:
        """Context manager for creating a new span and set it
        as the current span in this tracer's context.

        On exiting the context manager stops the span and set its parent as the
        current span.

        Example::

            with tracer.start_as_current_span("one") as parent:
                parent.add_event("parent's event")
                with tracer.start_as_current_span("two") as child:
                    child.add_event("child's event")
                    tracer.get_current_span()  # returns child
                tracer.get_current_span()      # returns parent
            tracer.get_current_span()          # returns previously active span

        This is a convenience method for creating spans attached to the
        tracer's context. Applications that need more control over the span
        lifetime should use :meth:`start_span` instead. For example::

            with tracer.start_as_current_span(name) as span:
                do_work()

        is equivalent to::

            span = tracer.start_span(name)
            with tracer.use_span(span, end_on_exit=True):
                do_work()

        Args:
            name: The name of the span to be created.
            parent: The span's parent. Defaults to the current span.
            kind: The span's kind (relationship to parent). Note that is
                meaningful even if there is no parent.
            attributes: The span's attributes.
            links: Links span to other spans

        Yields:
            The newly-created span.
        """

    @contextmanager  # type: ignore
    @abc.abstractmethod
    def use_span(
        self, span: "Span", end_on_exit: bool = False
    ) -> typing.Iterator[None]:
        """Context manager for controlling a span's lifetime.

        Set the given span as the current span in this tracer's context.

        On exiting the context manager set the span that was previously active
        as the current span (this is usually but not necessarily the parent of
        the given span). If ``end_on_exit`` is ``True``, then the span is also
        ended when exiting the context manager.

        Args:
            span: The span to start and make current.
            end_on_exit: Whether to end the span automatically when leaving the
                context manager.
        """


class DefaultTracer(Tracer):
    """The default Tracer, used when no Tracer implementation is available.

    All operations are no-op.
    """

    def get_current_span(self) -> "Span":
        # pylint: disable=no-self-use
        return INVALID_SPAN

    def start_span(
        self,
        name: str,
        parent: ParentSpan = Tracer.CURRENT_SPAN,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: typing.Optional[types.Attributes] = None,
        links: typing.Sequence[Link] = (),
        start_time: typing.Optional[int] = None,
        set_status_on_exception: bool = True,
    ) -> "Span":
        # pylint: disable=unused-argument,no-self-use
        return INVALID_SPAN

    @contextmanager  # type: ignore
    def start_as_current_span(
        self,
        name: str,
        parent: ParentSpan = Tracer.CURRENT_SPAN,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: typing.Optional[types.Attributes] = None,
        links: typing.Sequence[Link] = (),
    ) -> typing.Iterator["Span"]:
        # pylint: disable=unused-argument,no-self-use
        yield INVALID_SPAN

    @contextmanager  # type: ignore
    def use_span(
        self, span: "Span", end_on_exit: bool = False
    ) -> typing.Iterator[None]:
        # pylint: disable=unused-argument,no-self-use
        yield


_TRACER_PROVIDER = None


def get_tracer(
    instrumenting_module_name: str, instrumenting_library_version: str = ""
) -> "Tracer":
    """Returns a `Tracer` for use by the given instrumentation library.

    This function is a convenience wrapper for
    opentelemetry.trace.get_tracer_provider().get_tracer
    """
    return get_tracer_provider().get_tracer(
        instrumenting_module_name, instrumenting_library_version
    )


def set_tracer_provider(tracer_provider: TracerProvider) -> None:
    """Sets the current global :class:`~.TracerProvider` object."""
    global _TRACER_PROVIDER  # pylint: disable=global-statement
    _TRACER_PROVIDER = tracer_provider


def get_tracer_provider() -> TracerProvider:
    """Gets the current global :class:`~.TracerProvider` object."""
    global _TRACER_PROVIDER  # pylint: disable=global-statement

    if _TRACER_PROVIDER is None:
        _TRACER_PROVIDER = (
            Configuration().tracer_provider  # type: ignore # pylint: disable=no-member
        )

    return _TRACER_PROVIDER  # type: ignore
