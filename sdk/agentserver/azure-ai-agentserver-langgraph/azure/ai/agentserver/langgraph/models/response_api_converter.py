# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="call-overload,override"
"""Base interface for converting between LangGraph internal state and OpenAI-style responses.

A LanggraphStateConverter implementation bridges:
  1. Incoming CreateResponse (wrapped in AgentRunContext) -> initial graph state
  2. Internal graph state -> final non-streaming Response
  3. Streaming graph state events -> ResponseStreamEvent sequence
  4. Declares which stream mode (if any) is supported for a given run context

Concrete implementations should:
  * Decide and document the shape of the state dict they return in request_to_state
  * Handle aggregation, error mapping, and metadata propagation in state_to_response
  * Incrementally translate async stream_state items in state_to_response_stream

Do NOT perform network I/O directly inside these methods (other than awaiting the
provided async iterator). Keep them pure transformation layers so they are testable.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, AsyncIterator, Dict, TypedDict, Union

from langgraph.types import Command, Interrupt, StateSnapshot

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class GraphInputArguments(TypedDict):
    """TypedDict for LangGraph input arguments."""
    input: Union[Dict[str, Any], Command, None]
    config: Dict[str, Any]
    context: Dict[str, Any]
    stream_mode: str


class ResponseAPIConverter(ABC):
    """
    Abstract base class for LangGraph input/output <-> response conversion.

    Orchestrates the conversions

    :meta private:
    """
    @abstractmethod
    async def convert_request(self, context: AgentRunContext) -> GraphInputArguments:
        """Convert the incoming request to a serializable dict for LangGraph.

        This is a convenience wrapper around request_to_state that only returns
        dict states, raising ValueError if a Command is returned instead.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The initial LangGraph arguments
        :rtype: GraphInputArguments
        """

    @abstractmethod
    async def convert_response_non_stream(self, output: Any, context: AgentRunContext) -> Response:
        """Convert the completed LangGraph state into a final non-streaming Response object.

        This is a convenience wrapper around state_to_response that retrieves
        the current state snapshot asynchronously.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The final non-streaming Response object.
        :rtype: Response
        """

    @abstractmethod
    async def convert_response_stream(self, output: Any, context: AgentRunContext) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Convert an async iterator of partial state updates into stream events.

        This is a convenience wrapper around state_to_response_stream that retrieves
        the current stream of state updates asynchronously.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: An async generator yielding ResponseStreamEvent objects.
        :rtype: AsyncGenerator[ResponseStreamEvent, None]
        """
