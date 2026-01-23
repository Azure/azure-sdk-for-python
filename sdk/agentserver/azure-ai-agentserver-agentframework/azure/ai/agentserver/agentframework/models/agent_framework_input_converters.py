# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=too-many-nested-blocks,too-many-return-statements,too-many-branches
# mypy: disable-error-code="no-redef"
from __future__ import annotations

from typing import Dict, List, Optional

from agent_framework import (
    AgentThread,
    ChatMessage,
    RequestInfoEvent,
    Role as ChatRole,
    WorkflowCheckpoint,
)
from agent_framework._types import TextContent

from azure.ai.agentserver.core.logger import get_logger

logger = get_logger()


class AgentFrameworkInputConverter:
    """Normalize inputs for agent.run.

    Accepts: str | List | None
    Returns: None | str | ChatMessage | list[str] | list[ChatMessage]
    """
    def __init__(self, *, hitl_helper=None) -> None:
        self._hitl_helper = hitl_helper

    async def transform_input(
        self,
        input: str | List[Dict] | None,
        agent_thread: Optional[AgentThread] = None,
        checkpoint: Optional[WorkflowCheckpoint] = None,
    ) -> str | ChatMessage | list[str] | list[ChatMessage] | None:
        logger.debug("Transforming input of type: %s", type(input))

        if input is None:
            return None

        if isinstance(input, str):
            return input

        if self._hitl_helper:
            # load pending requests from checkpoint and thread messages if available
            thread_messages = []
            if agent_thread and agent_thread.message_store:
                thread_messages = await agent_thread.message_store.list_messages()
            pending_hitl_requests = self._hitl_helper.get_pending_hitl_request(thread_messages, checkpoint)
            if pending_hitl_requests:
                logger.info("Pending HitL requests: %s", list(pending_hitl_requests.keys()))
                hitl_response = self._hitl_helper.validate_and_convert_hitl_response(
                    input,
                    pending_requests=pending_hitl_requests)
                if hitl_response:
                    return hitl_response

        return self._transform_input_internal(input)

    def _transform_input_internal(
        self,
        input: str | List[Dict] | None,
    ) -> str | ChatMessage | list[str] | list[ChatMessage] | None:
        try:
            if isinstance(input, list):
                messages: list[str | ChatMessage] = []

                for item in input:
                    # Case 1: ImplicitUserMessage with content as str or list of ItemContentInputText
                    if self._is_implicit_user_message(item):
                        content = item.get("content", None)
                        if isinstance(content, str):
                            messages.append(content)
                        elif isinstance(content, list):
                            text_parts: list[str] = []
                            for content_item in content:
                                text_content = self._extract_input_text(content_item)
                                if text_content:
                                    text_parts.append(text_content)
                            if text_parts:
                                messages.append(" ".join(text_parts))

                    # Case 2: Explicit message params (user/assistant/system)
                    elif (
                        item.get("type") == "message"
                        and item.get("role") is not None
                        and item.get("content") is not None
                    ):
                        role_map = {
                            "user": ChatRole.USER,
                            "assistant": ChatRole.ASSISTANT,
                            "system": ChatRole.SYSTEM,
                        }
                        role = role_map.get(item.get("role", "user"), ChatRole.USER)

                        content_text = ""
                        item_content = item.get("content", None)
                        if item_content and isinstance(item_content, list):
                            text_parts: list[str] = []
                            for content_item in item_content:
                                item_text = self._extract_input_text(content_item)
                                if item_text:
                                    text_parts.append(item_text)
                            content_text = " ".join(text_parts) if text_parts else ""
                        elif item_content and isinstance(item_content, str):
                            content_text = str(item_content)

                        if content_text:
                            messages.append(ChatMessage(role=role, text=content_text))

                # Determine the most natural return type
                if not messages:
                    return None
                if len(messages) == 1:
                    return messages[0]
                if all(isinstance(m, str) for m in messages):
                    return [m for m in messages if isinstance(m, str)]
                if all(isinstance(m, ChatMessage) for m in messages):
                    return [m for m in messages if isinstance(m, ChatMessage)]

                # Mixed content: coerce ChatMessage to str by extracting TextContent parts
                result: list[str] = []
                for msg in messages:
                    if isinstance(msg, ChatMessage):
                        text_parts: list[str] = []
                        for c in getattr(msg, "contents", []) or []:
                            if isinstance(c, TextContent):
                                text_parts.append(c.text)
                        result.append(" ".join(text_parts) if text_parts else str(msg))
                    else:
                        result.append(str(msg))
                return result

            raise TypeError(f"Unsupported input type: {type(input)}")
        except Exception as e:
            logger.error("Error processing messages: %s", e, exc_info=True)
            raise Exception(f"Error processing messages: {e}") from e  # pylint: disable=broad-exception-raised

    def _is_implicit_user_message(self, item: Dict) -> bool:
        return "content" in item and "role" not in item and "type" not in item

    def _extract_input_text(self, content_item: Dict) -> str:
        if content_item.get("type") == "input_text" and "text" in content_item:
            text_content = content_item.get("text")
            if isinstance(text_content, str):
                return text_content
        return None  # type: ignore

    def _validate_and_convert_hitl_response(
        self,
        pending_request: Dict,
        input: List[Dict],
    ) -> Optional[List[ChatMessage]]:
        if not self._hitl_helper:
            logger.warning("HitL helper not provided; cannot validate HitL response.")
            return None
        if isinstance(input, str):
            logger.warning("Expected list input for HitL response validation, got str.")
            return None
        if not isinstance(input, list) or len(input) != 1:
            logger.warning("Expected single-item list input for HitL response validation.")
            return None

        item = input[0]
        if item.get("type") != "function_call_output":
            logger.warning("Expected function_call_output type for HitL response validation.")
            return None
        call_id = item.get("call_id", None)
        if not call_id or call_id not in pending_request:
            logger.warning("Function call output missing valid call_id for HitL response validation.")
            return None
        request_info = pending_request[call_id]
        if isinstance(request_info, dict):
            request_info = RequestInfoEvent.from_dict(request_info)
        if not isinstance(request_info, RequestInfoEvent):
            logger.warning("No valid pending request info found for call_id: %s", call_id)
            return None

        return self._hitl_helper.convert_response(request_info, item)
