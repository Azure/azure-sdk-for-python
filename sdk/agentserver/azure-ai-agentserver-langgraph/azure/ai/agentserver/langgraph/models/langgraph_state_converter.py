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

import datetime
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, AsyncIterator, Dict, cast

from azure.ai.agentserver.core.models import Response, ResponseStreamEvent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .langgraph_request_converter import LangGraphRequestConverter
from .langgraph_response_converter import LangGraphResponseConverter
from .langgraph_stream_response_converter import LangGraphStreamResponseConverter


class LanggraphStateConverter(ABC):
    """
    Abstract base class for LangGraph state <-> response conversion.

    :meta private:
    """

    @abstractmethod
    def get_stream_mode(self, context: AgentRunContext) -> str:
        """Return a string indicating streaming mode for this run.

        Examples: "values", "updates", "messages", "custom", "debug".
        Implementations may inspect context.request.stream or other flags.
        Must be fast and side-effect free.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The streaming mode as a string.
        :rtype: str
        """

    @abstractmethod
    def request_to_state(self, context: AgentRunContext) -> Dict[str, Any]:
        """Convert the incoming request (via context) to an initial LangGraph state.

        Return a serializable dict that downstream graph execution expects.
        Should not mutate the context. Raise ValueError on invalid input.

        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The initial LangGraph state as a dictionary.
        :rtype: Dict[str, Any]
        """

    @abstractmethod
    def state_to_response(self, state: Any, context: AgentRunContext) -> Response:
        """Convert a completed LangGraph state into a final non-streaming Response object.

        Implementations must construct and return an models.Response.
        The returned object should include output items, usage (if available),
        and reference the agent / conversation from context.

        :param state: The completed LangGraph state.
        :type state: Any
        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: The final non-streaming Response object.
        :rtype: Response
        """

    @abstractmethod
    async def state_to_response_stream(
        self, stream_state: AsyncIterator[Dict[str, Any] | Any], context: AgentRunContext
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        """Convert an async iterator of partial state updates into stream events.

        Yield ResponseStreamEvent objects in the correct order. Implementations
        are responsible for emitting lifecycle events (created, in_progress, deltas,
        completed, errors) consistent with the OpenAI Responses streaming contract.

        :param stream_state: An async iterator of partial LangGraph state updates.
        :type stream_state: AsyncIterator[Dict[str, Any] | Any]
        :param context: The context for the agent run.
        :type context: AgentRunContext

        :return: An async generator yielding ResponseStreamEvent objects.
        :rtype: AsyncGenerator[ResponseStreamEvent, None]
        """


class LanggraphMessageStateConverter(LanggraphStateConverter):
    """Converter implementation for langgraph built-in MessageState."""

    def get_stream_mode(self, context: AgentRunContext) -> str:
        if context.request.get("stream"):
            return "messages"
        return "updates"

    def request_to_state(self, context: AgentRunContext) -> Dict[str, Any]:
        converter = LangGraphRequestConverter(context.request)
        return converter.convert()

    def state_to_response(self, state: Any, context: AgentRunContext) -> Response:
        converter = LangGraphResponseConverter(context, state)
        output = converter.convert()

        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()

        # Create Response with all required fields
        response: Response = cast(Response, {
            "object": "response",
            "id": context.response_id,
            "agent": agent_id,
            "conversation": conversation,
            "metadata": context.request.get("metadata", {}),
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "output": output,
            "temperature": context.request.get("temperature", 1.0),
            "top_p": context.request.get("top_p", 1.0),
            "user": context.request.get("user", ""),
            "instructions": context.request.get("instructions", ""),
            "parallel_tool_calls": context.request.get("parallel_tool_calls", True),
        })
        return response

    async def state_to_response_stream(
        self, stream_state: AsyncIterator[Dict[str, Any] | Any], context: AgentRunContext
    ) -> AsyncGenerator[ResponseStreamEvent, None]:
        response_converter = LangGraphStreamResponseConverter(stream_state, context)
        async for result in response_converter.convert():
            yield result
