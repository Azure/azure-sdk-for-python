# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Callable, Dict, List, Optional

from pyrit.models import (
    PromptRequestResponse,
    construct_response_from_request,
)
from pyrit.prompt_target import PromptChatTarget

logger = logging.getLogger(__name__)


class _CallbackChatTarget(PromptChatTarget):
    def __init__(
        self,
        *,
        callback: Callable[[List[Dict], bool, Optional[str], Optional[Dict[str, Any]]], Dict],
        stream: bool = False,
    ) -> None:
        """
        Initializes an instance of the _CallbackChatTarget class.

        It is intended to be used with PyRIT where users define a callback function
        that handles sending a prompt to a target and receiving a response.
        The _CallbackChatTarget class is a wrapper around the callback function that allows it to be used
        as a target in the PyRIT framework.
        For that reason, it merely handles additional functionality such as memory.

        Args:
            callback (Callable): The callback function that sends a prompt to a target and receives a response.
            stream (bool, optional): Indicates whether the target supports streaming. Defaults to False.
        """
        PromptChatTarget.__init__(self)
        self._callback = callback
        self._stream = stream

    async def send_prompt_async(self, *, prompt_request: PromptRequestResponse) -> PromptRequestResponse:

        self._validate_request(prompt_request=prompt_request)
        request = prompt_request.request_pieces[0]

        messages = self._memory.get_chat_messages_with_conversation_id(conversation_id=request.conversation_id)

        messages.append(request.to_chat_message())

        # Extract context from request labels if available
        # The context is stored in memory labels when the prompt is sent by orchestrator
        context_dict = {}
        if hasattr(request, "labels") and request.labels and "context" in request.labels:
            context_data = request.labels["context"]
            if context_data and isinstance(context_data, dict):
                # context_data is always a dict with 'contexts' list
                # Each context can have its own context_type and tool_name
                contexts = context_data.get("contexts", [])

                # Build context_dict to pass to callback
                context_dict = {"contexts": contexts}

                # Check if any context has agent-specific fields for logging
                has_agent_fields = any(
                    isinstance(ctx, dict)
                    and ("context_type" in ctx and "tool_name" in ctx and ctx["tool_name"] is not None)
                    for ctx in contexts
                )

                if has_agent_fields:
                    tool_names = [
                        ctx.get("tool_name") for ctx in contexts if isinstance(ctx, dict) and "tool_name" in ctx
                    ]
                    logger.debug(f"Extracted agent context: {len(contexts)} context source(s), tool_names={tool_names}")
                else:
                    logger.debug(f"Extracted model context: {len(contexts)} context source(s)")

        # response_context contains "messages", "stream", "session_state, "context"
        response = await self._callback(messages=messages, stream=self._stream, session_state=None, context=context_dict)  # type: ignore

        # Store token_usage before processing tuple
        token_usage = None
        if isinstance(response, dict) and "token_usage" in response:
            token_usage = response["token_usage"]

        if type(response) == tuple:
            response, tool_output = response
            request.labels["tool_calls"] = tool_output
            # Check for token_usage in the response dict from tuple
            if isinstance(response, dict) and "token_usage" in response:
                token_usage = response["token_usage"]

        response_text = response["messages"][-1]["content"]

        response_entry = construct_response_from_request(request=request, response_text_pieces=[response_text])

        # Add token_usage to the response entry's labels (not the request)
        if token_usage:
            response_entry.request_pieces[0].labels["token_usage"] = token_usage
            logger.debug(f"Captured token usage from callback: {token_usage}")

        return response_entry

    def _validate_request(self, *, prompt_request: PromptRequestResponse) -> None:
        if len(prompt_request.request_pieces) != 1:
            raise ValueError("This target only supports a single prompt request piece.")

        if prompt_request.request_pieces[0].converted_value_data_type != "text":
            raise ValueError("This target only supports text prompt input.")

    def is_json_response_supported(self) -> bool:
        """Indicates that this target supports JSON response format."""
        return False
