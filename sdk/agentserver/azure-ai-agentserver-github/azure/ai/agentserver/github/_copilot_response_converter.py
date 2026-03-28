# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Non-streaming response conversion for the Copilot adapter.

Streaming SSE events are built inline in ``CopilotAdapter._run_streaming``
using dict-based construction (matching the proven hosted-agent-cli pattern).
This module provides only the non-streaming ``CopilotResponseConverter``.
"""
import datetime
from typing import Optional

from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponsesAssistantMessageItemResource,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class CopilotResponseConverter:
    """Builds a non-streaming OpenAI Response from the final assistant text."""

    @staticmethod
    def to_response(
        text: str,
        context: AgentRunContext,
        extra_output: Optional[list] = None,
    ) -> OpenAIResponse:
        """Build a complete Response object from the final assistant text.

        If *text* is empty, a fallback message is used so the response is
        never blank.

        :param extra_output: Additional output items (e.g. MCP OAuth consent
            requests) appended after the message item.
        """
        item_id = context.id_generator.generate_message_id()
        if not text.strip():
            text = "(No response text was produced by the agent.)"

        output = [
            ResponsesAssistantMessageItemResource(
                id=item_id,
                status="completed",
                content=[
                    ItemContentOutputText(text=text, annotations=[]),
                ],
            )
        ]
        if extra_output:
            output.extend(extra_output)

        return OpenAIResponse(  # type: ignore[call-overload]
            id=context.response_id,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            output=output,
        )
