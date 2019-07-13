from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.tracing.context import tracing_context
from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.tracing.common import set_span_contexts
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.settings import settings

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, TypeVar

    HTTPResponseType = TypeVar("HTTPResponseType")
    HTTPRequestType = TypeVar("HTTPRequestType")


class DistributedTracingPolicy(SansIOHTTPPolicy):
    """The policy to create spans for Azure Calls"""

    def __init__(self, name_of_spans="Azure Call"):
        # type: (str, str, str) -> None
        self.name_of_child_span = name_of_spans
        self.parent_span_dict = {}

    def set_header(self, request, span):
        # type: (PipelineRequest[HTTPRequestType], Any) -> None
        """
        Sets the header information on the span.
        """
        headers = span.to_header()
        request.http_request.headers.update(headers)

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], Any) -> None
        parent_span = tracing_context.current_span.get()  # type: AbstractSpan

        if parent_span is None:
            return

        only_propagate = settings.tracing_should_only_propagate()
        if only_propagate:
            self.set_header(request, parent_span)
            return

        child = parent_span.span(name=self.name_of_child_span)
        child.start()

        set_span_contexts(child)
        self.parent_span_dict[child] = parent_span
        self.set_header(request, child)

    def end_span(self, request, response=None):
        # type: (PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, HTTPResponseType]) -> None
        span = tracing_context.current_span.get()  # type: AbstractSpan
        only_propagate = settings.tracing_should_only_propagate()
        if span and not only_propagate:
            # span.add_attribute("http.url", request.http_request)
            if response:
                span.add_attribute("status_code", response.http_response.status_code)
            else:
                span.add_attribute("status_code", 522)
            span.finish()
            set_span_contexts(self.parent_span_dict[span])

    def on_response(self, request, response, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, HTTPResponseType], Any) -> None
        self.end_span(request, response=response)

    def on_exception(self, request, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], Any) -> bool
        self.end_span(request)
