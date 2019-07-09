from abc import ABC, abstractmethod, abstractproperty, abstractstaticmethod


class AbstractSpan(ABC):
    @abstractmethod
    def __init__(self, span=None, name=None):
        # type: (Any, str) -> None
        """
        If a span is given wraps the span. Else a new span is created.
        The optional arguement name is given to the new span.
        """
        pass

    @abstractmethod
    def span(self, name="child_span"):
        # type: (str) -> AbstractSpan
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
    def to_header(self, headers):
        # type: (Dict[str, str]) -> Dict[str, str]
        """
        Returns a dictionary with the header labels and values.
        """
        pass

    @abstractmethod
    def from_header(self, headers):
        # type: (Dict[str, str]) -> Any
        """
        Given a dictionary returns a new tracer with the span context
        extracted from that dictionary.
        """
        pass

    @abstractproperty
    def span_instance(self):
        # type: () -> Any
        """
        Returns the span the class is wrapping.
        """
        pass

    @abstractstaticmethod
    def end_tracer(tracer):
        # type: (Any) -> None
        """
        If a tracer exists, exports and ends the tracer.
        """
        pass

    @abstractstaticmethod
    def get_current_span():
        # type: () -> AbstractSpan
        """
        Get the current span from the execution context. Return None otherwise.
        """
        pass

    @abstractstaticmethod
    def get_current_tracer():
        # type: () -> Any
        """
        Get the current tracer from the execution context. Return None otherwise.
        """
        pass

    @abstractstaticmethod
    def set_current_span(span):
        # type: (AbstractSpan) -> None
        """
        Set the given span as the current span in the execution context.
        """
        pass

    @abstractstaticmethod
    def set_current_tracer(tracer):
        # type: (Any) -> None
        """
        Set the given tracer as the current tracer in the execution context.
        """
        pass
