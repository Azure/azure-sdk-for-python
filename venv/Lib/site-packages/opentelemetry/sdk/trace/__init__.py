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


import abc
import atexit
import logging
import random
import threading
from contextlib import contextmanager
from types import TracebackType
from typing import Iterator, Optional, Sequence, Tuple, Type

from opentelemetry import context as context_api
from opentelemetry import trace as trace_api
from opentelemetry.sdk import util
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util import BoundedDict, BoundedList
from opentelemetry.sdk.util.instrumentation import InstrumentationInfo
from opentelemetry.trace import SpanContext, sampling
from opentelemetry.trace.propagation import SPAN_KEY
from opentelemetry.trace.status import Status, StatusCanonicalCode
from opentelemetry.util import time_ns, types

logger = logging.getLogger(__name__)

MAX_NUM_ATTRIBUTES = 32
MAX_NUM_EVENTS = 128
MAX_NUM_LINKS = 32


class SpanProcessor:
    """Interface which allows hooks for SDK's `Span` start and end method
    invocations.

    Span processors can be registered directly using
    :func:`TracerProvider.add_span_processor` and they are invoked
    in the same order as they were registered.
    """

    def on_start(self, span: "Span") -> None:
        """Called when a :class:`opentelemetry.trace.Span` is started.

        This method is called synchronously on the thread that starts the
        span, therefore it should not block or throw an exception.

        Args:
            span: The :class:`opentelemetry.trace.Span` that just started.
        """

    def on_end(self, span: "Span") -> None:
        """Called when a :class:`opentelemetry.trace.Span` is ended.

        This method is called synchronously on the thread that ends the
        span, therefore it should not block or throw an exception.

        Args:
            span: The :class:`opentelemetry.trace.Span` that just ended.
        """

    def shutdown(self) -> None:
        """Called when a :class:`opentelemetry.sdk.trace.Tracer` is shutdown.
        """

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Export all ended spans to the configured Exporter that have not yet
        been exported.

        Args:
            timeout_millis: The maximum amount of time to wait for spans to be
                exported.

        Returns:
            False if the timeout is exceeded, True otherwise.
        """


class MultiSpanProcessor(SpanProcessor):
    """Implementation of :class:`SpanProcessor` that forwards all received
    events to a list of `SpanProcessor`.
    """

    def __init__(self):
        # use a tuple to avoid race conditions when adding a new span and
        # iterating through it on "on_start" and "on_end".
        self._span_processors = ()  # type: Tuple[SpanProcessor, ...]
        self._lock = threading.Lock()

    def add_span_processor(self, span_processor: SpanProcessor) -> None:
        """Adds a SpanProcessor to the list handled by this instance."""
        with self._lock:
            self._span_processors = self._span_processors + (span_processor,)

    def on_start(self, span: "Span") -> None:
        for sp in self._span_processors:
            sp.on_start(span)

    def on_end(self, span: "Span") -> None:
        for sp in self._span_processors:
            sp.on_end(span)

    def shutdown(self) -> None:
        for sp in self._span_processors:
            sp.shutdown()


class EventBase(abc.ABC):
    def __init__(self, name: str, timestamp: Optional[int] = None) -> None:
        self._name = name
        if timestamp is None:
            self._timestamp = time_ns()
        else:
            self._timestamp = timestamp

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    @abc.abstractmethod
    def attributes(self) -> types.Attributes:
        pass


class Event(EventBase):
    """A text annotation with a set of attributes.

    Args:
        name: Name of the event.
        attributes: Attributes of the event.
        timestamp: Timestamp of the event. If `None` it will filled
            automatically.
    """

    def __init__(
        self,
        name: str,
        attributes: types.Attributes = None,
        timestamp: Optional[int] = None,
    ) -> None:
        super().__init__(name, timestamp)
        self._attributes = attributes

    @property
    def attributes(self) -> types.Attributes:
        return self._attributes


class LazyEvent(EventBase):
    """A text annotation with a set of attributes.

    Args:
        name: Name of the event.
        event_formatter: Callable object that returns the attributes of the
            event.
        timestamp: Timestamp of the event. If `None` it will filled
            automatically.
    """

    def __init__(
        self,
        name: str,
        event_formatter: types.AttributesFormatter,
        timestamp: Optional[int] = None,
    ) -> None:
        super().__init__(name, timestamp)
        self._event_formatter = event_formatter

    @property
    def attributes(self) -> types.Attributes:
        return self._event_formatter()


class Span(trace_api.Span):
    """See `opentelemetry.trace.Span`.

    Users should create `Span` objects via the `Tracer` instead of this
    constructor.

    Args:
        name: The name of the operation this span represents
        context: The immutable span context
        parent: This span's parent, may be a `SpanContext` if the parent is
            remote, null if this is a root span
        sampler: The sampler used to create this span
        trace_config: TODO
        resource: Entity producing telemetry
        attributes: The span's attributes to be exported
        events: Timestamped events to be exported
        links: Links to other spans to be exported
        span_processor: `SpanProcessor` to invoke when starting and ending
            this `Span`.
    """

    # Initialize these lazily assuming most spans won't have them.
    _empty_attributes = BoundedDict(MAX_NUM_ATTRIBUTES)
    _empty_events = BoundedList(MAX_NUM_EVENTS)
    _empty_links = BoundedList(MAX_NUM_LINKS)

    def __init__(
        self,
        name: str,
        context: trace_api.SpanContext,
        parent: trace_api.ParentSpan = None,
        sampler: Optional[sampling.Sampler] = None,
        trace_config: None = None,  # TODO
        resource: None = None,
        attributes: types.Attributes = None,  # TODO
        events: Sequence[Event] = None,  # TODO
        links: Sequence[trace_api.Link] = (),
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        span_processor: SpanProcessor = SpanProcessor(),
        instrumentation_info: InstrumentationInfo = None,
        set_status_on_exception: bool = True,
    ) -> None:

        self.name = name
        self.context = context
        self.parent = parent
        self.sampler = sampler
        self.trace_config = trace_config
        self.resource = resource
        self.kind = kind
        self._set_status_on_exception = set_status_on_exception

        self.span_processor = span_processor
        self.status = None
        self._lock = threading.Lock()

        if attributes is None:
            self.attributes = Span._empty_attributes
        else:
            self.attributes = BoundedDict.from_map(
                MAX_NUM_ATTRIBUTES, attributes
            )

        if events is None:
            self.events = Span._empty_events
        else:
            self.events = BoundedList.from_seq(MAX_NUM_EVENTS, events)

        if links is None:
            self.links = Span._empty_links
        else:
            self.links = BoundedList.from_seq(MAX_NUM_LINKS, links)

        self._end_time = None  # type: Optional[int]
        self._start_time = None  # type: Optional[int]
        self.instrumentation_info = instrumentation_info

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    def __repr__(self):
        return '{}(name="{}", context={})'.format(
            type(self).__name__, self.name, self.context
        )

    def __str__(self):
        return (
            '{}(name="{}", context={}, kind={}, '
            "parent={}, start_time={}, end_time={})"
        ).format(
            type(self).__name__,
            self.name,
            self.context,
            self.kind,
            repr(self.parent),
            util.ns_to_iso_str(self.start_time) if self.start_time else "None",
            util.ns_to_iso_str(self.end_time) if self.end_time else "None",
        )

    def get_context(self):
        return self.context

    def set_attribute(self, key: str, value: types.AttributeValue) -> None:
        with self._lock:
            if not self.is_recording_events():
                return
            has_ended = self.end_time is not None
            if not has_ended:
                if self.attributes is Span._empty_attributes:
                    self.attributes = BoundedDict(MAX_NUM_ATTRIBUTES)
        if has_ended:
            logger.warning("Setting attribute on ended span.")
            return

        if not key:
            logger.warning("invalid key (empty or null)")
            return

        if isinstance(value, Sequence):
            error_message = self._check_attribute_value_sequence(value)
            if error_message is not None:
                logger.warning("%s in attribute value sequence", error_message)
                return
        elif not isinstance(value, (bool, str, int, float)):
            logger.warning("invalid type for attribute value")
            return

        self.attributes[key] = value

    @staticmethod
    def _check_attribute_value_sequence(sequence: Sequence) -> Optional[str]:
        """
        Checks if sequence items are valid and are of the same type
        """
        if len(sequence) == 0:
            return None

        first_element_type = type(sequence[0])

        if first_element_type not in (bool, str, int, float):
            return "invalid type"

        for element in sequence:
            if not isinstance(element, first_element_type):
                return "different type"
        return None

    def _add_event(self, event: EventBase) -> None:
        with self._lock:
            if not self.is_recording_events():
                return
            has_ended = self.end_time is not None
            if not has_ended:
                if self.events is Span._empty_events:
                    self.events = BoundedList(MAX_NUM_EVENTS)
        if has_ended:
            logger.warning("Calling add_event() on an ended span.")
            return
        self.events.append(event)

    def add_event(
        self,
        name: str,
        attributes: types.Attributes = None,
        timestamp: Optional[int] = None,
    ) -> None:
        if attributes is None:
            attributes = Span._empty_attributes
        self._add_event(
            Event(
                name=name,
                attributes=attributes,
                timestamp=time_ns() if timestamp is None else timestamp,
            )
        )

    def add_lazy_event(
        self,
        name: str,
        event_formatter: types.AttributesFormatter,
        timestamp: Optional[int] = None,
    ) -> None:
        self._add_event(
            LazyEvent(
                name=name,
                event_formatter=event_formatter,
                timestamp=time_ns() if timestamp is None else timestamp,
            )
        )

    def start(self, start_time: Optional[int] = None) -> None:
        with self._lock:
            if not self.is_recording_events():
                return
            has_started = self.start_time is not None
            if not has_started:
                self._start_time = (
                    start_time if start_time is not None else time_ns()
                )
        if has_started:
            logger.warning("Calling start() on a started span.")
            return
        self.span_processor.on_start(self)

    def end(self, end_time: Optional[int] = None) -> None:
        with self._lock:
            if not self.is_recording_events():
                return
            if self.start_time is None:
                raise RuntimeError("Calling end() on a not started span.")
            has_ended = self.end_time is not None
            if not has_ended:
                if self.status is None:
                    self.status = Status(canonical_code=StatusCanonicalCode.OK)

                self._end_time = (
                    end_time if end_time is not None else time_ns()
                )

        if has_ended:
            logger.warning("Calling end() on an ended span.")
            return

        self.span_processor.on_end(self)

    def update_name(self, name: str) -> None:
        with self._lock:
            has_ended = self.end_time is not None
        if has_ended:
            logger.warning("Calling update_name() on an ended span.")
            return
        self.name = name

    def is_recording_events(self) -> bool:
        return True

    def set_status(self, status: trace_api.Status) -> None:
        with self._lock:
            has_ended = self.end_time is not None
        if has_ended:
            logger.warning("Calling set_status() on an ended span.")
            return
        self.status = status

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Ends context manager and calls `end` on the `Span`."""

        if (
            self.status is None
            and self._set_status_on_exception
            and exc_val is not None
        ):

            self.set_status(
                Status(
                    canonical_code=StatusCanonicalCode.UNKNOWN,
                    description="{}: {}".format(exc_type.__name__, exc_val),
                )
            )

        super().__exit__(exc_type, exc_val, exc_tb)


def generate_span_id() -> int:
    """Get a new random span ID.

    Returns:
        A random 64-bit int for use as a span ID
    """
    return random.getrandbits(64)


def generate_trace_id() -> int:
    """Get a new random trace ID.

    Returns:
        A random 128-bit int for use as a trace ID
    """
    return random.getrandbits(128)


class Tracer(trace_api.Tracer):
    """See `opentelemetry.trace.Tracer`.

    Args:
        name: The name of the tracer.
        shutdown_on_exit: Register an atexit hook to shut down the tracer when
            the application exits.
    """

    def __init__(
        self,
        source: "TracerProvider",
        instrumentation_info: InstrumentationInfo,
    ) -> None:
        self.source = source
        self.instrumentation_info = instrumentation_info

    def get_current_span(self):
        return self.source.get_current_span()

    def start_as_current_span(
        self,
        name: str,
        parent: trace_api.ParentSpan = trace_api.Tracer.CURRENT_SPAN,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: Optional[types.Attributes] = None,
        links: Sequence[trace_api.Link] = (),
    ) -> Iterator[trace_api.Span]:
        span = self.start_span(name, parent, kind, attributes, links)
        return self.use_span(span, end_on_exit=True)

    def start_span(  # pylint: disable=too-many-locals
        self,
        name: str,
        parent: trace_api.ParentSpan = trace_api.Tracer.CURRENT_SPAN,
        kind: trace_api.SpanKind = trace_api.SpanKind.INTERNAL,
        attributes: Optional[types.Attributes] = None,
        links: Sequence[trace_api.Link] = (),
        start_time: Optional[int] = None,
        set_status_on_exception: bool = True,
    ) -> trace_api.Span:
        if parent is Tracer.CURRENT_SPAN:
            parent = self.get_current_span()

        parent_context = parent
        if isinstance(parent_context, trace_api.Span):
            parent_context = parent.get_context()

        if parent_context is not None and not isinstance(
            parent_context, trace_api.SpanContext
        ):
            raise TypeError

        if parent_context is None or not parent_context.is_valid():
            parent = parent_context = None
            trace_id = generate_trace_id()
            trace_flags = None
            trace_state = None
        else:
            trace_id = parent_context.trace_id
            trace_flags = parent_context.trace_flags
            trace_state = parent_context.trace_state

        context = trace_api.SpanContext(
            trace_id,
            generate_span_id(),
            is_remote=False,
            trace_flags=trace_flags,
            trace_state=trace_state,
        )

        # The sampler decides whether to create a real or no-op span at the
        # time of span creation. No-op spans do not record events, and are not
        # exported.
        # The sampler may also add attributes to the newly-created span, e.g.
        # to include information about the sampling decision.
        sampling_decision = self.source.sampler.should_sample(
            parent_context,
            context.trace_id,
            context.span_id,
            name,
            attributes,
            links,
        )

        if sampling_decision.sampled:
            options = context.trace_flags | trace_api.TraceFlags.SAMPLED
            context.trace_flags = trace_api.TraceFlags(options)
            if attributes is None:
                span_attributes = sampling_decision.attributes
            else:
                # apply sampling decision attributes after initial attributes
                span_attributes = attributes.copy()
                span_attributes.update(sampling_decision.attributes)
            span = Span(
                name=name,
                context=context,
                parent=parent,
                sampler=self.source.sampler,
                resource=self.source.resource,
                attributes=span_attributes,
                span_processor=self.source._active_span_processor,  # pylint:disable=protected-access
                kind=kind,
                links=links,
                instrumentation_info=self.instrumentation_info,
                set_status_on_exception=set_status_on_exception,
            )
            span.start(start_time=start_time)
        else:
            span = trace_api.DefaultSpan(context=context)
        return span

    @contextmanager
    def use_span(
        self, span: trace_api.Span, end_on_exit: bool = False
    ) -> Iterator[trace_api.Span]:
        try:
            token = context_api.attach(context_api.set_value(SPAN_KEY, span))
            try:
                yield span
            finally:
                context_api.detach(token)

        except Exception as error:  # pylint: disable=broad-except
            if (
                span.status is None
                and span._set_status_on_exception  # pylint:disable=protected-access  # noqa
            ):
                span.set_status(
                    Status(
                        canonical_code=StatusCanonicalCode.UNKNOWN,
                        description="{}: {}".format(
                            type(error).__name__, error
                        ),
                    )
                )

            raise

        finally:
            if end_on_exit:
                span.end()


class TracerProvider(trace_api.TracerProvider):
    def __init__(
        self,
        sampler: sampling.Sampler = trace_api.sampling.ALWAYS_ON,
        resource: Resource = Resource.create_empty(),
        shutdown_on_exit: bool = True,
    ):
        self._active_span_processor = MultiSpanProcessor()
        self.resource = resource
        self.sampler = sampler
        self._atexit_handler = None
        if shutdown_on_exit:
            self._atexit_handler = atexit.register(self.shutdown)

    def get_tracer(
        self,
        instrumenting_module_name: str,
        instrumenting_library_version: str = "",
    ) -> "trace_api.Tracer":
        if not instrumenting_module_name:  # Reject empty strings too.
            instrumenting_module_name = "ERROR:MISSING MODULE NAME"
            logger.error("get_tracer called with missing module name.")
        return Tracer(
            self,
            InstrumentationInfo(
                instrumenting_module_name, instrumenting_library_version
            ),
        )

    @staticmethod
    def get_current_span() -> Span:
        return context_api.get_value(SPAN_KEY)  # type: ignore

    def add_span_processor(self, span_processor: SpanProcessor) -> None:
        """Registers a new :class:`SpanProcessor` for this `TracerProvider`.

        The span processors are invoked in the same order they are registered.
        """

        # no lock here because MultiSpanProcessor.add_span_processor is
        # thread safe
        self._active_span_processor.add_span_processor(span_processor)

    def shutdown(self):
        """Shut down the span processors added to the tracer."""
        self._active_span_processor.shutdown()
        if self._atexit_handler is not None:
            atexit.unregister(self._atexit_handler)
            self._atexit_handler = None
