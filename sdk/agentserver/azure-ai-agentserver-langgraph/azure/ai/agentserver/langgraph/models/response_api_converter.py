# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="call-overload,override"
"""Base interface for converting between LangGraph internal state and OpenAI-style responses.

A ResponseAPIConverter implementation bridges:
  1. Incoming CreateResponse (wrapped in AgentRunContext) -> GraphInputArguments to invoke graph
  2. Graph output -> final non-streaming Response
  3. Streaming graph output events -> ResponseStreamEvent sequence

Concrete implementations should:
  * Decide and document the shape of input arguments they return in convert_request
  * Handle aggregation, error mapping, and metadata propagation in convert_response_non_stream
  * Incrementally translate async stream_state items in convert_response_stream

Do NOT perform network I/O directly inside these methods (other than awaiting the
provided async iterator). Keep them pure transformation layers so they are testable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterable, AsyncIterator, Dict, TypedDict, Union

from langgraph.types import Command

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from .._context import LanggraphRunContext


class GraphInputArguments(TypedDict):
    """TypedDict for LangGraph input arguments."""
    input: Union[Dict[str, Any], Command, None]
    config: Dict[str, Any]
    context: LanggraphRunContext
    stream_mode: str


class ResponseAPIConverter(ABC):
    """
    Abstract base class for LangGraph input/output <-> response conversion.

    Orchestrates the conversions

    :meta private:
    """
    @abstractmethod
    async def convert_request(self, context: LanggraphRunContext) -> GraphInputArguments:
        """Convert the incoming request to a serializable dict for LangGraph.

        This is a convenience wrapper around request_to_state that only returns
        dict states, raising ValueError if a Command is returned instead.

        :param context: The context for the agent run.
        :type context: LanggraphRunContext

        :return: The initial LangGraph arguments
        :rtype: GraphInputArguments
        """

    @abstractmethod
    async def convert_response_non_stream(self, output: Any, context: LanggraphRunContext) -> Response:
        """Convert the completed LangGraph state into a final non-streaming Response object.

        This is a convenience wrapper around state_to_response that retrieves
        the current state snapshot asynchronously.

        :param output: The LangGraph output to convert.
        :type output: Any
        :param context: The context for the agent run.
        :type context: LanggraphRunContext

        :return: The final non-streaming Response object.
        :rtype: Response
        """

    @abstractmethod
    async def convert_response_stream(
            self,
            output: AsyncIterator[Union[Dict[str, Any], Any]],
            context: LanggraphRunContext,
        ) -> AsyncIterable[ResponseStreamEvent]:
        """Convert an async iterator of LangGraph stream events into stream events.

        This is a convenience wrapper around state_to_response_stream that retrieves
        the current stream of state updates asynchronously.

        :param output: An async iterator yielding LangGraph stream events
        :type output: AsyncIterator[Dict[str, Any] | Any]
        :param context: The context for the agent run.
        :type context: LanggraphRunContext

        :return: An async iterable yielding ResponseStreamEvent objects.
        :rtype: AsyncIterable[ResponseStreamEvent]
        """
        raise NotImplementedError
