# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Protocol that defines what functions wrappers of tracing libraries should implement."""
from enum import Enum

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union, Callable

    from azure.core.pipeline.transport import HttpRequest, HttpResponse

try:
    from typing_extensions import Protocol
except ImportError:
    Protocol = object  # type: ignore


class SpanKind(Enum):
    UNSPECIFIED = 1
    SERVER = 2
    CLIENT = 3
    PRODUCER = 4
    CONSUMER = 5
    INTERNAL = 6


class AbstractSpan(Protocol):
    """Wraps a span from a distributed tracing implementation."""

    def __init__(self, span=None, name=None):  # pylint: disable=super-init-not-called
        # type: (Optional[Any], Optional[str]) -> None
        """
        If a span is given wraps the span. Else a new span is created.
        The optional arguement name is given to the new span.
        """

    def span(self, name="child_span"):
        # type: (Optional[str]) -> AbstractSpan
        """
        Create a child span for the current span and append it to the child spans list.
        The child span must be wrapped by an implementation of AbstractSpan
        """

    @property
    def kind(self):
        # type: () -> Optional[SpanKind]
        """Get the span kind of this span."""

    @kind.setter
    def kind(self, value):
        # type: (SpanKind) -> None
        """Set the span kind of this span."""

    def __enter__(self):
        """Start a span."""

    def __exit__(self, exception_type, exception_value, traceback):
        """Finish a span."""

    def start(self):
        # type: () -> None
        """Set the start time for a span."""

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""

    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        """

    def add_attribute(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: str
        """

    def set_http_attributes(self, request, response=None):
        # type: (HttpRequest, HttpResponse) -> None
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: HttpRequest
        :param response: The response received by the server. Is None if no response received.
        :type response: HttpResponse
        """

    def get_trace_parent(self):
        # type: () -> str
        """Return traceparent string.

        :return: a traceparent string
        :rtype: str
        """

    @property
    def span_instance(self):
        # type: () -> Any
        """
        Returns the span the class is wrapping.
        """

    @classmethod
    def link(cls, traceparent):
        # type: (Dict[str, str]) -> None
        """
        Given a traceparent, extracts the context and links the context to the current tracer.

        :param traceparent: A string representing a traceparent
        :type traceparent: str
        """

    @classmethod
    def link_from_headers(cls, headers):
        # type: (Dict[str, str]) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A dictionary of the request header as key value pairs.
        :type headers: dict
        """

    @classmethod
    def get_current_span(cls):
        # type: () -> Any
        """
        Get the current span from the execution context. Return None otherwise.
        """

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Any
        """
        Get the current tracer from the execution context. Return None otherwise.
        """

    @classmethod
    def set_current_span(cls, span):
        # type: (Any) -> None
        """
        Set the given span as the current span in the execution context.
        """

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Any) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        """

    @classmethod
    def with_current_context(cls, func):
        # type: (Callable) -> Callable
        """Passes the current spans to the new context the function will be run in.

        :param func: The function that will be run in the new context
        :return: The target the pass in instead of the function
        """
