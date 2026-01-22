# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Callable, Dict, List, Optional

from openai import RateLimitError as OpenAIRateLimitError
from pyrit.exceptions import (
    EmptyResponseException,
    RateLimitException,
    pyrit_target_retry,
)
from pyrit.models import (
    Message,
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
        retry_enabled: bool = True,
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
            retry_enabled (bool, optional): Enables retry with exponential backoff for rate limit errors
                and empty responses using PyRIT's @pyrit_target_retry decorator. Defaults to True.
        """
        PromptChatTarget.__init__(self)
        self._callback = callback
        self._stream = stream
        self._retry_enabled = retry_enabled

    async def send_prompt_async(self, *, message: Message) -> List[Message]:
        """
        Sends a prompt to the callback target and returns the response.

        When retry_enabled=True (default), this method will retry on rate limit errors
        and empty responses using PyRIT's exponential backoff strategy.

        Args:
            message: The message to send to the target.

        Returns:
            A list containing the response message.

        Raises:
            RateLimitException: When rate limit is hit and retries are exhausted.
            EmptyResponseException: When callback returns empty response and retries are exhausted.
        """
        if self._retry_enabled:
            return await self._send_prompt_with_retry(message=message)
        else:
            return await self._send_prompt_impl(message=message)

    @pyrit_target_retry
    async def _send_prompt_with_retry(self, *, message: Message) -> List[Message]:
        """
        Internal method with retry decorator applied.

        This method wraps _send_prompt_impl with PyRIT's retry logic for handling
        rate limit errors and empty responses with exponential backoff.
        """
        return await self._send_prompt_impl(message=message)

    async def _send_prompt_impl(self, *, message: Message) -> List[Message]:
        """
        Core implementation of send_prompt_async.

        Handles conversation history, context extraction, callback invocation,
        and response processing. Translates OpenAI RateLimitError to PyRIT's
        RateLimitException for retry handling.
        """
        self._validate_request(prompt_request=message)
        request = message.get_piece(0)

        # Get conversation history and convert to chat message format
        conversation_history = self._memory.get_conversation(conversation_id=request.conversation_id)
        messages: List[Dict[str, str]] = []
        for msg in conversation_history:
            for piece in msg.message_pieces:
                messages.append({
                    "role": piece.api_role if hasattr(piece, 'api_role') else str(piece.role),
                    "content": piece.converted_value or piece.original_value or ""
                })

        # Add current request
        messages.append({
            "role": request.api_role if hasattr(request, 'api_role') else str(request.role),
            "content": request.converted_value or request.original_value or ""
        })

        logger.debug(f"Sending the following prompt to the prompt target: {request}")

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

        # Invoke callback with exception translation for retry handling
        try:
            # response_context contains "messages", "stream", "session_state, "context"
            response = await self._callback(messages=messages, stream=self._stream, session_state=None, context=context_dict)  # type: ignore
        except OpenAIRateLimitError as e:
            # Translate OpenAI RateLimitError to PyRIT RateLimitException for retry decorator
            logger.warning(f"Rate limit error from callback, translating for retry: {e}")
            raise RateLimitException(status_code=429, message=str(e)) from e
        except Exception as e:
            # Check for rate limit indicators in error message (fallback detection)
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str or "too many requests" in error_str:
                logger.warning(f"Rate limit detected in error message, translating for retry: {e}")
                raise RateLimitException(status_code=429, message=str(e)) from e
            raise

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

        # Check for empty response and raise EmptyResponseException for retry
        if not response_text or (isinstance(response_text, str) and response_text.strip() == ""):
            logger.warning("Callback returned empty response")
            raise EmptyResponseException(message="Callback returned empty response")

        response_entry = construct_response_from_request(request=request, response_text_pieces=[response_text])

        # Add token_usage to the response entry's labels (not the request)
        if token_usage:
            response_entry.get_piece(0).labels["token_usage"] = token_usage
            logger.debug(f"Captured token usage from callback: {token_usage}")

        logger.debug("Received the following response from the prompt target" + f"{response_text}")
        return [response_entry]

    def _validate_request(self, *, prompt_request: Message) -> None:
        if len(prompt_request.message_pieces) != 1:
            raise ValueError("This target only supports a single prompt request piece.")

        if prompt_request.get_piece(0).converted_value_data_type != "text":
            raise ValueError("This target only supports text prompt input.")

    def is_json_response_supported(self) -> bool:
        """Indicates that this target supports JSON response format."""
        return False
