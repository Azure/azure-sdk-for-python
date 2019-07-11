# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import abc
from abc import abstractmethod

try:
    ABC = abc.ABC
except AttributeError:  # Python 2.7, abc exists, but not ABC
    ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})  # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Optional


class AbstractSpan(ABC):
    @abstractmethod
    def __init__(self, span=None, name=None):
        # type: (Optional[Any], Optional[str]) -> None
        """
        If a span is given wraps the span. Else a new span is created.
        The optional arguement name is given to the new span.
        """
        pass

    @abstractmethod
    def span(self, name="child_span"):
        # type: (Optional[str]) -> AbstractSpan
        """
        Create a child span for the current span and append it to the child spans list.
        The child span must be wrapped by an implementation of AbstractSpan
        """
        pass

    @abstractmethod
    def start(self):
        # type: () -> None
        """Set the start time for a span."""
        pass

    @abstractmethod
    def finish(self):
        # type: () -> None
        """Set the end time for a span."""
        pass

    @abstractmethod
    def to_header(self):
        # type: () -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        """
        pass

    @property
    @abstractmethod
    def span_instance(self):
        # type: () -> Any
        """
        Returns the span the class is wrapping.
        """
        pass

    @classmethod
    @abstractmethod
    def from_header(cls, headers):
        # type: (Dict[str, str]) -> Any
        """
        Given a dictionary returns a new tracer with the span context
        extracted from that dictionary.

        :param headers: A dictionary of the request header as key value pairs.
        :type headers: Dict
        """
        pass

    @classmethod
    @abstractmethod
    def get_current_span(cls):
        # type: () -> Any
        """
        Get the current span from the execution context. Return None otherwise.
        """
        pass

    @classmethod
    @abstractmethod
    def get_current_tracer(cls):
        # type: () -> Any
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        pass

    @classmethod
    @abstractmethod
    def set_current_span(cls, span):
        # type: (Any) -> None
        """
        Set the given span as the current span in the execution context.
        """
        pass

    @classmethod
    @abstractmethod
    def set_current_tracer(cls, tracer):
        # type: (Any) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        """
        pass
