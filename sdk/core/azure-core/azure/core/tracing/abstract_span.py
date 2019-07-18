# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Protocol that defines what functions wrappers of tracing libraries should implement."""

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union

    from azure.core.pipeline.transport import HttpRequest, HttpResponse

try:
    from typing_extensions import Protocol
except ImportError:
    Protocol = object


class AbstractSpan(Protocol):
    """Wraps a span from a distributed tracing implementation."""

    def __init__(self, span=None, name=None):  # pylint: disable=super-init-not-called
        # type: (Optional[Any], Optional[str]) -> None
        """
        If a span is given wraps the span. Else a new span is created.
        The optional arguement name is given to the new span.
        """
        pass

    def span(self, name="child_span"):
        # type: (Optional[str]) -> AbstractSpan
        """
        Create a child span for the current span and append it to the child spans list.
        The child span must be wrapped by an implementation of AbstractSpan
        """
        pass

    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        pass

    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        pass

    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        """
        pass

    def add_attribute(self, key, value):
        # type: (str, Union[str, int]) -> None
        """
        Add attribute (key value pair) to the current span.

        :param key: The key of the key value pair
        :type key: str
        :param value: The value of the key value pair
        :type value: str
        """
        pass

    def set_http_attributes(self, request, response=None):
        # type: (HttpRequest, HttpResponse) -> None
        """
        Add correct attributes for a http client span.

        :param request: The request made
        :type request: HttpRequest
        :param response: The response received by the server. Is None if no response received.
        :type response: HttpResponse
        """
        pass

    @property
    def span_instance(self):
        # type: () -> Any
        """
        Returns the span the class is wrapping.
        """
        pass

    @classmethod
    def link(cls, headers):
        # type: (Dict[str, str]) -> None
        """
        Given a dictionary, extracts the context and links the context to the current tracer.

        :param headers: A dictionary of the request header as key value pairs.
        :type headers: dict
        """
        pass

    @classmethod
    def get_current_span(cls):
        # type: () -> Any
        """
        Get the current span from the execution context. Return None otherwise.
        """
        pass

    @classmethod
    def get_current_tracer(cls):
        # type: () -> Any
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        pass

    @classmethod
    def set_current_span(cls, span):
        # type: (Any) -> None
        """
        Set the given span as the current span in the execution context.
        """
        pass

    @classmethod
    def set_current_tracer(cls, tracer):
        # type: (Any) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        """
        pass
